#!/usr/bin/env python3
"""
Main entry point for selenium_spider
"""

import argparse
import signal
import sys

from selenium_spider import setup_logger
from selenium_spider.spiders.example_spider import ExampleSpider


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
        default="example",
        help="Spider name to run (default: example)",
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

    args = parser.parse_args()

    try:
        # Run the specified spider
        if args.spider.lower() == "example":
            spider = ExampleSpider()
            spider.run()

            if spider.data:
                spider.export_data(format_type=args.output)

        else:
            logger.error(f"Unknown spider: {args.spider}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error running spider: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
