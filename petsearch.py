#!/usr/bin/python3

# ----------PetSearch command line tool----------#
#
# petsearch is a command line tool to help
# search for pets of a given type and from a
# location.
#
# usage: petfinderSP.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]
#
# See comment on main function for basic process
# and Readme for the details.
#
# Author: Sayam Patel (sdpate11 AT ncsu.edu)
# Date created: Apr 17 2019
#
# ---------------------------------------------#


import argparse, requests, json
import sys
from textwrap import TextWrapper


class PetSearch:

    #----global constants and vars----#

    #valid search result status from API
    PFAPI_OK = 100
    #value inplace of key:val pair missing from dictionary
    MISS = "<UNKNOWN>"
    #number of characters for line wrap in pet description
    WRAP_TEXT = 70
    # default search count
    DEFAULT_COUNT = 25


    def __init__(self, type, location, print_json):
        self.type = type
        self.location = location
        self.print_json = print_json
        self.url = 'https://q93x2sq2y7.execute-api.us-east-1.amazonaws.com/staging/pet.find'
        self.searches = 0
        self.offset = 0
        self._end_search = False
         #making the query for the url
        self.query = {'output': 'full',
                    'offset': self.offset,
                    'animal': type,
                    'location': location}
        self.data = {}

    @property
    def end_search(self):
        """returns whether or search has ended
        (ie returned pets < DEFAULT_COUNT)"""
        return self._end_search

    @end_search.setter
    def end_search(self, bool_val):
        assert(isinstance(bool_val, bool));
        self._end_search = bool_val

    def perform_search(self):
        """Sets data, offset, and end_search field. Checks for error
            in requesting the search or in the returned API data"""
        #getting from url
        self.query["offset"] = self.offset
        response = requests.get(self.url, params=self.query)

        #error check on get (connection error)
        if (response.status_code != requests.codes.ok):
            response.raise_for_status()

        #error check on API returned data
        self.data = json.loads(response.text) #dictionary
        status = self.data["petfinder"]["header"]["status"]
        code = int(status["code"])
        if (code != self.PFAPI_OK): #error from API
            print(f'Err: {code} {status["message"]}')
            parser.parse_args(["-h"]) #extra help message
            sys.exit(1);

        #number of hits this search = offset of this search - last offset
        self.num_hits = int(self.data["petfinder"]["lastOffset"]) - self.offset
        if (self.num_hits < self.DEFAULT_COUNT):
            self.end_search = True

        #store offset from API
        self.offset = int(self.data["petfinder"]["lastOffset"])

    def get_output(self):
        if (self.print_json): #raw json format
            return str(self.data)
        else:
            self.json_to_normal()

    def json_to_normal(self):
        """Prints human readable text from the data dictionary of pet searches.
        data is assumed to have format:
        {  ..., "petfinder": {..., lastOffset: "...", pets: [], ...} }

        Fields from pets printed: Name, Age, Sex, Photo url, description

        NOTE: dict assumed to be valid (ie petfinder->header->status-> = 100)"""

        #search info and summary
        print(f"Searching for {self.type} in {self.location}")
        print(f"Found {self.searches} {self.type} in {self.location}")
        print("Pets:")
        pets = self.data["petfinder"]["pets"] #pets dict

        #keys to get: age, sex, media.photos[0].url, description
        for pet in pets: #each loop will gather info on a pet and print it
            #get all the relevant fields for a pet
            name = self.get_value(pet, ["name"])
            if (name != self.MISS): #capitalize
                name = name.capitalize()

            #getting age field
            age = self.get_value(pet, ["age"])
            #getting sex field
            sex = self.get_value(pet, ["sex"])

            #to get url: pet->media->[photos][0]->url
            photos = self.get_value(pet, ["media", "photos"] )
            url = self.MISS
            if (photos != self.MISS and photos != None): #checkin for valid photos
                url = self.get_value(photos[0], "url")

            #formatting description text
            description = self.get_value(pet, ["description"])
            #wrapping and formatting lines
            wrapper = TextWrapper(width=self.WRAP_TEXT, subsequent_indent='\t\t', \
            replace_whitespace=False)
            wrapped = "\n".join(wrapper.wrap(description))

            #printing output
            output = "Name: {} \n\t" + "Age: {} \n\t" + "Sex: {} \n\t" + \
                    "Photo: {}\n\t" + "Description: {}\n\t"
            print(output.format(name, age, sex, url, wrapped))


    def get_value(self, pet_dict, keys):
        """Looks for the value of a given keys in a nested dictionary.
        If key not found: catches KeyError and returns the default MISS string
        Also returns MISS if value for a key is null/None
        Ex: keys =  ["media", "photos"]
        returns: pet_dict["media"]["photos"]. Checking at each level for a valid
        value.

        pet_dict: dictonary to search
        keys: list of keys for the dictionary
        returns: string of the value if found, else return MISS string"""

        value = pet_dict
        for key in keys:
            try:
                value = value[key]
            except KeyError: #key missing
                return self.MISS
            #key exists but check if val is null or of len 0
            if (value == None or len(value) == 0):
                return self.MISS
        return value
#end class

def main():
    """usage: petfinderSP.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]

    Basic process (see Readme for details):
    1) Process arguments (uses argparse)
    2) Make PetSearch object to request API server
    if prompted by user (uses requests)
    3) Format and output results (either normal or json format)"""

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

    #----(2) Request the server----#

    #making PetSearch object from input
    ps = PetSearch(args.type, args.location, args.json)

    #loop for subsequent searches
    while (True):
        #searching on server
        ps.perform_search()

        #----(3) Printing output----#
        print(ps.get_output())

        #ask user to continue search
        if (not ps.end_search):
            user_input = ""
            user_input = input("There could be more pets out there! Look for more? (y/n)")
            while (user_input.lower() != "y" or user_input.lower() != "n"):
                user_input = input("Invalid input. Look for more pets? (y/n)")
            if (user_input.lower() == "n"):
                break
        else:
            print("No more results found.")



main()
