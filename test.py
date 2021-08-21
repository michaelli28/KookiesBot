from math import comb
import random
import time
while True:
    i=None
    num2= random.randint(1,10)
    num1 = random.randint(num2,10)
    while num1 == num2 and num1 != 10:
        num1 = random.randint(num2,10)
    print(str(num1) + " choose " + str(num2))
    i = input("answer\n")
    if i == str(comb(num1,num2)):
        print("good job!!")
    else:
        print("nope the answer was " + str(comb(num1,num2)))
