"""
Template Utilities
=================
Utilities for handling template rendering, including defensive value handling.

This module provides functions to safely access and format data for templates,
particularly for handling null or missing values gracefully.
"""

import json
from typing import Any, Dict, List, Optional, Union


def safe_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Safely access nested dictionary values by dot notation path.
    
    Args:
        data: Dictionary to access
        path: Dot notation path (e.g., "dns_connection_analysis.details.domains")
        default: Value to return if path doesn't exist
        
    Returns:
        Value at path or default if not found
    """
    if not data or not isinstance(data, dict):
        return default
        
    if "." not in path:
        return data.get(path, default)
    
    parts = path.split(".", 1)
    first, rest = parts[0], parts[1]
    
    if first not in data:
        return default
        
    return safe_get(data[first], rest, default)


def safe_number(value: Any, default: Union[int, float] = 0) -> Union[int, float]:
    """
    Safely convert a value to a number, handling various types and edge cases.
    
    Args:
        value: Value to convert to number
        default: Default value if conversion fails
        
    Returns:
        Numeric representation or default
    """
    if value is None:
        return default
        
    if isinstance(value, (int, float)):
        return value
        
    # Handle string representations
    if isinstance(value, str):
        # Remove formatting
        clean_value = value.replace(',', '').replace('s', '').strip()
        try:
            if '.' in clean_value:
                return float(clean_value)
            else:
                return int(clean_value)
        except (ValueError, TypeError):
            return default
            
    return default


def format_ms(milliseconds: Any, precision: int = 1, default: str = "0ms") -> str:
    """
    Format milliseconds to a human-readable string.
    
    Args:
        milliseconds: Time in milliseconds
        precision: Decimal precision for seconds
        default: Default string if value is invalid
        
    Returns:
        Formatted string (e.g., "300ms" or "2.5s")
    """
    ms = safe_number(milliseconds)
    
    if ms == 0:
        return default
        
    if ms < 1000:
        return f"{int(ms)}ms"
    
    seconds = ms / 1000
    return f"{seconds:.{precision}f}s"


def format_bytes(bytes_value: Any, precision: int = 1, default: str = "0B") -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        bytes_value: Size in bytes
        precision: Decimal precision
        default: Default string if value is invalid
        
    Returns:
        Formatted string (e.g., "1.5KB" or "2.3MB")
    """
    bytes_val = safe_number(bytes_value)
    
    if bytes_val == 0:
        return default
        
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    
    while bytes_val >= 1024 and unit_index < len(units) - 1:
        bytes_val /= 1024
        unit_index += 1
    
    return f"{bytes_val:.{precision}f}{units[unit_index]}"


def ensure_list(value: Any) -> List:
    """
    Ensure a value is a list, handling various input types.
    
    Args:
        value: Value to convert to list
        
    Returns:
        List representation of value
    """
    if value is None:
        return []
        
    if isinstance(value, list):
        return value
        
    if isinstance(value, str):
        # Handle string-encoded JSON arrays
        if value.startswith('[') and value.endswith(']'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return [value]
        
    # For dictionaries, wrap in a list
    if isinstance(value, dict):
        return [value]
        
    # For other iterables, convert to list
    try:
        return list(value)
    except:
        return [value]


def default_if_none(value: Any, default: Any) -> Any:
    """
    Return default if value is None.
    
    Args:
        value: Value to check
        default: Default value if None
        
    Returns:
        value or default
    """
    return default if value is None else value


def truncate_string(value: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string if it exceeds max_length.
    
    Args:
        value: String to truncate
        max_length: Maximum length before truncating
        suffix: String to append when truncated
        
    Returns:
        Truncated string
    """
    if not isinstance(value, str):
        return str(value)
        
    if len(value) <= max_length:
        return value
        
    return value[:max_length - len(suffix)] + suffix
