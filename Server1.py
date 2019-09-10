import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 6767))
s.listen(1)
connection, address = s.accept()
with open("arch-lockscreen.png", "rb") as f:
	connection.send(f.read())

connection.close()
s.close()