# Purpose: verifies ExtractAgent.from_crossref parses title, authors, year, DOI, URL, subjects.
# Utility: proves JSON → normalised record mapping without hitting the network.

from agents.extract import ExtractAgent

def test_extract_from_crossref_minimal():
    x = ExtractAgent()
    # Minimal Crossref-like payload (shape mirrors /works "message.items")
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.5555/xyz",
                    "title": ["A Study on Widgets"],
                    "author": [{"given": "Ada", "family": "Lovelace"}, {"given": "Alan", "family": "Turing"}],
                    "issued": {"date-parts": [[2021, 3, 1]]},
                    "URL": "https://doi.org/10.5555/xyz",
                    "abstract": "Abstract text…",
                    "subject": ["Computer Science", "History"]
                }
            ]
        }
    }
    recs = x.from_crossref(payload, cap=10)
    assert len(recs) == 1
    r = recs[0]
    assert r["source"] == "crossref"
    assert r["doi"] == "10.5555/xyz"
    assert r["title"] == "A Study on Widgets"
    assert r["authors"] == ["Ada Lovelace", "Alan Turing"]
    assert r["year"] == 2021
    assert r["url"] == "https://doi.org/10.5555/xyz"
    assert "Computer Science" in r["subjects"]
