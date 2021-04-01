from draw import drawer
from draw.pool import Pool
from datetime import datetime


class GameMaster:
    def __init__(self):
        self.ticket_pool = Pool()
        self.player_list = []

    def register(self):
        user_id = self.get_user_id()
        return f"You register with id {user_id}"

    @staticmethod
    def start_game():
        print("game started")

    @staticmethod
    def get_user_id():
        return int(datetime.now().timestamp() * 1000000)

    def buy_ticket(self):
        user_id = self.get_user_id()
        lucky_ticket = drawer.draw()
        #TODO check winner instead of check pool list
        print("start")

        while self.ticket_pool.is_ticket_in_poll(ticket=lucky_ticket):
            if self.ticket_pool.is_full():
                return f'full'
            lucky_ticket = drawer.draw()
        print("end")
        self.ticket_pool.add_to_poll(lucky_ticket)
        self.player_list.append(user_id)
        return f"You buy ticket {lucky_ticket} with id {user_id}"
        # return [lucky_ticket,user_id]

    def notify_winner(self):
        winner_index = self.ticket_pool.get_winner()
        print("winner_index")
        if winner_index >= 0:
            winner_id = self.player_list[winner_index]
            return f"Lucky ticket is {self.ticket_pool.price}. Winner is {winner_id} ! Congratulations!"
        else:
            return f"Lucky ticket is {self.ticket_pool.price}. Has no winner in this round"

    def restart(self):
        self.ticket_pool.reset()

