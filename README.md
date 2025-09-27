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

---

## Automated Testing

Run unit tests using **pytest**:
```
pytest -q
```

---

##Project Structure
```
├── cli.py                   # Command-line entry point
├── agents/
│   ├── __init__.py          # Package marker (exports agents)
│   ├── discovery.py         # Builds request plans for arXiv, Crossref, DOAJ
│   ├── fetch.py             # Executes HTTP requests (requests.Session, timeouts)
│   ├── extract.py           # Normalises arXiv (Atom) + Crossref/DOAJ (JSON) to common schema
│   ├── storage.py           # Dedupes and writes CSV, HTML, JSON log
│   └── coordinator.py       # Orchestrates the multi-agent workflow
├── tests/                   # Unit tests (pytest)
│   └── test_storage_dedupe.py
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignore caches, venv, and results
└── results/                 # Output folder (auto-created)
```

---

##Project Architecture

- DiscoveryAgent – translates the user query into API request plans. Demonstrates two approaches intentionally:
		- arXiv: manual query-string construction.
		- Crossref/DOAJ: pass params dict and let requests encode.
- FetchAgent – executes plans via requests.Session with timeouts and polite headers.
- ExtractAgent – parses and normalises heterogeneous payloads into a unified record:

  ```JSON
  {
  "source": "...",
  "doi": "...",
  "arxiv_id": "...",
  "title": "...",
  "authors": ["..."],
  "abstract": "...",
  "year": 2024,
  "url": "...",
  "subjects": ["..."]
  ```
- StorageAgent – de-duplicates across sources (priority: DOI → arXiv ID → title) and persists CSV/HTML/JSON.
- CoordinatorAgent – orchestrates the flow end-to-end (plans → fetch → extract → dedupe → persist).

---
## Technical Documentation

**APIs**  
- [arXiv API User Manual](https://arxiv.org/help/api/user-manual) – Atom feed query parameters and record structure.  
- [Crossref REST API](https://api.crossref.org/swagger-ui/index.html) – JSON response fields and query parameters.  
- [DOAJ API v3](https://doaj.org/api/v3/docs) – optional open access metadata endpoint.  

**Python Libraries**  
- [requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/) – HTTP client used for API calls.  
- [feedparser: Universal Feed Parser](https://feedparser.readthedocs.io/en/latest/) – parses arXiv Atom XML to Python objects.  
- [python-dateutil](https://dateutil.readthedocs.io/en/stable/) – parses publication dates to extract years.  
- [pytest](https://docs.pytest.org/en/stable/) – unit testing framework for evidence of testing.  
