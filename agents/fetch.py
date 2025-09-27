"""
Imports:
- typing is used to describe the expected shape of the data.
  Here it makes clear that execute() returns a List of (source, payload) tuples.
- time provides sleep() which we use to pause politely between requests.
- logging lets us record warnings if a request fails, instead of crashing silently.
- requests is the HTTP client used to actually call the APIs (handles GET, params, headers, etc.).
"""

from typing import List, Dict, Any, Tuple
import time
import logging
import requests

# Create a logger for this file (so warnings show up with the module name).
log = logging.getLogger(__name__)

# Set a default timeout (20s) so slow APIs can't hang the run forever.
DEFAULT_TIMEOUT = 20


class FetchAgent:
    """
    FetchAgent
    ----------
    This agent takes the request "plans" built by DiscoveryAgent and uses those plasn to call the relevant APIs.
    It uses the requests library to perform HTTP GETs, parses JSON or text depending on source,
    and returns a list of (source, payload). If one call fails it logs a warning instead of stopping.
    """

    def __init__(self, user_agent: str = "UoEO-Intelligent-Agents-Student/1.0"):
        # Create a reusable HTTP session (faster than opening a new connection each time).
        # Add a custom User-Agent header so API providers can identify this client.
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def execute(self, plans: List[Dict[str, Any]]) -> List[Tuple[str, Any]]:
        # The output will be a list of (source, payload) tuples.
        out: List[Tuple[str, Any]] = []

        # Loop over each request plan.
        for i, p in enumerate(plans):
            try:
                # Perform the HTTP request with method/url/params/headers from the plan.
                resp = self.session.request(
                    p["method"],
                    p["url"],
                    params=p.get("params"),
                    headers=p.get("headers") or {},
                    timeout=DEFAULT_TIMEOUT,
                )

                # Raise an exception if the response status is an error (4xx or 5xx).
                resp.raise_for_status()

                # Decide how to handle the body: JSON if Content-Type indicates JSON,
                # otherwise keep the response as raw text (e.g. arXiv XML).
                ctype = resp.headers.get("Content-Type", "")
                payload = resp.json() if "application/json" in ctype else resp.text

                # Save the result as (source, payload).
                out.append((p["source"], payload))

                # Add a short delay (0.3s) between requests to be polite and avoid rate limits.
                if i < len(plans) - 1:
                    time.sleep(0.3)

            except requests.RequestException as e:
                # If the request fails (network error, timeout, bad response),
                # log a warning but continue with the remaining requests.
                log.warning("Fetch failed for %s: %s", p.get("source", "?"), e)

        # Return the list of (source, payload) results for ExtractAgent to process.
        return out
