# LiveWire Store Architecture

## Overview

This document describes the store architecture used in the LiveWire demo app. The current implementation uses in-memory stores that provide a simple and consistent interface for data management.

## Store Types

The application uses the following stores:

1. **Customer Store**: Manages customer/member data
   - Key: member_id
   - Value: Customer object (first_name, last_name, email, etc.)

2. **User Store**: Manages user authentication data
   - Key: email
   - Value: User object (password_hash, subscriber_id, etc.)

3. **Call Info Store**: Manages call context across requests
   - Key: call_id
   - Value: Call info object (context, info, etc.)

4. **Active Subscribers Store**: Tracks online subscribers and their addresses
   - Key: project_id → subscriber_id
   - Value: Subscriber info (address, online status, last_seen)

## Current Implementation

The current store implementation provides:

1. **Common Interface**: All stores are accessed through the `get_store()` function
2. **Store Registry**: A central registry ensures consistent access to stores
3. **Error Handling**: A `store_operation` decorator provides consistent error handling
4. **Basic CRUD Operations**: Each store module provides functions for basic CRUD operations

## Usage Example

```python
# Getting a store
from stores import get_store, CUSTOMER_STORE
store = get_store(CUSTOMER_STORE)

# Using helper functions
from stores.customer_store import get_customer, add_customer
customer = get_customer("AB12345")
add_customer({
    "member_id": "M123456",
    "first_name": "Jane",
    "last_name": "Smith"
})
```

## Path to Persistence

Currently, all stores are in-memory and will be lost on application restart. When persistence is needed, consider these approaches:

1. **Database Backend**: Implement a simple database (SQLite, PostgreSQL) with models that match the store structure
2. **File-based Storage**: Use JSON or pickle files to save/load store data between restarts
3. **Caching Layer**: Add Redis or another caching solution for temporary persistence

The implementation should maintain the same interface so that code using the stores doesn't need to change.

## Best Practices

1. **Keep It Simple**: The current architecture is deliberately simple - maintain this simplicity
2. **Use the Decorator**: Always use the `@store_operation` decorator for error handling
3. **Log Appropriately**: Include useful logging statements for debugging
4. **Document New Stores**: Update this README when adding new store types 