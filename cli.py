import argparse
import logging
from datetime import datetime
from agents.coordinator import CoordinatorAgent

def _slugify(text: str) -> str:
    import re
    t = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", t)[:80]

def main():
    p = argparse.ArgumentParser(
        description="Academic Research Online Agent (arXiv + Crossref [+ DOAJ optional])"
    )
    p.add_argument("query", help='Search query, e.g., "machine learning for fraud detection"')
    p.add_argument("--max-items", type=int, default=100, help="Soft cap per source (1–200)")
    p.add_argument("--out-dir", default="results", help="Output directory")
    p.add_argument("--with-doaj", action="store_true", help="Also query DOAJ (optional)")
    p.add_argument("--save-snapshots", action="store_true", help="Save raw payload snapshots")
    p.add_argument("--mailto", default="", help="Email for Crossref polite requests (optional)")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_id = f"{_slugify(args.query)}_{ts}"

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

    logging.info("CSV:  %s", outputs["csv"])
    logging.info("HTML: %s", outputs["html"])
    logging.info("LOG:  %s", outputs["log"])

if __name__ == "__main__":
    main()