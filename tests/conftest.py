import pytest

@pytest.fixture
def sample_arxiv_atom():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.56789</id>
        <title>Sample arXiv Paper</title>
        <summary>Abstract text here.</summary>
        <published>2024-05-12T12:00:00Z</published>
        <author><name>Jane Doe</name></author>
        <link href="http://arxiv.org/abs/1234.56789" rel="alternate" type="text/html"/>
      </entry>
    </feed>"""

@pytest.fixture
def sample_crossref_json():
    return {
      "message": {
        "items": [{
          "DOI": "10.1000/xyz123",
          "title": ["Crossref Item"],
          "author": [{"given": "John", "family": "Smith"}],
          "abstract": "CR abstract",
          "URL": "https://doi.org/10.1000/xyz123",
          "issued": {"date-parts": [[2023, 2, 1]]},
          "subject": ["AI", "ML"]
        }]
      }
    }