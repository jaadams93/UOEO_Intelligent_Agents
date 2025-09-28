# Purpose: verifies StorageAgent.write_csv creates a CSV with required headers and correct row count.
# Utility: quick file integrity check for evidence of execution.

from agents.storage import StorageAgent
import csv

def test_write_csv_headers_and_rows(tmp_path):
    s = StorageAgent()
    items = [
        {
            "source": "crossref",
            "doi": "10.1/a",
            "arxiv_id": None,
            "title": "A",
            "authors": ["Ada Lovelace"],
            "abstract": "x",
            "year": 2021,
            "url": "http://example.com/a",
            "subjects": ["CS"],
        },
        {
            "source": "arxiv",
            "doi": None,
            "arxiv_id": "http://arxiv.org/abs/1234",
            "title": "B",
            "authors": ["Alan Turing"],
            "abstract": "y",
            "year": 2020,
            "url": "http://arxiv.org/abs/1234",
            "subjects": ["Math"],
        },
    ]
    csv_path = s.write_csv(items, out_dir=str(tmp_path), run_id="r1")
    # Read back and assert headers + row count
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    assert headers == ["source","doi","arxiv_id","title","authors","abstract","year","url","subjects"]
    assert len(rows) == 2
