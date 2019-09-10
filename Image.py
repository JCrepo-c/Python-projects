import requests

image = requests.get("https://www.python.org/static/img/python-logo.png").content
with open("logo.png", "wb+") as f:
		f.write(image)