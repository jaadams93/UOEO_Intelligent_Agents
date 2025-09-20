from typing import Dict, Any, List, Tuple
from agents.discovery import DiscoveryAgent
from agents.fetch import FetchAgent
from agents.extract import ExtractAgent
from storage import Storage

class CoordinatorAgent:
    def __init__(self):
        self.discovery = DiscoveryAgent()
        self.fetch = FetchAgent()
        self.extract = ExtractAgent()
        self.storage = Storage()

    def run(
        self,
        query: str,
        max_items: int,
        out_dir: str,
        run_id: str,
        with_doaj: bool = False,
        save_snapshots: bool = False,
        mailto: str = "",
    ) -> Dict[str, str]:
        plans = self.discovery.build_plans(query=query, max_items=max_items, with_doaj=with_doaj, mailto=mailto)
        raw: List[Tuple[str, Any]] = self.fetch.execute(plans)

        records: List[Dict[str, Any]] = []
        snapshots: Dict[str, Any] = {}

        for src, payload in raw:
            if src == "arxiv":
                records.extend(self.extract.from_arxiv(payload, cap=max_items))
                if save_snapshots:
                    snapshots["arxiv"] = {"atom": payload[:20000]}
            elif src == "crossref":
                records.extend(self.extract.from_crossref(payload, cap=max_items))
                if save_snapshots:
                    snapshots["crossref"] = payload
            elif src == "doaj":
                records.extend(self.extract.from_doaj(payload, cap=max_items))
                if save_snapshots:
                    snapshots["doaj"] = payload

        unique = self.storage.dedupe(records)
        return self.storage.persist(
            out_dir=out_dir,
            run_id=run_id,
            query=query,
            items=unique,
            snapshots=(snapshots if save_snapshots else None),
        )