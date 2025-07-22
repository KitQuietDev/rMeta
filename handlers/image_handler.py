"""
Image Metadata Scrubber for rMeta

Uses piexif to remove EXIF metadata from supported image formats.
"""

import piexif

supported_extensions = {"jpg", "jpeg", "png"}


def scrub(file_path):
    """
    Scrubs metadata from an image file in place.

    Args:
        file_path (str): Path to the image file (.jpg, .jpeg, .png).
    """
    try:
        piexif.remove(file_path)
    except Exception as e:
        print(f"Error scrubbing image metadata: {e}")
