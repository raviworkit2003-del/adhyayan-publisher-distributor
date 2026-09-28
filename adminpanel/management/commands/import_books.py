import os
import re
import time
from decimal import Decimal
import pandas as pd
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from s1app.models import Author, Book, Category, Publisher


class Command(BaseCommand):
    help = "Import and enrich books from CSV with Google Books and Open Library fallback"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def clean_isbn(self, raw_isbn):
        """Clean string float artefacts (.0), hyphens, and spaces."""
        if pd.isna(raw_isbn):
            return ""
        val = str(raw_isbn).strip()
        if val.endswith(".0"):
            val = val[:-2]
        # Keep only digits and X/x for ISBN-10
        return re.sub(r"[^0-9Xx]", "", val)

    def fetch_open_library_cover(self, session, isbn):
        """Fetch cover from Open Library using HEAD request (lightweight)."""
        if not isbn:
            return ""
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
        try:
            res = session.head(url, timeout=5, allow_redirects=True)
            if res.status_code == 200:
                content_len = int(res.headers.get("content-length", 0))
                # Skip 1x1 blank placeholder images
                if content_len > 1000 or content_len == 0:
                    return url
        except requests.RequestException:
            pass
        return ""

    def fetch_google_data(self, session, isbn, title, api_key):
        """Fetch description and cover from Google Books API."""
        description = ""
        thumbnail = ""

        # Priority 1: Search by ISBN
        query = f"isbn:{isbn}" if isbn else f"intitle:{requests.utils.quote(title[:50])}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1&key={api_key}"

        try:
            res = session.get(url, timeout=6)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                if items:
                    vol_info = items[0].get("volumeInfo", {})
                    description = vol_info.get("description", "")
                    image_links = vol_info.get("imageLinks", {})

                    raw_thumb = (
                        image_links.get("extraLarge")
                        or image_links.get("large")
                        or image_links.get("medium")
                        or image_links.get("thumbnail")
                        or image_links.get("smallThumbnail")
                    )
                    if raw_thumb:
                        thumbnail = raw_thumb.replace("http://", "https://")
        except requests.RequestException:
            pass

        return description, thumbnail

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        self.stdout.write(self.style.SUCCESS(f"Reading file: {csv_file}"))

        # Read ISBN column strictly as string to avoid float conversions
        df = pd.read_csv(csv_file, dtype={"source_isbn": str})
        total_rows = len(df)
        self.stdout.write(self.style.SUCCESS(f"Found {total_rows} total rows in CSV"))

        api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")

        books_created = 0
        books_skipped = 0
        covers_found = 0
        covers_missing = 0

        with requests.Session() as session:
            for index, row in df.iterrows():
                isbn = self.clean_isbn(row.get("source_isbn"))
                title = str(row.get("title", "")).strip()

                if not isbn and not title:
                    self.stdout.write(self.style.WARNING(f"Row {index + 1}: Missing both ISBN and Title. Skipping."))
                    continue

                self.stdout.write(f"\nProcessing {index + 1}/{total_rows} | ISBN: {isbn or 'N/A'}")

                # ----------------------------------------------------
                # Check Existing Book in Database
                # ----------------------------------------------------
                existing_book = None
                if isbn:
                    existing_book = Book.objects.filter(isbn=isbn).first()

                # Agar book already DB me hai
                if existing_book:
                    books_skipped += 1
                    # Agar pehle se cover maujood hai
                    if existing_book.thumbnail:
                        covers_found += 1
                        self.stdout.write(self.style.NOTICE(f"Already in DB with cover: {existing_book.title[:30]}"))
                        continue
                    else:
                        # Cover missing tha, sirf Open Library se dhoondo (Zero Google Load)
                        ol_cover = self.fetch_open_library_cover(session, isbn)
                        if ol_cover:
                            existing_book.thumbnail = ol_cover
                            existing_book.save(update_fields=["thumbnail"])
                            covers_found += 1
                            self.stdout.write(self.style.SUCCESS(f"Added missing cover via Open Library: {existing_book.title[:30]}"))
                        else:
                            covers_missing += 1
                            self.stdout.write(self.style.WARNING(f"Already in DB, no cover found on Open Library"))
                        continue

                # ----------------------------------------------------
                # Nayi Book: Fetch Cover & Description
                # ----------------------------------------------------
                # 1. Pehle lightweight Open Library check karein
                thumbnail = self.fetch_open_library_cover(session, isbn)
                description = ""

                # 2. Agar Open Library par cover na ho ya description chahiye ho, tabhi Google API hit karein
                if not thumbnail or not description:
                    g_desc, g_thumb = self.fetch_google_data(session, isbn, title, api_key)
                    if not description:
                        description = g_desc
                    if not thumbnail and g_thumb:
                        thumbnail = g_thumb

                    # Safe rate limit delay taaki 429 Too Many Requests na aaye
                    time.sleep(0.4)

                if thumbnail:
                    covers_found += 1
                    self.stdout.write(self.style.SUCCESS("Cover found!"))
                else:
                    covers_missing += 1
                    self.stdout.write(self.style.WARNING("Cover not found"))

                # ----------------------------------------------------
                # Safe Category Handling (Prevents Slug Crash)
                # ----------------------------------------------------
                raw_subject = str(row.get("subject", "")).strip()
                if not raw_subject or raw_subject.lower() == "nan":
                    raw_subject = "General"

                cat_slug = slugify(raw_subject) or "general"

                category = Category.objects.filter(slug=cat_slug).first()
                if not category:
                    category, _ = Category.objects.get_or_create(
                        name=raw_subject,
                        defaults={"slug": cat_slug, "description": ""},
                    )

                # ----------------------------------------------------
                # Author & Publisher Handling
                # ----------------------------------------------------
                author_name = str(row.get("author", "Unknown")).strip()
                author, _ = Author.objects.get_or_create(name=author_name)

                publisher_name = str(row.get("publisher", "Unknown")).strip()
                publisher, _ = Publisher.objects.get_or_create(
                    company_name=publisher_name,
                    defaults={"Phone": "", "Email": "", "address": "", "website": ""},
                )

                # ----------------------------------------------------
                # Data Parsing
                # ----------------------------------------------------
                pages = row.get("pages")
                pages = 0 if pd.isna(pages) else int(pages)

                price = row.get("list_price")
                price = Decimal("0") if pd.isna(price) else Decimal(str(price))

                year = row.get("year")
                publish_date = None if pd.isna(year) else f"{int(year)}-01-01"

                # ----------------------------------------------------
                # Save Book to Database
                # ----------------------------------------------------
                book, created = Book.objects.get_or_create(
                    isbn=isbn or f"TEMP-{index}",
                    defaults={
                        "title": title,
                        "category": category,
                        "publisher": publisher,
                        "language": str(row.get("language", "")),
                        "number_of_pages": pages,
                        "edition": str(row.get("binding", "")),
                        "price": price,
                        "description": description,
                        "publish_date": publish_date,
                        "available": True,
                        "stock_quantity": 0,
                        "thumbnail": thumbnail,
                    },
                )

                book.author.add(author)
                if created:
                    books_created += 1

        # ----------------------------------------------------
        # Final Summary
        # ----------------------------------------------------
        self.stdout.write("\n" + self.style.SUCCESS("=" * 40))
        self.stdout.write(self.style.SUCCESS("           IMPORT COMPLETE              "))
        self.stdout.write(self.style.SUCCESS("=" * 40))
        self.stdout.write(f"Total CSV Rows:     {total_rows}")
        self.stdout.write(self.style.NOTICE(f"Books Skipped (in DB): {books_skipped}"))
        self.stdout.write(self.style.SUCCESS(f"New Books Created:  {books_created}"))
        self.stdout.write(self.style.SUCCESS(f"Total Covers Found: {covers_found}"))
        self.stdout.write(self.style.WARNING(f"Covers Missing:     {covers_missing}"))
        self.stdout.write(self.style.SUCCESS("=" * 40))