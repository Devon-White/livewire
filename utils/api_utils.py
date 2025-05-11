"""
API utilities for the LiveWire demo app.
Provides consistent error handling and response formatting for API endpoints.
"""
from flask import jsonify, request
import logging
from functools import wraps
import inspect
import json

logger = logging.getLogger(__name__)

def api_error(message, status_code=400, log_level='warning', details=None):
    """
    Create a standardized error response for API endpoints.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        log_level (str): Logging level ('info', 'warning', 'error', etc.)
        details (dict): Optional additional error details
        
    Returns:
        tuple: (response_json, status_code) for Flask to return
    """
    log_func = getattr(logger, log_level, logger.warning)
    
    # Include status code and details (if any) in log
    if details:
        log_func(f"API Error ({status_code}): {message} - Details: {details}")
    else:
        log_func(f"API Error ({status_code}): {message}")
    
    # Construct response
    response = {
        'error': True,
        'message': message
    }
    
    # Add details if provided
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def api_success(data=None, message=None, status_code=200):
    """
    Create a standardized success response for API endpoints.
    
    Args:
        data (dict, optional): Response data
        message (str, optional): Success message
        status_code (int): HTTP status code
        
    Returns:
        tuple: (response_json, status_code) for Flask to return
    """
    response = {'success': True}
    
    if data is not None:
        response['data'] = data
        
    if message is not None:
        response['message'] = message
        
    return jsonify(response), status_code

def _validate_field_type(field_name, value, expected_type, custom_error=None):
    """
    Validate that a field has the expected type
    
    Args:
        field_name (str): Name of the field
        value: Value to validate
        expected_type (type or tuple): Expected type(s)
        custom_error (str): Optional custom error message
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Handle special case for None values
    if value is None:
        return False, custom_error or f"Field '{field_name}' cannot be null or missing"
    
    # Handle special case for 'str' and checking for empty strings
    if expected_type == str and value == "":
        return False, custom_error or f"Field '{field_name}' cannot be empty"
    
    if not isinstance(value, expected_type):
        type_names = expected_type.__name__ if not isinstance(expected_type, tuple) else \
                    " or ".join(t.__name__ for t in expected_type)
        return False, custom_error or f"Field '{field_name}' must be of type {type_names}"
    
    return True, None

def validate_json_request(required_fields=None, field_types=None, custom_validators=None):
    """
    Decorator for API endpoints that require JSON data with specific fields and types.
    
    Args:
        required_fields (list): Optional list of required fields in the JSON body
        field_types (dict): Optional dict mapping field names to expected types
        custom_validators (dict): Optional dict mapping field names to validator functions
            Each validator should take a value and return (is_valid, error_message)
        
    Returns:
        The decorated function or an error response
    """
    # Normalize parameters
    required_fields = required_fields or []
    field_types = field_types or {}
    custom_validators = custom_validators or {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            validation_errors = []
            
            # Check if request has JSON content type
            if not request.is_json:
                return api_error(
                    'This endpoint only accepts JSON data', 
                    400, 
                    details={'content_type': request.content_type}
                )
            
            # Try to parse JSON data
            try:
                # Force parsing to catch malformed JSON early
                _ = request.json
            except json.JSONDecodeError as e:
                return api_error(
                    'Malformed JSON in request body', 
                    400, 
                    details={'parse_error': str(e)}
                )
                
            # If required fields are specified, validate their presence
            if required_fields:
                missing = []
                for field in required_fields:
                    if field not in request.json:
                        missing.append(field)
                
                if missing:
                    return api_error(
                        f'Missing required fields in request body', 
                        400, 
                        details={'missing_fields': missing}
                    )
            
            # If field types are specified, validate them
            for field, expected_type in field_types.items():
                # Skip if field isn't in the request (already handled by required_fields)
                if field not in request.json:
                    continue
                
                # Validate type
                is_valid, error = _validate_field_type(field, request.json[field], expected_type)
                if not is_valid:
                    validation_errors.append(error)
            
            # Run custom validators
            for field, validator in custom_validators.items():
                # Skip if field isn't in the request
                if field not in request.json:
                    continue
                
                # Run the validator
                is_valid, error = validator(request.json[field])
                if not is_valid:
                    validation_errors.append(error)
            
            # Return validation errors if any
            if validation_errors:
                return api_error(
                    'Validation failed for request body', 
                    400, 
                    details={'validation_errors': validation_errors}
                )
                    
            # All validation passed, proceed with the actual function
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Common validators
def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import re
    if not isinstance(email, str):
        return False, "Email must be a string"
    
    # Basic email format check
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None

# Remove validate_phone as it is unused 