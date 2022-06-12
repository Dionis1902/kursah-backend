import asyncio
import os
import websockets
import aiohttp
from constans import *


async def get_weather_data(town):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no'.format(os.environ.get('API'), town)) as resp:
            data = await resp.json()
            icon_id = images.index(int(data['current']['condition']['icon'].split('/')[-1].split('.')[0]))
            return 'update|{}|{}|{}|{}'.format(int(data['current']['temp_c']), data['current']['humidity'],
                                               data['current']['is_day'], icon_id)


async def hello(websocket, _):
    data = await websocket.recv()
    split_data = data.split('|')
    print(split_data)
    if split_data[0] == 'innit':
        await websocket.send(await get_weather_data(split_data[1]))

start_server = websockets.serve(hello, "0.0.0.0", 8765)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start_server)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
