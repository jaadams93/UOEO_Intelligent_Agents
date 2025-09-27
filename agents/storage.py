# agents/storage.py

from __future__ import annotations
from typing import List, Dict, Any
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

"""
Imports:
- typing: type hints for lists/dicts of records.
- csv: writes a UTF-8 CSV for Excel/Sheets/etc.
- json: writes a small log of the run (evidence of execution).
- pathlib.Path: path-safe file handling across OSs.
- datetime: used to stamp the HTML footer.
"""

# Normalised record shape
Record = Dict[str, Any]
REQUIRED_COLUMNS = [
    "source", "doi", "arxiv_id", "title", "authors", "abstract", "year", "url", "subjects"
]


class StorageAgent:
    """
    StorageAgent
    ------------
    Writes final outputs:
    - CSV (one row per record)
    - HTML (quick browse + filter)
    - JSON log (counts, filenames, timestamp, optional API snapshots)
    """

    def __init__(self, ensure_dirs: bool = True):
        # Auto-create the output directory unless disabled.
        self.ensure_dirs = ensure_dirs

    def _ensure_out_dir(self, out_dir: str) -> Path:
        """Ensure the output directory exists and return it as a Path."""
        p = Path(out_dir)
        if self.ensure_dirs:
            p.mkdir(parents=True, exist_ok=True)
        return p

    # -------------------------
    # CSV
    # -------------------------
    def write_csv(self, records: List[Record], out_dir: str, run_id: str) -> str:
        """
        Write records to UTF-8 CSV. Returns the path.
        - Lists (authors/subjects) are joined with '; ' so they fit one cell.
        - Missing keys filled with empty strings for consistency.
        """
        out_path = self._ensure_out_dir(out_dir) / f"{run_id}.csv"

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
        - Client-side search: one input filters rows by title/abstract/authors.
        - No external CSS/JS to keep it portable.
        """
        out_path = self._ensure_out_dir(out_dir) / f"{run_id}.html"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Minimal escaping for text inserted into HTML.
        def esc(x: Any) -> str:
            s = "" if x is None else str(x)
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Build table rows.
        rows = []
        for r in records:
            title = esc(r.get("title", ""))
            url = r.get("url") or ""
            link = (
                f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{title or "(no title)"}</a>'
                if url else esc(title or "(no title)")
            )
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
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }}
    h1 {{ font-size: 20px; margin: 0 0 8px; }}
    .meta {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
    #q {{ width: 100%; max-width: 560px; padding: 8px 10px; margin: 12px 0 16px; border: 1px solid #ccc; border-radius: 6px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-top: 1px solid #eee; padding: 8px 10px; vertical-align: top; }}
    th {{ text-align: left; background: #fafafa; position: sticky; top: 0; }}
    td.abstract {{ max-width: 560px; }}
    .count {{ font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Results for: {esc(query)}</h1>
  <div class="meta">Generated: {ts} · Items: <span id="count">{len(records)}</span></div>
  <input id="q" placeholder="Type to filter by title, abstract, or authors..." />

  <table id="tbl">
    <thead>
      <tr>
        <th>Source</th>
        <th>DOI</th>
        <th>arXiv ID</th>
        <th>Title</th>
        <th>Authors</th>
        <th>Year</th>
        <th>Subjects</th>
        <th>Abstract</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>

  <script>
    const q = document.getElementById('q');
    const tbody = document.querySelector('#tbl tbody');
    const count = document.getElementById('count');
    q.addEventListener('input', () => {{
      const term = q.value.trim().toLowerCase();
      let shown = 0;
      for (const tr of tbody.rows) {{
        const t = tr.innerText.toLowerCase();
        const ok = !term || t.includes(term);
        tr.style.display = ok ? '' : 'none';
        if (ok) shown++;
      }}
      count.textContent = shown;
    }});
  </script>
</body>
</html>"""

        out_path.write_text(html, encoding="utf-8")
        return str(out_path)

    # -------------------------
    # DEDUPLICATION
    # -------------------------
    def dedupe(self, records: List[Record]) -> List[Record]:
        """
        Remove duplicates across sources using a simple priority:
        - Prefer DOI as the primary key (case-insensitive).
        - If no DOI, fall back to arXiv ID.
        - If neither, fall back to a normalised title key.
        First occurrence wins, but missing fields are merged if later duplicates
        provide extra data (e.g., filling abstract/authors).
        """
        def norm(s: Any) -> str:
            return "" if not s else str(s).strip().lower()

        seen: Dict[str, int] = {}     # key -> index in 'unique'
        unique: List[Record] = []

        for rec in records:
            key = ""
            doi = norm(rec.get("doi"))
            axv = norm(rec.get("arxiv_id"))
            ttl = norm(rec.get("title"))
            if doi:
                key = f"doi:{doi}"
            elif axv:
                key = f"arxiv:{axv}"
            elif ttl:
                key = f"title:{ttl[:120]}"  # guard against very long titles

            if key and key in seen:
                # Merge missing fields into the existing record.
                idx = seen[key]
                existing = unique[idx]

                # Merge helper for scalar fields (fill if empty).
                for fld in ("doi", "arxiv_id", "title", "abstract", "year", "url", "source"):
                    if not existing.get(fld) and rec.get(fld):
                        existing[fld] = rec[fld]

                # Merge list fields (authors/subjects) with de-duplication.
                for lf in ("authors", "subjects"):
                    a = existing.get(lf) or []
                    b = rec.get(lf) or []
                    if isinstance(a, list) and isinstance(b, list):
                        merged = a + [x for x in b if x not in a]
                        existing[lf] = merged
                # Keep existing otherwise (first occurrence wins).
            else:
                # First time seeing this key (or no key at all) → append as-is.
                seen[key] = len(unique)
                unique.append(rec)

        return unique

    # -------------------------
    # PERSIST ORCHESTRATION
    # -------------------------
    def persist(
        self,
        out_dir: str,
        run_id: str,
        query: str,
        items: List[Record],
        snapshots: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        """
        Orchestrate writing outputs and return their paths:
        - CSV (records)
        - HTML (interactive view)
        - JSON log (metadata + optional snapshots)
        """
        outp = self._ensure_out_dir(out_dir)

        csv_path = self.write_csv(items, out_dir, run_id)
        html_path = self.write_html(items, out_dir, run_id, query)

        # Build a small log for evidence of execution.
        log_obj = {
            "run_id": run_id,
            "query": query,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "counts": {
                "total_records": len(items),
            },
            "files": {
                "csv": csv_path,
                "html": html_path,
            },
        }

        # Attach optional API snapshots for evidence/debugging.
        if snapshots:
            log_obj["snapshots"] = snapshots

        log_path = str(outp / f"{run_id}.log.json")
        Path(log_path).write_text(json.dumps(log_obj, ensure_ascii=False, indent=2), encoding="utf-8")

        return {"csv": csv_path, "html": html_path, "log": log_path}
