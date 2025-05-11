"""
SignalWire API client for the LiveWire demo app.
Provides a consistent interface for interacting with SignalWire APIs.
"""
import requests
import base64
import logging
import time
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

logger = logging.getLogger(__name__)

class SignalWireAPIError(Exception):
    """
    Exception raised for SignalWire API errors.
    
    Attributes:
        message (str): Error message from the API or error handler
        status_code (int, optional): HTTP status code from the API response
        is_retryable (bool): Indicates whether the error is potentially retryable
    """
    
    def __init__(self, message, status_code=None, is_retryable=False):
        """
        Initialize the SignalWire API error.
        
        Args:
            message (str): Error message
            status_code (int, optional): HTTP status code
            is_retryable (bool): Whether this error can be retried
        """
        self.message = message
        self.status_code = status_code
        self.is_retryable = is_retryable
        super().__init__(self.message)

class SignalWireClient:
    """
    Client for interacting with SignalWire APIs.
    
    This class provides a consistent interface for all SignalWire API operations,
    including SWML handlers, subscriber management, and call control.
    
    Features:
    - Consistent error handling with custom exceptions
    - Automatic retry for transient errors
    - Exponential backoff for rate limiting
    - Detailed logging for debugging
    - Helper methods for common operations
    """
    
    def __init__(self, project_id, auth_token, space_name, max_retries=3, retry_delay=1):
        """
        Initialize the SignalWire client with credentials.
        
        Args:
            project_id (str): SignalWire project ID
            auth_token (str): SignalWire auth token
            space_name (str): SignalWire space name (domain part of the URL)
            max_retries (int): Maximum number of retries for retryable errors
            retry_delay (float): Base delay in seconds between retries (increases exponentially)
        """
        self.project_id = project_id
        self.auth_token = auth_token
        self.space_name = space_name
        self.base_url = f"https://{space_name}.signalwire.com/api"
        self._headers = self._get_auth_headers()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def _get_auth_headers(self):
        """
        Generate authorization headers for API requests.
        
        Returns:
            dict: Headers with Basic authentication and JSON content type
        """
        auth = base64.b64encode(f"{self.project_id}:{self.auth_token}".encode()).decode()
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Basic {auth}'
        }
    
    def _is_retryable_error(self, status_code):
        """
        Determine if an error status code is retryable.
        
        Args:
            status_code (int): HTTP status code
            
        Returns:
            bool: True if the error should be retried, False otherwise
        """
        # 429 (too many requests), 500, 502, 503, 504 (server errors) are retryable
        return status_code in (429, 500, 502, 503, 504)
    
    def _request(self, method, endpoint, data=None, params=None, retries_left=None):
        """
        Make a request to the SignalWire API with retry logic.
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, etc.)
            endpoint (str): API endpoint path
            data (dict): Optional JSON payload
            params (dict): Optional URL parameters
            retries_left (int): Number of retries left (used internally)
            
        Returns:
            dict: Response data on success
            
        Raises:
            SignalWireAPIError: On API error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Set initial retries if not specified
        if retries_left is None:
            retries_left = self.max_retries
        
        try:
            logger.debug(f"SignalWire API request: {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers,
                json=data,
                params=params,
                timeout=10  # Set a reasonable timeout
            )
            
            # Raise exception for non-2xx responses
            response.raise_for_status()
            
            # Return JSON data if present
            if response.text:
                return response.json()
            else:
                return {"status": "success"}
                
        except HTTPError as e:
            # Handle API errors
            error_text = e.response.text
            status_code = e.response.status_code
            
            # Check retry conditions for appropriate status codes
            if retries_left > 0 and self._is_retryable_error(status_code):
                # Calculate backoff time with exponential backoff
                backoff = self.retry_delay * (2 ** (self.max_retries - retries_left))
                
                # Log retry attempt
                logger.warning(
                    f"Retryable error encountered: {status_code}. "
                    f"Retrying in {backoff:.2f}s. Attempts left: {retries_left}"
                )
                
                # Wait before retry
                time.sleep(backoff)
                
                # Recurse with one fewer retry
                return self._request(method, endpoint, data, params, retries_left - 1)
            
            # Parse error response
            try:
                error_data = e.response.json()
                error_msg = error_data.get('message', str(e))
            except:
                error_msg = error_text or str(e)
            
            # Enhanced logging for different error types
            if status_code == 429:
                logger.error(f"Rate limit exceeded: {method} {url} - {error_msg}")
            elif status_code >= 500:
                logger.error(f"SignalWire server error: {method} {url} - {status_code} - {error_msg}")
            else:
                logger.error(f"SignalWire API error: {method} {url} - {status_code} - {error_msg}")
                
            # Determine if the error would be retryable for the caller
            is_retryable = self._is_retryable_error(status_code)
            
            raise SignalWireAPIError(error_msg, status_code, is_retryable)
            
        except Timeout as e:
            # Handle timeout errors specifically
            logger.error(f"SignalWire API timeout: {method} {url} - {str(e)}")
            
            # Retry on timeout if we have retries left
            if retries_left > 0:
                backoff = self.retry_delay * (2 ** (self.max_retries - retries_left))
                logger.warning(f"Retrying after timeout in {backoff:.2f}s. Attempts left: {retries_left}")
                time.sleep(backoff)
                return self._request(method, endpoint, data, params, retries_left - 1)
                
            raise SignalWireAPIError(f"Request timed out: {str(e)}", is_retryable=True)
            
        except ConnectionError as e:
            # Handle connection errors
            logger.error(f"SignalWire API connection error: {method} {url} - {str(e)}")
            
            # Retry on connection error if we have retries left
            if retries_left > 0:
                backoff = self.retry_delay * (2 ** (self.max_retries - retries_left))
                logger.warning(f"Retrying after connection error in {backoff:.2f}s. Attempts left: {retries_left}")
                time.sleep(backoff)
                return self._request(method, endpoint, data, params, retries_left - 1)
                
            raise SignalWireAPIError(f"Connection error: {str(e)}", is_retryable=True)
            
        except RequestException as e:
            # Handle all other request errors
            logger.exception(f"SignalWire request failed: {method} {url} - {str(e)}")
            raise SignalWireAPIError(f"Request failed: {str(e)}")
    
    # SWML Handler methods
    
    def get_swml_handler(self, handler_id):
        """
        Get an existing SWML handler by ID.
        
        Args:
            handler_id (str): The ID of the SWML handler to retrieve
            
        Returns:
            dict: Details of the requested SWML handler
            
        Raises:
            SignalWireAPIError: If the handler doesn't exist or other API error
        """
        return self._request('GET', f"fabric/resources/external_swml_handlers/{handler_id}")
    
    def create_swml_handler(self, name, request_url):
        """
        Create a new SWML handler.
        
        Args:
            name (str): Name for the new SWML handler
            request_url (str): The URL that SignalWire will send requests to
            
        Returns:
            dict: Details of the created SWML handler including the ID
            
        Raises:
            SignalWireAPIError: If creation fails
        """
        payload = {
            "name": name,
            "primary_request_url": request_url
        }
        return self._request('POST', "fabric/resources/external_swml_handlers", payload)
    
    def update_swml_handler(self, handler_id, name, request_url):
        """
        Update an existing SWML handler.
        
        Args:
            handler_id (str): The ID of the SWML handler to update
            name (str): New name for the SWML handler
            request_url (str): New URL that SignalWire will send requests to
            
        Returns:
            dict: Updated handler details
            
        Raises:
            SignalWireAPIError: If update fails or handler doesn't exist
        """
        payload = {
            "name": name,
            "primary_request_url": request_url
        }
        return self._request('PATCH', f"fabric/resources/external_swml_handlers/{handler_id}", payload)
        
    def get_handler_addresses(self, handler_id):
        """
        Get addresses for a SWML handler.
        
        Args:
            handler_id (str): The ID of the SWML handler
            
        Returns:
            dict: Details of the addresses associated with the handler
            
        Raises:
            SignalWireAPIError: If retrieval fails or handler doesn't exist
        """
        return self._request('GET', f"fabric/resources/external_swml_handlers/{handler_id}/addresses")
    
    # Subscriber methods
    
    def get_subscriber(self, subscriber_id):
        """
        Get subscriber details by ID.
        
        Args:
            subscriber_id (str): The ID of the subscriber to retrieve
            
        Returns:
            dict: Details of the requested subscriber
            
        Raises:
            SignalWireAPIError: If the subscriber doesn't exist or other API error
        """
        return self._request('GET', f"fabric/resources/subscribers/{subscriber_id}")
    
    def get_subscribers(self):
        """
        Get all subscribers.
        
        Returns:
            dict: List of all subscribers in the account
            
        Raises:
            SignalWireAPIError: If retrieval fails
        """
        return self._request('GET', "fabric/resources/subscribers")
        
    def get_subscriber_by_email(self, email):
        """
        Find a subscriber by email.
        
        Args:
            email (str): Email address to search for (case-insensitive)
            
        Returns:
            tuple: (subscriber_data, subscriber_id) or (None, None) if not found
        """
        try:
            response = self.get_subscribers()
            
            # Check all subscribers for matching email
            for sub in response.get('data', []):
                if sub.get('subscriber', {}).get('email', '').lower() == email.lower():
                    return sub.get('subscriber'), sub.get('id')
            
            # No match found
            return None, None
            
        except SignalWireAPIError:
            # Log and return None, None on API error
            return None, None
        
    def create_subscriber(self, subscriber_data):
        """Create a new subscriber"""
        return self._request('POST', "fabric/resources/subscribers", subscriber_data)
    
    def update_subscriber(self, subscriber_id, update_data):
        """
        Update an existing subscriber.
        
        Args:
            subscriber_id (str): The subscriber ID to update
            update_data (dict): Fields to update
            
        Returns:
            dict: Updated subscriber data
        """
        return self._request('PUT', f"fabric/resources/subscribers/{subscriber_id}", update_data)
    
    def get_subscriber_addresses(self, subscriber_id):
        """Get addresses for a subscriber"""
        return self._request('GET', f"fabric/resources/subscribers/{subscriber_id}/addresses")
        
    def create_subscriber_token(self, reference):
        """
        Create a subscriber authentication token.
        
        Args:
            reference (str): Reference string (typically email) for the token
            
        Returns:
            str: The subscriber token
        """
        payload = {"reference": reference}
        response = self._request('POST', "fabric/subscribers/tokens", data=payload)
        return response.get('token')
        
    def fetch_subscriber_address(self, subscriber_id):
        """
        Fetch the audio address for a subscriber, trimming everything after '?'.
        
        Args:
            subscriber_id (str): The subscriber ID
            
        Returns:
            str: The audio address or None if not found
            
        Raises:
            SignalWireAPIError: On API error
        """
        try:
            # Get addresses for the subscriber
            addresses_response = self.get_subscriber_addresses(subscriber_id)
            
            # Extract audio address
            data = addresses_response.get('data', [])
            if not data:
                logger.warning(f"No addresses found for subscriber {subscriber_id}")
                return None
                
            address_obj = data[0]
            channels = address_obj.get('channels') or address_obj.get('channel')
            
            if not channels or 'audio' not in channels:
                logger.warning(f"No audio channel found for subscriber {subscriber_id}")
                return None
                
            audio_path = channels['audio']
            address = audio_path.split('?')[0]
            
            logger.debug(f"Found subscriber address: {address}")
            return address
            
        except SignalWireAPIError as e:
            logger.warning(f"Error fetching subscriber address: {e.message}")
            return None
            
        except Exception as e:
            logger.exception(f"Unexpected error fetching subscriber address: {str(e)}")
            return None
    
    # Call control methods
    
    def send_ai_message(self, call_id, role, message_text):
        """
        Send a message to an AI agent during a call.
        
        Args:
            call_id (str): The ID of the active call
            role (str): Role of the message sender (e.g., "system", "user")
            message_text (str): The content of the message to send
            
        Returns:
            dict: Response from the API
            
        Raises:
            SignalWireAPIError: If the message cannot be sent
        """
        payload = {
            "id": call_id,
            "command": "calling.ai_message",
            "params": {
                "role": role,
                "message_text": message_text
            }
        }
        return self._request('POST', "calling/calls", payload)
    
    def unhold_ai_agent(self, call_id):
        """
        Unhold an AI agent during a call.
        
        Args:
            call_id (str): The ID of the active call
            
        Returns:
            dict: Response from the API
            
        Raises:
            SignalWireAPIError: If the unhold operation fails
        """
        payload = {
            "id": call_id,
            "command": "calling.ai_unhold"
        }
        return self._request('POST', "calling/calls", payload)
    
    def notify_ai_about_new_member(self, call_id, message_text):
        """
        Notify an AI agent about a new member and unhold the agent.
        This is a convenience method that combines send_ai_message and unhold_ai_agent.
        
        Args:
            call_id (str): The ID of the active call
            message_text (str): The message text to send to the AI agent
            
        Returns:
            dict: The response from the unhold request
            
        Raises:
            SignalWireAPIError: If either the message sending or unhold operation fails
        """
        # First, send the message
        self.send_ai_message(call_id, "system", message_text)
        
        # Then, unhold the agent
        return self.unhold_ai_agent(call_id)
    
    # Guest token methods
    
    def create_guest_token(self, allowed_address):
        """
        Create a guest token for the call widget.
        
        Args:
            allowed_address (str): The address ID that this token is allowed to connect to
            
        Returns:
            dict: Response containing the token
            
        Raises:
            SignalWireAPIError: If token creation fails
        """
        payload = {
            "allowed_address": allowed_address,
            "expires_seconds": 3600  # Token valid for 1 hour
        }
        return self._request('POST', "fabric/guests/tokens", payload)
    
    # Helper methods
    
    def extract_audio_destination(self, addresses_response):
        """
        Extract the audio destination from an addresses response.
        
        Args:
            addresses_response (dict): Response from get_handler_addresses
            
        Returns:
            str: The audio destination URL or None if not found
        """
        data = addresses_response.get('data', [])
        if not data:
            return None
            
        channels = data[0].get('channels') or data[0].get('channel')
        if not channels or 'audio' not in channels:
            return None
            
        audio_path = channels['audio']
        return audio_path.split('?')[0] 