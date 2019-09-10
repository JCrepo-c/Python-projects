import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 6667))
s.listen(1)
connection, address = s.accept()
message = input()
message = message.encode()
connection.send(message)
incoming = connection.recv(64)
incoming = incoming.decode("utf-8")
print(incoming)
s.close()