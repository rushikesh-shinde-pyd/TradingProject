# Django Imports
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Third-Party Library Imports
from asgiref.sync import sync_to_async


def save_file_async(file_content, file_path):
    return sync_to_async(default_storage.save)(file_path, ContentFile(file_content))


def save_json_file_async(candles, filename):
    file_path = f'{settings.MEDIA_ROOT}/converted/{filename}'
    return sync_to_async(candles.to_json)(file_path, orient='records', lines=True)
