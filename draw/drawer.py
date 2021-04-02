import random
from itertools import combinations

class Drawer:

    def __init__(self,lower,upper,num_of_ticket):
        self.lower = lower
        self.upper = upper
        self.num_of_ticket = num_of_ticket
        self.max = self.get_max()

    def get_max(self):
        res = 1
        for i in range(self.upper - self.num_of_ticket,self.upper):
            res *= i
        return res

    def draw(self):
        return random.sample(range(self.lower, self.upper), self.num_of_ticket)



