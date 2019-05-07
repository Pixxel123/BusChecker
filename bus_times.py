import requests
from datetime import datetime
from pprint import pprint
from types import SimpleNamespace
from transport_api_keys import app_id, app_key


def url_parameters():
    bus_url = f"https://transportapi.com/v3/uk/bus/stop/490001220D/live.json?app_id={app_id}&app_key={app_key}&group=route&nextbuses=no"
    response = requests.get(bus_url)
    full_data = response.json()
    response.raise_for_status()
    return full_data


def get_buses():
    bus_services = url_parameters()
    for buses in bus_services['departures']['R9']:
        try:
            bus = SimpleNamespace(  # initialises bus namespace
                    bus_eta = buses['expected_departure_time'])
        except KeyError:
            bus = SimpleNamespace(
                    bus_status = 'Test except')
        return bus.__dict__

bus_info = get_buses()

print(bus_info)

print(bus_info.get('bus_eta'))

time_end = bus_info.get('bus_eta')
time_now = datetime.now().strftime('%H:%M')

time_now_timeobject = datetime.strptime(time_now, '%H:%M')
time_end_timeobject = datetime.strptime(time_end, '%H:%M')
time_difference = time_end_timeobject - time_now_timeobject
print('Next bus: ' + str(int(time_difference.total_seconds()/60)) + ' mins')