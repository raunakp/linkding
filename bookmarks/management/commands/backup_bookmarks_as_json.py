import os
from datetime import datetime
import json
from django.core.management.base import BaseCommand
from bookmarks.models import Bookmark
from bookmarks.api.serializers import BookmarkSerializer

class Command(BaseCommand):
    help = "Exports all bookmarks to a JSON file in API format"

    def add_arguments(self, parser):
        parser.add_argument(
            "destination",
            nargs="?",
            type=str,
            help="Destination JSON file path (optional)",
        )

    def handle(self, *args, **options):
        destination = options.get("destination")
        if not destination:
            os.makedirs("backups", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = f"backups/linkding_bookmarks_{timestamp}.json"

        bookmarks = Bookmark.objects.all()
        serializer = BookmarkSerializer(bookmarks, many=True)
        data = serializer.data

        # Cleaning logic:
        # 1. Remove properties with empty strings or null values.
        # 2. Remove properties with empty arrays.
        # 3. Remove is_archived, unread, shared if their value is False.
        def clean_dict(d):
            return {
                k: v for k, v in d.items()
                if v not in ("", None) and
                   not (isinstance(v, list) and len(v) == 0) and
                   not (k in ("is_archived", "unread", "shared") and v is False)
            }

        cleaned_data = [clean_dict(item) for item in data]

        with open(destination, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exported {len(cleaned_data)} bookmarks to {destination}"))


# Documentation of cleaning decisions:
# 1. Properties with empty strings or null values are removed to avoid clutter and only keep meaningful data.
# 2. Properties with empty arrays are removed as they do not convey useful information.
# 3. The boolean fields is_archived, unread, and shared are only included if True, making the export concise and focused
