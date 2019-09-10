#!/usr/bin/env python3

# Banking Application Server
# Final application project in my Python course
# Questions? Email shawnduong@pm.me

import hashlib
import os
import socket
import threading
import time

ip   = "127.0.0.1"																# Localhost.
port = 9999																		# Port the program listens on.
key  = "f52fbd32b2b3b86ff88ef6c490628285f482af15ddcb29541f94bcf526a3f6c7"		# Used to verify the client.

# For demonstration purposes, the plaintext key is "hunter2".

codes =	{																		# Protocol codes.
	"OK_AUTH"   : "10",
	"BAD_AUTH"  : "11",
	"OK_LOGIN"  : "20",
	"BAD_LOGIN" : "21",
	"OK_DEPO"   : "30",
	"BAD_DEPO"  : "31",
	"OK_DRAW"   : "40",
	"BAD_DRAW"  : "41",
	"OK_TSFR"   : "50",
	"BAD_TSFR"  : "51",
	"OK_STAT"   : "60",
	"BAD_STAT"  : "61",
	}

def log(text: str) -> None:														# Log function.
	'''
	Log some text to the terminal, including a timestamp.
	'''

	print("\r[%s] %s" % (time.strftime("%H:%M:%S"), text))						# Logging.

def authorize(connection: socket.socket) -> bool:								# Authorize function.
	'''
	Authorizes a client.
	'''

	sentKey = connection.recv(128).decode("utf-8").strip("\n")					# Receive a key from the client.
	hashKey = hashlib.sha256(sentKey.encode()).hexdigest()						# Hash the received key.

	return hashKey == key														# Return the comparison of the keys.

def authenticate(connection: socket.socket, address: tuple) -> str:				# Authenticate function.
	'''
	Authenticates a client.
	Returns the string of the username authenticated.
	'''

	while True:																	# Loop forever.
		try:																	# Try...
			sentData = connection.recv(128).decode("utf-8")						# Receive data.
			username, password = sentData.split(":")							# Parse the data.
		except:																	# Except...
			username, password = "FAIL", "FAIL"									# Fail mode.

		with open("userCredentials.data", "r") as f:							# Open a file of user credentials.
			data = f.read().split("\n")											# Read it and split by the line.

		if "%s:%s" % (															# If the supplied credentials are present...
			username,
			hashlib.sha256(password.encode()).hexdigest()
		) in data:
			log("Successful login to %s %s:%d" % (								# Logging.
				username, address[0], address[1]))
			connection.send(codes["OK_LOGIN"].encode())							# Send an OK_LOGIN code.
			return username														# Return the username.
		else:																	# If they're not present...
			try:																# Try to
				connection.send(codes["BAD_LOGIN"].encode())					# Send a BAD_LOGIN code.
				log("Failed login attempt to %s from %s:%d" % (					# Logging.
					username, address[0], address[1]))
			except BrokenPipeError:												# If the connection broke...
				log("Broken connection from %s:%s" % (							# Logging.
					address[0], address[1]))
				connection.close()												# Close the connection.
				return 1														# Return with an error.

def deposit(username: str, amount: float, address: tuple) -> int:				# Deposit function.
	'''
	Deposit function.
	Returns 0 if no error, else 1.
	'''

	with open("userAccounts.data", "r") as f:									# Open up a file.
		data = f.read()															# Read it.

	if not username in data:													# If the username is not present...
		log("Unsuccessful deposit of $%d to %s from %s:%d" % (					# Logging.
			amount, username, address[0], address[1]))
		return 1																# Exit with an error.

	newData = ""																# String for new data.

	for line in data.split("\n"):												# Loop through the old data.
		if username in line:													# If the username is present...
			oldBal   = float(line.split()[1])									# Get the old balance
			newData += "%s %.2f\n" % (username, amount + oldBal)				# And write the update data.
		else:																	# Else...
			newData += line + "\n"												# Just write the line.

	with open("userAccounts.data", "w") as f:									# Open up the file again.
		f.write(newData.rstrip())												# Write the new data.

	log("Successful deposit of $%.2f to %s from %s:%d" % (						# Logging.
		amount, username, address[0], address[1]))

	return 0																	# Exit with no error.

def withdraw(username: str, amount: float, address: tuple) -> int:				# Deposit function.
	'''
	Withdraw function.
	Returns 0 if no error, else 1.
	'''

	with open("userAccounts.data", "r") as f:									# Open up a file.
		data = f.read()															# Read it.

	if not username in data:													# If the username is not present...
		log("Unsuccessful withdraw of $%.2f from %s from %s:%d" % (				# Logging.
			amount, username, address[0], address[1]))
		return 1																# Exit with an error.

	newData = ""																# String for new data.

	for line in data.split("\n"):												# Loop through the old data.
		if username in line:													# If the username is present...
			oldBal   = float(line.split()[1])									# Get the old balance
			newData += "%s %.2f\n" % (username, amount - oldBal)				# And write the update data.
		else:																	# Else...
			newData += line + "\n"												# Just write the line.

	with open("userAccounts.data", "w") as f:									# Open up the file again.
		f.write(newData.rstrip())												# Write the new data.

	log("Successful withdraw of $%.2f from %s from %s:%d" % (					# Logging.
		amount, username, address[0], address[1]))

	return 0																	# Exit with no error.

