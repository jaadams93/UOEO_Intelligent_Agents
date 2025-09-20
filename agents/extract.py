from typing import Any, Dict, List
import feedparser
from dateutil.parser import parse as parse_date

class ExtractAgent:
    def from_arxiv(self, atom_text: str, cap: int) -> List[Dict[str, Any]]:
        feed = feedparser.parse(atom_text)
        items: List[Dict[str, Any]] = []
        for e in feed.entries[:cap]:
            arxiv_id = getattr(e, "id", None)
            title = (getattr(e, "title", "") or "").strip()
            abstract = (getattr(e, "summary", "") or "").strip()
            authors = [a.get("name", "").strip() for a in getattr(e, "authors", [])]
            published = getattr(e, "published", None)
            year = None
            if published:
                try:
                    year = parse_date(published).year
                except Exception:
                    pass
            url = getattr(e, "link", None)
            doi = None
            for link in getattr(e, "links", []):
                if (link.get("title") or "").lower() == "doi":
                    doi = link.get("href")
            items.append({
                "source": "arxiv",
                "doi": doi,
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "year": year,
                "url": url,
                "subjects": [],
            })
        return items

    def from_crossref(self, obj: Dict[str, Any], cap: int) -> List[Dict[str, Any]]:
        message = (obj or {}).get("message", {})
        raw_items = message.get("items", []) or []
        items: List[Dict[str, Any]] = []
        for it in raw_items[:cap]:
            title_list = it.get("title") or []
            title = (title_list[0] if title_list else "").strip()
            authors = []
            for a in it.get("author", []) or []:
                given, family = a.get("given", ""), a.get("family", "")
                name = (f"{given} {family}".strip()).strip()
                if name:
                    authors.append(name)
            year = None
            issued = (it.get("issued") or {}).get("date-parts", [])
            if issued and issued[0]:
                year = issued[0][0]
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
        results = (obj or {}).get("results") or (obj or {}).get("hits") or []
        out: List[Dict[str, Any]] = []
        for r in results[:cap]:
            rec = r.get("bibjson") or r.get("source") or r
            doi = None
            for idf in rec.get("identifier", []):
                if (idf.get("type") or "").lower() == "doi":
                    doi = idf.get("id")
            title = (rec.get("title") or "").strip()
            authors = [a.get("name", "").strip() for a in rec.get("author", [])]
            abstract = rec.get("abstract")
            year = rec.get("year")
            url = rec.get("link", [{}])[0].get("url") if rec.get("link") else None
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