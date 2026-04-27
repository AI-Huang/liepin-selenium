from src.liepin_crawler import LiepinCrawler


def main():
    crawler = LiepinCrawler()
    crawler.crawl()
    crawler.print_results(limit=10)
    crawler.save_to_file()


if __name__ == "__main__":
    main()
