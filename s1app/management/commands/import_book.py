from django.core.management.base import BaseCommand
import pandas as pd
from django.utils.text import slugify

from s1app.models import Book , Author , Category , Publisher

class Command(BaseCommand):
    help = "Import books from CSV"

    def add_arguments(self, parser):
        parser .add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):

        csv_file = kwargs["csv_file"]

        df = pd.read_csv(csv_file)

        self.stdout.write(
                self.style.SUCCESS(f"Found {len(df)} books.")
            )

        df = pd.read_csv(csv_file)
        df = df.dropna(subset=["title", "authors"])
        df["publisher"] = df["publisher"].fillna("Unknown Publisher")
        df["categories"] = df["categories"].fillna("General")
        df["description"] = df["description"].fillna("")
        df["page_count"] = df["page_count"].fillna(0)
        df["list_price"] = df["list_price"].fillna(0)
        df["thumbnail"] = df["thumbnail"].fillna("")
        df["published_date"] = df["published_date"].fillna("2000-01-01")
        for index, row in df.iterrows():
            isbn = row["isbn_13"]
            if pd.isna(isbn):
                isbn = f"978000{index:07d}"
            author, _ = Author.objects.get_or_create(
                name = row["authors"]
            )
            publisher, _= Publisher.objects.get_or_create(
                company_name=row["publisher"]
            )
            try:
                category_name = row["categories"].strip().rstrip(".")
                slug = slugify(category_name)
                category, _=Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": category_name,
                        "description": "",
                    },
                )
            except Exception:
                print("Category:", row["categories"])
                print("Slug:", slugify(row["categories"]))
                raise
                        
            def clean_date(value):
                value = str(value).strip()

                # YYYY
                if len(value) == 4 and value.isdigit():
                    return f"{value}-01-01"

                # YYYY-MM
                if (
                    len(value) == 7
                    and value[:4].isdigit()
                    and value[5:7].isdigit()
                    and value[4] == "-"
                ):
                    return f"{value}-01"

                # YYYY-MM-DD
                if (
                    len(value) == 10
                    and value[:4].isdigit()
                    and value[5:7].isdigit()
                    and value[8:10].isdigit()
                    and value[4] == "-"
                    and value[7] == "-"
                ):
                    return value

                # Everything else
                return "2000-01-01"

            book, created = Book.objects.update_or_create(
                isbn=isbn,
                defaults={
                    "title": row["title"],
                    "category": category,
                    "publisher": publisher,
                    "language": row["language"],
                    "number_of_pages": row["page_count"],
                    "edition": "1st Edition",
                    "price": row["list_price"],
                    "description": row["description"],
                    "publish_date": clean_date(row["published_date"]),
                    "thumbnail": row["thumbnail"],
                }
            )
            