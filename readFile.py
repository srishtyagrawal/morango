import matplotlib.pyplot as plt
import numpy

def readFile (filename):
	x = []
	y = []
	with open(filename, "r") as ins:
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
	return (x, y)

(x, y) = readFile ("results/100AddNew")
plt.plot(x, y, "ro")
plt.show()

#(a, b) = readFile ("results/fullBiDiff")
#print "fullBiDiff"
#print a[50]
#print b[50]
"""
(x, y) = readFile ("results/fullBiDiff")
(a, b) = readFile ("results/biStarDiff")
(n, m) = readFile ("results/ringDiffBi")
plt.plot(x, y, "ro")
plt.plot(a, b, "g^")
plt.plot(n, m, "bs")
plt.legend(['Mesh Topology', 'Star Topology', 'Ring Topology'], loc = 2)
plt.ylabel('Num random communications for achieving eventual consistency')
plt.xlabel('Total nodes in the network arranged in different topologies')
#plt.show()
coefficients1 = numpy.polyfit(x, y, 2)
polynomial1 = numpy.poly1d(coefficients1)
print polynomial1
coefficients2 = numpy.polyfit(a, b, 2)
polynomial2 = numpy.poly1d(coefficients2)
print polynomial2
coefficients3 = numpy.polyfit(n, m, 2)
polynomial3 = numpy.poly1d(coefficients3)
print polynomial3
"""
