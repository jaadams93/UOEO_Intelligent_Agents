# agents/storage.py

from __future__ import annotations
from typing import List, Dict, Any
import csv
import json
import os
from pathlib import Path
from datetime import datetime

"""
Imports:
- typing: type hints for lists/dicts of records.
- csv: writes a UTF-8 CSV so you can open results in Excel/Sheets/etc.
- json: writes a small log of the run (evidence of execution).
- os / pathlib: create folders + build file paths safely on any OS.
- datetime: used only to stamp the HTML page footer (optional).
"""

# Our normalised record shape (for clarity)
Record = Dict[str, Any]
REQUIRED_COLUMNS = [
    "source", "doi", "arxiv_id", "title", "authors", "abstract", "year", "url", "subjects"
]


class StorageAgent:
    """
    StorageAgent
    ------------
    Takes a list of normalised records and writes:
    - a CSV file  (one row per record)
    - a simple HTML results page (client-side filter/search)
    - a small JSON log (what we wrote, counts, timestamps)
    Filenames are based on the run_id and out_dir provided by the Coordinator.
    """

    def __init__(self, ensure_dirs: bool = True):
        # Keep behaviour simple: auto-create the output directory unless told not to.
        self.ensure_dirs = ensure_dirs

    def _ensure_out_dir(self, out_dir: str) -> Path:
        """
        Make sure the output folder exists. Returns a Path to it.
        """
        p = Path(out_dir)
        if self.ensure_dirs:
            p.mkdir(parents=True, exist_ok=True)
        return p

    # -------------------------
    # CSV
    # -------------------------
    def write_csv(self, records: List[Record], out_dir: str, run_id: str) -> str:
        """
        Write records to a UTF-8 CSV. Returns the file path as a string.
        - Lists (authors/subjects) are joined with '; ' so they fit in one cell.
        - Missing keys are filled as empty strings for consistency.
        """
        out_path = self._ensure_out_dir(out_dir) / f"{run_id}.csv"

        # Prepare rows with safe defaults and string-join for list fields.
        def _row(rec: Record) -> Dict[str, str]:
            return {
                "source": rec.get("source", "") or "",
                "doi": rec.get("doi", "") or "",
                "arxiv_id": rec.get("arxiv_id", "") or "",
                "title": rec.get("title", "") or "",
                "authors": "; ".join(rec.get("authors", []) or []),
                "abstract": rec.get("abstract", "") or "",
                "year": str(rec.get("year", "") or ""),
                "url": rec.get("url", "") or "",
                "subjects": "; ".join(rec.get("subjects", []) or []),
            }

        with out_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
            w.writeheader()
            for rec in records:
                w.writerow(_row(rec))

        return str(out_path)

    # -------------------------
    # HTML
    # -------------------------
    def write_html(self, records: List[Record], out_dir: str, run_id: str, query: str) -> str:
        """
        Write a lightweight HTML page for quick browsing/filtering.
        - Pure client-side search: a single input that filters rows by title/abstract/author.
        - No external CSS/JS (keeps it portable and marker-friendly).
        """
        out_path = self._ensure_out_dir(out_dir) / f"{run_id}.html"
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Escape helper for minimal safety in HTML text (very simple).
        def esc(x: Any) -> str:
            s = "" if x is None else str(x)
            return (
                s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
            )

        # Build table rows
        rows = []
        for r in records:
            title = esc(r.get("title", ""))
            url = r.get("url") or ""
            link = f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{title or "(no title)"}</a>' if url else esc(title or "(no title)")
            authors = esc("; ".join(r.get("authors", []) or []))
            abstract = esc(r.get("abstract", "") or "")
            year = esc(r.get("year", "") or "")
            doi = esc(r.get("doi", "") or "")
            arx = esc(r.get("arxiv_id", "") or "")
            src = esc(r.get("source", "") or "")
            subs = esc("; ".join(r.get("subjects", []) or []))

            rows.append(
                f"<tr>"
                f"<td>{src}</td>"
                f"<td>{doi}</td>"
                f"<td>{arx}</td>"
                f"<td>{link}</td>"
                f"<td>{authors}</td>"
                f"<td>{year}</td>"
                f"<td>{subs}</td>"
                f"<td class='abstract'>{abstract}</td>"
                f"</tr>"
            )

        html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Results: {esc(query)}</title>
  <meta name="viewport" content="
