import zmq

from database import (
    initialize_database,
    create_user,
    get_user_by_username
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("tcp://127.0.0.1:5555")

print("Authentication microservice listening on port 5555.")

def handle_login(data):
    username = data.get("username")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not isinstance(password, str)
        or not username.strip()
        or not password
    ):

        return {
            "success": False,
            "status": 400,
            "error": "Invalid credentials format"
        }

    user = get_user_by_username(username.strip())

    if user is None:
        return {
            "success": False,
            "status": 401,
            "error": "Invalid username or password"
        }

    if not check_password_hash(user["password_hash"], password):
        return {
            "success": False,
            "status": 401,
            "error": "Invalid username or password"
        }

    return {
        "success": True,
        "status": 200,
        "message": "Login successful",
        "username": user["username"]
    }


def handle_register(data):
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return {
            "success": False,
            "status": 400,
            "error": "Invalid credentials format"
        }

    username = username.strip()

    if not username or len(password) < 12:
        return {
            "success": False,
            "status": 400,
            "error": "Username is required and password must be at least 12 characters"
        }

    existing_user = get_user_by_username(username)

    if existing_user is not None:
        return {
            "success": False,
            "status": 409,
            "error": "Username already registered"
        }

    password_hash = generate_password_hash(password)

    try:
        user_id = create_user(username, password_hash)

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "status": 409,
            "error": "Username already registered"
        }

    return {
        "success": True,
        "status": 201,
        "message": "Account created successfully",
        "user_id": user_id
    }


initialize_database()

while True:
    message = socket.recv_json()

    if not isinstance(message, dict):
        response = {
            "success": False,
            "status": 400,
            "error": "Invalid request format"
        }

    elif message.get("action") == "login":
        print("Received login request")
        response = handle_login(message)

    elif message.get("action") == "register":
        print("Received registration request")
        response = handle_register(message)

    else:
        response = {
            "success": False,
            "status": 400,
            "error": "Unknown action"
        }

    socket.send_json(response)

