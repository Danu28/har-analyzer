"""
Schema Validation Utilities
==========================
Provides utilities for validating JSON data against a schema.

This module uses jsonschema to validate data structures against JSON schemas.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema package not found. Schema validation will be limited.")

# Path to schema directory
SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

def validate_against_schema(
    data: Dict[str, Any], 
    schema_file: str = "agent_summary_schema.json", 
    raise_exception: bool = False
) -> Dict[str, Any]:
    """
    Validate data against a JSON schema
    
    Args:
        data: Data to validate
        schema_file: Schema file name (in schemas directory)
        raise_exception: Whether to raise an exception on validation failure
        
    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": List[str] or None,
            "data": Original data
        }
    """
    result = {
        "valid": True,
        "errors": None,
        "data": data
    }
    
    # If jsonschema is not available, skip validation
    if not HAS_JSONSCHEMA:
        result["valid"] = None
        result["errors"] = ["jsonschema package not installed. Cannot validate."]
        return result
        
    schema_path = SCHEMA_DIR / schema_file
    
    # Check if schema file exists
    if not schema_path.exists():
        result["valid"] = False
        result["errors"] = [f"Schema file not found: {schema_path}"]
        
        if raise_exception:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        return result
    
    # Load schema
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except Exception as e:
        result["valid"] = False
        result["errors"] = [f"Error loading schema: {str(e)}"]
        
        if raise_exception:
            raise ValueError(f"Error loading schema: {str(e)}")
        return result
    
    # Validate data
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    
    if errors:
        result["valid"] = False
        result["errors"] = [_format_validation_error(error) for error in errors]
        
        if raise_exception:
            raise jsonschema.exceptions.ValidationError(
                f"Validation failed: {len(errors)} errors found"
            )
    
    return result

def _format_validation_error(error: jsonschema.exceptions.ValidationError) -> str:
    """Format a validation error into a human-readable message"""
    path = "/".join(str(p) for p in error.path) if error.path else "root"
    return f"At {path}: {error.message}"

def check_missing_fields(data: Dict[str, Any], required_fields: Dict[str, List[str]]) -> List[str]:
    """
    Check for missing required fields in the data
    
    Args:
        data: Data to check
        required_fields: Dictionary of section names to lists of required field names
        
    Returns:
        List of error messages for missing fields
    """
    errors = []
    
    for section, fields in required_fields.items():
        if section not in data:
            errors.append(f"Missing required section: '{section}'")
            continue
            
        for field in fields:
            if field not in data[section]:
                errors.append(f"Missing required field: '{section}.{field}'")
                
    return errors
