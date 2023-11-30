# CS355-Project-AlexH
 
# Protocol Specification

## Communication
	The communication of the program is split into two different segments, first is the server. Each can be assumed that any files inside are localized to a separate machine representing the program i.e., all clients will have the contents of client, but can not see any of contents of server and vice versa. All is accomplished using [python socket library](https://docs.python.org/3/library/socket.html).  

	The client serves as the representation of Alice and Bob, where it can interact with different fields of the server.

	The server is the place where Alice and Bob can freely communicate with one another. The server houses all information that sent between Alice, Bob, and all other parties. The server provides the following functions based on these codes:

	* ``0``, 
