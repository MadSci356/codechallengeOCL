#!/usr/bin/python3


import argparse
import requests

"""
petfinderSP is a command line tool to help search for pets of a given type and
from a location.

usage: petfinderSP.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]

Basic process (see Readme for details):
1) Process arguments (uses argparse)
2) Request searches if prompted by user (uses requests)
3) Format and output results (either normal or json format)

Author: Sayam Patel (sdpate11 AT ncsu.edu)
Date created: Apr 17 2019
"""

#----(1) Process arguments----#

#----Description and help strings----#
desc = "Simple Pet Finder using Oak City Labs API"
animal_arg_help = "Animal type. eg: dog/cat/rabbit"
loc_arg_help = "Location to search. eg: Raleigh,NC/Charleston,SC"
json_arg_help = "Print out JSON results instead of normal output"
#----END strings----#

#building arg parse object
parser = argparse.ArgumentParser(description = desc)
parser.add_argument("-t", "--type", required=True, help=animal_arg_help)
parser.add_argument("-l", "--location", required=True, help=loc_arg_help)
parser.add_argument("-j", "--json", help=json_arg_help, action="store_true")
args = parser.parse_args()


#----(2) Request the search----#
url = 'https://q93x2sq2y7.execute-api.us-east-1.amazonaws.com/staging/pet.find'
#making the query for the url
query = {'output': 'full', 'animal': args.type, 'location': args.location}

#TODO: error check on get
response = requests.get(url, params=query) #getting from url

#----(3) printing the results----#

if (args.json): #raw json format
        print(response.text)
else:
    print("human readable text here.")
    #TODO: print human readable text
