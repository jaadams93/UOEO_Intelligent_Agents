from typing import List, Dict, Any, Optional
import os, csv, json, hashlib, html

class Storage:
    @staticmethod
    def _ensure_dir(path: str) -> None:
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _key(rec: Dict[str, Any]) -> str:
        if rec.get("doi"):
            return f"doi:{str(rec['doi']).lower()}"
        if rec.get("arxiv_id"):
            return f"arxiv:{rec['arxiv_id']}"
        return "titlehash:" + hashlib.sha1((rec.get("title") or "").lower().encode("utf-8")).hexdigest()

    def dedupe(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out: List[Dict[str, Any]] = []
        for r in items:
            k = self._key(r)
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out

    def persist(
        self,
        out_dir: str,
        run_id: str,
        query: str,
        items: List[Dict[str, Any]],
        snapshots: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        self._ensure_dir(out_dir)
        csv_path = os.path.join(out_dir, f"{run_id}.csv")
        html_path = os.path.join(out_dir, f"{run_id}.html")
        log_path = os.path.join(out_dir, f"{run_id}.log.json")

        self._write_csv(csv_path, items)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self._render_html(items, title=f'Results for "{html.escape(query)}"'))

        log_obj: Dict[str, Any] = {"query": query, "run_id": run_id}
        if snapshots:
            index: Dict[str, str] = {}
            for k, v in snapshots.items():
                p = os.path.join(out_dir, f"{run_id}.{k}.json")
                with open(p, "w", encoding="utf-8") as sf:
                    json.dump(v, sf, ensure_ascii=False, indent=2)
                index[k] = os.path.basename(p)
            log_obj["snapshots"] = index

        with open(log_path, "w", encoding="utf-8") as lf:
            json.dump(log_obj, lf, ensure_ascii=False, indent=2)

        return {"csv": csv_path, "html": html_path, "log": log_path}

    @staticmethod
    def _write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
        rows = rows or []
        fieldnames = sorted({k for r in rows for k in r.keys()}) if rows else [
            "source","doi","arxiv_id","title","authors","abstract","year","url","subjects"
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                normalized = {}
                for k, v in r.items():
                    normalized[k] = ", ".join(map(str, v)) if isinstance(v, list) else v
                w.writerow(normalized)

    @staticmethod
    def _render_html(items: List[Dict[str, Any]], title: str) -> str:
        def esc(x: Optional[str]) -> str:
            return html.escape(x or "")
        head = f"""<!doctype html><html><head><meta charset="utf-8">
<title>{title}</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:24px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;vertical-align:top}}
th{{cursor:pointer;position:sticky;top:0;background:#fafafa}}
input[type="search"]{{padding:8px;width:40%;margin:12px 0}}
small{{color:#666}}
</style></head><body>
<h1>{title}</h1>
<input id="q" type="search" placeholder="Filter by keyword…">
<small>Click headers to sort.</small>
<table id="t"><thead>
<tr>
<th>Source</th><th>Title</th><th>Authors</th><th>Year</th><th>DOI/arXiv</th><th>Subjects</th><th>Abstract</th>
</tr></thead><tbody>
"""
        rows = []
        for r in items:
            title_txt = esc(r.get("title"))
            url = r.get("url") or "#"
            authors = esc(", ".join(r.get("authors") or []))
            year = esc(str(r.get("year") or ""))
            subjects = esc(", ".join(r.get("subjects") or []))
            doi = r.get("doi")
            arxiv_id = r.get("arxiv_id")
            if doi:
                id_html = f'<a href="https://doi.org/{esc(doi)}">{esc(doi)}</a>'
            elif arxiv_id and r.get("url"):
                id_html = f'<a href="{esc(url)}">{esc(arxiv_id)}</a>'
            else:
                id_html = esc(arxiv_id or "")
            abstract = r.get("abstract") or ""
            abstract = abstract[:500] + ("…" if len(abstract) > 500 else "")
            rows.append(
                f"<tr><td>{esc(r.get('source'))}</td>"
                f"<td><a href='{esc(url)}'>{title_txt}</a></td>"
                f"<td>{authors}</td>"
                f"<td>{year}</td>"
                f"<td>{id_html}</td>"
                f"<td>{subjects}</td>"
                f"<td>{esc(abstract)}</td></tr>"
            )
        tail = """</tbody></table>
<script>
const q=document.getElementById('q');const tb=document.getElementById('t').tBodies[0];
q.addEventListener('input',()=>{const v=q.value.toLowerCase();[...tb.rows].forEach(r=>{
  r.style.display = r.innerText.toLowerCase().includes(v) ? '' : 'none';
});});
[...document.querySelectorAll('th')].forEach((th,i)=>th.addEventListener('click',()=>{
  const rows=[...tb.rows];const asc=th.dataset.asc!=='true';th.dataset.asc=asc;
  rows.sort((a,b)=>{const A=a.cells[i].innerText.toLowerCase();const B=b.cells[i].innerText.toLowerCase();
    return asc?A.localeCompare(B):B.localeCompare(A)});rows.forEach(r=>tb.appendChild(r));
}));
</script>
</body></html>"""
        return head + "\n".join(rows) + tail
