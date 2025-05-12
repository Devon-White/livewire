"""
API utilities for the LiveWire demo app.
Provides consistent error handling and response formatting for API endpoints.
"""

import inspect
import json
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, List, Union

from flask import jsonify, request

logger = logging.getLogger(__name__)


def api_error(
    message: str,
    status_code: int = 400,
    log_level: str = "warning",
    details: Optional[Dict[str, Any]] = None,
) -> Tuple[Any, int]:
    """
    Create a standardized error response for API endpoints.

    Args:
        message (str): Error message
        status_code (int): HTTP status code
        log_level (str): Logging level ('info', 'warning', 'error', etc.)
        details (Optional[Dict[str, Any]]): Optional additional error details

    Returns:
        Tuple[Any, int]: (response_json, status_code) for Flask to return
    """
    log_func = getattr(logger, log_level, logger.warning)

    # Include status code and details (if any) in log
    if details:
        log_func(f"API Error ({status_code}): {message} - Details: {details}")
    else:
        log_func(f"API Error ({status_code}): {message}")

    # Construct response
    response = {"error": True, "message": message}

    # Add details if provided
    if details:
        response["details"] = details

    return jsonify(response), status_code


def api_success(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = 200,
) -> Tuple[Any, int]:
    """
    Create a standardized success response for API endpoints.

    Args:
        data (Optional[Dict[str, Any]]): Response data
        message (Optional[str]): Success message
        status_code (int): HTTP status code

    Returns:
        Tuple[Any, int]: (response_json, status_code) for Flask to return
    """
    response = {"success": True}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return jsonify(response), status_code


def _get_nested_value(data: Dict[str, Any], path: str) -> Tuple[Any, bool]:
    """
    Get a value from a nested dictionary using dot notation.
    
    Args:
        data (Dict[str, Any]): The dictionary to search in
        path (str): The path to the value using dot notation (e.g., "user.address.city")
        
    Returns:
        Tuple[Any, bool]: (value, exists_flag)
    """
    if not path:
        return None, False
        
    parts = path.split('.')
    current = data
    
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None, False
        current = current[part]
        
    return current, True


def _validate_field_type(
    field_name: str, value: Any, expected_type: Any, required: bool = False, custom_error: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a field has the expected type

    Args:
        field_name (str): Name of the field
        value (Any): Value to validate
        expected_type (type or tuple): Expected type(s)
        required (bool): Whether the field is required
        custom_error (Optional[str]): Optional custom error message

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # For optional fields, allow None or empty string
    if not required and (value is None or (expected_type == str and value == "")):
        return True, None

    # For required fields, enforce non-empty
    if required:
        if value is None:
            return False, custom_error or f"Field '{field_name}' cannot be null or missing"
        if expected_type == str and value == "":
            return False, custom_error or f"Field '{field_name}' cannot be empty"

    if not isinstance(value, expected_type):
        type_names = (
            expected_type.__name__
            if not isinstance(expected_type, tuple)
            else " or ".join(t.__name__ for t in expected_type)
        )
        return (
            False,
            custom_error or f"Field '{field_name}' must be of type {type_names}",
        )

    return True, None


def validate_json_request(
    required_fields: Optional[List[str]] = None,
    field_types: Optional[Dict[str, Any]] = None,
    custom_validators: Optional[Dict[str, Callable]] = None,
) -> Callable:
    """
    Decorator for API endpoints that require JSON data with specific fields and types.
    Supports nested fields using dot notation (e.g., "user.address.city").

    Args:
        required_fields (Optional[list]): Optional list of required fields in the JSON body
        field_types (Optional[dict]): Optional dict mapping field names to expected types
        custom_validators (Optional[dict]): Optional dict mapping field names to validator functions
            Each validator should take a value and return (is_valid, error_message)

    Returns:
        Callable: The decorated function or an error response
    """
    # Normalize parameters
    required_fields = required_fields or []
    field_types = field_types or {}
    custom_validators = custom_validators or {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_errors = []

            # Check if request has JSON content type
            if not request.is_json:
                return api_error(
                    "This endpoint only accepts JSON data",
                    400,
                    details={"content_type": request.content_type},
                )

            # Try to parse JSON data
            try:
                data = request.json
            except json.JSONDecodeError as e:
                return api_error(
                    "Malformed JSON in request body",
                    400,
                    details={"parse_error": str(e)},
                )

            # If required fields are specified, validate their presence
            if required_fields:
                missing = []
                for field in required_fields:
                    # Handle nested fields
                    value, exists = _get_nested_value(data, field) if '.' in field else (data.get(field), field in data)
                    if not exists:
                        missing.append(field)

                if missing:
                    return api_error(
                        f"Missing required fields in request body",
                        400,
                        details={"missing_fields": missing},
                    )

            # If field types are specified, validate them
            for field, expected_type in field_types.items():
                is_required = field in required_fields
                # Handle nested fields
                if '.' in field:
                    value, exists = _get_nested_value(data, field)
                    if exists:  # Skip if field doesn't exist (already handled by required_fields)
                        is_valid, error = _validate_field_type(field, value, expected_type, required=is_required)
                        if not is_valid:
                            validation_errors.append(error)
                else:
                    # Skip if field isn't in the request (already handled by required_fields)
                    if field not in data:
                        continue
                    # Validate type
                    is_valid, error = _validate_field_type(field, data[field], expected_type, required=is_required)
                    if not is_valid:
                        validation_errors.append(error)

            # Run custom validators
            for field, validator in custom_validators.items():
                # Handle nested fields
                if '.' in field:
                    value, exists = _get_nested_value(data, field)
                    if exists:  # Skip if field doesn't exist
                        is_valid, error = validator(value)
                        if not is_valid:
                            validation_errors.append(error) 
                else:
                    # Skip if field isn't in the request
                    if field not in data:
                        continue

                    # Run the validator
                    is_valid, error = validator(data[field])
                    if not is_valid:
                        validation_errors.append(error)

            # Return validation errors if any
            if validation_errors:
                return api_error(
                    "Validation failed for request body",
                    400,
                    details={"validation_errors": validation_errors},
                )

            # All validation passed, proceed with the actual function
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Common validators
def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format

    Args:
        email (str): Email to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    import re

    # Check type first
    if not isinstance(email, str):
        return False, "Email must be a string"

    # Basic email format check
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Valid email
    return True, None


# Remove validate_phone as it is unused
