import unittest
from threading import Thread

from draw.drawer import Drawer
from draw.pool import Pool
from server import app, socketio


class TestDraw(unittest.TestCase):
    def setUp(self):
        self.drawer = Drawer(lower=1, upper=5, num_of_ticket=3)

    def tearDown(self):
        pass

    def test_draw(self):
        ticket = self.drawer.draw()
        self.assertTrue(len(ticket), self.drawer.num_of_ticket)
        for number in ticket:
            self.assertTrue(self.drawer.upper > number >= self.drawer.lower)

    def test_max(self):
        self.assertTrue(self.drawer.max, 24)


class TestPool(unittest.TestCase):
    def setUp(self):
        self.pool = Pool()
        self.drawer = Drawer(lower=1, upper=5, num_of_ticket=3)

    def tearDown(self):
        pass

    def test_add_to_pool(self):
        self.assertEqual(len(self.pool.pool), 0)
        ticket = self.drawer.draw()
        self.pool.add_to_poll(ticket)
        self.assertEqual(len(self.pool.pool), 1)

    def test_pool_full(self):
        maximum = self.drawer.max
        ticket = [-1]
        for i in range(maximum):
            ticket = self.pool.draw(i)
        self.assertTrue(ticket != [-1])
        full_ticket = self.pool.draw(maximum)
        self.assertTrue(full_ticket, [-1])

    def test_pool_reset(self):
        maximum = self.drawer.max
        ticket = [-1]
        for i in range(maximum):
            ticket = self.pool.draw(i)
        self.assertEqual(len(self.pool.pool), maximum)
        self.pool.reset()
        self.assertEqual(len(self.pool.pool), 0)
        self.assertEqual(self.pool.winner, "-")

    def test_winner_exist(self):
        maximum = self.drawer.max
        for i in range(maximum):
            ticket = self.pool.draw(user_id=i + 1)
        self.assertTrue(self.pool.winner != "-")

    def test_is_ticket_in_poll(self):
        ticket = self.drawer.draw()
        self.pool.add_to_poll(ticket)
        self.assertTrue(self.pool.is_ticket_in_poll(ticket))


class TestLotterySocketIO(unittest.TestCase):
    def setUp(self):
        self.drawer = Drawer(lower=1, upper=5, num_of_ticket=3)

    def tearDown(self):
        pass

    def test_connect(self):
        client = socketio.test_client(app)
        client2 = socketio.test_client(app)
        self.assertTrue(client.is_connected())
        self.assertTrue(client2.is_connected())
        self.assertNotEqual(client.eio_sid, client2.eio_sid)
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["args"], [{"data": "Connected"}])
        client.disconnect()
        self.assertFalse(client.is_connected())
        self.assertTrue(client2.is_connected())
        client2.disconnect()
        self.assertFalse(client2.is_connected())

    def test_buy_ticket(self):
        client = socketio.test_client(app)
        client.emit("buy_ticket", client.eio_sid)
        received = client.get_received()
        response = [resp for resp in received if resp["name"] == "server_response"]
        self.assertEqual(response[0]["name"], "server_response")
        data = response[0]["args"][0]["data"]
        self.assertEqual(len(data[0]), 3)
        self.assertTrue(isinstance(data[1], str))
        self.assertTrue(len(data[1]) > 1)

    def test_one_player_buy_ticket_full(self):
        client = socketio.test_client(app)
        maximum = self.drawer.max
        for i in range(maximum):
            client.emit("buy_ticket", client.eio_sid)
        client.emit("buy_ticket", client.eio_sid)
        received = client.get_received()
        self.assertEqual(received[-1]["args"][0]["data"][0], [-1])

    def test_thread_buyer(self):
        client = socketio.test_client(app)
        client2 = socketio.test_client(app)
        maximum = self.drawer.max
        for i in range(maximum - 1):
            client.emit("buy_ticket", client.eio_sid)

        p1 = Thread(target=client.emit, args=("buy_ticket", client.eio_sid))
        p2 = Thread(target=client2.emit, args=("buy_ticket", client2.eio_sid))
        p1.start()
        p2.start()

        received = client2.get_received()
        self.assertEqual(received[-1]["args"][0]["data"][0], [-1])


if __name__ == "__main__":
    unittest.main()
