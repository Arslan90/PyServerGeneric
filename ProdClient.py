import socket               # Import socket module
import time

s = socket.socket()         # Create a socket object
HOST = '127.0.0.1'  # Local host
PORT = 19999  # Aun port arbitraire

s.connect((HOST, PORT))
s.send("ShortestPath_297162704_82660198")
data = s.recv(1024)
while data:
    print data
    time.sleep(5)
    data = s.recv(1024)
s.close                     # Close the socket when done