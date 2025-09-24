"""
This first section imports several libraries:
- argparse is used to accept command line interace inputs
- logging and datetime are used to create time-stamped logs and create a unique run ID 
- agents.coordinator imports the agent module that coordinates the process and prints the output to the results folder
"""

import argparse
import logging
from datetime import datetime
from agents.coordinator import CoordinatorAgent

#This code takes the search query and creates a character-limited file name for the search results

def _slugify(text: str) -> str:
    import re
    t = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", t)[:80]

"""
This section defines the command line interface that accepts the user query. 

It first fsets up an ArgumentPasrder with a description of the program. 
It contains one positional argument, the only mandatory argument - is the user query. 
It then includes a number of optional arguments:
- The max numbers of items (to limit retrieval);
- The output directory (in this case defaulting to 'results';
- Toggle for with or without DOAJ;
- Output the API payload;
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
    default=True,
    help="Save raw API payloads (default: True)"
    )
    args = p.parse_args()

    """This code uses Python's built-in logging module to print messages to the console. 
    This shows different levels of loggin, in this case:
    - INFO showing normal progess (such as 'file saved');
    - WARNING shows something that is unexpected but not fatal;
    - ERROR means something has gone wrong. 
    Each message will also inlcude the time that the log is created. 
    """
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    """
    This creates the runID which forms the basis for the output file names.
    It combines the user query (turned into a safe slug – lowercase with dashes, no special characters)
    and the current UTC time.
    """
    
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_id = f"{_slugify(args.query)}_{ts}"

    """
    Take the user input from the CLI (parsed into args) and pass it into the CoordinatorAgent.
    The Coordinator uses these values (query, max items, output folder, DOAJ toggle, etc.)
    to run the full pipeline: Discovery → Fetch → Extract → Storage.
    """
    
    coord = CoordinatorAgent()
    outputs = coord.run(
        query=args.query,
        max_items=max(1, min(args.max_items, 200)),
        out_dir=args.out_dir,
        run_id=run_id,
        with_doaj=args.with_doaj,
        save_snapshots=args.save_snapshots,
        mailto=args.mailto.strip(),
    )

    """
    Log the locations of the output files so the user can see where results were saved.
    These come from the outputs dictionary created by the CoordinatorAgent.
    """
    
    logging.info("CSV:  %s", outputs["csv"])
    logging.info("HTML: %s", outputs["html"])
    logging.info("LOG:  %s", outputs["log"])

if __name__ == "__main__":
    main()
