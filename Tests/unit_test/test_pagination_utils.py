"""
Unit tests for pagination utility functions.

This module tests the normalize_pagination function to ensure it correctly
normalizes and validates pagination parameters.
"""

import pytest
import sys
import os

# Add the swagger_server module to the path so we can import it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../python-flask-server-generated'))

from swagger_server.service.utils import normalize_pagination


class TestNormalizePagination:
    """Test cases for the normalize_pagination function."""

    def test_normalize_pagination_with_defaults(self):
        """Test that default values are applied when None is passed."""
        page, per_page = normalize_pagination(None, None)
        assert page == 1, "Default page should be 1"
        assert per_page == 10, "Default per_page should be 10"

    def test_normalize_pagination_with_valid_values(self):
        """Test that valid values are returned unchanged."""
        page, per_page = normalize_pagination(2, 20)
        assert page == 2, "Page should be 2"
        assert per_page == 20, "Per page should be 20"

    def test_normalize_pagination_page_minimum(self):
        """Test that page is at least 1."""
        # Test with 0
        page, per_page = normalize_pagination(0, 10)
        assert page == 1, "Page should be minimum 1"

        # Test with negative
        page, per_page = normalize_pagination(-5, 10)
        assert page == 1, "Page should be minimum 1"

    def test_normalize_pagination_per_page_minimum(self):
        """Test that per_page defaults to 10 when 0 or negative is passed (treats 0 as falsy)."""
        # Test with 0 - treated as falsy, defaults to 10
        page, per_page = normalize_pagination(1, 0)
        assert per_page == 10, "Per page should default to 10 when 0 is passed (0 is falsy)"

        # Test with negative - clamped to minimum 1
        page, per_page = normalize_pagination(1, -10)
        assert per_page == 1, "Per page should be minimum 1 for negative values"

    def test_normalize_pagination_per_page_maximum(self):
        """Test that per_page is capped at 50."""
        # Test with exactly 50
        page, per_page = normalize_pagination(1, 50)
        assert per_page == 50, "Per page should be 50"

        # Test with more than 50
        page, per_page = normalize_pagination(1, 100)
        assert per_page == 50, "Per page should be capped at 50"

        # Test with way more than 50
        page, per_page = normalize_pagination(1, 1000)
        assert per_page == 50, "Per page should be capped at 50"

    def test_normalize_pagination_boundary_values(self):
        """Test boundary values for both parameters."""
        # Minimum boundary
        page, per_page = normalize_pagination(1, 1)
        assert page == 1, "Page should be 1"
        assert per_page == 1, "Per page should be 1"

        # Maximum boundary
        page, per_page = normalize_pagination(9999, 50)
        assert page == 9999, "Page should be 9999"
        assert per_page == 50, "Per page should be 50"

    def test_normalize_pagination_only_page_provided(self):
        """Test when only page is provided."""
        page, per_page = normalize_pagination(page=3, per_page=None)
        assert page == 3, "Page should be 3"
        assert per_page == 10, "Per page should default to 10"

    def test_normalize_pagination_only_per_page_provided(self):
        """Test when only per_page is provided."""
        page, per_page = normalize_pagination(page=None, per_page=15)
        assert page == 1, "Page should default to 1"
        assert per_page == 15, "Per page should be 15"

    def test_normalize_pagination_return_type(self):
        """Test that the function returns a tuple."""
        result = normalize_pagination(1, 10)
        assert isinstance(result, tuple), "Result should be a tuple"
        assert len(result) == 2, "Result should have 2 elements"

    def test_normalize_pagination_common_scenarios(self):
        """Test common real-world pagination scenarios."""
        # First page with default size
        page, per_page = normalize_pagination(1, 10)
        assert page == 1 and per_page == 10

        # Second page
        page, per_page = normalize_pagination(2, 10)
        assert page == 2 and per_page == 10

        # Large page number
        page, per_page = normalize_pagination(100, 20)
        assert page == 100 and per_page == 20

        # User trying to get too many items
        page, per_page = normalize_pagination(1, 500)
        assert per_page == 50, "Should cap at 50 items per page"

    @pytest.mark.parametrize("page,per_page,expected_page,expected_per_page", [
        (1, 10, 1, 10),
        (2, 20, 2, 20),
        (0, 10, 1, 10),  # Min page
        (-1, 10, 1, 10),  # Negative page
        (5, 50, 5, 50),  # Max per_page
        (5, 100, 5, 50),  # Over max per_page
        (5, 0, 5, 10),  # per_page 0 defaults to 10 (treated as falsy)
        (5, -5, 5, 1),  # Negative per_page
        (None, None, 1, 10),  # All defaults
        (None, 25, 1, 25),  # Default page
        (3, None, 3, 10),  # Default per_page
    ])
    def test_normalize_pagination_parametrized(self, page, per_page, expected_page, expected_per_page):
        """Parametrized test for various pagination scenarios."""
        result_page, result_per_page = normalize_pagination(page, per_page)
        assert result_page == expected_page, f"Page mismatch: expected {expected_page}, got {result_page}"
        assert result_per_page == expected_per_page, f"Per_page mismatch: expected {expected_per_page}, got {result_per_page}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
