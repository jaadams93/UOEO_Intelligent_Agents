from typing import Dict, Any, List, Tuple
from agents.discovery import DiscoveryAgent
from agents.fetch import FetchAgent
from agents.extract import ExtractAgent
from agents.storage import StorageAgent

"""
Imports:
- typing: type hints for data passed between steps.
- specialist agents: DiscoveryAgent, FetchAgent, ExtractAgent, StorageAgent.
"""


class CoordinatorAgent:
    """
    Coordinates the system workflow:
      1) Build API request plans (DiscoveryAgent)
      2) Execute requests (FetchAgent)
      3) Extract and normalise results (ExtractAgent)
      4) Deduplicate and persist outputs (StorageAgent)
    """

    def __init__(self):
        # Instantiate specialist agents.
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
        save_snapshots: bool = False,  # kept for compatibility; forced ON below for demo
    ) -> Dict[str, str]:
        """
        Execute the full pipeline.

        Inputs:
          - query: search query string
          - max_items: cap on results per source
          - out_dir: output directory for CSV/HTML/log
          - run_id: unique identifier used in filenames
          - with_doaj: include DOAJ as an additional source if True
          - save_snapshots: CLI flag (forced ON for demo in this method)

        Returns:
          Dict with file paths for CSV, HTML, and JSON log outputs.
        """

        # Demo behaviour: force raw API snapshots ON regardless of CLI flag.
        save_snapshots = True

        # Step 1: Build request plans for each API.
        plans = self.discovery.build_plans(
            query=query,
            max_items=max_items,
            with_doaj=with_doaj,
        )

        # Step 2: Execute requests and collect raw payloads.
        raw: List[Tuple[str, Any]] = self.fetch.execute(plans)

        # Containers for parsed records and raw snapshots (for evidence).
        records: List[Dict[str, Any]] = []
        snapshots: Dict[str, Any] = {}

        # Step 3: Route payloads to appropriate extraction methods.
        for src, payload in raw:
            if src == "arxiv":
                records.extend(self.extract.from_arxiv(payload, cap=max_items))
                if save_snapshots:
                    # Store a truncated Atom feed for evidence.
                    snapshots["arxiv"] = {"atom": payload[:20000]}
            elif src == "crossref":
                records.extend(self.extract.from_crossref(payload, cap=max_items))
                if save_snapshots:
                    snapshots["crossref"] = payload
            elif src == "doaj":
                records.extend(self.extract.from_doaj(payload, cap=max_items))
                if save_snapshots:
                    snapshots["doaj"] = payload

        # Step 4: Deduplicate records across sources.
        unique = self.storage.dedupe(records)

        # Step 5: Persist outputs and return file paths.
        return self.storage.persist(
            out_dir=out_dir,
            run_id=run_id,
            query=query,
            items=unique,
            snapshots=(snapshots if save_snapshots else None),
        )
