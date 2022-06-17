import json
import time
import requests
from flask import Flask, render_template
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy

from constans import images

app = Flask('API')
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
sock = Sock(app)

webpages = set()
outdoor = {}
apikey = '365746c5963c425192004235221206'
update_time = 60


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, default=lambda: int(time.time()) * 1000)
    home_temperature = db.Column(db.Float)
    home_humidity = db.Column(db.Float)
    outdoor_temperature = db.Column(db.Float)
    outdoor_humidity = db.Column(db.Float)
    co2 = db.Column(db.Integer)
    pressure = db.Column(db.Integer)


db.create_all()


def get_weather_data(town):
    if outdoor.get(town, {}).get('time') and outdoor.get(town, {}).get('time', time.time()) - time.time() < update_time:
        return 'update|{}|{}|{}|{}'.format(*outdoor[town].values())
    r = requests.get('https://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no'.format(apikey, town))
    data = r.json()
    outdoor[town] = {
        'temp': data['current']['temp_c'],
        'humidity': data['current']['humidity'],
        'is_day':  data['current']['is_day'],
        'icon_id': images.index(int(data['current']['condition']['icon'].split('/')[-1].split('.')[0]))
    }
    return 'update|{}|{}|{}|{}'.format(*outdoor[town].values())


@app.route('/')
def index():
    home_temperature_data, home_humidity_data, co2_data, outdoor_temperature_data, \
        outdoor_humidity_data, pressure_data = [], [], [], [], [], []

    for i in Data.query.all():
        home_temperature_data.append([i.time, i.home_temperature])
        home_humidity_data.append([i.time, i.home_humidity])
        co2_data.append([i.time, i.co2])
        outdoor_temperature_data.append([i.time, i.outdoor_temperature])
        outdoor_humidity_data.append([i.time, i.outdoor_humidity])
        pressure_data.append([i.time, i.pressure])

    return render_template('index.html',
                           home_temperature_data=home_temperature_data,
                           home_humidity_data=home_humidity_data,
                           co2_data=co2_data,
                           outdoor_temperature_data=outdoor_temperature_data,
                           outdoor_humidity_data=outdoor_humidity_data,
                           pressure_data=pressure_data)


@sock.route('/')
def echo(ws):
    global webpages
    while True:
        data = ws.receive().split('|')
        if data[0] == 'innit':
            if data[1] == 'web':
                webpages.add(ws)
            elif data[1] == 'sensor':
                ws.send(get_weather_data(data[2]))
        elif data[0] == 'update':
            if data[1] == 'sensor':
                ws.send(get_weather_data(data[2]))
                new_data = Data(home_temperature=data[3],
                                home_humidity=data[4],
                                outdoor_temperature=outdoor[data[2]]['temp'],
                                outdoor_humidity=outdoor[data[2]]['humidity'],
                                co2=data[5],
                                pressure=data[6])

                db.session.add(new_data)
                db.session.commit()
                data = {
                    'time': new_data.time,
                    'home_temperature': new_data.home_temperature,
                    'outdoor_temperature': new_data.outdoor_temperature,
                    'home_humidity': new_data.home_humidity,
                    'outdoor_humidity': new_data.outdoor_humidity,
                    'co2': new_data.co2,
                    'pressure': new_data.pressure
                }
                new_webpages = set()
                for webpage in webpages:
                    try:
                        webpage.send(json.dumps(data))
                        new_webpages.add(webpage)
                    except (Exception,):
                        pass
                webpages = new_webpages


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
