import matplotlib.pyplot as plt
import numpy
x = []
y = []
with open("fullBiDiff", "r") as ins:
	array = []
	for line in ins:
        	array.append(line)

for i in range(len(array)):
	if (i%2==0):
		x.append(int(array[i]))
	else :
		temp = array[i].split(",")
		temp[0] = temp[0][1:]		
		temp[-1] = temp[-1][:-2]
		total = 0
		for j in temp :
			total = total + int(j)
		total = total/100
		y.append(total)
coefficients = numpy.polyfit(x, y, 2)
polynomial = numpy.poly1d(coefficients)
ys = polynomial(x)
print coefficients
print polynomial
plt.plot(x, y, 'ro')
plt.ylabel('Total number of random one way communication')
plt.xlabel('Total nodes in star topology')
plt.show()


