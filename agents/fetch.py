from typing import List, Dict, Any, Tuple
import time
import logging
import requests

log = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 20

class FetchAgent:
    def __init__(self, user_agent: str = "UoEO-Intelligent-Agents-Student/1.0"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def execute(self, plans: List[Dict[str, Any]]) -> List[Tuple[str, Any]]:
        out: List[Tuple[str, Any]] = []
        for i, p in enumerate(plans):
            try:
                resp = self.session.request(
                    p["method"],
                    p["url"],
                    params=p.get("params"),
                    headers=p.get("headers") or {},
                    timeout=DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                ctype = resp.headers.get("Content-Type", "")
                payload = resp.json() if "application/json" in ctype else resp.text
                out.append((p["source"], payload))
                if i < len(plans) - 1:
                    time.sleep(0.3)
            except requests.RequestException as e:
                log.warning("Fetch failed for %s: %s", p.get("source", "?"), e)
        return out