import zmq

context = zmq.Context()

socket = context.socket(zmq.REQ)

socket.connect("tcp://127.0.0.1:5555")
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.setsockopt(zmq.SNDTIMEO, 5000)
socket.setsockopt(zmq.LINGER, 0)

request_data = {
    "action": "register",
    "username": "ZeroMQTestUser",
    "password": "TestPassword123!"
}

try:
    socket.send_json(request_data)

    response = socket.recv_json()

    print("Server response:", response)

except xmq.Again:
    print("Authentication microservice timed out.")

except zmq.ZMQError as error:
    print("ZeroMQ communication error:", error)

finally:
    socket.close()
    context.term()