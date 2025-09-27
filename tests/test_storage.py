from agents.storage import StorageAgent
import os, json

def test_dedupe_and_persist(tmp_path):
    s = StorageAgent()
    items = [
        {"source": "crossref", "doi": "10.1/a", "arxiv_id": None, "title": "A", "authors": [],
         "abstract": None, "year": 2023, "url": None, "subjects": []},
        {"source": "arxiv", "doi": None, "arxiv_id": "http://arxiv.org/abs/1234", "title": "A",
         "authors": [], "abstract": None, "year": 2024, "url": "http://arxiv.org/abs/1234", "subjects": []},
        {"source": "crossref", "doi": "10.1/a", "arxiv_id": None, "title": "A duplicate", "authors": [],
         "abstract": None, "year": 2023, "url": None, "subjects": []},
    ]

    # Deduplication should reduce to 2 unique records
    unique = s.dedupe(items)
    assert len(unique) == 2

    # Persist results into temp dir
    out = s.persist(
        out_dir=str(tmp_path),
        run_id="run_1",
        query="q",
        items=unique,
        snapshots={"x": {"ok": True}},
    )

    # Check files exist
    assert os.path.exists(out["csv"])
    assert os.path.exists(out["html"])
    assert os.path.exists(out["log"])

    # Check log contents
    with open(out["log"], "r", encoding="utf-8") as f:
        log = json.load(f)
    assert log["run_id"] == "run_1"
    assert "snapshots" in log