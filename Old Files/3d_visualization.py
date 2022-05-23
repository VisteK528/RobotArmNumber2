import matplotlib.pyplot as plt
import math

"""fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x, y, z = [1, 1.5], [1, 2.4], [3.4, 1.4]
ax.scatter(x, y, z, color='b', s=100)
ax.plot(x, y, z, color='black')

plt.show()"""


SHOULDER_LENGTH = 20.75
ELBOW_LENGTH = 14.28
END_EFFECTOR = 5

def calculate_angles(x, y, z):
    rads = math.atan2(y, x)
    if y < 0:
        rads += 2 * math.pi
    degrees = (rads * 180) / math.pi

    print("Kąt w stopniach: ", degrees)
    print('Kąt w radianach: ', rads)
    # |OA| point
    r = math.sqrt(pow(x, 2) + pow(y, 2))

    #print(r)
    hypotenuse = math.sqrt(pow(r, 2) + pow(z, 2))
    print(r)
    #print(hypotenuse)
    alfa_1 = math.atan(z / r)
    cos_alfa = (pow(ELBOW_LENGTH, 2) - pow(hypotenuse, 2) - pow(SHOULDER_LENGTH, 2)) / (
                -2 * hypotenuse * SHOULDER_LENGTH)

    cos_beta = (pow(hypotenuse, 2) - pow(SHOULDER_LENGTH, 2) - pow(ELBOW_LENGTH, 2)) / (
                -2 * SHOULDER_LENGTH * ELBOW_LENGTH)

    alfa = ((math.acos(cos_alfa)) + alfa_1)
    beta = math.acos(cos_beta)

    return alfa, beta, rads, alfa_1



x, y, z = input('Podaj koordynaty punktu docelowego: ').split()

x, y, z = float(x), float(y), float(z)

# Punkt A
alfa, beta, _, alfa_1 = calculate_angles(x, y, z)
print('Tangens: ', math.tan(alfa+beta))
A_X = math.sqrt(pow(SHOULDER_LENGTH, 2)/(1+pow(math.tan(alfa), 2)))
A_Y = A_X*math.tan(alfa)



# Punkt B
print('New tan: ', alfa_1*180/math.pi)
c = -(pow(ELBOW_LENGTH, 2) - pow(A_X, 2) - pow(A_Y, 2))
b = (-2*A_X - 2*A_Y*math.tan(alfa_1))
a = (1 + pow(math.tan(alfa_1), 2))
delta = pow(b, 2) - 4*a*c
delta_sqrt = math.sqrt(delta)

B_X_1 = (-b-delta_sqrt)/(2*a)
B_X_2 = (-b+delta_sqrt)/(2*a)

B_Y_1 = B_X_1*math.tan(alfa_1)
B_Y_2 = B_X_2*math.tan(alfa_1)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

print(B_X_1, B_Y_1)
print(B_X_2, B_Y_2)
X, Y, Z = [0, A_X, B_X_2], [0, 0, 0], [0, A_Y, B_Y_2]
ax.scatter(X, Y, Z, color='b', s=100)
ax.scatter(x, y, z, color='r', s=200)
ax.plot(X, Y, Z, color='black')

LINE_X, LINE_Y, LINE_Z = [0, 5], [0, 0], [0, math.tan(alfa_1)*180]

print(X, Y, Z)
print(alfa*180/math.pi, beta*180/math.pi)
plt.show()

