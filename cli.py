"""
This first section imports several libraries:
- argparse: accepts command-line inputs
- logging + datetime: create time-stamped logs and a unique run ID
- agents.coordinator: imports the agent that coordinates the full pipeline
"""

import argparse
import logging
from datetime import datetime
from agents.coordinator import CoordinatorAgent


# This function turns the search query into a safe, short slug for filenames.
def _slugify(text: str) -> str:
    import re
    t = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", t)[:80]


"""
This section defines the command line interface that accepts the user query.

It first sets up an ArgumentParser with a description of the program.
It contains one positional (mandatory) argument: the user query.
It then includes optional arguments:
- max items per source (to limit retrieval)
- output directory (defaults to 'results')
- toggle to include DOAJ
- save raw API payload snapshots (ON by default for the demo)
"""
def main():
    p = argparse.ArgumentParser(
        description="Academic Research Online Agent (arXiv + Crossref [+ DOAJ optional])"
    )
    p.add_argument("query", help='Search query, e.g., "machine learning for fraud detection"')
    p.add_argument("--max-items", type=int, default=100, help="Soft cap per source (1–200)")
    p.add_argument("--out-dir", default="results", help="Output directory")
    p.add_argument("--with-doaj", action="store_true", help="Also query DOAJ (optional)")
    p.add_argument(
        "--save-snapshots",
        action="store_true",
        default=True,  # demo choice: snapshots ON by default
        help="Save raw API payloads (default: True for demo)"
    )
    args = p.parse_args()

    """
    Configure logging to print messages to the console with timestamps.
    Levels used:
    - INFO: normal progress (e.g., 'file saved')
    - WARNING: something unexpected but not fatal
    - ERROR: something went wrong
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    """
    Create a run_id used as the basis for output filenames.
    It combines the query (as a safe slug) and the current UTC timestamp.
    """
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_id = f"{_slugify(args.query)}_{ts}"

    """
    Pass the parsed CLI inputs to the CoordinatorAgent.
    The Coordinator runs the pipeline: Discovery → Fetch → Extract → Storage.
    """
    coord = CoordinatorAgent()
    outputs = coord.run(
        query=args.query,
        max_items=max(1, min(args.max_items, 200)),
        out_dir=args.out_dir,
        run_id=run_id,
        with_doaj=args.with_doaj,
        save_snapshots=args.save_snapshots,  # always True by default for the demo
    )

    """
    Log the locations of the output files so the user can see where results were saved.
    """
    logging.info("CSV:  %s", outputs["csv"])
    logging.info("HTML: %s", outputs["html"])
    logging.info("LOG:  %s", outputs["log"])


if __name__ == "__main__":
    main()
