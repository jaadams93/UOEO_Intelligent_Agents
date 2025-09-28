# Purpose: verifies ExtractAgent.from_arxiv parses Atom XML (title, authors, abstract, year, id/link).
# Utility: proves XML → normalised record mapping without hitting the network.

from agents.extract import ExtractAgent

# Tiny valid Atom feed with a single entry (kept minimal but parseable by feedparser).
ATOM_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>arXiv Query: sample</title>
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <updated>2024-06-30T12:00:00Z</updated>
    <published>2024-05-01T00:00:00Z</published>
    <title>Sample Paper Title</title>
    <summary>Short abstract text.</summary>
    <author><name>Grace Hopper</name></author>
    <author><name>Barbara Liskov</name></author>
    <link rel="alternate" type="text/html" href="http://arxiv.org/abs/1234.5678v1"/>
    <link title="doi" href="https://doi.org/10.1234/abcd"/>
  </entry>
</feed>
"""

def test_extract_from_arxiv_atom_minimal():
    x = ExtractAgent()
    recs = x.from_arxiv(ATOM_SAMPLE, cap=5)
    assert len(recs) == 1
    r = recs[0]
    assert r["source"] == "arxiv"
    assert r["arxiv_id"] == "http://arxiv.org/abs/1234.5678v1"
    assert r["doi"] == "https://doi.org/10.1234/abcd"
    assert r["title"] == "Sample Paper Title"
    assert r["authors"] == ["Grace Hopper", "Barbara Liskov"]
    assert r["abstract"] == "Short abstract text."
    assert r["year"] == 2024
    assert r["url"] == "http://arxiv.org/abs/1234.5678v1"