def transfer(sender: str, amount: float, recipient: str, address: tuple) -> int:# Transfer function.
	'''
	Transfer function.
	Returns a 0 if no error, else 1.
	'''

	with open("userAccounts.data", "r") as f:									# Open up a file.
		data = f.read()															# Read it.

	if not ( sender in data and recipient in data ):							# If the username is not present...
		log("Unsuccessful transfer of $%.2f from %s to %s from %s:%d" % 		# Logging.
			(amount, sender, recipient, address[0], address[1]))
		return 1																# Exit with an error.

	withdraw(sender, amount, address)											# Withdraw from the sender.
	deposit(recipient, amount, address)											# Deposit from the recipient.

	log("Successful transfer of $%.2f from %s to %s from %s:%d" % (				# Logging.
		amount, sender, recipient, address[0], address[1]))

	return 0																	# Exit with no error.

def status(username: str, address: tuple) -> int:								# Status function.
	'''
	Status function.
	Returns 0 if no error, else 1.
	'''

	with open("userAccounts.data", "r") as f:									# Open a file.
		data = f.readlines()													# Read it.

	for line in data:															# Loop through the data.
		if username in line:													# If the username is there...
			balance = line.split()[1]											# Get the balance.
			log("Successful status request of %s from %s:%d" % (				# Logging.
				username, address[0], address[1]))
			return 0, float(balance)											# Exit with no error and the balance.

	log("Unsuccessful status request of %s from %s:%d" % (						# Logging.
		username, address[0], address[1]))
	return 1, None																# Exit with an error.

def handler(connection: socket.socket, address: tuple) -> None:					# Handler function.
	'''
	Handler for connections.
	'''

	log("Connection received from %s:%d" % (address[0], address[1]))			# Logging.

	authorized = authorize(connection)											# Authorize the connection.

	if not authorized:															# If unauthorized...
		log("Unsuccessful authorization from %s:%d" % (							# Logging.
			address[0], address[1]))
		connection.send(codes["BAD_AUTH"].encode())								# Send a BAD_AUTH code.
		connection.close()														# Close the connection.
		log("Connection ended with %s:%d" % (									# Logging.
			address[0], address[1]))
		return																	# Exit the function.
	else:
		log("Successful authorization from %s:%d" % (							# Logging.
			address[0], address[1]))
		connection.send(codes["OK_AUTH"].encode())								# Send an OK_AUTH code.

	username = authenticate(connection, address)								# Authenticate the connection.

	if username == 1:															# If there was an error.
		log("Connection broken with %s:%s" % (									# Logging.
			address[0], address[1]))
		connection.close()														# Close the connection.
		return																	# Exit.

	while True:																	# Loop forver.

		try:																	# Try to receive data from the user.
			message = connection.recv(128).decode("utf-8").split()				# Receive something from the user.
			action  = message[0]												# The action is the first segment of data.
			args    = message[1::]												# The args are everything afterwards.
		except:																	# If something goes wrong.
			log("Connection broken with %s:%s" % (								# Logging.
				address[0], address[1]))
			connection.close()													# Close the connection.
			return																# Exit.

		if action == "D":														# If the action is to deposit...
			code = deposit(args[0], float(args[1]), address)					# Call the deposit function.
			if code == 0:														# If there was no error...
				connection.send(codes["OK_DEPO"].encode())						# Send an OK_DEPO code.
			else:																# Otherwise...
				connection.send(codes["BAD_DEPO"].encode())						# Send a BAD_DEPO code.
		elif action == "W":														# If the action is to withdraw...
			code = withdraw(args[0], float(args[1]), address)					# Call the withdraw function.
			if code == 0:														# If there was no error...
				connection.send(codes["OK_DRAW"].encode())						# Send an OK_DRAW code.
			else:																# Otherwise...
				connection.send(codes["BAD_DRAW"].encode())						# Send a BAD_DRAW code.
		elif action == "T":														# If the action is to transfer...
			code = transfer(													# Call the transfer function.
				args[0], float(args[1]), args[2], address)
			if code == 0:														# If there was no error...
				connection.send(codes["OK_TSFR"].encode())						# Send an OK_TSFR code.
			else:																# Otherwise...
				connection.send(codes["BAD_TSFR"].encode())						# Send a BAD_TSFR code.
		elif action == "S":														# If the action is to display the status...
			code, data = status(args[0], address)								# Call the status function.
			if code == 0:														# If there was no error...
				connection.send(codes["OK_STAT"].encode())						# Send an OK_STAT code.
				connection.send(("%.2f" % data).encode())						# Send the data.
			else:																# Otherwise...
				connection.send(codes["BAD_STAT"].encode())						# Send a BAD_STAT code.
		elif action == "E":														# If the action is to exit...
			connection.close()													# Close the connection.
			log("Client-side connection closed by %s:%d" % (					# Logging.
				address[0], address[1]))
			return																# Exit.
		else:																	# Otherwise...
			log("Unknown action from %s:%d" % (									# Logging.
				address[0], address[1]))

def main() -> None:																# Main function.
	'''
	Main function.
	'''

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:				# Instantiate a socket.

		try:
			s.bind((ip, port))													# Bind to an IP and port.
			s.listen(8)															# Listen for up to 8 connections.

			log("Listening for connectons on %s:%d" % (ip, port))				# Logging.

			while True:															# Loop forever.
				connection, address = s.accept()								# Accept a connection.
				threading.Thread(												# Instantiate a thread.
					target=handler,												# Run the handler function.
					args=(connection, address)									# Pass the connection and address.
				).start()														# Start the thread.

		except KeyboardInterrupt:												# If an interrupt is detected...
			log("Interrupt detected. Closing sockets.")							# Logging.
			s.close()															# Close the socket.
			os._exit(1)															# End execution.

if __name__ == "__main__":														# Run protection.
	main()																		# Call the main function.
