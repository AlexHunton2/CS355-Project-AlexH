# CS 355 Project

[Github Repo](https://github.com/AlexHunton2/CS355-Project-AlexH)

Note: not sure how to not include "de-anomymizing" information when the link to the github has to be included.
 
## Protocol Specification

### Communication
The communication of the program is split into two different segments, first is the server. Each can be assumed that any files inside are localized to a separate machine representing the program i.e., all clients will have the contents of client, but can not see any of contents of server and vice versa. 

Clients are assumed only be to see the following directories:
* ``client, comm, crypto`` and corresponding person folder (``alice_files`` or ``bob_files``). 

Server is assumed only to be see the following directories:
* ``server, comm, crypto``

The client serves as the representation of Alice and Bob, where it can interact with different fields of the server.

The server is the place where Alice and Bob can freely communicate with one another. The server houses all information that sent between Alice, Bob, and all other parties. The server does is not assumed to be private or provide any features where clients can authenticate themselves to one another. The server merely functions to authenticate and securely communicate with clients. The server provides the following functions based on these codes:

*  0: Upload the given hash to the clients connected session.
*  1: Retrieve all hashes that do not belong to the client who requested them.

It is evident that the server does little, and merely serves to broadcast given hashes without interface from an adversary. 

Communication between client and server after the welcome phase relies on encryption and authentication. Encryption is accomplished through RSA and authentication is accomplished through DSS/DSA. More detail on this spoken about in the protocol specification and security analysis.

### Protocol / Code Specification

Protocol is split into three major parts, by the end any clients connected to the server are able to confirm that any other clients connected may or may not have code segments that match their own.

#### Welcome Phase

To start, a client must prepare their given segments of code. For testing purposes, I've created a python script which will create a single identical random 500 MB file, and another random file located in the Bob and Alice folders. This will serve to show the utility of the program.

```console
$ python genfiles.py
```

Next, the server must be started. In the root directory, run the following command. The server start by generating its own set of RSA and DSA keys.

```console
$ python -m server.server.py
```

Two clients can be connected using this command in the root directory.

```console
$ python -m client.client
```

Upon connecting to the server, the server will forward it's public key to the client. The client will then generate its own set of RSA and DSA keys. The client will forward this set of keys to the server. The server and client now has it's own key set for encryption and authentication along with the other's public set. 


#### Upload Phase

From this point on, all messages sent between the server and client will be encrypted and then signed. The receiver can then verify and decrypt. This is accomplished using ``Socket`` class defined in ``comm/ahcomm.py``. The server will have ``Socket`` for each connected client and be able to use the methods written to message the client. Each client will have ``Socket`` representing the server to be used to communicate. Messages sent are packaged as followed:
```
header -> size of cipher in bytes
cipher -> the encrypted message
header -> size of signature in bytes
signature -> cipher signed
```

The receiver the message will then be able to consume this payload and verify and decrypt using the public key made available in the Welcome phase. Crypto functions are defined in ``crypto/ahcrypto.py``, this takes advantage of the libraries listed below.

During the upload phase, clients will be asked to specify a folder location of where the code segments are located. Clients provide the program with the folder location, the program will then hash the entire file using SHA-256 and forward this hash to the server. The server will then accept this hash and store it with the client's current session. Clients are expected to complete this phase before moving on. A client who does not provide any files is assumed to have none.

#### Request Phase

In this phase, clients are free to request the server as many times as they desire for all available hashes that are not them. The server will then provide all the hashes that it has been made available by other connected clients. The client is then able to examine each of these hashes and compare it against it's own. If there is a match, then a client can be sure that there exist a client connected to the server who shares a code segment with themselves. The code segment will be listed to them in the program.

#### Notes on the protocol

I would like to make a few notes on the protocol itself that I find important.

* If Bob, Alice, and Eve all connect to the server and upload their code segments, and there exist a match, then none of them know who has the match. I.e, Bob knows that Alice OR Eve has a code segment that he has but it is impossible for him to figure that out without breaking the encryption of the server. The project information does not specify if this is a necessary requirement that any client can identify who else shares the code segment.

* The server is meant to be as bare bones as possible, directly connecting Bob and Alice seems like a bad idea and peer-to-peer communication using sockets is out of my wheel house. As such, the server is *meant* to act simply as a way for clients to broadcast to all other clients what they got, and for other clients to know that an adversary didn't interfere. 


## Security Analysis

### Communication Goals
* Any party to broadcast their hash without their communication between disturbed or altered. 
* Any party to request a hash from a trusted source without the hash being compromised or altered.
* Any party cannot determine the origin of any hash that exists on the server.

All of these goals were accomplished using RSA and DSS technologies. Through encryption no one reading the messages between the server and client could determine the hash contained inside. Through DSS, the cipher could not be altered by an adversary as that would break the signature. Both ensure that the communication of the clients and server remain undisturbed.


### Segment Comparison
* Any party can freely compare their code segment without directly comparing their code segment. 
* Any party cannot reverse the comparison hash.

Through hashing, two parties can determine whether or not their 500 MB code segment is the same. Due to the collision-prevention properties of SHA-256, each code segment has unique hash. Furthermore, each hash cannot be reversed, so publicly distributing the hash does not reveal the code segment. 

### Libraries Used:
* Python Standard Library (socket, threading, hashlib, os)
* [Python socket library](https://docs.python.org/3/library/socket.html).  
* [PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/index.html).
