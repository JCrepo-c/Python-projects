import matplotlib.pyplot

f = lambda x: 7 * x**2 + 8*x - 10

xcooridnates = []
ycooridnates = []
x = -50
while x <50:
	ycooridnates.append(f(x))
	xcooridnates.append(x)
	x += 0.1

matplotlib.pyplot.plot(xcooridnates,ycooridnates)
matplotlib.pyplot.show()