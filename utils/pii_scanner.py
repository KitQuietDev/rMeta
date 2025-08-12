# utils/pii_scanner.py

"""
PII Scanner for rMeta

Scans plain text for common types of personally identifiable information (PII):
✅ Email addresses
✅ Phone numbers
✅ Social Security Numbers (SSNs)
✅ Physical addresses (basic heuristics)
✅ Names (optional, heuristic-based)

Returns a set of detected PII types.
"""

import re

# Regular expressions for common PII patterns
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "address": re.compile(r"\b\d{1,5}\s+\w+(?:\s+\w+)*\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)\b", re.IGNORECASE),
    # Optional name detection (very heuristic)
    "name": re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")  # e.g., "John Smith"
}

def scan_text_for_pii(text: str) -> set[str]:
    """
    Scans the given text for PII patterns.

    Args:
        text (str): The plain text content to scan.

    Returns:
        set[str]: A set of detected PII types (e.g., {"email", "phone"}).
    """
    found = set()

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found.add(pii_type)

    return found
