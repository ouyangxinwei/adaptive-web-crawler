from scrapling.fetchers import Fetcher


def main():
    url = "https://quotes.toscrape.com/"

    print("=" * 50)
    print("Adaptive Web Crawler - Scrapling Test")
    print("=" * 50)

    print(f"\nFetching: {url}")

    page = Fetcher.get(url)

    title = page.css("title::text").get()
    quotes = page.css("span.text::text").getall()
    authors = page.css("small.author::text").getall()

    print("\n[Page Title]")
    print(title)

    print("\n[Quotes]")
    for index, quote in enumerate(quotes[:3], start=1):
        print(f"{index}. {quote}")

    print("\n[Authors]")
    for index, author in enumerate(authors[:3], start=1):
        print(f"{index}. {author}")

    print("\n[Summary]")
    print(f"Quotes found: {len(quotes)}")
    print(f"Authors found: {len(authors)}")


if __name__ == "__main__":
    main()
