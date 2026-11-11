# Login and Registration Microservice

**CS 361 — Group Integration**

This standalone Python microservice registers users and verifies login credentials over **ZeroMQ (REQ/REP)**. It stores users in a local SQLite database and hashes passwords with Werkzeug.

## Files to share

```text
LoginMicroservice/
├── auth_zmq_service.py    # ZeroMQ REP server (required)
├── database.py            # SQLite helpers (required)
├── auth_zmq_client.py     # Example REQ client
└── README.md              # This document
```

## Requirements

- Python 3.10 or newer
- `pyzmq`
- `Werkzeug`
- The service and client must be running on the **same computer** with the current localhost configuration.

`requirements.txt` should contain:

```text
pyzmq
Werkzeug
```

## Setup

From the directory containing `auth_zmq_service.py`:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python auth_zmq_service.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 auth_zmq_service.py
```

The server listens at **`tcp://127.0.0.1:5555`**. 

## Communication contract

- **Transport:** ZeroMQ TCP
- **Pattern:** REQ (client) → REP (service)
- **Address:** `tcp://127.0.0.1:5555`
- **Message format:** JSON-compatible Python dictionaries sent with `send_json()`
- **Reply format:** JSON-compatible dictionary returned with `recv_json()`
- **Order:** Every client request receives one reply before the next request on that REQ socket.
- **Status codes:** The `status` field resembles HTTP status codes for familiarity, but these are **values in JSON**, not actual HTTP statuses.

### Register an account

**Request**

```json
{"action":"register","username":"sampleuser","password":"ExamplePassword123!"}
```

**Success response (example)**

```json
{"success":true,"status":201,"message":"Account created successfully","user_id":1}
```

Possible failure statuses: `400` (missing/invalid data or password shorter than 12 characters), `409` (username already registered).

### Log in

**Request**

```json
{"action":"login","username":"sampleuser","password":"ExamplePassword123!"}
```

**Success response (current implementation)**

```json
{"success":true,"status":200,"message":"Login successful","username":"sampleuser"}
```

Possible failure statuses: `400` (invalid credentials format), `401` (wrong password or nonexistent username). Both invalid-account cases return the same message:

```json
{"success":false,"status":401,"error":"Invalid username or password"}
```

Unknown actions or non-object JSON requests return status `400` with an error message.

**Note:** The current login response does not contain a `user_id`. If the team needs IDs to link records to accounts, agree on that contract and add `"user_id": user["id"]` to the successful login dictionary before integration.

## Sample client integration

The provided `auth_zmq_client.py` demonstrates the communication pattern. A minimal example is:

```python
import zmq

# Create one REQ socket for one request/reply exchange.
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 seconds
socket.setsockopt(zmq.SNDTIMEO, 5000)  # 5 seconds
socket.setsockopt(zmq.LINGER, 0)
socket.connect("tcp://127.0.0.1:5555")

try:
    socket.send_json({
        "action": "login",
        "username": "sampleuser",
        "password": "ExamplePassword123!"
    })
    result = socket.recv_json()
    print(result)
except zmq.Again:
    print("Authentication service timed out")
finally:
    socket.close()
    context.term()
```


