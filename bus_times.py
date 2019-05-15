from flask import Flask
from flask import render_template
from flask import request
import requests
from datetime import datetime
from transport_api_keys import app_id, app_key

app = Flask(__name__)


def url_parameters():
    atocode = request.args.get('atocode')
    route_to_search = request.args.get('route')
    bus_url = f"https://transportapi.com/v3/uk/bus/stop/{atocode}/live.json?app_id={app_id}&app_key={app_key}&group=route&nextbuses=no"
    response = requests.get(bus_url)
    full_data = response.json()
    response.raise_for_status()
    return full_data, route_to_search


def get_location():
    bus_location = url_parameters()[0]
    bus_info = []
    bus_stop = bus_location['name']
    bus_info.append(bus_stop)
    return bus_info


def get_services():
    bus_services = url_parameters()[0]
    route_to_search = url_parameters()[1]
    bus_service_departures = []  # initialises empty list of departure times
    for service in bus_services['departures'][route_to_search]:
        time_end = service['best_departure_estimate']  # sets departure estimate to variable for time comparison
        time_now = datetime.now().strftime('%H:%M')  # gets time now in hour and minute format
        time_end_timeobject = datetime.strptime(time_end, '%H:%M')
        time_now_timeobject = datetime.strptime(time_now, '%H:%M')  # creates timeobject for end time to allow comparitive operations
        time_difference = time_end_timeobject - time_now_timeobject  # time difference is TIME_END - TIME_nOW
        time_difference_minutes = int(time_difference.total_seconds() / 60)  # converts time difference to minutes
        if time_difference_minutes < 1:  # if less than a minute
            bus_service_departures.append(str('due'))  # due message for buses almost arriving
        else:
            bus_service_departures.append(f'{time_difference_minutes} mins')  # minutes to arrival
    return bus_service_departures  # return list of departures


def shortenend_services():  # function to only grab the next service and after, instead of all
    service_departures = get_services()  # sets bus_service_departures to variable
    first_services = service_departures[:2]  # gets 0 and 1 values from bus_service_departures
    return first_services  # returns services


def location_info():
    bus_location_info = get_location()[0]
    return bus_location_info


def formatted_bus_times():
    formatted_times = ', '.join(shortenend_services())
    return formatted_times


@app.route('/')
@app.route('/home')
def home_page():
    string = 'Hello World! Flask is running!'
    return string


@app.route("/getbus", methods=["GET"])
def main_page():
    for item in url_parameters():
        get_location()
        get_services()
    return render_template('bus_page.html', bus_info=location_info(), formatted_times=formatted_bus_times())


if __name__ == '__main__':
    app.run()
