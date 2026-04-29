#!/usr/bin/env python3
"""
Main entry point for selenium_spider
"""

import argparse
import signal
import sys

from liepin_selenium import setup_logger
from liepin_selenium.spiders.example_spider import ExampleSpider
from liepin_selenium.spiders.keyword_spider import KeywordSpider


def signal_handler(signum, frame):
    """Handle exit signals"""
    logger = setup_logger("main")
    logger.info(f"Received signal {signum}, exiting gracefully...")
    sys.exit(0)


def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger = setup_logger("main")
    logger.info("=" * 60)
    logger.info("Selenium Spider Framework")
    logger.info("=" * 60)

    parser = argparse.ArgumentParser(description="Run selenium spiders")
    parser.add_argument(
        "--spider",
        type=str,
        default="keyword",
        help="Spider name to run (example, keyword)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="python",
        help="Search keyword for job listings (default: python)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to crawl (default: None, crawl all pages)",
    )

    args = parser.parse_args()

    try:
        # Run the specified spider
        if args.spider.lower() == "example":
            spider = ExampleSpider()
            spider.run()

            if spider.data:
                spider.export_data(format_type=args.output)

        elif args.spider.lower() == "keyword":
            spider = KeywordSpider(keyword=args.keyword)
            spider.run(max_pages=args.max_pages)

            if spider.data:
                spider.export_data(format_type=args.output)
                spider.preview_results()

        else:
            logger.error(f"Unknown spider: {args.spider}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error running spider: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
