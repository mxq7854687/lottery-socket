from draw import drawer
from draw.pool import Pool
from datetime import datetime


class GameMaster:
    def __init__(self):
        self.ticket_pool = Pool()
        self.player_list = []

    @staticmethod
    def get_user_id():
        return int(datetime.now().timestamp() * 1000000)

    def buy_ticket(self):
        user_id = self.get_user_id()
        ticket = self.ticket_pool.draw(user_id)

        self.player_list.append(user_id)
        return [ticket, user_id]

    def notify_winner(self):
        winner_index = self.ticket_pool.get_winner()
        return winner_index

    def restart(self):
        self.ticket_pool.reset()
