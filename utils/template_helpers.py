"""
Template Helper Functions
========================
Helper functions for use in Jinja2 templates to handle data safely and consistently.

These functions can be included in templates to provide defensive coding,
formatting, and other utilities.
"""

import re
import json
from datetime import datetime
from typing import Any, Dict, List, Union, Optional


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary, return default if not found."""
    if data is None:
        return default
    return data.get(key, default)


def safe_format_time(milliseconds: Union[int, float, str, None], 
                    default: str = "N/A") -> str:
    """Format milliseconds as a human-readable string with appropriate units."""
    if milliseconds is None:
        return default
        
    try:
        ms = float(milliseconds)
    except (ValueError, TypeError):
        return default
        
    if ms < 1:
        return "0ms"
    elif ms < 1000:
        return f"{int(ms)}ms"
    elif ms < 60000:
        return f"{ms/1000:.2f}s"
    else:
        return f"{ms/60000:.2f}min"


def safe_format_size(bytes_value: Union[int, float, str, None],
                    default: str = "N/A") -> str:
    """Format bytes as a human-readable string with appropriate units."""
    if bytes_value is None:
        return default
        
    try:
        bytes_val = float(bytes_value)
    except (ValueError, TypeError):
        return default
        
    if bytes_val < 1:
        return "0B"
    elif bytes_val < 1024:
        return f"{int(bytes_val)}B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val/1024:.2f}KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val/(1024*1024):.2f}MB"
    else:
        return f"{bytes_val/(1024*1024*1024):.2f}GB"


def safe_length(value: Any, default: int = 0) -> int:
    """Safely get the length of a value, return default if not a collection."""
    if value is None:
        return default
    try:
        return len(value)
    except (TypeError, AttributeError):
        return default


def safe_json_parse(json_string: str, default: Any = None) -> Any:
    """Safely parse a JSON string, return default if parsing fails."""
    if not json_string or not isinstance(json_string, str):
        return default
        
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return default


def truncate_url(url: str, max_length: int = 50) -> str:
    """Truncate a URL to a maximum length while preserving important parts."""
    if not url or not isinstance(url, str):
        return ""
        
    if len(url) <= max_length:
        return url
        
    # Extract domain
    match = re.search(r"https?://([^/]+)", url)
    if not match:
        return url[:max_length-3] + "..."
        
    domain = match.group(1)
    prefix = match.group(0)  # http:// or https://
    
    # If domain itself is too long, truncate it
    if len(domain) > max_length - 10:
        return domain[:max_length-3] + "..."
        
    # Try to keep the domain and part of the path
    path_max = max_length - len(prefix) - 3
    path_part = url[len(prefix):]
    
    if len(path_part) > path_max:
        path_part = path_part[:path_max] + "..."
            
    return f"{prefix}{path_part}"


def format_date(date_string: str, 
                format_str: str = "%B %d, %Y", 
                default: str = "Unknown date") -> str:
    """Format a date string, return default if parsing fails."""
    if not date_string:
        return default
        
    try:
        # Try ISO format first
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime(format_str)
    except (ValueError, AttributeError):
        # Try other common formats
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
            return date.strftime(format_str)
        except ValueError:
            pass
            
        try:
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            return date.strftime(format_str)
        except ValueError:
            return default


def get_css_class(value: Union[int, float, None], 
                 thresholds: Dict[str, Union[int, float]],
                 default: str = "info") -> str:
    """Get a CSS class based on thresholds."""
    if value is None:
        return default
        
    try:
        val = float(value)
    except (ValueError, TypeError):
        return default
        
    if "danger" in thresholds and val >= thresholds["danger"]:
        return "danger"
    elif "warning" in thresholds and val >= thresholds["warning"]:
        return "warning"
    elif "success" in thresholds and val >= thresholds["success"]:
        return "success"
    else:
        return default


def percentage(value: Union[int, float], total: Union[int, float], 
              default: str = "0%") -> str:
    """Calculate percentage and format as string."""
    if not value or not total:
        return default
        
    try:
        percent = (float(value) / float(total)) * 100
        return f"{percent:.1f}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def register_template_filters(app):
    """Register all template filters with a Flask app."""
    app.jinja_env.filters["safe_get"] = safe_get
    app.jinja_env.filters["safe_format_time"] = safe_format_time
    app.jinja_env.filters["safe_format_size"] = safe_format_size
    app.jinja_env.filters["safe_length"] = safe_length
    app.jinja_env.filters["safe_json_parse"] = safe_json_parse
    app.jinja_env.filters["truncate_url"] = truncate_url
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["get_css_class"] = get_css_class
    app.jinja_env.filters["percentage"] = percentage
