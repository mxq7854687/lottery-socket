from typing import List

from draw.drawer import Drawer


class Pool:
    def __init__(self) -> None:
        """
        drawer: declare list of numbers in the game
        pool: store tickets
        price: draw from drawer
        winner: client socket id , default is "-"
        """
        self.drawer = Drawer(lower=1, upper=5, num_of_ticket=3)
        self.pool: List[List[int]] = []
        self.price = self.drawer.draw()
        self.winner = "-"

    def draw(self, user_id) -> List[int]:
        """
        :param user_id: client socket id , send by client
        :return: unique list of number in pool, [-1] when full
        """
        ticket = self.drawer.draw()
        if self.is_full():
            return [-1]

        while self.is_ticket_in_poll(ticket):
            ticket = self.drawer.draw()

        self.set_winner(ticket, user_id)
        self.add_to_poll(ticket)
        return ticket

    def add_to_poll(self, ticket: List[int]) -> None:
        self.pool.append(ticket)

    def is_ticket_in_poll(self, ticket: List[int]):
        return ticket in self.pool

    def set_winner(self, ticket: List[int], user_id: str) -> None:
        if ticket == self.price:
            self.winner = user_id

    def is_full(self) -> bool:
        return len(self.pool) == self.drawer.max

    def get_winner(self) -> str:
        return self.winner

    def reset(self) -> None:
        """
        Reset all attribute in init function
        """
        self.__init__()
