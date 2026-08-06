"""
Canonical HCP Master Dictionary manager.
Provides 100% benchmark accurate doctor information for verification during manual review.
"""

class MasterDictionary:
    """
    Verified Reference Dictionary of Healthcare Professionals.
    This serves as the single source of truth (100% correct baseline information).
    """

    def __init__(self, sample_records=None):
        self.dictionary_db = sample_records or []

    def get_all(self):
        """Return all verified dictionary entries."""
        return self.dictionary_db

    def find_by_name(self, name_query: str):
        """Search dictionary by doctor name."""
        if not name_query:
            return []
        query = name_query.upper().strip()
        results = []
        for entry in self.dictionary_db:
            if query in entry.get("name", "").upper() or query in entry.get("canonical_name", "").upper():
                results.append(entry)
        return results

    def get_by_id(self, dict_id: str):
        """Retrieve dictionary entry by ID."""
        for entry in self.dictionary_db:
            if entry.get("id") == dict_id:
                return entry
        return None
