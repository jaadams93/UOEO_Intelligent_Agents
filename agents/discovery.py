"""
DiscoveryAgent
--------------

This agent takes the user query and builds HTTP request "plans" for arXiv, Crossref,
and (optionally) DOAJ. Each plan is a dictionary describing a request, with keys for
source, method, url, params, and headers. These plans are then passed to another agent (FetchAgent) to build and execute the requests. 

Two different approaches to building API calls are used. This is intentional to demonstrate different approaches to building API requests. 

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
This code first imports some libraries. 

typing is used here to describe the shape of data we return which is then used later in 'build_plans()' to provide a list of dictionaries (one dict per API request plan).

urllib.parse calls:
- 'quote_plus', which makes the user query safe inside a URL 
- 'urlencode', which turns a dict of parameters into a query string like "a=1&b=2"
"""


class DiscoveryAgent:
    #Define the base API endpoints. This provides a single location to update API HTML. 
    ARXIV_BASE = "https://export.arxiv.org/api/query"
    CROSSREF_BASE = "https://api.crossref.org/works"
    DOAJ_BASE = "https://doaj.org/api/v3/search/articles"

    """
    Turn the user's query and options into HTTP request "plans".
    A plan is  a dict with: source, method, url, params, headers.
    The FetchAgent will execute these plans; this file does not do network calls.
    """
    def build_plans(self, query: str, max_items: int, with_doaj: bool = False, mailto: str = "") -> List[Dict[str, Any]]:
        #This code cleans up the request and limits the minimum number of requests to 1.
        q = query.strip()
        cap = max(1, max_items)
        plans: List[Dict[str, Any]] = []

        
        # -----------------------------
        # arXiv plan
        # -----------------------------
        # arXiv expects most parameters directly in the URL.
        # Here we build the full query string ourselves (manual encoding).
        # This contrasts with Crossref/DOAJ, where we pass a params dict and let
        # the requests library encode automatically.
        # Showing both styles demonstrates two valid approaches to API calls.
        # API docs: https://arxiv.org/help/api/user-manual
        arxiv_params = {
            "search_query": f"all:{quote_plus(q)}",
            "start": 0,
            "max_results": min(cap, 200),
        }
        plans.append({
            "source": "arxiv",
            "method": "GET",
            "url": f"{self.ARXIV_BASE}?{urlencode(arxiv_params)}",  # full URL built manually
            "params": None,   # not needed here, since URL already encoded
            "headers": {},    # empty now; placeholder for consistency
        })
                
        # -----------------------------
        # Crossref plan
        # -----------------------------
        # Unlike arXiv, here we pass a params dict instead of building the URL manually.
        # The requests library will attach these params to the URL automatically.
        # This demonstrates the second common style of API request construction.
        # API docs: https://api.crossref.org/swagger-ui/index.html
        crossref_params = {
            "query": q,
            "rows": min(cap, 100),  # typical Crossref per-request cap
            "select": "DOI,title,author,abstract,URL,issued,subject,type",
        }
        plans.append({
            "source": "crossref",
            "method": "GET",
            "url": self.CROSSREF_BASE,
            "params": crossref_params,  # sent separately; not pre-encoded into URL
            "headers": {},
        })


        # -----------------------------
        # DOAJ plan (optional)
        # -----------------------------
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

     
