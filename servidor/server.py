import sys
import socket
import threading

connections = []
MAX_SIMULTANEOUS_CONNECTIONS = 25

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def ejecutar_consola(server):
    while True:
        imprimir_menu_principal()
        opcion = int(input("Opción: (1-5)"))
        if opcion == 1:
            print("Actualmente hay {} conecciones".format(len(connections)))
        elif opcion == 4:
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


def crear_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    return sock


def ejecutar_servidor(sock):

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            # Receive the data in small chunks and retransmit it
            data = connection.recv(1024)
            mensaje = str(data)
            print(mensaje)

            if mensaje == b"HELLO":
                if len(connections > 25):
                    connection.sendall(b"RECHAZADO")

                else:
                    connections.append(connection)
                    connection.sendall(b"APROBADO")
            else:
                connection.sendall(b"RECHAZADO")

        finally:
            # Clean up the connection
            connection.close()


def main():

    sock = crear_servidor()

    hilo_consola = threading.Thread(target=ejecutar_consola, args=(sock, ))
    hilo_consola.start()

    ejecutar_servidor(sock)


if __name__ == "__main__":
    main()