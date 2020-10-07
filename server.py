import sys
import socket
import threading
from os import listdir, stat
from os.path import isfile, join
from utilities import hash_file
from datetime import datetime

connections = []
threads = []
MAX_SIMULTANEOUS_CONNECTIONS = 25
PATH_ARCHIVOS = "archivos"

CHUNK_SIZE = 100 * 1024 # 5kB
HOST = ''  # Standard loopback interface address (localhost)
PORT = 25565        # Port to listen on (non-privileged ports are > 1023)
now = datetime.now()


def main():
    sock = crear_servidor()

    hilo_consola = threading.Thread(target=ejecutar_consola, args=(sock, ))
    hilo_consola.start()

    ejecutar_servidor(sock)


def crear_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(25)

    return sock


def ejecutar_consola(server):
    while True:
        imprimir_menu_principal()
        opcion = int(input("Opción [1-3]: "))
        if opcion == 1:
            print("Actualmente hay {} conexiones".format(len(connections)))
            f = open('logg.txt','wt')
            f.write(str(now) + "Actualmente hay {} conexiones".format(len(connections)))
            print("Actualmente hay {} conexiones".format(len(connections)))
            f.close()
        elif opcion == 2:
            if not len(connections):
                print("No hay conexiones en este momento.")
                continue

            print("De los siguientes archivos, seleccione el que quiere enviar a los clientes.")
            listaArchivos = listdir(PATH_ARCHIVOS)
            print(listaArchivos)
            indiceArchivo = int(input("Opción: "))

            if indiceArchivo < 0 or indiceArchivo > len(listaArchivos):
                return print("Opción invalida")
            
            rutaArchivo = join(PATH_ARCHIVOS, listaArchivos[indiceArchivo-1])

            hashed = hash_file(rutaArchivo) 
           
            print(len(connections), list(map(lambda x: x[1][0], connections)))
            opcion_destinatarios = input("A cuantos clientes desea trasmitir el paquete: [Para enviarselo a todos, escriba 'all'] ")
            limite = len(connections) if opcion_destinatarios == "all" else min(len(connections), max(int(opcion_destinatarios, 0)))
            
            # Ejecuta los hilos de las conexiones para empezar a enviar los archivos, recibe el mensaje si el servidor recibio completo el archivo y cierra la conexión
            for i in range(limite):
                connection = connections[i]
                threadConnection = threading.Thread(target=enviar_archivo, args=(connection[0], rutaArchivo, hashed))
                threads.append(threadConnection)
                threadConnection.start()


            for thread in threads:
                thread.join()

            # Quita las conexiones ya cerradas
            connections.clear() 
            del connections[:]


        elif opcion == 3:
            server.close()
            break
        else:
            print("Vuelva a intentarlo.")


def imprimir_menu_principal():
    print("""
*****************************************************
*****************************************************

Bienvenido a la consola de ejecución del servidor: 
Seleccion alguna de la siguientes opciones:

    1. Ver la cantidad de clientes conectados
    2. Enviar archivo a clientes
    3. Salir

******************************************************   
******************************************************

    """)

def ejecutar_servidor(sock):
    while True:
        # Wait for a connection
        #print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            # Receive the data in small chunks
            data = connection.recv(1024)
            mensaje = data.decode("utf-8")

            if mensaje == "HELLO":
                connections.append((connection, client_address))
                connection.sendall(b"APROBADO")

            else:
                connection.sendall(b"RECHAZADO")
            
        except:
            connection.close()


def enviar_archivo(socket, rutaArchivo:str, hash):
    filesize = stat(rutaArchivo).st_size
    mensajeArchivo = "ARCHIVO:{0}:{1}".format(rutaArchivo.split(".")[-1], filesize)
    socket.sendall(mensajeArchivo.encode("utf-8"))

    data = socket.recv(1024)
    mensaje = data.decode("utf-8")

    if mensaje == "PREPARADO": 
        with open(rutaArchivo, 'rb') as f:
            data = f.read(CHUNK_SIZE)
            start_ts = datetime.now().timestamp()
            while data:
                socket.sendall(data)
                data = f.read(CHUNK_SIZE)

        print("Archivo enviado")

        #Espera a recibir la confirmación de terminar
        data = socket.recv(1024)
        message = data.decode("utf-8")
        

        if message.startswith("RECIBIDO"):
            end_ts = float(message.split(":")[-1])

            final_time = (end_ts-start_ts)/1000
            print(start_ts, end_ts)
            print("Archivo enviado en {:0.9f} segundos".format(final_time))

            socket.sendall("HASH:{}".format(hash).encode("utf-8"))
            socket.close()
        
        else:
            print("El archivo no fue recibido")

if __name__ == "__main__":
    main()