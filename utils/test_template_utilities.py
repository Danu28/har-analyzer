"""
Test Template Utilities
=====================
Tests for the template_utilities module to ensure safe data handling.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.template_utilities import (
    safe_get, 
    safe_number, 
    format_ms, 
    format_bytes,
    ensure_list,
    default_if_none,
    truncate_string
)


class TestTemplateUtilities(unittest.TestCase):
    
    def test_safe_get(self):
        """Test the safe_get function for nested dictionary access."""
        test_data = {
            "metadata": {
                "har_name": "test",
                "nested": {
                    "value": 123
                }
            },
            "empty": None
        }
        
        # Test successful path
        self.assertEqual(safe_get(test_data, "metadata.har_name"), "test")
        self.assertEqual(safe_get(test_data, "metadata.nested.value"), 123)
        
        # Test missing paths with default
        self.assertIsNone(safe_get(test_data, "missing"))
        self.assertEqual(safe_get(test_data, "missing", "default"), "default")
        self.assertEqual(safe_get(test_data, "metadata.missing"), None)
        self.assertEqual(safe_get(test_data, "metadata.missing", "default"), "default")
        
        # Test with empty/null values
        self.assertIsNone(safe_get(test_data, "empty.anything"))
        self.assertIsNone(safe_get(None, "any.path"))
        self.assertEqual(safe_get({}, "any.path", "default"), "default")
    
    def test_safe_number(self):
        """Test the safe_number function for various inputs."""
        # Test valid numbers
        self.assertEqual(safe_number(100), 100)
        self.assertEqual(safe_number(99.9), 99.9)
        
        # Test string numbers
        self.assertEqual(safe_number("100"), 100)
        self.assertEqual(safe_number("99.9"), 99.9)
        
        # Test formatted strings
        self.assertEqual(safe_number("1,234"), 1234)
        self.assertEqual(safe_number("2.5s"), 2.5)
        
        # Test invalid values
        self.assertEqual(safe_number(None), 0)
        self.assertEqual(safe_number("invalid"), 0)
        self.assertEqual(safe_number("invalid", 42), 42)
        
    def test_format_ms(self):
        """Test the format_ms function."""
        # Test milliseconds formatting
        self.assertEqual(format_ms(500), "500ms")
        self.assertEqual(format_ms("500"), "500ms")
        
        # Test seconds formatting
        self.assertEqual(format_ms(1500), "1.5s")
        self.assertEqual(format_ms(2000), "2.0s")
        
        # Test precision
        self.assertEqual(format_ms(1234, precision=2), "1.23s")
        self.assertEqual(format_ms(1234, precision=0), "1s")
        
        # Test defaults
        self.assertEqual(format_ms(0), "0ms")
        self.assertEqual(format_ms(None), "0ms")
        self.assertEqual(format_ms("invalid", default="N/A"), "N/A")
        
    def test_format_bytes(self):
        """Test the format_bytes function."""
        # Test byte formatting
        self.assertEqual(format_bytes(500), "500.0B")
        
        # Test kilobyte formatting
        self.assertEqual(format_bytes(1500), "1.5KB")
        
        # Test megabyte formatting
        self.assertEqual(format_bytes(1500000), "1.4MB")
        
        # Test precision
        self.assertEqual(format_bytes(1500, precision=2), "1.46KB")
        self.assertEqual(format_bytes(1500, precision=0), "1KB")
        
        # Test defaults
        self.assertEqual(format_bytes(0), "0B")
        self.assertEqual(format_bytes(None), "0B")
        self.assertEqual(format_bytes("invalid", default="N/A"), "N/A")
        
    def test_ensure_list(self):
        """Test the ensure_list function."""
        # Test with lists
        self.assertEqual(ensure_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(ensure_list([]), [])
        
        # Test with non-lists
        self.assertEqual(ensure_list("test"), ["test"])
        self.assertEqual(ensure_list(123), [123])
        self.assertEqual(ensure_list(None), [])
        
        # Test with JSON string
        self.assertEqual(ensure_list('[1, 2, 3]'), [1, 2, 3])
        
        # Test with dictionary
        self.assertEqual(ensure_list({"a": 1}), [{"a": 1}])
        
    def test_default_if_none(self):
        """Test the default_if_none function."""
        self.assertEqual(default_if_none(None, "default"), "default")
        self.assertEqual(default_if_none("value", "default"), "value")
        self.assertEqual(default_if_none(0, "default"), 0)
        
    def test_truncate_string(self):
        """Test the truncate_string function."""
        # Test no truncation needed
        self.assertEqual(truncate_string("short text", 20), "short text")
        
        # Test truncation
        self.assertEqual(truncate_string("this is a long text", 10), "this is...")
        
        # Test custom suffix
        self.assertEqual(truncate_string("this is a long text", 10, suffix="!"), "this is a!")
        
        # Test non-string input
        self.assertEqual(truncate_string(123, 10), "123")


if __name__ == "__main__":
    unittest.main()
