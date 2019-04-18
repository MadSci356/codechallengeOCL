#!/usr/bin/python3


import argparse
import requests
import json
import sys

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

#constants and global vars
PFAPI_OK = 100 #valid search result status from API
MISS = "<UNKNOWN>" #value inplace of key:val pair missing from dictionary
data = {} #dictionary for holding data from reponse

#functions
"""
    Prints human readable text from the data dictionary of pet searches.
   data is assumed to have format:
   {  ...,
      "petfinder": {..., lastOffset: "...", pets: [], ...} }

   where each pet in the pets list has format:
    {...,
     age: "adult",
     media: {photos: [{url= "..."}, ...]},
     name: "whiskers",
     sex: "M/F",
     description: "..." }
    NOTE: dict assumed to be valid (ie petfinder->header->status-> = 100)

    Print format:
    Name: Name
        Age: age
        Sex: M/F
        Photo: url
        Description: wrapped with 70 words.
            new lines indented twice."""
def json_to_normal():

    #TODO: print search criteria used
    #TODO: summary of search
    pets = data["petfinder"]["pets"]
    for pet in pets:
        name = get_value(pet, "name")
        if (name != MISS) {#capitali
            name = name.capitalize()
        }
        #age
        #Sex
        #photo url
        #Desc


def get_value(pet, key):
    value = ""
    try:
        value = pet[key]
    except KeyError: #key missing
        value = MISS
    if len(value) == 0: #value is empty
        value = MISS
    return value

#----(1) Process arguments----#

#Description and help strings
desc = "Simple Pet Finder using Oak City Labs API"
animal_arg_help = "Animal type. eg: dog/cat/rabbit"
loc_arg_help = "Location to search. eg: Raleigh,NC/Charleston,SC"
json_arg_help = "Print out JSON results instead of normal output"

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

#getting from url
response = requests.get(url, params=query)

#error check on get (connection error)
if (response.status_code != requests.codes.ok):
    response.raise_for_status()

#error check on API returned data
data = json.loads(response.text) #dictionary
status = data["petfinder"]["header"]["status"]
code = int(status["code"])
if (code != PFAPI_OK): #error from API
    print(f'Err: {code} {status["message"]}')
    parser.parse_args("") #TODO: artificially inflict help message??
    sys.exit(1);


#----(3) printing the results----#
if (args.json): #raw json format
        print(data)
else:
    json_to_normal(data)
