import requests
import sys	
import configparser
import os

# Send the name of the song being played to a Google form
# Usage: python recordsong.py <name of song>

# set up a Google Form
# Set the URL (minus the last /viewform 

if len(sys.argv) < 2:
	sys.exit()

# Load in config.  Look for the config.ini in the same folder
# as this script
config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')

# Help from https://stackoverflow.com/a/55815520
url =  config['RecordSong']['form_url'] + "/formResponse"
form_data = {'entry.2022304067':sys.argv[1]}
r = requests.post(url, data=form_data)
print ("Google Form submit status: {}".format(r.status_code))
