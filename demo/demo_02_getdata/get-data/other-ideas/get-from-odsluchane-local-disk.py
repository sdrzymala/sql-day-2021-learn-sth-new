# import basic packages
import sys
import json
from time import sleep
from datetime import datetime, timedelta
from numpy import random

# import packages for webscrapping
import requests
from bs4 import BeautifulSoup





# set up default parameters
if len(sys.argv) != 4: 
    sys.argv.append("RMF FM") # radio name
    sys.argv.append(3) # number of days to parse
    sys.argv.append(str(datetime.today().strftime('%Y-%m-%d'))) # start date




# assign script arguments to variables
current_radio_name = sys.argv[1]
number_of_days = int(sys.argv[2])
start_date = datetime.strptime(sys.argv[3] , '%Y-%m-%d') 





hours = [
    {"hour_from" : "0",  "hour_to": "2"},
    {"hour_from" : "2",  "hour_to": "4"},
    {"hour_from" : "4",  "hour_to": "6"},
    {"hour_from" : "6",  "hour_to": "8"},
    {"hour_from" : "8",  "hour_to": "10"},
    {"hour_from" : "10", "hour_to": "12"},
    {"hour_from" : "12", "hour_to": "14"},
    {"hour_from" : "14", "hour_to": "16"},
    {"hour_from" : "16", "hour_to": "18"},
    {"hour_from" : "18", "hour_to": "20"},
    {"hour_from" : "20", "hour_to": "22"},
    {"hour_from" : "22", "hour_to": "0"},
]




# get radio list with names and id's from main page
page_radio_list = requests.get('https://www.odsluchane.eu/')
soup_radio_list = BeautifulSoup(page_radio_list.content, 'html.parser')
radio_list_combo = soup_radio_list.find("selektor")
radio_list = radio_list_combo.attrs[":stations-default"]
radio_list_json = json.loads(radio_list)
main_radio_stations = [radio_group["stations"] for radio_group in radio_list_json if radio_group["groupName"] == "Ogólnopolskie"][0]


# find the id of the current radio, saerch using the name, get first
radio_station = [radio for radio in main_radio_stations if radio["name"] == current_radio_name][0]

# prepare a placeholder list to keep the playlist data
playlist = []

# prepare a list of days (as index numbers) that needs to be parsed
# if we want to parse three days (n=3), then the list will be [1,2,3]
# then we will iterate through that list and substract the start date with each of those numbers
for n in range(1,number_of_days+1,1):

    # substract the next day to find a proper date
    current_day = start_date - timedelta(days=n)

    # iterate through each defined hours
    for hour in hours:

        try:

            # get html content from the page and find the playlist table
            #sleep(random.uniform(0, 1))
            search_url = f"https://www.odsluchane.eu/szukaj.php?r={radio_station['id']}&date={current_day.strftime('%d-%m-%Y')}&time_from={hour['hour_from']}&time_to={hour['hour_to']}"
            page_playlist = requests.get(search_url)
            soup_playlist = BeautifulSoup(page_playlist.content, 'html.parser')
            playlist_table = soup_playlist.find("tbody")
            
            # iterate through each song in the playlist
            songs_in_playlisy = playlist_table.find_all("tr")
            for song_in_playlist_row in songs_in_playlisy:

                # there is one header row for each hour, that will be skipped
                # the standard row with song details contains exactly 3 columns
                number_of_column = len(song_in_playlist_row.find_all("td"))
                if number_of_column == 3:

                    # get song name and artist
                    playlist_song = song_in_playlist_row.find_all("td")[1].text
                    playlist_song_artist = playlist_song.split("-")[0].strip()
                    playlist_song_name = playlist_song.split("-")[1].strip()

                    # get date and time of the song
                    playlist_song_time = song_in_playlist_row.find_all("td")[0].text
                    playlist_song_hour = int(playlist_song_time.split(":")[0].strip())
                    playlist_song_minutes = int(playlist_song_time.split(":")[1].strip())
                    playlist_song_datetime = datetime(current_day.year, current_day.month, current_day.day, playlist_song_hour, playlist_song_minutes)
                    
                    # create a dictionary with single song entry
                    playlist_single_entry = {}
                    playlist_single_entry["datetime"] = playlist_song_datetime
                    playlist_single_entry["artist"] = playlist_song_artist
                    playlist_single_entry["title"] = playlist_song_name

                    # add current entry to the entire list (playlist)
                    playlist.append(playlist_single_entry)

        except:
            # at this point we don't handle the exceptions, if there is any issue we will just log that information
            print (f"time: {datetime.now()}, radio: {radio_station['name']}, day: {current_day.strftime('%d-%m-%Y')}, hour: {hour['hour_from']} - {hour['hour_to']} - error")

    # report success on radio and day level
    print (f"time: {datetime.now()}, radio: {radio_station['name']}, day: {current_day.strftime('%d-%m-%Y')} - done")

    # save data on year basis - after parsing the first day of each month
    # or if that the last day of defined range, n == number of dats
    if n == number_of_days or (current_day.day == 1 and current_day.month == 1):

        # convert playlist to json
        data = json.dumps(playlist, indent=4, sort_keys=True, default=str)

        # specify file name and file path
        output_file_path = "./data/" + radio_station['name'].replace(' ', '').strip() + "_" + str(current_day.year) + ".json"

        # save data to file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(data)

        # once the current data are saved, clear the list
        playlist = []

# report script success
print ("done")