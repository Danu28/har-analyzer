"""
Test Template Helpers
==================
Tests for the template_helpers module.

These tests verify that the template helper functions work correctly,
especially for edge cases and defensive coding situations.
"""

import unittest
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.template_helpers import (
    safe_get,
    safe_format_time,
    safe_format_size,
    safe_length,
    safe_json_parse,
    truncate_url,
    format_date,
    get_css_class,
    percentage
)


class TestTemplateHelpers(unittest.TestCase):
    """Test suite for template helper functions."""

    def test_safe_get(self):
        """Test safe_get function."""
        data = {"a": 1, "b": {"c": 2}}
        self.assertEqual(safe_get(data, "a"), 1)
        self.assertEqual(safe_get(data, "x"), None)
        self.assertEqual(safe_get(data, "x", 42), 42)
        self.assertEqual(safe_get(None, "a", "default"), "default")
        self.assertEqual(safe_get({}, "a", "empty"), "empty")

    def test_safe_format_time(self):
        """Test safe_format_time function."""
        self.assertEqual(safe_format_time(500), "500ms")
        self.assertEqual(safe_format_time(1500), "1.50s")
        self.assertEqual(safe_format_time(90000), "1.50min")
        self.assertEqual(safe_format_time("1500"), "1.50s")
        self.assertEqual(safe_format_time(None), "N/A")
        self.assertEqual(safe_format_time("invalid"), "N/A")
        self.assertEqual(safe_format_time(None, "Unknown"), "Unknown")
        self.assertEqual(safe_format_time(0), "0ms")

    def test_safe_format_size(self):
        """Test safe_format_size function."""
        self.assertEqual(safe_format_size(500), "500B")
        self.assertEqual(safe_format_size(1500), "1.46KB")
        self.assertEqual(safe_format_size(1500000), "1.43MB")
        self.assertEqual(safe_format_size("1500"), "1.46KB")
        self.assertEqual(safe_format_size(None), "N/A")
        self.assertEqual(safe_format_size("invalid"), "N/A")
        self.assertEqual(safe_format_size(None, "Unknown"), "Unknown")
        self.assertEqual(safe_format_size(0), "0B")

    def test_safe_length(self):
        """Test safe_length function."""
        self.assertEqual(safe_length([1, 2, 3]), 3)
        self.assertEqual(safe_length("abc"), 3)
        self.assertEqual(safe_length(None), 0)
        self.assertEqual(safe_length(123), 0)
        self.assertEqual(safe_length(None, 42), 42)

    def test_safe_json_parse(self):
        """Test safe_json_parse function."""
        self.assertEqual(safe_json_parse('{"a": 1, "b": 2}'), {"a": 1, "b": 2})
        self.assertEqual(safe_json_parse('[1, 2, 3]'), [1, 2, 3])
        self.assertEqual(safe_json_parse('invalid'), None)
        self.assertEqual(safe_json_parse(''), None)
        self.assertEqual(safe_json_parse(None), None)
        self.assertEqual(safe_json_parse('invalid', []), [])

    def test_truncate_url(self):
        """Test truncate_url function."""
        self.assertEqual(truncate_url("https://example.com/path"), "https://example.com/path")
        
        # Just verify that truncation happens, but don't test exact output
        # since the exact truncation algorithm might be adjusted
        truncated = truncate_url("https://example.com/very/long/path/that/exceeds/limit", 30)
        self.assertTrue(len(truncated) <= 30)
        self.assertTrue(truncated.startswith("https://"))
        self.assertTrue("..." in truncated)
        
        # For very long domains, verify the same properties
        truncated = truncate_url("https://verylongdomainnamethatexceedslimit.com", 30)
        self.assertTrue(len(truncated) <= 30)
        self.assertTrue("..." in truncated)
        
        self.assertEqual(truncate_url(""), "")
        self.assertEqual(truncate_url(None), "")

    def test_format_date(self):
        """Test format_date function."""
        self.assertEqual(format_date("2023-07-25T12:34:56"), "July 25, 2023")
        self.assertEqual(format_date("2023-07-25"), "July 25, 2023")
        self.assertEqual(format_date(""), "Unknown date")
        self.assertEqual(format_date(None), "Unknown date")
        self.assertEqual(format_date("invalid"), "Unknown date")
        self.assertEqual(format_date("2023-07-25", "%Y-%m-%d"), "2023-07-25")
        self.assertEqual(format_date("invalid", default="Custom default"), "Custom default")

    def test_get_css_class(self):
        """Test get_css_class function."""
        thresholds = {"danger": 80, "warning": 50, "success": 0}
        self.assertEqual(get_css_class(90, thresholds), "danger")
        self.assertEqual(get_css_class(60, thresholds), "warning")
        self.assertEqual(get_css_class(30, thresholds), "success")
        self.assertEqual(get_css_class(None, thresholds), "info")
        self.assertEqual(get_css_class("invalid", thresholds), "info")
        self.assertEqual(get_css_class(None, thresholds, "default"), "default")

    def test_percentage(self):
        """Test percentage function."""
        self.assertEqual(percentage(50, 100), "50.0%")
        self.assertEqual(percentage(33, 100), "33.0%")
        self.assertEqual(percentage(0, 100), "0%")
        self.assertEqual(percentage(100, 0), "0%")
        self.assertEqual(percentage(None, 100), "0%")
        self.assertEqual(percentage(50, None), "0%")
        self.assertEqual(percentage("invalid", 100), "0%")
        self.assertEqual(percentage(None, None, "N/A"), "N/A")


if __name__ == "__main__":
    unittest.main()
