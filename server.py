import sys
import socket
import threading
from os import listdir
from os.path import isfile, join

connections = []
threads = []
MAX_SIMULTANEOUS_CONNECTIONS = 25
PATH_ARCHIVOS = "archivos"

CHUNK_SIZE = 5 * 1024
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def main():
    sock = crear_servidor()

    hilo_consola = threading.Thread(target=ejecutar_consola, args=(sock, ))
    hilo_consola.start()

    ejecutar_servidor(sock)


def crear_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    return sock


def ejecutar_consola(server):
    while True:
        imprimir_menu_principal()
        opcion = int(input("Opción: (1-5)"))
        if opcion == 1:
            print("Actualmente hay {} conexiones".format(len(connections)))
        elif opcion == 2:
            print("De los siguientes archivos, seleccione el que quiere enviar a los clientes.")
            listaArchivos = listdir(PATH_ARCHIVOS)
            print(listaArchivos)
            indiceArchivo = int(input("Opción: "))

            if indiceArchivo < 0 or indiceArchivo > len(listaArchivos):
                return print("Opción invalida")
            
            rutaArchivo = join(PATH_ARCHIVOS, listaArchivos[indiceArchivo-1])
           
           
            print("Indique las IP's a las cuales quieren enviar los archivos (la posición empezando en uno separada por comas):")
            print(list(map(lambda x: x[1][0], connections)))
            print("Si quiere enviarlo a todos, tecleé 'all'")
            destinatarios = input("Opción: ")


            # Ejecuta los hilos de las conexiones para empezar a enviar los archivos
            for connection in connections:
                threadConnection = threading.Thread(target=enviar_archivo, args=(connection[0], rutaArchivo))
                threads.append(threadConnection)
                threadConnection.start()
            
            # Quita las conexiones ya cerradas
            connections.clear()  # Added in Python 3.3
            del connections[:]

        elif opcion == 3:
            server.close()
            break
        else:
            print("Vuelva a intentarlo.")


def imprimir_menu_principal():
    print("""Bienvenido a la consola de ejecución del servidor: 
    Selecciones alguna de la siguientes opciones:
        1. Ver la cantidad de clientes conectados
        2. Enviar archivo a clientes
        3. Salir
    """)

def ejecutar_servidor(sock):
    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            # Receive the data in small chunks
            data = connection.recv(1024)
            mensaje = data.decode("utf-8")

            if mensaje == "HELLO":
                if len(connections) > 25:
                    connection.sendall(b"RECHAZADO")

                else:
                    connections.append((connection, client_address))
                    connection.sendall(b"APROBADO")
            else:
                connection.sendall(b"RECHAZADO")
            
        except:
            connection.close()


def enviar_archivo(socket, rutaArchivo):

    socket.sendall(b"ARCHIVO")

    data = socket.recv(1024)
    mensaje = data.decode("utf-8")

    if mensaje == "PREPARADO": 
        with open(rutaArchivo, 'rb') as f:
            data = f.read(CHUNK_SIZE)
            while data:
                socket.sendall(data)
                data = f.read(CHUNK_SIZE)
        socket.close()



if __name__ == "__main__":
    main()