# Test Purpose: verifies StorageAgent can (a) deduplicate simple inputs and (b) persist outputs to disk.
# Utility: proves core pipeline outputs (CSV/HTML/LOG) are created correctly and log contains snapshots.

from agents.storage import StorageAgent
import os, json

def test_dedupe_and_persist(tmp_path):
    s = StorageAgent()
    # Two Crossref items share DOI; one arXiv record with a distinct arXiv ID → expect 2 unique records
    items = [
        {"source":"crossref","doi":"10.1/a","arxiv_id":None,"title":"A","authors":[],"abstract":None,"year":2023,"url":None,"subjects":[]},
        {"source":"arxiv","doi":None,"arxiv_id":"http://arxiv.org/abs/1234","title":"A","authors":[],"abstract":None,"year":2024,"url":"http://arxiv.org/abs/1234","subjects":[]},
        {"source":"crossref","doi":"10.1/a","arxiv_id":None,"title":"A duplicate","authors":[],"abstract":None,"year":2023,"url":None,"subjects":[]},
    ]
    unique = s.dedupe(items)
    assert len(unique) == 2  # dedupe by DOI

    # Persist to a temp directory (pytest tmp_path is auto-cleaned)
    out = s.persist(out_dir=str(tmp_path), run_id="run_1", query="q", items=unique, snapshots={"x": {"ok": True}})

    # Files exist
    assert os.path.exists(out["csv"])
    assert os.path.exists(out["html"])
    assert os.path.exists(out["log"])

    # Log integrity: run_id echoed + snapshots captured
    with open(out["log"], "r", encoding="utf-8") as f:
        log = json.load(f)
    assert log["run_id"] == "run_1"
    assert "snapshots" in log
