import socket
import os, os.path
import time
import sys

server_address = 'ESEmbarcados'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise
# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print 'starting up on %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
e1 = []
e2 = []
i = 0
count = 0
while count < 1200:
    # Wait for a connection
    print  'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            #print float(data)
            #print repr(data)
            try:
                data = float(data.replace("\x00",""))
                print data
                if data:
                    if i == 0:
                        e1.append(data)
                        i = i + 1
                    else:
                        e2.append(data)
                        i = 0
                    print 'sending data back to the client'
                    connection.sendall("ack")
                    count = count + 1
                else:
                    print 'no more data from', client_address
                    break
            except:
                pass
    finally:
        # Clean up the connection
        connection.close()

d = {'e1': e1, 'e2': e2}
dataFrame = DataFrame(data=d, index=index)