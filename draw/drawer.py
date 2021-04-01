import random
from itertools import combinations

# class Drawer:
#
#     def __init__(self):
#         self.lower = 1
#         self.upper = 49
#         self.num_of_ticket = 7
#
#     def draw(self):
#         return random.sample(range(self.lower, self.upper), self.num_of_ticket)
#

# 49P7,  49C7 ,[[permutation],[permutation]]
# 49C7 + 7!

#TODO use generator
def draw():
    return random.sample(range(1,50),7)


