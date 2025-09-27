from typing import Dict, Any, List, Tuple
from agents.discovery import DiscoveryAgent
from agents.fetch import FetchAgent
from agents.extract import ExtractAgent
from agents.storage import StorageAgent

"""
Imports:
- typing: provides type hints for the structures passed between steps.
- specialist agents: DiscoveryAgent, FetchAgent, ExtractAgent, StorageAgent.
"""


class CoordinatorAgent:
    """
    Coordinates the workflow of the system by:
      1. Building API request plans with DiscoveryAgent
      2. Executing requests with FetchAgent
      3. Extracting and normalising results with ExtractAgent
      4. Deduplicating and persisting results with StorageAgent
    """

    def __init__(self):
        # Instantiate each of the specialist agents.
        self.discovery = DiscoveryAgent()
        self.fetch = FetchAgent()
        self.extract = ExtractAgent()
        self.storage = StorageAgent()

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
        """
        Executes the full pipeline. 
        Inputs:
          - query: user’s search query
          - max_items: cap on results per source
          - out_dir: directory for CSV/HTML outputs
          - run_id: unique identifier used in filenames
          - with_doaj: include DOAJ as an additional source if True
          - save_snapshots: save raw API payloads if True
          - mailto: optional polite header for Crossref requests

        Returns:
          Dictionary containing file paths for CSV, HTML, and JSON log outputs.
        """

        # Step 1: Build the request plans for each API.
        plans = self.discovery.build_plans(
            query=query, max_items=max_items, with_doaj=with_doaj, mailto=mailto
        )

        # Step 2: Execute the requests and collect raw payloads.
        raw: List[Tuple[str, Any]] = self.fetch.execute(plans)

        # Containers for parsed records and optional raw snapshots.
        records: List[Dict[str, Any]] = []
        snapshots: Dict[str, Any] = {}

        # Step 3: Route each payload to the appropriate extraction method.
        for src, payload in raw:
            if src == "arxiv":
                records.extend(self.extract.from_arxiv(payload, cap=max_items))
                if save_snapshots:
                    snapshots["arxiv"] = {"atom": payload[:20000]}  # truncated
            elif src == "crossref":
                records.extend(self.extract.from_crossref(payload, cap=max_items))
                if save_snapshots:
                    snapshots["crossref"] = payload
            elif src == "doaj":
                records.extend(self.extract.from_doaj(payload, cap=max_items))
                if save_snapshots:
                    snapshots["doaj"] = payload

        # Step 4: Deduplicate records across multiple sources.
        unique = self.storage.dedupe(records)

        # Step 5: Persist final results to disk and return file paths.
        return self.storage.persist(
            out_dir=out_dir,
            run_id=run_id,
            query=query,
            items=unique,
            snapshots=(snapshots if save_snapshots else None),
        )
