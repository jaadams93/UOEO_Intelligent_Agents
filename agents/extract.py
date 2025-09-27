from typing import Any, Dict, List
import feedparser
from dateutil.parser import parse as parse_date

"""
Imports:
- typing gives type hints so it's clear what shapes we return (List[Dict[str, Any]]).
- feedparser reads arXiv's Atom XML into a friendly Python object (entries, links, etc.).
- dateutil.parser.parse converts date strings (e.g. '2024-05-01T12:30:00Z') into datetime objects.
"""


class ExtractAgent:
    """
    ExtractAgent
    ------------
    Takes raw payloads from FetchAgent and normalises them into a common record format:
      {
        "source": "...",      # arxiv | crossref | doaj
        "doi": "...",         # string or None
        "arxiv_id": "...",    # string or None
        "title": "...",
        "authors": ["...","..."],
        "abstract": "...",
        "year": 2024,         # int or None
        "url": "...",
        "subjects": ["..."]   # list (may be empty)
      }

    Each method handles one source and returns a list of records, capped by 'cap'.
    """

    def from_arxiv(self, atom_text: str, cap: int) -> List[Dict[str, Any]]:
        """
        Parse arXiv Atom XML (as text) into our normalised record list.
        - feedparser turns the feed into entries with id/title/summary/authors/links/etc.
        - We try to parse 'published' to get a publication year.
        - DOI sometimes appears as a link with title 'doi'.
        """
        feed = feedparser.parse(atom_text)
        items: List[Dict[str, Any]] = []

        # Only take up to 'cap' entries for this run.
        for e in feed.entries[:cap]:
            # Basic fields with safe fallbacks (getattr avoids crashes if missing).
            arxiv_id = getattr(e, "id", None)
            title = (getattr(e, "title", "") or "").strip()
            abstract = (getattr(e, "summary", "") or "").strip()
            authors = [a.get("name", "").strip() for a in getattr(e, "authors", [])]

            # Try to parse a year from the published date (if present).
            published = getattr(e, "published", None)
            year = None
            if published:
                try:
                    year = parse_date(published).year
                except Exception:
                    # If date parsing fails, we just leave year as None.
                    pass

            # Main link back to the arXiv record.
            url = getattr(e, "link", None)

            # DOI (if available) is often exposed as a <link title="doi" href="...">
            doi = None
            for link in getattr(e, "links", []):
                if (link.get("title") or "").lower() == "doi":
                    doi = link.get("href")

            # Build the normalised record.
            items.append({
                "source": "arxiv",
                "doi": doi,
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "url": url,
                "subjects": [],  # arXiv subject tags aren't included here; can be added later if needed
            })

        return items

    def from_crossref(self, obj: Dict[str, Any], cap: int) -> List[Dict[str, Any]]:
        """
        Parse Crossref JSON into our normalised records.
        - Crossref wraps results under obj["message"]["items"].
        - Titles come as a list; we take the first.
        - Authors are objects with 'given' and 'family' names (join them).
        - Year is usually in 'issued': {'date-parts': [[YYYY, MM, DD]]}
        """
        message = (obj or {}).get("message", {})
        raw_items = message.get("items", []) or []
        items: List[Dict[str, Any]] = []

        for it in raw_items[:cap]:
            # Title is often a list; pick the first string.
            title_list = it.get("title") or []
            title = (title_list[0] if title_list else "").strip()

            # Authors come as a list of dicts with 'given' and 'family'.
            authors = []
            for a in it.get("author", []) or []:
                given, family = a.get("given", ""), a.get("family", "")
                name = (f"{given} {family}".strip()).strip()
                if name:
                    authors.append(name)

            # Extract a year if available from 'issued' date-parts.
            year = None
            issued = (it.get("issued") or {}).get("date-parts", [])
            if issued and issued[0]:
                year = issued[0][0]

            # Build the normalised record.
            items.append({
                "source": "crossref",
                "doi": it.get("DOI"),
                "arxiv_id": None,
                "title": title,
                "authors": authors,
                "abstract": it.get("abstract"),
                "year": year,
                "url": it.get("URL"),
                "subjects": it.get("subject") or [],
            })

        return items

    def from_doaj(self, obj: Dict[str, Any], cap: int) -> List[Dict[str, Any]]:
        """
        Parse DOAJ JSON into our normalised records.
        - DOAJ has had schema differences ('results' vs 'hits'); we handle both.
        - 'bibjson' (newer) or 'source' (older) sections hold the metadata.
        - DOI appears under identifier/type='doi'.
        """
        # Support both shapes: {results: [...]} or {hits: [...]}
        results = (obj or {}).get("results") or (obj or {}).get("hits") or []
        out: List[Dict[str, Any]] = []

        for r in results[:cap]:
            # 'bibjson' (common) or 'source' (older index); fall back to r itself.
            rec = r.get("bibjson") or r.get("source") or r

            # Find a DOI if identifiers are present.
            doi = None
            for idf in rec.get("identifier", []):
                if (idf.get("type") or "").lower() == "doi":
                    doi = idf.get("id")

            title = (rec.get("title") or "").strip()
            authors = [a.get("name", "").strip() for a in rec.get("author", [])]
            abstract = rec.get("abstract")
            year = rec.get("year")

            # DOAJ often provides a list of links; use the first if available.
            url = rec.get("link", [{}])[0].get("url") if rec.get("link") else None

            # Subjects are usually a list of dicts with a 'term' field.
            subjects = [s.get("term", "") for s in rec.get("subject", [])]

            out.append({
                "source": "doaj",
                "doi": doi,
                "arxiv_id": None,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "url": url,
                "subjects": subjects,
            })

        return out
