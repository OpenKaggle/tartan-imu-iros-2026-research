"""app.py — TartanIMU Challenge · per-sequence & per-platform scoring (HF Space / Gradio).

Participants upload their submission CSV and immediately get every number the technical
report asks for: Table III (overall), Table IV (per platform) and Table V (all 89 sequences).

Ground truth and the team whitelist live in a PRIVATE HF Dataset and are read with a token
from the Space's secrets. This file is public; the data is not.

Environment variables (Space -> Settings -> Variables and secrets):
  SOLUTION_REPO      private dataset repo id,
                     e.g. "Tartan-IMU/IROS-Tartan-IMU-Challenge-test-solution"
  SOLUTION_FILE      default "full_solution.csv"
  TEAMS_FILE         default "teams.txt", one Kaggle team name per line, '#' = comment
  LEDGER_REPO        where the submission ledger is stored (default: SOLUTION_REPO)
  HF_TOKEN           (secret) read access to the above repo
  DAILY_LIMIT        default 5
  REQUIRE_TEAMS      default true — refuse to start if the whitelist is missing
  STRICT_TEAM_MATCH  default false — tolerate case/space differences, record canonical name
  LOCAL_SOLUTION / LOCAL_TEAMS   local paths, development only
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import re
import tempfile
import threading
import time
import unicodedata

import gradio as gr
import pandas as pd

from scorer import (ROW_ID, RTE_DELTA, SubmissionError, overall_table, platform_table,
                    score_detailed, sequence_table, validate)

SOLUTION_REPO = os.environ.get("SOLUTION_REPO", "")
SOLUTION_FILE = os.environ.get("SOLUTION_FILE", "full_solution.csv")
TEAMS_FILE = os.environ.get("TEAMS_FILE", "teams.txt")
LEDGER_REPO = os.environ.get("LEDGER_REPO", SOLUTION_REPO)
HF_TOKEN = os.environ.get("HF_TOKEN", "")
DAILY_LIMIT = int(os.environ.get("DAILY_LIMIT", "5"))
LOCAL_SOLUTION = os.environ.get("LOCAL_SOLUTION", "")
LOCAL_TEAMS = os.environ.get("LOCAL_TEAMS", "")
REQUIRE_TEAMS = os.environ.get("REQUIRE_TEAMS", "true").lower() not in ("0", "false", "no")
STRICT_TEAM_MATCH = os.environ.get("STRICT_TEAM_MATCH", "false").lower() in ("1", "true", "yes")
LEDGER_FILE = "ledger.jsonl"
MAX_BYTES = 40 * 1024 * 1024

_lock = threading.Lock()


def _hf_get(repo: str, fname: str) -> str:
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo_id=repo, filename=fname, repo_type="dataset", token=HF_TOKEN)


def load_solution() -> pd.DataFrame:
    if LOCAL_SOLUTION:
        return pd.read_csv(LOCAL_SOLUTION)
    if not (SOLUTION_REPO and HF_TOKEN):
        raise RuntimeError("SOLUTION_REPO / HF_TOKEN are not configured.")
    return pd.read_csv(_hf_get(SOLUTION_REPO, SOLUTION_FILE))


def load_teams() -> list:
    p = LOCAL_TEAMS if LOCAL_TEAMS else (
        _hf_get(SOLUTION_REPO, TEAMS_FILE) if (SOLUTION_REPO and HF_TOKEN) else "")
    if not p or not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.strip() and not line.lstrip().startswith("#"):
            out.append(line.strip())
    return out


def team_key(s: str) -> str:
    """Normalisation key: NFKC + collapsed whitespace + lowercase."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip().lower()


SOLUTION = load_solution()
SOLUTION[ROW_ID] = SOLUTION[ROW_ID].astype(str)
EXPECTED_IDS = set(SOLUTION[ROW_ID])
N_EXPECTED = len(EXPECTED_IDS)
N_SEQ = SOLUTION["traj_id"].nunique()
TEAMS_TTL = int(os.environ.get("TEAMS_TTL_SEC", "300"))
_teams_lock = threading.Lock()
_teams_cache = {"at": 0.0, "list": [], "key": {}}


