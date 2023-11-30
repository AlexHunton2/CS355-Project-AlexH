import socket
import struct
import threading

from Crypto import Signature

import crypto.ahcrypto as ahc

from Crypto.PublicKey import RSA
from Crypto.PublicKey import ECC

from comm.ahcomm import Socket

PORT = 12346

# Start by generating keys
RSA_KEY = ahc.generateRSAKey()
RSA_PUB_KEY = RSA_KEY.public_key().export_key('PEM')
RSA_PRIV_KEY = RSA_KEY.export_key('PEM')

DSS_PRIV_KEY = ahc.generateDSSKey()
DSS_PUB_KEY = DSS_PRIV_KEY.public_key()


# Create registry for client connections
lock = threading.Lock()

clients = {}
def register_client(client : Socket):
    global clients
    with lock:
        # client pub rsa, server priv, client pub dss, server priv dss
        clients[client] = []
        return clients[client]

def get_client(client : Socket):
    global clients
    with lock:
        return clients[client]

def clear_client(client: Socket):
    global clients
    with lock:
        del clients[client]


def handle_client(client : Socket):
    global clients
    # Continuously check for incoming data from the client
    while True:
        try:
            data = client.read()
            if not data:
                # No more data, the client has closed the connection
                break


            inst = data.decode().split(":")[0]
            message = data.decode().split(":")[1]

            if (inst == "0"):
                # UPLOAD HASH TO CLIENT
                get_client(client).append(message)
                client.send("Success.")
            elif (inst == "1"):
                # SEND ALL HASHES THAT DONT BELONG TO CLIENT
                hashes_except_owned = [value for key, value in clients.items() if key != client]
                if (len(hashes_except_owned) > 0):
                    client.send("|".join(hashes_except_owned[0]))
                else:
                    client.send("")
            else:
                client.send("Error: Malformed message.")
        except Exception:
            break      

    # Close the connection with the client

    clear_client(client)
    client_socket.close()
    print(f'Connection with {client_address} closed')

def intepret_request(data):
    response = ""

    return response

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = ('localhost', PORT)
server_socket.bind(server_address)

# Listen for incoming connections (maximum 5 connections in the queue)
server_socket.listen(5)
print('Server listening on {}:{}'.format(*server_address))

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()
    print('Connected to', client_address)

    # WELCOME PHASE
    try:
        # WELCOME: Send public keys over to clients who connect
        pub_keys = RSA_PUB_KEY.decode('utf-8') + ":"
        pub_keys += str(DSS_PUB_KEY.export_key(format='PEM'))
        client_socket.send(pub_keys.encode())

        # WELCOME: Get public keys of client and register
        client_keys = client_socket.recv(1024).decode()
        client_rsa = client_keys.split(":")[0]
        client_dss = ECC.import_key(client_keys.split(":")[1])
    except Exception:
        print("Connection failed at welcome phase: {Exception}")
        client_socket.close()

    client = Socket(client_socket, client_address, client_rsa, RSA_PRIV_KEY, client_dss, DSS_PRIV_KEY)
    register_client(client)
    print(client)

    # Create a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=[client])
    client_thread.start()