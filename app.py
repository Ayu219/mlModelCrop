from flask import Flask, request, jsonify
import pickle
import numpy as np
from pyowm import OWM
import pandas as pd
from datetime import date

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
    K = request.form.get('phos')
    P = request.form.get('potas')
    pH = request.form.get('pH')

    input_query = np.array([[N, P, K, actualtemp, humidity, pH, rainfall]])
    result = model.predict(input_query)[0]
    return jsonify({'crop': result})


if __name__ == '__main__':
    app.run(debug=True)
