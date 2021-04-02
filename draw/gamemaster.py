from draw.pool import Pool


class GameMaster():
    def __init__(self):
        self.ticket_pool = Pool()
        self.player_list = []

    def buy_ticket(self, client_id):
        ticket = self.ticket_pool.draw(client_id)

        self.player_list.append(client_id)
        return [ticket, client_id]

    def notify_winner(self):
        winner_index = self.ticket_pool.get_winner()
        return [self.ticket_pool.price, winner_index]

    def restart(self):
        self.ticket_pool.reset()
