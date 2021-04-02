import random
from typing import List


class Drawer:

    def __init__(self, lower: int, upper: int, num_of_ticket: int):
        """
        :param lower: the lower bound of drawer
        :param upper: the upper bound of drawer
        :param num_of_ticket: number of selected ticket, lower <= num_of_ticket < upper
        """
        self.lower = lower
        self.upper = upper
        self.num_of_ticket = num_of_ticket
        self.max = self.get_max()

    @property
    def num_of_ticket(self):
        return self._num_of_ticket

    @num_of_ticket.setter
    def num_of_ticket(self,value):
        if self.lower <= value < self.upper:
            self._num_of_ticket = value
        raise ValueError("should be lower <= num_of_ticket < upper")

    def get_max(self) -> int:
        """
        :return: the total length of permutation
        """
        res = 1
        for i in range(self.upper - self.num_of_ticket, self.upper):
            res *= i
        return res

    def draw(self) -> List[int]:
        """
        :return: permutation result
        """
        return random.sample(range(self.lower, self.upper), self.num_of_ticket)
