"""
This code first inmports some libraries. 

typing is used here to describe the shape of data we return which is then used later in 'build_plans()' to provide a list of dictionaries (one dict per API request plan).

urllib.parse calls:
- 'quote_plus', which makes the user query safe inside a URL 
- 'urlencode', which turns a dict of parameters into a query string like "a=1&b=2"
"""

from typing import List, Dict, Any
from urllib.parse import urlencode, quote_plus



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

        # arXiv (Atom)
        arxiv_params = {"search_query": f"all:{quote_plus(q)}", "start": 0, "max_results": min(cap, 200)}
        plans.append({
            "source": "arxiv",
            "method": "GET",
            "url": f"{self.ARXIV_BASE}?{urlencode(arxiv_params)}",
            "params": None,
            "headers": {}
        })

        # Crossref (JSON) + optional mailto etiquette
        crossref_params = {"query": q, "rows": min(cap, 100), "select": "DOI,title,author,abstract,URL,issued,subject,type"}
        if mailto:
            crossref_params["mailto"] = mailto
        plans.append({
            "source": "crossref",
            "method": "GET",
            "url": self.CROSSREF_BASE,
            "params": crossref_params,
            "headers": {}
        })

        if with_doaj:
            doaj_params = {"q": q, "page": 1, "pageSize": min(cap, 100)}
            plans.append({
                "source": "doaj",
                "method": "GET",
                "url": self.DOAJ_BASE,
                "params": doaj_params,
                "headers": {}
            })

        return plans
