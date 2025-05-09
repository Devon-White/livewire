# customer_store.py
# Global in-memory store for customer/member data
# Structure: {member_id: {first_name, last_name, email, phone, premium_member, ...}}

customer_store = {
    "AB12345": {
        "member_id": "AB12345",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "premium_member": True
    }
}

def get_customer_store():
    return customer_store 