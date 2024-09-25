Run the server: `fastapi dev main.py`
Open the chat page for a user 'darwin': `http://localhost:8000/user/darwin`
Open the chat page for a user 'angie': `http://localhost:8000/user/angie`

TODO If a user is offline, save message on server with a TTL of 30 days
TODO When a client connects, retrieve messages sent while offline
TODO Messages should be assigned an ID by the server
TODO A recipient sends an ack to the sender
TODO A client sends a heartbeat to the server every 30 seconds
TODO Authentication
TODO Client can send a close command
