"""Tests for extraction queue with concurrency management."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os


class TestExtractionQueue:
    """Tests for the extraction queue."""

    @pytest.mark.asyncio
    async def test_queue_limits_concurrency(self):
        """Queue should limit concurrent extractions to MAX_CONCURRENT."""
        from app.core.extraction_queue import process_extraction_queue, MAX_CONCURRENT

        # Track concurrent executions
        concurrent_count = 0
        max_concurrent_seen = 0
        lock = asyncio.Lock()

        async def mock_extract(item_id, url, api_key, db):
            nonlocal concurrent_count, max_concurrent_seen
            async with lock:
                concurrent_count += 1
                if concurrent_count > max_concurrent_seen:
                    max_concurrent_seen = concurrent_count

            await asyncio.sleep(0.1)  # Simulate work

            async with lock:
                concurrent_count -= 1

            return {"item_id": item_id, "status": "success", "price": 10.0}

        # Create 20 mock items (more than MAX_CONCURRENT)
        items = [MagicMock(id=i, url=f"http://example.com/{i}") for i in range(20)]

        with patch('app.core.extraction_queue.extract_single_item', side_effect=mock_extract):
            with patch('app.core.extraction_queue.get_api_key', return_value="fake_key"):
                results = await process_extraction_queue(items, MagicMock())

        assert max_concurrent_seen <= MAX_CONCURRENT
        assert len(results) == 20

    @pytest.mark.asyncio
    async def test_queue_processes_all_items(self):
        """Queue should process all items and return results."""
        from app.core.extraction_queue import process_extraction_queue

        async def mock_extract(item_id, url, api_key, db):
            return {"item_id": item_id, "status": "success", "price": 10.0}

        items = [MagicMock(id=i, url=f"http://example.com/{i}") for i in range(5)]

        with patch('app.core.extraction_queue.extract_single_item', side_effect=mock_extract):
            with patch('app.core.extraction_queue.get_api_key', return_value="fake_key"):
                results = await process_extraction_queue(items, MagicMock())

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["item_id"] == i

    @pytest.mark.asyncio
    async def test_queue_continues_on_failure(self):
        """Queue should continue processing even if one item fails."""
        from app.core.extraction_queue import process_extraction_queue

        call_count = 0

        async def mock_extract(item_id, url, api_key, db):
            nonlocal call_count
            call_count += 1
            if item_id == 2:
                raise Exception("Simulated failure")
            return {"item_id": item_id, "status": "success", "price": 10.0}

        items = [MagicMock(id=i, url=f"http://example.com/{i}") for i in range(5)]

        with patch('app.core.extraction_queue.extract_single_item', side_effect=mock_extract):
            with patch('app.core.extraction_queue.get_api_key', return_value="fake_key"):
                results = await process_extraction_queue(items, MagicMock())

        # All items should be attempted
        assert call_count == 5
        # Results should include all items (success and failure)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_queue_returns_error_for_failed_items(self):
        """Queue should return error status for failed items."""
        from app.core.extraction_queue import process_extraction_queue

        async def mock_extract(item_id, url, api_key, db):
            if item_id == 1:
                raise Exception("API error")
            return {"item_id": item_id, "status": "success", "price": 10.0}

        items = [MagicMock(id=i, url=f"http://example.com/{i}") for i in range(3)]

        with patch('app.core.extraction_queue.extract_single_item', side_effect=mock_extract):
            with patch('app.core.extraction_queue.get_api_key', return_value="fake_key"):
                results = await process_extraction_queue(items, MagicMock())

        # Check that failed item has error status
        failed = [r for r in results if r.get("status") == "error"]
        assert len(failed) == 1
        assert failed[0]["item_id"] == 1

    @pytest.mark.asyncio
    async def test_queue_empty_items(self):
        """Queue should handle empty item list gracefully."""
        from app.core.extraction_queue import process_extraction_queue

        results = await process_extraction_queue([], MagicMock())
        assert results == []

    @pytest.mark.asyncio
    async def test_queue_no_api_key(self):
        """Queue should return error when no API key configured."""
        from app.core.extraction_queue import process_extraction_queue

        items = [MagicMock(id=1, url="http://example.com/1")]

        with patch('app.core.extraction_queue.get_api_key', return_value=None):
            results = await process_extraction_queue(items, MagicMock())

        assert len(results) == 1
        assert results[0]["status"] == "error"
        assert "GEMINI_API_KEY" in results[0].get("error", "")
