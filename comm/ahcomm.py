import socket
import struct

import crypto.ahcrypto as ahc

class Socket:
    def __init__(self, socket : socket.socket, address, RSA_PUB, RSA_PRIV, DSS_PUB, DSS_PRIV):
        self.socket = socket
        self.address = address
        self.RSA_PUB = RSA_PUB # RECEIVER PUB (YOUR) I encrypt with your public
        self.RSA_PRIV = RSA_PRIV # SENDER PRIV (MINE) I decrypt with my private
        self.DSS_PUB = DSS_PUB # RECEIVER PUB (YOUR) I sign with your public
        self.DSS_PRIV = DSS_PRIV # SENDER PRIV (MINE) I verify with my public

    def send(self, message):
        payload = ahc.encrypt_and_sign(message, self.RSA_PUB, self.DSS_PRIV)
        cipherheader = struct.pack("!I", len(payload[0]))
        self.socket.sendall(cipherheader)
        self.socket.sendall(payload[0])

        sigheader = struct.pack("!I", len(payload[1]))
        self.socket.sendall(sigheader)

        self.socket.sendall(payload[1])

    def read(self):
        header_size = struct.calcsize("!I")
        header = self.socket.recv(header_size)
        if not header:
            return None

        # Unpack the header to get the size of the first payload
        payload_size = struct.unpack("!I", header)[0]

        # Receive the first payload
        cipher = self.socket.recv(payload_size)

        # Receive the header containing the size of the second payload
        header = self.socket.recv(header_size)
        if not header:
            return None

        # Unpack the header to get the size of the second payload
        payload_size = struct.unpack("!I", header)[0]

        # Receive the second payload
        signature = self.socket.recv(payload_size)

        message = ahc.verify_and_decrypt(cipher, self.RSA_PRIV, self.DSS_PUB, signature)
        return message