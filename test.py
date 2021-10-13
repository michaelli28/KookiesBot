# from math import comb
# import random
# import time
# while True:
#     i=None
#     num2= random.randint(1,10)
#     num1 = random.randint(num2,10)
#     while num1 == num2 and num1 != 10:
#         num1 = random.randint(num2,10)
#     print(str(num1) + " choose " + str(num2))
#     i = input("answer\n")
#     if i == str(comb(num1,num2)):
#         print("good job!!")
#     else:
#         print("nope the answer was " + str(comb(num1,num2)))
"""characters = [' ','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
order = dict(zip(numbers, characters))
print(order)


class Letter:
    def get_letter(self):
        return order[self.code]


class OddLetter(Letter):
    def __init__(self, num_code):
        self.code = num_code


class EvenLetter(Letter):
    def __init__(self, num_code):
        self.code = num_code


class BlankLetter(Letter):
    def __init__(self, num_code):
        self.code = num_code


letters = []
letters.append(EvenLetter(8))
letters.append(OddLetter(5))
letters.append(EvenLetter(12))
letters.append(EvenLetter(12))
letters.append(OddLetter(15))
letters.append(BlankLetter(0))
letters.append(OddLetter(23))
letters.append(OddLetter(15))
letters.append(OddLetter(18))
letters.append(EvenLetter(12))
letters.append(EvenLetter(4))

print("".join([letter.get_letter() for letter in letters]))
"""

p = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
for prime in p:
    if ((prime**6)-1)%5==0:
        if ((prime**5)-1)%6==0:
            print(prime)