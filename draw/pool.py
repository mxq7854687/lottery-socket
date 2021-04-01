from draw import drawer
from itertools import permutations

class Pool:
    def __init__(self,):
        self.pool = []
        self.price = drawer.draw()
        self.winner = -1

    def add_to_poll(self,ticket):
        self.pool.append(ticket)

    def is_ticket_in_poll(self,ticket):
        return ticket in self.pool

    def set_winner(self,):
        return

    def is_full(self):
        return len(self.pool) == 24

    def get_winner(self):
        for i in range(len(self.pool)):
            if self.pool[i] == self.price:
                return i
        return -1

    def reset(self):
        self.pool = []
        self.price = drawer.draw()