A small multi-agent Python tool that queries **arXiv** (Atom) and **Crossref** (JSON), normalises and de-duplicates results (priority: **DOI → arXiv ID → title-hash**), then exports:
- a timestamped **CSV**
- a simple **HTML** page (client-side filter/sort)
- a small **LOG** file (JSON) with reproducible run parameters
- optional **raw snapshots** for evidence

> **DOAJ** is **optional** via `--with-doaj` (off by default).

## Install (pip + venv)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt



#To run

python cli.py "machine learning for fraud detection" --max-items 100 --save-snapshots
# Output files: ./results/<slug>_<YYYYMMDD_HHMMSS>.csv|html|log.json

#To test

pytest -q