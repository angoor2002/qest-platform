from langchain.tools import tool
from pymongo import MongoClient
from datetime import datetime
from bson.binary import Binary, UuidRepresentation
from uuid import uuid4
from datetime import datetime, date, timezone
import random
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri=os.getenv('MONGODB_URI')
# Setup MongoDB
client = MongoClient(mongo_uri)
db = client['qest_db']

def create_client(name: str, email: str,phone: str) -> str:
    """
    Inserts a new client into the 'clients' collection.
    """
    client_id = str(uuid4())
    # Parse ISO date string into aware datetime at midnight UTC

    # Current UTC timestamp
    now = datetime.now(timezone.utc)

    client_data = {
        "_id": client_id,
        "name": name,
        "email": email,
        "phone": phone,
        "created_at": now,
    }

    db.clients.insert_one(client_data)
    return f"Client {name} with ID {client_id} created."

def create_order(client_id: str = None,service_id: str = None,amount: float = None,status: str = None,service_type: str=None) -> str:
    if amount is None or status is None:
        return "Error: 'amount' and 'status' are required."

    # Random service type
    service_type = random.choice(['course', 'class'])

    # Timestamp
    created_dt = datetime.now(timezone.utc)
    order_data = {
        "_id": str(uuid4()),
        "client_id": client_id,
        "service_id": service_id,
        "service_type": service_type,
        "amount": amount,
        "status": status,
        "created_at": created_dt
    }
    db.orders.insert_one(order_data)
    return f"Order '{order_data['_id']}' created: client={client_id}, service={service_id}, type={service_type}, amount={amount}, status={status}"


# print(create_client("Zakir","zakircodes@gmail.com","9674282229"))
# res=db.clients.find_one({ "name": "Zakir" })
# print(res)
# print(create_order(client_id="d1b2c3f4-5678-90ab-cdef-1234567890ab", service_id="a1b2c3d4-5678-90ab-cdef-1234567890ab", amount=100.0, status="pending"))
# res=db.orders.find_one({ "client_id": "d1b2c3f4-5678-90ab-cdef-1234567890ab" })
# print(res)
