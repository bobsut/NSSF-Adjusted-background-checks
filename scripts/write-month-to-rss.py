#!/usr/bin/env python
import datetime
import re
from io import BytesIO

import pdfplumber
import requests
from feedgen.feed import FeedGenerator

PDF_URL = "https://www.fbi.gov/file-repository/active_records_in_the_nics-indices.pdf"
SLUG = "data-liberation-project/nics-firearm-background-checks"


def parse_date(pdf):
    text = pdf.pages[0].extract_text(x_tolerance=5)
    date_pat = r"UPDATED:\s+As of (.+)\n"
    updated_date = re.search(date_pat, text).group(1)
    updated_date = re.sub(r"\s*,", ",", updated_date)
    d = datetime.datetime.strptime(updated_date, "%B %d, %Y")
    return d


def get_date():
    raw = requests.get(PDF_URL).content
    pdf = pdfplumber.open(BytesIO(raw))
    return parse_date(pdf)


def generate_feed(date):
    date_str = date.strftime("%Y-%m-%d")
    date_str_rss = date.isoformat() + "Z00:00"
    feed = FeedGenerator()
    feed.id(SLUG)
    feed.title("NICS Background Check PDF Updates")
    feed.description("A simple RSS feed indicating the latest NICS PDF date.")
    feed.author({"name": "The Data Liberation Project"})
    feed.link(href=f"https://github.com/{SLUG}", rel="self")
    feed.lastBuildDate(date_str_rss)
    feed.language("en")
    entry = feed.add_entry()
    entry.id(f"{SLUG}:{date_str}")
    entry.title(f"NICS PDFs updated {date_str}")
    entry.published(date_str_rss)
    entry.link(href=f"{PDF_URL}/view")
    return feed


def main():
    date = get_date()
    feed = generate_feed(date)
    feed.rss_file("data/feeds/latest-month-available.rss", pretty=True)


if __name__ == "__main__":
    main()
