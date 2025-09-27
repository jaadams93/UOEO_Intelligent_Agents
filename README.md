# Academic Research Online Agent

A lightweight multi-agent Python tool that queries **arXiv** (Atom) and **Crossref** (JSON), normalises and de-duplicates results (priority: **DOI → arXiv ID → title-hash**), then exports:

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
