from flask import Flask, request, jsonify
import pickle
import numpy as np
from pyowm import OWM
import pandas as pd
from datetime import date
import datetime

import requests

model = pickle.load(open('model.pkl', 'rb'))


def month(state, city):
    todays_date = date.today()

    owm = OWM('c706f5b72e2e8e0eaf78a1a673fb53ee')  # using the api key
    rf = pd.read_csv("aslirainfall.csv")
    mgr = owm.weather_manager()

    weatheratplace = mgr.weather_at_place(city)
    weather = weatheratplace.weather
    temp = weather.temperature("celsius")
    humidity = weather.humidity
    actualtemp = temp["temp"]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    actualm = months[todays_date.month % 12 - 1].upper()
    temp = weather.temperature("celsius")
    d = rf["STATES"].tolist()
    i = d.index(state)
    rainfall = float(rf.loc[i, actualm])
    return [rainfall, humidity, actualtemp]


app = Flask(__name__)


@app.route('/')
def home():
    return "Hello World"


@app.route('/predict', methods=['POST'])
def predict():
    state = request.form.get('state')
    state = state.upper().strip()
    city = request.form.get('city')
    city = city.capitalize()
    api = month(state, city)
    rainfall = api[0]
    humidity = api[1]
    actualtemp = api[2]
    N = request.form.get('nitro')
    K = request.form.get('potas')
    P = request.form.get('phos')
    pH = request.form.get('pH')

    input_query = np.array([[N, P, K, actualtemp, humidity, pH, rainfall]])
    result = model.predict(input_query)[0]
    return jsonify({'crop': result})


@app.route('/rainfall',methods=['POST'])
def rainfall():
    rai = []

    num  = request.form.get('day')
    city = request.form.get('city')
    city = city.capitalize()
    url = 'https://api.weatherapi.com/v1/forecast.json?key=0c4e45c25eef409485265300230702&q=' + city + '&days=' + num
    res = requests.get(url)
    data = res.json()

    m = int(num)
    rain = {1195: "Heavy Rain", 1276: "Moderate or Heavy rain with Thunder", 1240: "Light rain shower",
            1243: "Moderate or Heavy rain shower", 1246: "Torrential rain shower", 1183: "Light rain"}
    if (m < 14):
        for i in range(0, m):
            curr = data['forecast']['forecastday'][i]['date']
            print(data['forecast']['forecastday'][i]['hour'][0]['condition']['text'])
            cd = data['forecast']['forecastday'][i]['hour'][0]['condition']['code']
            if cd == 1195 or cd == 1276 or cd == 1240 or cd == 1243 or cd == 1246 or cd == 1183:
                 rai.append(curr)


    else:  # executes when we have to find the weather for 14-300 days
        t = 0
        de = data['forecast']['forecastday'][0]['date']
        date = de
        date = date.split("-")
        date = [int(i) for i in date]
        y, mo, d = date[0], date[1], date[2]
        start_date = datetime.date(y, mo, d)
        for i in range(0, m):

            if i < 12:
                curr = data['forecast']['forecastday'][i]['date']
                cd = data['forecast']['forecastday'][i]['hour'][0]['condition']['code']
                if cd == 1195 or cd == 1276 or cd == 1240 or cd == 1243 or cd == 1246 or cd == 1183:
                    rai.append(curr)

            else:

                if t == 0:
                    delta = datetime.timedelta(days=14)
                    start_date += delta
                    delta = datetime.timedelta(days=1)

                    t = 1
                else:
                    delta = datetime.timedelta(days=1)
                    start_date += delta
                url1 = 'http://api.weatherapi.com/v1/future.json?key=0c4e45c25eef409485265300230702&q=' + city + '&dt=' + str(
                    start_date)
                res1 = requests.get(url1)
                data1 = res1.json()
                cd = data1['forecast']['forecastday'][0]['day']['condition']['code']  # to get the weather code

                if cd == 1195 or cd == 1276 or cd == 1240 or cd == 1243 or cd == 1246 or cd == 1183:
                    rai.append(start_date)
    return jsonify({'rainfall': rai})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
