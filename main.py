import os
import logging
import time

from websocket_server import WebsocketServer
from constans import *
import requests
import threading


def get_weather_data(town):
    r = requests.get('https://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no'.format(os.environ.get('API'), town))
    data = r.json()
    print(data)
    icon_id = images.index(int(data['current']['condition']['icon'].split('/')[-1].split('.')[0]))
    return 'update|{}|{}|{}|{}'.format(int(data['current']['temp_c']), data['current']['humidity'],
                                           data['current']['is_day'], icon_id)


def update_data(server: WebsocketServer, client, town):
    while True:
        try:
            server.send_message(client, get_weather_data(town))
            time.sleep(60)
        except Exception as e:
            print(e)
            break


def message_received(client, server, message):
    data = message.split('|')
    print(data)
    if data[0] == 'innit':
        threading.Thread(target=update_data, args=(server, client, data[1]), daemon=True).start()


def main():
    server = WebsocketServer(host='0.0.0.0', port=8765, loglevel=logging.CRITICAL)
    server.set_fn_message_received(message_received)
    server.run_forever()


if __name__ == '__main__':
    main()
