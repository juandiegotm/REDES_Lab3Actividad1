import sys
import socket
import threading
from os import listdir
from os.path import isfile, join
import datetime
from utilities import hash_file

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 25565        # Port to listen on (non-privileged ports are > 1023)
CHUNK_SIZE = 100 * 1024

PATH_RECIBIDOS = join("recibidos")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (HOST, PORT)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

# Send data
message = b'HELLO'
print('sending {!r}'.format(message))
sock.sendall(message)

# Look for the response
data = sock.recv(1024)
message = data.decode("utf-8")

if message == "APROBADO":
    data = sock.recv(1024)
    message = data.decode("utf-8")
    if message.startswith("ARCHIVO"):
        # Notifica al servidor que está listo para la rececpción del archivo
        sock.sendall(b"PREPARADO")

        filename = str(datetime.datetime.now().timestamp()) + "." + str(message.split(":")[-1])
        with open(join(PATH_RECIBIDOS, filename), "wb") as f:        
            chunk = sock.recv(CHUNK_SIZE)
            while chunk:
                f.write(chunk)
                chunk = sock.recv(CHUNK_SIZE)
        
        sock.sendall(b"RECIBIDO")
        
        # Recibe el HASH
        data = sock.recv(1024)
        message = data.decode("utf-8")
        print(message)

        if message.startswith("HASH"):
            serverhash = message.split(":")[-1]
            if hash_file(join(PATH_RECIBIDOS, filename)) == serverhash:
                print("El hash coicide")
            else:
                print("El hash no coincide")

sock.close()