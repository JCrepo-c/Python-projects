import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 6667))
incoming = s.recv(64)
incoming = incoming.decode("utf-8")
print(incoming)
message = input()
message = message.encode()
s.send(message)
s.close()