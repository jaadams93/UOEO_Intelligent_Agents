# Academic Research Online Agent

A lightweight multi-agent tool, developed with Python, that queries academic resource datase **arXiv** (Atom) and **Crossref** (JSON), normalises and de-duplicates results (priority: **DOI → arXiv ID → title-hash**), and then exports:

- a timestamped **CSV** (structured research results)
- a simple **HTML** page (client-side filter/search for browsing)
- a small **LOG** file (JSON) with reproducible run parameters
- optional **raw API snapshots** (for evidence/debugging)

> **DOAJ** is optional via `--with-doaj` (off by default).

---

## Features

- **Multi-agent architecture**: Discovery, Fetch, Extract, Storage, and Coordinator agents cooperate to complete the workflow.
- **API-first**: uses official APIs (no scraping) for stability, ethics, and reproducibility.
- **Reproducible runs**: timestamped filenames + JSON log of parameters and counts.
- **Portable**: runs locally, no database or cloud required.
- **Evidence-friendly**: optional raw snapshots of API payloads.

---

## Prerequisites

- Python **3.10+**
- (Recommended) GitHub Codespaces or any environment with internet access

---

## Install (pip + venv)

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows (PowerShell)

pip install -r requirements.txt
```

---

## Run a query 

The tools accepts inputs via a simple Command Line Interface using a positional arguments, with several optional arguments:
- query (positional) – the search query, e.g. "machine learning for fraud detection".
- --max-items INT – soft cap per source (default: 100; typical caps: arXiv≈200, Crossref≈100).
- --out-dir PATH – output directory (default: results).
- --with-doaj – include DOAJ as an additional source (off by default).
- --save-snapshots – save raw API payloads (useful for assignment evidence).

After instantiating the environment and installing the requirements, execute the folowing sample query: 

```bash
python cli.py "machine learning for fraud detection" --max-items 100 --save-snapshots
```

This will search for 'machine learning for fraud detection'. You can insert any query here. 

This will produce several outputs:
```
results/machine-learning-for-fraud-detection_YYYYMMDD_HHMMSS.csv
results/machine-learning-for-fraud-detection_YYYYMMDD_HHMMSS.html
results/machine-learning-for-fraud-detection_YYYYMMDD_HHMMSS.log.json
```
These are: 
	-	CSV – structured dataset (open in Excel/Sheets or load into analysis tools).
	-	HTML – lightweight results page with a search box (client-side filtering).
	-	LOG – JSON with run parameters, counts, timestamps, file paths.
	-  	Snapshots – optional raw API payloads (useful for evidence of execution).
