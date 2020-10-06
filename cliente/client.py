import socket
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (HOST, PORT)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    # Send data
    message = b'HELLO'
    print('sending {!r}'.format(message))
    sock.sendall(message)

    # Look for the response
    data = sock.recv(1024)
    print(data)
    

finally:
    print('closing socket')
    sock.close()