from flask import Flask
from flask import render_template
from flask import request
import requests
import requests_cache
from datetime import datetime
from transport_api_keys import app_id, app_key

app = Flask(__name__)

requests_cache.install_cache('bus_cache', backend='sqlite', expire_after=120)  


def bus_url_parameters():
    atocode = request.args.get('atocode')
    route_to_search = request.args.get('route')
    bus_url = f"https://transportapi.com/v3/uk/bus/stop/{atocode}/live.json?app_id={app_id}&app_key={app_key}&group=route&nextbuses=no"
    response = requests.get(bus_url)
    full_data = response.json()
    response.raise_for_status()
    return full_data, route_to_search  # bus_url_parameters()[0] = full_data, bus_url_parameters()[1] = route_to_search


def get_location():
    bus_location = bus_url_parameters()[0]  # full_data
    bus_info = []
    bus_stop = bus_location['name']  # name in full_data json
    bus_info.append(bus_stop)
    return bus_info


def bus_get_services(routes_lookup):  # routes_lookup for use of routes in for loop to get multiple buses
    bus_services = bus_url_parameters()[0]
    bus_service_departures = []  # initialises empty list of departure times
    for service in bus_services['departures'][routes_lookup]:
        time_end = service['best_departure_estimate']  # sets departure estimate to variable for time comparison
        time_now = datetime.now().strftime('%H:%M')  # gets time now in hour and minute format
        time_end_timeobject = datetime.strptime(time_end, '%H:%M')  # creates timeobject for end time to allow comparitive operations
        time_now_timeobject = datetime.strptime(time_now, '%H:%M')
        time_difference = time_end_timeobject - time_now_timeobject  # time difference is TIME_END - TIME_nOW
        time_difference_minutes = int(time_difference.total_seconds() / 60)  # converts time difference to minutes
        if time_difference_minutes < 1:  # if less than a minute
            bus_service_departures.append(str('due'))  # due message for buses almost arriving
        else:
            bus_service_departures.append(f"{time_difference_minutes} min{'s' if time_difference_minutes > 1 else ''}")  # mins if more than 1 minute, min if 1 min
        first_services = bus_service_departures[:2]  # gets 0 and 1 values from bus_service_departures to only show the next and after, instead of all
        formatted_times = ', '.join(first_services)  # adds commas between each time
    return bus_service_departures, formatted_times  # bus_get_services(routes_lookup)[0] = bus_service_departures, bus_get_services(routes_lookup)[1] = formatted_times


def get_multiple_buses():
    split_route = bus_url_parameters()[1].split(',')  # splits bus_routes list by comma
    try:
        bus_time_info = []  # initialize empty list
        for routes in split_route:  # for each route
            bus_get_services(routes)
            bus_time_info.append(f'{routes} -> {bus_get_services(routes)[1]}')  # prints route and corresponding times
    except KeyError:  # if route info is not available yet, prevent error
        bus_time_info  # don't add anything to list if info not available
    return bus_time_info


@app.route("/getbus", methods=["GET"])
def bus_main_page():
    for item in bus_url_parameters():
        get_multiple_buses()
    return render_template('bus_page.html', bus_stop_name=get_location()[0], bus_route_info=get_multiple_buses())


if __name__ == '__main__':
    app.run()