def get_teams():
    """The whitelist, re-read from HF at most every TEAMS_TTL seconds.

    This used to be a module-level constant, which meant a team that joined Kaggle
    after the Space booted could never be scored: sync_teams.py refreshed teams.txt
    on the Hub every 10 minutes, but this process never looked at it again.

    Two guards, because a bad refresh must not be worse than no refresh:
      * an empty or failed read never replaces a non-empty list -- otherwise one
        network hiccup would lock every team out at once;
      * the timestamp advances even on failure, so a persistent outage degrades to
        "serve the last good list" instead of hammering the Hub on every request.
    """
    now = time.time()
    with _teams_lock:
        if now - _teams_cache["at"] > TEAMS_TTL:
            try:
                fresh = load_teams()
                if fresh:
                    _teams_cache["list"] = fresh
                    _teams_cache["key"] = {team_key(t): t for t in fresh}
                else:
                    print("[teams] refresh returned an empty list; keeping "
                          f"{len(_teams_cache['list'])} cached names")
            except Exception as exc:                     # noqa: BLE001
                print(f"[teams] refresh failed ({exc}); keeping "
                      f"{len(_teams_cache['list'])} cached names")
            _teams_cache["at"] = now
        return _teams_cache["list"], _teams_cache["key"]


TEAMS = load_teams()
_teams_cache["list"] = TEAMS
_teams_cache["key"] = {team_key(t): t for t in TEAMS}
_teams_cache["at"] = time.time()
if not TEAMS and REQUIRE_TEAMS:
    raise RuntimeError(
        "The team whitelist is empty (TEAMS_FILE missing or all comments). Without it the "
        "rule 'team name must match Kaggle' does not exist, so this app refuses to start. "
        "Provide teams.txt, or set REQUIRE_TEAMS=false to deliberately accept any name.")
print(f"[boot] {N_EXPECTED} windows / {N_SEQ} sequences; {len(TEAMS)} teams; "
      f"limit {DAILY_LIMIT}/day; RTE window {RTE_DELTA}s; teams TTL {TEAMS_TTL}s")


def read_ledger() -> list:
    if LOCAL_SOLUTION:
        p = "ledger_local.jsonl"
        return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
    try:
        p = _hf_get(LEDGER_REPO, LEDGER_FILE)
    except Exception:
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def append_ledger(rec: dict) -> None:
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in read_ledger() + [rec]) + "\n"
    if LOCAL_SOLUTION:
        open("ledger_local.jsonl", "w").write(body)
        return
    from huggingface_hub import HfApi
    HfApi(token=HF_TOKEN).upload_file(
        path_or_fileobj=body.encode(), path_in_repo=LEDGER_FILE,
        repo_id=LEDGER_REPO, repo_type="dataset")


def quota_left(team: str) -> int:
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    used = sum(1 for r in read_ledger()
               if r.get("team") == team and r.get("ts", "").startswith(today))
    return max(0, DAILY_LIMIT - used)


def resolve_team(raw: str):
    """Return (canonical team name, error message)."""
    t = (raw or "").strip()
    if not t:
        return None, "❌ Please enter your team name, exactly as it appears on Kaggle."
    teams, teams_key = get_teams()
    if not teams:
        return t, None
    if t in teams:
        return t, None
    hit = teams_key.get(team_key(t))
    if hit and STRICT_TEAM_MATCH:
        return None, ("❌ Team name does not match the spelling registered on Kaggle. "
                      "It is **%s** — please copy it exactly (case and spacing matter)." % hit)
    if hit:
        return hit, None
    return None, (
        "❌ '%s' is not in the list of participating teams, so it cannot be scored.\n\n"
        "This site's team list is synced from the **public Kaggle leaderboard** and contains "
        "only teams with **at least one Kaggle submission**. If you have not submitted to "
        "Kaggle yet, please do that first, then come back: the list is pulled from Kaggle "
        "every 10 minutes and this page re-reads it every 5, so allow up to 15 minutes.\n\n"
        "If you have already submitted, check that your team name matches Kaggle exactly "
        "(case, spaces, `@`, `-`)." % t)


