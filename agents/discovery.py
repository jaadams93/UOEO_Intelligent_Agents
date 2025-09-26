"""
DiscoveryAgent
--------------

This agent takes the user query and builds HTTP request "plans" for arXiv, Crossref,
and (optionally) DOAJ. Each plan is a dictionary describing a request, with keys for
source, method, url, params, and headers. These plans are then passed to FetchAgent
to build and execute the actual HTTP requests. 

Two different approaches are used intentionally to demonstrate alternative ways of
building API requests:

- arXiv: parameters are manually encoded into the URL string.
- Crossref and DOAJ: parameters are passed as a Python dict and the requests library
  encodes them automatically.

API references:
- arXiv:    https://arxiv.org/help/api/user-manual
- Crossref: https://api.crossref.org/swagger-ui/index.html
- DOAJ:     https://doaj.org/api/v3/docs
"""

from typing import List, Dict, Any
from urllib.parse import urlencode, quote_plus
"""
Imports:
- typing is used to specify expected types (List[Dict[str, Any]]) for clarity.
- quote_plus makes a string safe for URLs (turns spaces into '+', escapes symbols).
- urlencode turns a dictionary into a query string like "a=1&b=2".
"""

class DiscoveryAgent:
    # Base API endpoints. Keeping them as constants makes updates easy if APIs change.
    ARXIV_BASE = "https://export.arxiv.org/api/query"
    CROSSREF_BASE = "https://api.crossref.org/works"
    DOAJ_BASE = "https://doaj.org/api/v3/search/articles"

    """
    Build API request "plans" for each data source.
    A plan is a dict with: source, method, url, params, headers.
    This function does not fetch anything itself — it just prepares the plans
    for FetchAgent to execute later.
    """
    def build_plans(self, query: str, max_items: int, with_doaj: bool = False) -> List[Dict[str, Any]]:
        # Clean up the user query and enforce at least 1 item.
        q = query.strip()
        cap = max(1, max_items)
        plans: List[Dict[str, Any]] = []

        # -----------------------------
        # arXiv plan
        # -----------------------------
        # arXiv expects parameters in the URL. We manually encode them here.
        # Demonstrates "manual encoding" style.
        # API docs: https://arxiv.org/help/api/user-manual
        arxiv_params = {
            "search_query": f"all:{quote_plus(q)}",
            "start": 0,
            "max_results": min(cap, 200),
        }
        plans.append({
            "source": "arxiv",
            "method": "GET",  # GET is standard; included for consistency
            "url": f"{self.ARXIV_BASE}?{urlencode(arxiv_params)}",  # full URL built manually
            "params": None,   # not needed, since query already in URL
            "headers": {},    # placeholder for future use
        })

        # -----------------------------
        # Crossref plan
        # -----------------------------
        # Here we pass params as a dict. requests will encode them automatically.
        # Demonstrates the "params dict" style.
        # API docs: https://api.crossref.org/swagger-ui/index.html
        crossref_params = {
            "query": q,
            "rows": min(cap, 100),
            "select": "DOI,title,author,abstract,URL,issued,subject,type",
        }
        plans.append({
            "source": "crossref",
            "method": "GET",
            "url": self.CROSSREF_BASE,
            "params": crossref_params,
            "headers": {},
        })

        # -----------------------------
        # DOAJ plan (optional)
        # -----------------------------
        # Only added if --with-doaj is passed in CLI.
        # API docs: https://doaj.org/api/v3/docs
        if with_doaj:
            doaj_params = {
                "q": q,
                "page": 1,
                "pageSize": min(cap, 100),
            }
            plans.append({
                "source": "doaj",
                "method": "GET",
                "url": self.DOAJ_BASE,
                "params": doaj_params,
                "headers": {},
            })

        # Return all request plans for FetchAgent to execute
        return plans
