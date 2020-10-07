import sys
import socket
import threading
from os import listdir, stat
from os.path import isfile, join
from datetime import datetime
from utilities import hash_file

now = datetime.now()
HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 25565        # Port to listen on (non-privileged ports are > 1023)
CHUNK_SIZE = 100 * 1024

PATH_RECIBIDOS = join("recibidos")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2000)

# Connect the socket to the port where the server is listening
server_address = (HOST, PORT)
sock.connect(server_address)

f = open('logg.txt','wt')
f.write(str(now) + 'connecting to {} port {}'.format(*server_address))
print('connecting to {} port {}'.format(*server_address))

# Send data
message = b'HELLO'
sock.sendall(message)

f = open('logg.txt','wt')
f.write(str(now)  +'sending {!r}'.format(message) )
print('sending {!r}'.format(message))

# Look for the response
data = sock.recv(1024)
message = data.decode("utf-8")

if message == "APROBADO":
    data = sock.recv(1024)
    message = data.decode("utf-8")
    if message.startswith("ARCHIVO"):
        data = message.split(":")
        extension = data[1] 
        tamanio = data[2]

        filename = str(datetime.now().timestamp()) + "." + extension

         # Notifica al servidor que está listo para la rececpción del archivo
        sock.sendall(b"PREPARADO")

        with open(join(PATH_RECIBIDOS, filename), "wb") as f:  
              
            restante = int(tamanio)
            while restante:
                chunk = sock.recv(min(restante, CHUNK_SIZE))
                restante -= len(chunk) 
                f.write(chunk)
            end_ts = datetime.now().timestamp()
 
        sock.sendall("RECIBIDO:{}".format(end_ts).encode('utf-8'))
        
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