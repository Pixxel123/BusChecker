from flask import Flask
from flask import render_template
from flask import request
import requests
from datetime import datetime
from transport_api_keys import app_id, app_key

app = Flask(__name__)


def bus_url_parameters():
    atocode = request.args.get('atocode')
    route_to_search = request.args.get('route')
    bus_url = f"https://transportapi.com/v3/uk/bus/stop/{atocode}/live.json?app_id={app_id}&app_key={app_key}&group=route&nextbuses=no"
    response = requests.get(bus_url)
    full_data = response.json()
    response.raise_for_status()
    return full_data, route_to_search  # bus_url_parameters()[0] = full_data, bus_url_parameters()[1] = route_to_search


def bus_get_location():
    bus_location = bus_url_parameters()[0]
    route_to_search = bus_url_parameters()[1]
    bus_info = []  # initialises empty list
    bus_stop = bus_location['stop_name']  # gets bus stop name
    bus_line = bus_location['departures'][route_to_search][0]['line']  # finds route name in first instance in json
    bus_destination = bus_location['departures'][route_to_search][0]['direction']
    bus_info.extend((bus_line, bus_stop, bus_destination))  # extend instead of append allows adding two values to list
    bus_route_name = bus_info[0]  # first value in list
    bus_stop_name = bus_info[1]  # second value in list
    bus_destination = bus_info[2]  # third value in list
    return bus_route_name, bus_stop_name, bus_destination


def bus_get_services():
    bus_services = bus_url_parameters()[0]
    route_to_search = bus_url_parameters()[1]
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
            bus_service_departures.append(f"{time_difference_minutes} min{'s' if time_difference_minutes > 1 else ''}")  # mins if more than 1 minute, mins if greater
        first_services = bus_service_departures[:2]  # gets 0 and 1 values from bus_service_departures to only show the next and after, instead of all
        formatted_times = ', '.join(first_services)  # adds commas between each time
    return formatted_times


@app.route('/')
@app.route('/home')
def home_page():
    string = 'Hello World! Flask is running!'
    return string


@app.route("/getbus", methods=["GET"])
def main_page():
    for item in bus_url_parameters():
        bus_get_location()
        bus_get_services()
    return render_template('bus_page.html', bus_name=bus_get_location()[0], bus_stop_info=bus_get_location()[1], bus_direction=bus_get_location()[2], formatted_times=bus_get_services())


if __name__ == '__main__':
    app.run()
