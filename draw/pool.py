from draw.drawer import Drawer


class Pool:
    def __init__(self, ):
        self.pool = []
        self.drawer = Drawer(lower=1,upper=5,num_of_ticket=3)
        self.price = self.drawer.draw()
        self.winner = -1

    def draw(self,user_id):
        ticket = self.drawer.draw()
        if self.is_full():
            return [-1]

        while self.is_ticket_in_poll(ticket):
            ticket = self.drawer.draw()

        self.set_winner(ticket,user_id)
        self.add_to_poll(ticket)
        return ticket

    def add_to_poll(self, ticket):
        self.pool.append(ticket)

    def is_ticket_in_poll(self, ticket):
        return ticket in self.pool

    def set_winner(self, ticket,user_id):
        if ticket == self.price:
            self.winner = user_id

    def is_full(self):
        return len(self.pool) == self.drawer.max

    def get_winner(self):
        return self.winner

    def reset(self):
        self.pool = []
        self.price = self.drawer.draw()
