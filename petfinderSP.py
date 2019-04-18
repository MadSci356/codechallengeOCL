#!/usr/bin/python3


import argparse, requests, json
import sys
from textwrap import TextWrapper


"""
petfinderSP is a command line tool to help search for pets of a given type and
from a location.

usage: petfinderSP.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]

See comment on main function for basic process and Readme for the details.

Author: Sayam Patel (sdpate11 AT ncsu.edu)
Date created: Apr 17 2019
"""

#----global constants and vars----#

#valid search result status from API
PFAPI_OK = 100

#value inplace of key:val pair missing from dictionary
MISS = "<UNKNOWN>"
#number of characters for line wrap in pet description
WRAP_TEXT = 70

#searches
count = 0


#----functions----#
"""
    Prints human readable text from the data dictionary of pet searches.
   data is assumed to have format:
   {  ...,
      "petfinder": {..., lastOffset: "...", pets: [], ...} }

   where each pet in the pets list has format:
    {...,
     age: "adult",
     media: {photos: [{url:"..."}, ...]},
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
            new lines indented twice.
    @param data dictionary from json output of """
def json_to_normal(data, args):
    #search info and summary
    print(f"Searching for {args.type} in {args.location}")
    global count
    count = int(data["petfinder"]["lastOffset"]) - count
    print(f"Found {count} {args.type} in {args.location}")
    print("Pets:")
    pets = data["petfinder"]["pets"]
    #keys to get: age, sex, media.photos.url, description
    for pet in pets:
        #get all the relevant fields for a pet
        name = get_value(pet, "name")
        if (name != MISS): #capitalize
            name = name.capitalize()

        #gettig rest of fields
        age = get_value(pet, "age")
        sex = get_value(pet, "sex")

        #to get url: pet->media->photos->url
        media = get_value(pet, "media")
        #check if media is valid
        photos = []
        url = MISS
        if (media != MISS and media != None):
            photos = get_value(media, "photos")
            #check photos is valid
            if (photos != MISS and photos != None):
                url = get_value(photos[0], "url")


        description = get_value(pet, "description")
        #wrapping and formatting lines
        wrapper = TextWrapper(width=WRAP_TEXT, subsequent_indent='\t\t', \
        replace_whitespace=False)
        wrapped = "\n".join(wrapper.wrap(description))

        #printing output
        output = "Name: {} \n\t" + "Age: {} \n\t" + "Sex: {} \n\t" + \
                "Photo: {}\n\t" + "Description: {}\n\t"
        print(output.format(name, age, sex, url, wrapped))

"""
    Looks for the value of a given key in the dictionary.
    If key not found: catches KeyError and returns the default MISS string
    Returns MISS if value for a key is null/None

    @param pet_dict dictonary to search
    @param key lookup key for the dictionary
    @return string of the value if found, else return MISS string"""
def get_value(pet_dict, key):
    value = ""
    try:
        value = pet_dict[key]
    except KeyError: #key missing
        return MISS

    #key exists but check if val is null or of len 0
    if (value == None or len(value) == 0):
        return MISS
    return value

"""
    usage: petfinderSP.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]

    Basic process (see Readme for details):
    1) Process arguments (uses argparse)
    2) Request searches if prompted by user (uses requests)
    3) Format and output results (either normal or json format)"""
def main():
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
        parser.parse_args(["-h"]) #extra help message
        sys.exit(1);


    #----(3) printing the results----#
    if (args.json): #raw json format
            print(data)
    else:
        json_to_normal(data, args)


main()
