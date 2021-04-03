from typing import List, Tuple, Union

from draw.pool import Pool


class GameMaster:
    def __init__(self):
        self.ticket_pool = Pool()
        self.player_list = []

    def buy_ticket(self, client_id: str) -> Tuple[List[int], str]:
        """
        :param client_id: client socket id
        :return: [draw result ,client socket id]
        """
        ticket = self.ticket_pool.draw(client_id)

        self.player_list.append(client_id)
        return ticket, client_id

    def notify_winner(self) -> Tuple[List[int], str]:
        """
        :return: winner_index would be "-" if no winner otherwise return client socket id
        """
        winner_id = self.ticket_pool.get_winner()
        return self.ticket_pool.price, winner_id

    def restart(self) -> None:
        self.ticket_pool.reset()
