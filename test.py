import unittest
import coverage

from draw.drawer import Drawer
from draw.pool import Pool
from draw.gamemaster import GameMaster

cov = coverage.coverage(branch=True)
cov.start()
from server import socketio, app


class TestDraw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        # cov.stop()
        # cov.report(include='flask_socketio/*', show_missing=True)
        pass

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

    def test_pool_full(self):
        maximum = self.drawer.max
        ticket = [-1]
        for i in range(maximum):
            ticket = self.pool.draw(i)
        self.assertTrue(ticket != [-1])
        full_ticket = self.pool.draw(maximum)
        self.assertTrue(full_ticket, -1)

    def test_pool_reset(self):
        maximum = self.drawer.max
        ticket = [-1]
        for i in range(maximum):
            ticket = self.pool.draw(i)
        self.assertEqual(len(self.pool.pool),maximum)
        self.pool.reset()
        self.assertEqual(len(self.pool.pool), 0)
        self.assertEqual(self.pool.winner, -1)

    def test_winner_exist(self):
        maximum = self.drawer.max
        for i in range(maximum):
            ticket = self.pool.draw(user_id=i + 1)
        self.assertTrue(self.pool.winner != -1)



class TestLotterySocketIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        # cov.stop()
        # cov.report(include='flask_socketio/*', show_missing=True)
        pass

    def setUp(self):
        self.drawer = Drawer(lower=1,upper=5,num_of_ticket=3)

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
        self.assertEqual(received[0]['args'], [{'data': 'Connected'}])
        client.disconnect()
        self.assertFalse(client.is_connected())
        self.assertTrue(client2.is_connected())
        client2.disconnect()
        self.assertFalse(client2.is_connected())

    def test_buy_ticket(self):
        client = socketio.test_client(app)
        client.emit('buy_ticket', '')
        received = client.get_received()
        print(received)
        self.assertEqual(len(received), 2)
        self.assertEqual(received[0]['name'], 'my_response')
        data = received[1]['args'][0]['data']
        self.assertEqual(len(data[0]), 3)
        self.assertTrue(isinstance(data[1], int))


    def test_one_player_buy_ticket_full(self):
        client = socketio.test_client(app)
        maximun = self.drawer.max
        for i in range(maximun):
            client.emit('buy_ticket', '')
        client.emit('buy_ticket','')
        received = client.get_received()
        self.assertEqual(received[-1]['args'][0]['data'][0],[-1])


    def test_connect_query_string_and_headers(self):
        client = socketio.test_client(
            app, query_string='?foo=bar&foo=baz',
            headers={'Authorization': 'Bearer foobar'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'connected')
        self.assertEqual(received[1]['args'], '{"foo": ["bar", "baz"]}')
        self.assertEqual(received[2]['args'],
                         '{"Authorization": "Bearer foobar"}')
        client.disconnect()

    def test_connect_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        self.assertTrue(client.is_connected('/test'))
        received = client.get_received('/test')
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected-test')
        self.assertEqual(received[1]['args'], '{}')
        self.assertEqual(received[2]['args'], '{}')
        client.disconnect(namespace='/test')
        self.assertFalse(client.is_connected('/test'))

    def test_connect_namespace_query_string_and_headers(self):
        client = socketio.test_client(
            app, namespace='/test', query_string='foo=bar',
            headers={'My-Custom-Header': 'Value'})
        received = client.get_received('/test')
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected-test')
        self.assertEqual(received[1]['args'], '{"foo": ["bar"]}')
        self.assertEqual(received[2]['args'], '{"My-Custom-Header": "Value"}')
        client.disconnect(namespace='/test')

    def test_connect_rejected(self):
        client = socketio.test_client(app, query_string='fail=1')
        self.assertFalse(client.is_connected())

    def test_disconnect(self):
        global disconnected
        disconnected = None
        client = socketio.test_client(app)
        client.disconnect()
        self.assertEqual(disconnected, '/')

    def test_disconnect_namespace(self):
        global disconnected
        disconnected = None
        client = socketio.test_client(app, namespace='/test')
        client.disconnect('/test')
        self.assertEqual(disconnected, '/test')

    def test_send(self):
        client = socketio.test_client(app)
        client.get_received()
        client.send('echo this message back')
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'echo this message back')

    def test_send_json(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client1.get_received()
        client2.get_received()
        client1.send({'a': 'b'}, json=True)
        received = client1.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')
        received = client2.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')

    def test_send_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.send('echo this message back', namespace='/test')
        received = client.get_received('/test')
        self.assertTrue(len(received) == 1)
        self.assertTrue(received[0]['args'] == 'echo this message back')

    def test_send_json_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.send({'a': 'b'}, json=True, namespace='/test')
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')

    def test_emit(self):
        client = socketio.test_client(app)
        client.get_received()
        client.emit('my custom event', {'a': 'b'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_emit_binary(self):
        client = socketio.test_client(app)
        client.get_received()
        client.emit('my custom event', {u'a': b'\x01\x02\x03'})
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], b'\x01\x02\x03')

    def test_request_event_data(self):
        client = socketio.test_client(app)
        client.get_received()
        global request_event_data
        request_event_data = None
        client.emit('other custom event', 'foo')
        expected_data = {'message': 'other custom event', 'args': ('foo',)}
        self.assertEqual(request_event_data, expected_data)
        client.emit('and another custom event', 'bar')
        expected_data = {'message': 'and another custom event',
                         'args': ('bar',)}
        self.assertEqual(request_event_data, expected_data)

    def test_emit_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.emit('my custom namespace event', {'a': 'b'}, namespace='/test')
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom namespace response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_broadcast(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client3 = socketio.test_client(app, namespace='/test')
        client2.get_received()
        client3.get_received('/test')
        client1.emit('my custom broadcast event', {'a': 'b'}, broadcast=True)
        received = client2.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')
        self.assertEqual(len(client3.get_received('/test')), 0)

    def test_broadcast_namespace(self):
        client1 = socketio.test_client(app, namespace='/test')
        client2 = socketio.test_client(app, namespace='/test')
        client3 = socketio.test_client(app)
        client2.get_received('/test')
        client3.get_received()
        client1.emit('my custom broadcast namespace event', {'a': 'b'},
                     namespace='/test')
        received = client2.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom namespace response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')
        self.assertEqual(len(client3.get_received()), 0)

    def test_session(self):
        flask_client = app.test_client()
        flask_client.get('/session')
        client = socketio.test_client(app, flask_test_client=flask_client)
        client.get_received()
        client.send('echo this message back')
        self.assertEqual(
            socketio.server.environ[client.eio_sid]['saved_session'],
            {'foo': 'bar'})
        client.send('test session')
        self.assertEqual(
            socketio.server.environ[client.eio_sid]['saved_session'],
            {'a': 'b', 'foo': 'bar'})

    def test_room(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client3 = socketio.test_client(app, namespace='/test')
        client1.get_received()
        client2.get_received()
        client3.get_received('/test')
        client1.emit('join room', {'room': 'one'})
        client2.emit('join room', {'room': 'one'})
        client3.emit('join room', {'room': 'one'}, namespace='/test')
        client1.emit('my room event', {'a': 'b', 'room': 'one'})
        received = client1.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my room response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')
        self.assertEqual(received, client2.get_received())
        received = client3.get_received('/test')
        self.assertEqual(len(received), 0)
        client1.emit('leave room', {'room': 'one'})
        client1.emit('my room event', {'a': 'b', 'room': 'one'})
        received = client1.get_received()
        self.assertEqual(len(received), 0)
        received = client2.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my room response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')
        client2.disconnect()
        socketio.emit('my room event', {'a': 'b'}, room='one')
        received = client1.get_received()
        self.assertEqual(len(received), 0)
        received = client3.get_received('/test')
        self.assertEqual(len(received), 0)
        client3.emit('my room namespace event', {'room': 'one'},
                     namespace='/test')
        received = client3.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'message')
        self.assertEqual(received[0]['args'], 'room message')
        socketio.close_room('one', namespace='/test')
        client3.emit('my room namespace event', {'room': 'one'},
                     namespace='/test')
        received = client3.get_received('/test')
        self.assertEqual(len(received), 0)

    def test_error_handling(self):
        client = socketio.test_client(app)
        client.get_received()
        global error_testing
        error_testing = False
        client.emit("error testing", "")
        self.assertTrue(error_testing)

    def test_error_handling_namespace(self):
        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        global error_testing_namespace
        error_testing_namespace = False
        client.emit("error testing", "", namespace='/test')
        self.assertTrue(error_testing_namespace)

    def test_error_handling_default(self):
        client = socketio.test_client(app, namespace='/unused_namespace')
        client.get_received('/unused_namespace')
        global error_testing_default
        error_testing_default = False
        client.emit("error testing", "", namespace='/unused_namespace')
        self.assertTrue(error_testing_default)

    def test_ack(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client3 = socketio.test_client(app)
        ack = client1.send('echo this message back', callback=True)
        self.assertEqual(ack, 'echo this message back')
        ack = client1.send('test noackargs', callback=True)
        # python-socketio releases before 1.5 did not correctly implement
        # callbacks with no arguments. Here we check for [] (the correct, 1.5
        # and up response) and None (the wrong pre-1.5 response).
        self.assertTrue(ack == [] or ack is None)
        ack2 = client2.send({'a': 'b'}, json=True, callback=True)
        self.assertEqual(ack2, {'a': 'b'})
        ack3 = client3.emit('my custom event', {'a': 'b'}, callback=True)
        self.assertEqual(ack3, {'a': 'b'})

    def test_noack(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client3 = socketio.test_client(app)
        no_ack_dict = {'noackargs': True}
        noack = client1.send("test noackargs", callback=False)
        self.assertIsNone(noack)
        noack2 = client2.send(no_ack_dict, json=True, callback=False)
        self.assertIsNone(noack2)
        noack3 = client3.emit('my custom event', no_ack_dict)
        self.assertIsNone(noack3)

    def test_error_handling_ack(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app, namespace='/test')
        client3 = socketio.test_client(app, namespace='/unused_namespace')
        errorack = client1.emit("error testing", "", callback=True)
        self.assertEqual(errorack, 'error')
        errorack_namespace = client2.emit("error testing", "",
                                          namespace='/test', callback=True)
        self.assertEqual(errorack_namespace, 'error/test')
        errorack_default = client3.emit("error testing", "",
                                        namespace='/unused_namespace',
                                        callback=True)
        self.assertEqual(errorack_default, 'error/default')

    def test_on_event(self):
        client = socketio.test_client(app)
        client.get_received()
        global request_event_data
        request_event_data = None
        client.emit('yet another custom event', 'foo')
        expected_data = {'message': 'yet another custom event',
                         'args': ('foo',)}
        self.assertEqual(request_event_data, expected_data)

        client = socketio.test_client(app, namespace='/test')
        client.get_received('/test')
        client.emit('yet another custom namespace event', {'a': 'b'},
                    namespace='/test')
        received = client.get_received('/test')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom namespace response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_connect_class_based(self):
        client = socketio.test_client(app, namespace='/ns')
        received = client.get_received('/ns')
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected-ns')
        self.assertEqual(received[1]['args'], '{}')
        self.assertEqual(received[2]['args'], '{}')
        client.disconnect('/ns')

    def test_connect_class_based_query_string_and_headers(self):
        client = socketio.test_client(
            app, namespace='/ns', query_string='foo=bar',
            headers={'Authorization': 'Basic foobar'})
        received = client.get_received('/ns')
        self.assertEqual(len(received), 3)
        self.assertEqual(received[0]['args'], 'connected-ns')
        self.assertEqual(received[1]['args'], '{"foo": ["bar"]}')
        self.assertEqual(received[2]['args'],
                         '{"Authorization": "Basic foobar"}')
        client.disconnect('/ns')

    def test_disconnect_class_based(self):
        global disconnected
        disconnected = None
        client = socketio.test_client(app, namespace='/ns')
        client.disconnect('/ns')
        self.assertEqual(disconnected, '/ns')

    def test_send_class_based(self):
        client = socketio.test_client(app, namespace='/ns')
        client.get_received('/ns')
        client.send('echo this message back', namespace='/ns')
        received = client.get_received('/ns')
        self.assertTrue(len(received) == 1)
        self.assertTrue(received[0]['args'] == 'echo this message back')

    def test_send_json_class_based(self):
        client = socketio.test_client(app, namespace='/ns')
        client.get_received('/ns')
        client.send({'a': 'b'}, json=True, namespace='/ns')
        received = client.get_received('/ns')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args']['a'], 'b')

    def test_server_disconnected(self):
        client = socketio.test_client(app, namespace='/ns')
        client.get_received('/ns')
        client.emit('exit', {}, namespace='/ns')
        self.assertFalse(client.is_connected('/ns'))
        with self.assertRaises(RuntimeError):
            client.emit('hello', {}, namespace='/ns')

    def test_emit_class_based(self):
        client = socketio.test_client(app, namespace='/ns')
        client.get_received('/ns')
        client.emit('my_custom_event', {'a': 'b'}, namespace='/ns')
        received = client.get_received('/ns')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'my custom response')
        self.assertEqual(received[0]['args'][0]['a'], 'b')

    def test_request_event_data_class_based(self):
        client = socketio.test_client(app, namespace='/ns')
        client.get_received('/ns')
        global request_event_data
        request_event_data = None
        client.emit('other_custom_event', 'foo', namespace='/ns')
        expected_data = {'message': 'other_custom_event', 'args': ('foo',)}
        self.assertEqual(request_event_data, expected_data)

    # def test_delayed_init(self):
    #     app = Flask(__name__)
    #     socketio = SocketIO(allow_upgrades=False, json=flask_json)
    #
    #     @socketio.on('connect')
    #     def on_connect():
    #         send({'connected': 'foo'}, json=True)
    #
    #     socketio.init_app(app, cookie='foo')
    #     self.assertFalse(socketio.server.eio.allow_upgrades)
    #     self.assertEqual(socketio.server.eio.cookie, 'foo')
    #
    #     client = socketio.test_client(app)
    #     received = client.get_received()
    #     self.assertEqual(len(received), 1)
    #     self.assertEqual(received[0]['args'], {'connected': 'foo'})

    def test_encode_decode(self):
        client = socketio.test_client(app)
        client.get_received()
        data = {'foo': 'bar', 'invalid': socketio}
        self.assertRaises(TypeError, client.emit, 'my custom event', data,
                          callback=True)
        data = {'foo': 'bar'}
        ack = client.emit('my custom event', data, callback=True)
        data['foo'] = 'baz'
        received = client.get_received()
        self.assertEqual(ack, {'foo': 'bar'})
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0], {'foo': 'bar'})

    def test_encode_decode_2(self):
        client = socketio.test_client(app)
        self.assertRaises(TypeError, client.emit, 'bad response')
        self.assertRaises(TypeError, client.emit, 'bad callback',
                          callback=True)
        client.get_received()
        ack = client.emit('changing response', callback=True)
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0], {'foo': 'bar'})
        self.assertEqual(ack, {'foo': 'baz'})


if __name__ == '__main__':
    unittest.main()
