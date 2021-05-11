import requests
import sys
import json
import time
import datetime
import os
from azure.storage.filedatalake import DataLakeFileClient, FileSystemClient, DataLakeDirectoryClient
from azure.core.exceptions import ResourceExistsError




def get_data_from_rmf(playlist_url):
    data_json = requests.get(playlist_url).json()
    data_json_as_string = json.dumps(data_json)
    return data_json_as_string

def get_data_from_zet(playlist_url):
    data = requests.get(playlist_url).text
    data_curated = str(data).replace("rdsData(","")[:-1]
    data_json = json.loads(str(data_curated)) 
    data_json_as_string = json.dumps(data_json)
    return data_json_as_string

def save_to_adls(connection_string, file_system, directory_path, file_name, data):
    file_system_client = FileSystemClient.from_connection_string(connection_string, file_system_name=file_system)
    directory_client = file_system_client.get_directory_client(directory_path)
    file_client = directory_client.create_file(file_name)
    file_client.append_data(data, 0, len(data))
    file_client.flush_data(len(data))




radios = {
        "zet": "https://rds.eurozet.pl/reader/var/radiozet.json",
        "rmf": "http://rmfon.pl/stacje/playlista_5.json.txt"
    }
sa_connection_string = "DefaultEndpointsProtocol=https;AccountName=sdsalearnsthnew;AccountKey=RJMELuc9ffZPf5D0gwcbxJp+hWTkQuW8lmWa1DRFSF59aDiatDsMJ6X/yC/dHZtB7kdGl3cJIrYry++6EnCb5g==;EndpointSuffix=core.windows.net"
sa_file_system = "learnsthnew"
sa_parent_directory_name = "raw"

if len(sys.argv) != 2: 
    sys.argv.append("rmf") 
    sys.argv.append(10) 
current_radio_name = sys.argv[1]
time_sleep = int(sys.argv[2])
current_radio_playlist = radios[current_radio_name]

# the code for different radios is different to get the json
# therefore we call a specif method for particular radio
if current_radio_name == "zet":
    current_radio_function = get_data_from_zet
elif current_radio_name == "rmf":
    current_radio_function = get_data_from_rmf

while True:
    try:
        current_data = current_radio_function(current_radio_playlist)
        current_sa_directory_path = f"{sa_parent_directory_name}/{current_radio_name}/{datetime.datetime.now().strftime(r'%Y/%m/%d/%H')}" 
        current_file_name = f"{current_radio_name}_{datetime.datetime.now().strftime(r'%Y%m%d_%H%M%S')}.json"
        save_to_adls(connection_string=sa_connection_string, 
                file_system=sa_file_system,
                directory_path=current_sa_directory_path,
                file_name=current_file_name,
                data=current_data)
        print (f"{current_sa_directory_path}/{current_file_name} has been created")
    except Exception as e:
        print (f"there was an error, but the script will continue\n: {str(e)}")

    time.sleep(time_sleep)
