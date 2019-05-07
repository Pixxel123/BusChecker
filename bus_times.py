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

def get_location():
    bus_location = url_parameters()
    bus_name = SimpleNamespace(
            bus_stop_name = bus_location['name'])
    return bus_name.__dict__
    
def get_buses():
    bus_services = url_parameters()
    for buses in bus_services['departures']['R9']:
        try:
            bus = SimpleNamespace(  # initialises bus namespace
                    bus_eta = buses['best_departure_estimate'])  # aimed or expected departure time, whichever is available. Live data (expected) is taken as the best if both are available
        except KeyError:
            bus = SimpleNamespace(
                    bus_status = 'Test except')
        return bus.__dict__

bus_info = get_buses()

bus_location_info = get_location()

print(bus_location_info)

print(bus_info)

print(bus_info.get('bus_eta'))

time_end = bus_info.get('bus_eta')
time_now = datetime.now().strftime('%H:%M')

time_now_timeobject = datetime.strptime(time_now, '%H:%M')
time_end_timeobject = datetime.strptime(time_end, '%H:%M')
time_difference = time_end_timeobject - time_now_timeobject
time_difference_minutes = int(time_difference.total_seconds()/60)

if  time_difference_minutes <= 1:
    print('Next bus: due')
else:
    print('Next bus: ' + str(time_difference_minutes) + ' mins')