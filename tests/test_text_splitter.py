"""
Unit tests for src/text_splitter.py

These tests capture the current (characterization) behavior of TextSplitter.
They are based on observations from the characterization test run on 2026-05-04.
No source code was modified.
"""
import pytest
from src.text_splitter import TextSplitter


@pytest.fixture
def splitter():
    return TextSplitter()


# ─── count_tokens ────────────────────────────────────────────────

class TestCountTokens:
    def test_simple_sentence(self, splitter):
        """Characterization: 'Hello world! This is a test.' → 8 tokens (o200k_base)."""
        assert splitter.count_tokens("Hello world! This is a test.") == 8

    def test_empty_string(self, splitter):
        """Empty string should return 0 tokens."""
        assert splitter.count_tokens("") == 0

    def test_single_word(self, splitter):
        """Single common word should return 1 token."""
        assert splitter.count_tokens("Hello") == 1

    def test_long_text_positive(self, splitter):
        """A longer string should always return a positive token count."""
        long_text = "word " * 500
        count = splitter.count_tokens(long_text)
        assert count > 0
        assert isinstance(count, int)


# ─── _split_page ─────────────────────────────────────────────────

class TestSplitPage:
    def test_splits_into_expected_chunks(self, splitter):
        """Characterization: with chunk_size=10, the test sentence splits into 3 chunks."""
        page = {
            "page": 1,
            "text": "This is a long sentence that should be split into smaller chunks if we set the chunk size small enough for testing purposes."
        }
        chunks = splitter._split_page(page, chunk_size=10, chunk_overlap=2)
        assert len(chunks) == 3

    def test_chunk_metadata(self, splitter):
        """Each chunk should carry page number, text, and length_tokens."""
        page = {"page": 5, "text": "A short text for testing."}
        chunks = splitter._split_page(page, chunk_size=300, chunk_overlap=50)
        assert len(chunks) >= 1
        chunk = chunks[0]
        assert chunk["page"] == 5
        assert isinstance(chunk["text"], str)
        assert isinstance(chunk["length_tokens"], int)
        assert chunk["length_tokens"] > 0

    def test_empty_page(self, splitter):
        """An empty page should produce an empty chunk list."""
        page = {"page": 1, "text": ""}
        chunks = splitter._split_page(page, chunk_size=300, chunk_overlap=50)
        assert chunks == []

    def test_short_text_single_chunk(self, splitter):
        """Text shorter than chunk_size should produce exactly 1 chunk."""
        page = {"page": 1, "text": "Short."}
        chunks = splitter._split_page(page, chunk_size=300, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "Short."


# ─── _get_serialized_tables_by_page ──────────────────────────────

class TestGetSerializedTablesByPage:
    def test_groups_by_page(self, splitter):
        """Characterization: tables should be grouped by their page number."""
        tables = [
            {
                "page": 2,
                "table_id": "t1",
                "serialized": {
                    "information_blocks": [
                        {"information_block": "Row 1: Data 1"},
                        {"information_block": "Row 2: Data 2"}
                    ]
                }
            }
        ]
        result = splitter._get_serialized_tables_by_page(tables)
        assert 2 in result
        assert len(result[2]) == 1
        assert result[2][0]["table_id"] == "t1"
        assert "Row 1: Data 1\nRow 2: Data 2" == result[2][0]["text"]

    def test_multiple_tables_same_page(self, splitter):
        """Multiple tables on the same page should all be grouped together."""
        tables = [
            {
                "page": 3, "table_id": "t1",
                "serialized": {"information_blocks": [{"information_block": "A"}]}
            },
            {
                "page": 3, "table_id": "t2",
                "serialized": {"information_blocks": [{"information_block": "B"}]}
            }
        ]
        result = splitter._get_serialized_tables_by_page(tables)
        assert len(result[3]) == 2

    def test_skips_tables_without_serialized(self, splitter):
        """Tables missing the 'serialized' key should be skipped."""
        tables = [{"page": 1, "table_id": "t1"}]
        result = splitter._get_serialized_tables_by_page(tables)
        assert result == {}

    def test_empty_list(self, splitter):
        """Empty table list should produce empty dict."""
        assert splitter._get_serialized_tables_by_page([]) == {}


# ─── _split_report ───────────────────────────────────────────────

class TestSplitReport:
    def test_basic_report_chunking(self, splitter):
        """A simple report with one page should produce chunks with correct ids and types."""
        report = {
            "content": {
                "pages": [
                    {"page": 1, "text": "This is page one content."}
                ]
            }
        }
        result = splitter._split_report(report)
        chunks = result["content"]["chunks"]
        assert len(chunks) >= 1
        assert chunks[0]["id"] == 0
        assert chunks[0]["type"] == "content"
        assert chunks[0]["page"] == 1

    def test_multi_page_ids_are_sequential(self, splitter):
        """Chunk IDs should be sequential across multiple pages."""
        report = {
            "content": {
                "pages": [
                    {"page": 1, "text": "Page one."},
                    {"page": 2, "text": "Page two."}
                ]
            }
        }
        result = splitter._split_report(report)
        chunks = result["content"]["chunks"]
        ids = [c["id"] for c in chunks]
        assert ids == list(range(len(ids)))

    def test_empty_pages(self, splitter):
        """Report with an empty page should produce no chunks for that page."""
        report = {
            "content": {
                "pages": [
                    {"page": 1, "text": ""},
                    {"page": 2, "text": "Some content."}
                ]
            }
        }
        result = splitter._split_report(report)
        chunks = result["content"]["chunks"]
        # Only page 2 should have chunks
        pages_with_chunks = set(c["page"] for c in chunks)
        assert 1 not in pages_with_chunks
        assert 2 in pages_with_chunks
