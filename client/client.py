import socket
import hashlib
import os

import crypto.ahcrypto as ahc

from Crypto.PublicKey import ECC

from comm.ahcomm import Socket

PORT = 12346

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', PORT)
server_socket.connect(server_address)
print('Connected to {}:{}'.format(*server_address))

# WELCOME PHASE: Receive the public keys from the server
server_public_keys = server_socket.recv(1024)
server_public_keys = server_public_keys.decode()

SERVER_RSA_PUB_KEY = server_public_keys.split(":")[0]
SERVER_DSS_PUB_KEY = ECC.import_key(server_public_keys.split(":")[1])

# Generate Client Keys
CLIENT_RSA_KEY = ahc.generateRSAKey()
CLIENT_RSA_PUB_KEY = CLIENT_RSA_KEY.public_key().export_key('PEM')
CLIENT_RSA_PRIV_KEY = CLIENT_RSA_KEY.export_key('PEM')

CLIENT_DSS_PRIV_KEY = ahc.generateDSSKey()
CLIENT_DSS_PUB_KEY = CLIENT_DSS_PRIV_KEY.public_key()

# WELCOME PHASE: Respond to server with client keys

# server pub rsa, client priv, server pub dss, client priv dss
socket = Socket(server_socket, server_address, SERVER_RSA_PUB_KEY, 
    CLIENT_RSA_PRIV_KEY, SERVER_DSS_PUB_KEY, CLIENT_DSS_PRIV_KEY)

pub_keys = CLIENT_RSA_PUB_KEY.decode('utf-8') + ":"
pub_keys += str(CLIENT_DSS_PUB_KEY.export_key(format='PEM'))
server_socket.send(pub_keys.encode())


'''
UPLOAD PHASE: client will securely inform of the server of the location of the 
files that client wishes to check with other clients connected to the server

Will hash files and upload those files to the server
'''
def hash_file(file_path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

client_hash_values = {}
def hash_folder(folder_path):
    global client_hash_values
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            hash_value = hash_file(file_path)
            client_hash_values[file_name] = hash_value


folder_location = input("Please enter folder location of files or exit: ");
if folder_location == "exit":
    server_socket.close()
    exit()


try:
    hash_folder(folder_location)
except Exception:
    print(f"Failed at upload phase: {Exception}")
    server_socket.close()
    exit()

for hash_value in client_hash_values.values():
    socket.send("0:" + hash_value)

    response = socket.read()
    if (response and response.decode() != "Success."):
        print(f"Failed at upload phase. {response}")
        server_socket.close()
        exit()

'''
REQUEST PHASE: client will then have the ability to request the server for other
connected client's hashes
'''
while True:
    _in = input("Press anything to check connected clients against files or exit: ")
    if (_in == "exit"):
        break

    socket.send("1:")

    response = socket.read()
    if not response:
        print("No response from server")
        continue

    hashes = response.decode().split("|")
    for file_name, file_hash in client_hash_values.items():
        if file_hash in hashes:
            print(f"A connected client shares the code segment: {file_name}")


# Close the connection with the server
server_socket.close()