def run(file_obj, team_raw: str):
    empty = (None, None, None, None)
    team, err = resolve_team(team_raw)
    if err or team is None:
        return (*empty, err or "❌ Invalid team name.")
    if file_obj is None:
        return (*empty, "❌ Please upload your submission CSV.")

    path = file_obj.name if hasattr(file_obj, "name") else file_obj
    if os.path.getsize(path) > MAX_BYTES:
        return (*empty, "❌ File larger than %d MB." % (MAX_BYTES // 10 ** 6))

    with _lock:
        left = quota_left(team)
        if left <= 0:
            return (*empty, "❌ Team '%s' has used all %d submissions for today (UTC). "
                            "Please come back tomorrow." % (team, DAILY_LIMIT))
        raw = open(path, "rb").read()
        md5 = hashlib.md5(raw).hexdigest()
        try:
            sub = pd.read_csv(io.BytesIO(raw))
        except Exception as e:
            return (*empty, "❌ Could not read the CSV: %s" % e)
        try:
            sub = validate(sub, EXPECTED_IDS)
            res = score_detailed(SOLUTION, sub)
        except SubmissionError as e:
            return (*empty, "❌ %s" % e)
        except Exception as e:
            print("[error]", repr(e))
            return (*empty, "❌ Internal error while scoring. Please contact the organizers.")
        append_ledger({"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                       "team": team, "md5": md5, "total": res["total"],
                       "macro_AVE": res["macro_AVE"], "macro_ATE20": res["macro_ATE20"],
                       "macro_RTE": res["macro_RTE"]})

    seq = sequence_table(res)
    out = os.path.join(tempfile.mkdtemp(), "per_sequence_%s.csv" % re.sub(r"\W+", "_", team))
    seq.to_csv(out, index=False)

    msg = ("### ✅ TartanIMU Score %.5f  (lower is better)\n\n"
           "macro AVE **%.5f** m/s  ·  macro ATE20 **%.5f** m  ·  macro RTE@%ds **%.5f** m\n\n"
           "Team `%s`  ·  submission md5 `%s`  ·  **%d/%d** submissions left today\n\n"
           "> Quote this **md5** in your technical report — it is how the committee "
           "reproduces the numbers below."
           % (res["total"], res["macro_AVE"], res["macro_ATE20"], RTE_DELTA, res["macro_RTE"],
              team, md5, left - 1, DAILY_LIMIT))
    return overall_table(res), platform_table(res), seq, out, msg


CSS = """
.gradio-container {max-width: 1180px !important;}
#hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #2b4c7e 100%);
  color: #f8fafc; border-radius: 16px; padding: 28px 32px; margin-bottom: 4px;
}
#hero h1 {margin: 0 0 6px 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.4px; color: #fff;}
#hero .sub {font-size: 1.02rem; opacity: .92; margin: 0;}
#hero .pills {margin-top: 16px;}
#hero .pill {
  display: inline-block; background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.22);
  border-radius: 999px; padding: 4px 13px; margin: 0 7px 7px 0; font-size: .84rem;
}
#scorecard {
  border: 1px solid var(--border-color-primary); border-left: 5px solid #c41230;
  border-radius: 12px; padding: 16px 20px; background: var(--background-fill-secondary);
  min-height: 92px;
}
#scorecard h3 {margin-top: 0 !important;}
.tblhead {margin: 18px 0 2px 0 !important;}
.tblhead h3 {margin: 0 0 2px 0 !important; font-size: 1.06rem;}
.tblhead p {margin: 0 !important; font-size: .87rem; opacity: .72;}
footer {display: none !important;}
#foot {text-align: center; font-size: .85rem; opacity: .7; margin-top: 26px;}
"""

THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=(gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"),
    font_mono=(gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"),
)

# Gradio 6 把 theme/css 从 Blocks() 移到了 launch()；传给 Blocks 会被静默忽略，
# 美化就全白做了。这里两边都兼容：能传给 Blocks 就传，否则留给 launch()。
_BLOCKS_KW, _LAUNCH_KW = {}, {}
if int(gr.__version__.split(".")[0]) >= 6:
    _LAUNCH_KW = {"theme": THEME, "css": CSS}
else:
    _BLOCKS_KW = {"theme": THEME, "css": CSS}

with gr.Blocks(title="TartanIMU Challenge · Scoring",
               analytics_enabled=False, **_BLOCKS_KW) as demo:

    gr.HTML(f"""
    <div id="hero">
      <h1>IMU Odometry Challenge &middot; Per-Sequence Scoring</h1>
      <p class="sub">Upload your submission and get every number your technical report asks for
      &mdash; scored with the <b>same logic as the Kaggle leaderboard</b>.</p>
      <div class="pills">
        <span class="pill">{N_SEQ} test sequences</span>
        <span class="pill">{N_EXPECTED:,} windows</span>
        <span class="pill">{DAILY_LIMIT} submissions / team / day</span>
        <span class="pill">Tables III &middot; IV &middot; V</span>
        <span class="pill">Free</span>
      </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=4):
            team = gr.Textbox(label="1 · Team name",
                              info="Exactly as it appears on the Kaggle leaderboard "
                                   "(case, spaces, @, - all matter).",
                              placeholder="e.g. CoCEL @POSTECH")
            up = gr.File(label="2 · Submission CSV", file_types=[".csv"],
                         height=110)
            btn = gr.Button("Score my submission", variant="primary", size="lg")
            dl = gr.File(label="Per-sequence CSV (Table V)", height=90)
        with gr.Column(scale=6):
            msg = gr.Markdown(
                "### Ready\n"
                "Enter your team name and upload a `window_id,vx,vy,vz` CSV "
                f"with exactly **{N_EXPECTED:,}** rows plus the header.\n\n"
                "Your score appears here, together with the three tables below.",
                elem_id="scorecard")

    with gr.Accordion("Rules and metric definitions", open=False):
        gr.Markdown(f"""
**Who can be scored.** The team list is synced from the **public Kaggle leaderboard** every
10 minutes. You must have made **at least one Kaggle submission**, and your team name here
must match the one on Kaggle. Teams that are not on the leaderboard are not scored.

**Quota.** {DAILY_LIMIT} submissions per team per day, resetting at 00:00 UTC — the same limit
as Kaggle.

**Submission format.** `window_id,vx,vy,vz`, exactly **{N_EXPECTED:,}** data rows.
`vx,vy,vz` is the mean **body-frame** velocity (m/s) of that 1-second window
(a window is 200 samples at 200 Hz). Every `window_id` from
`index/test_windows.csv` must appear exactly once.

**TartanIMU Score** — identical to the Kaggle leaderboard metric, **lower is better**,
an all-zero submission scores exactly 1.000:

```
Score = 0.6 x (macro AVE / 0.7356384388)  +  0.4 x (macro ATE20 / 3.1160277267)
```

| | Metric | Unit | What it measures |
|---|---|---|---|
| 60% | **AVE** | m/s | Per-window Euclidean velocity error, averaged window to trajectory to platform. |
| 40% | **ATE20** | m | Predictions integrated into a path, compared with ground truth over 20 m segments after an SE(3) (Umeyama) alignment. |
| — | **RTE** | m | Relative Trajectory Error over {RTE_DELTA}-second windows (Sturm *et al.*, IROS 2012), as used in AirIO. Measures **local** drift. **Does not enter the ranking** — reported for your analysis. |

All three are macro-averaged over the four platforms, each contributing exactly 25%.
""")

    gr.Markdown("### Table III &mdash; Overall challenge performance\n"
                "Copy this row into your report.", elem_classes="tblhead")
    otbl = gr.Dataframe(interactive=False, wrap=True)

    gr.Markdown("### Table IV &mdash; Performance by platform\n"
                "Row labels already match the template.", elem_classes="tblhead")
    ptbl = gr.Dataframe(interactive=False, wrap=True)

    gr.Markdown(f"### Table V &mdash; Per-sequence results\n"
                f"All {N_SEQ} test sequences. Use the download button for the full CSV.",
                elem_classes="tblhead")
    seqtbl = gr.Dataframe(interactive=False, wrap=True)

    gr.HTML("""
    <div id="foot">
      <a href="https://superodometry.com/imuchallenge" target="_blank">Challenge home</a> &nbsp;·&nbsp;
      <a href="https://www.kaggle.com/competitions/tartan-imu-challenge-iros2026" target="_blank">Kaggle</a> &nbsp;·&nbsp;
      <a href="https://github.com/superxslam/TartanIMU" target="_blank">Starter code</a>
      <br>IROS 2026 &middot; Cross-Platform Inertial Positioning
    </div>
    """)

    btn.click(run, inputs=[up, team], outputs=[otbl, ptbl, seqtbl, dl, msg])

if __name__ == "__main__":
    demo.launch(**_LAUNCH_KW)
