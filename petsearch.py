#!/usr/bin/python3

# ----------PetSearch command line tool----------#
#
# petsearch is a command line tool to help
# search for pets of a given type and from a
# location.
#
# usage: petsearch.py [-h] -t TYPE -l LOCATION [-o OFFSET] [-j]

#
# See docstring on main function for basic process
# and project Readme for more details.
#
# Author: Sayam Patel (sdpate11 AT ncsu.edu)
# Date created: Apr 18 2019
#
# ----------------------------------------------#


import argparse, requests, json
import sys
import textwrap


class PetSearch:
    """PetSearch class is used to help manage formatting and printing of
        petfinder API search results. The task of parsing from JSON dictionary
        to human readable is broken down with the functions in this class.

        Stores attributes that help perform subsequent searches on a criteria
        after the initial (by default 25) search.

        In a production level code the constants and functions here would be
        private (prefixed with _) and tested with formal test unit cases.

        Further functions can be added for more printed output for a pet search.
        See get_output().
        """

    #----constants----#

    #valid search result status from API
    PFAPI_OK = 100
    #value inplace of key:val pair missing from dictionary
    MISS = "<UNKNOWN>"
    #number of characters for line wrap in pet description
    WRAP_TEXT = 70
    # default search count
    DEFAULT_COUNT = 25


    def __init__(self, type, location, use_json, offset=0,):
        """Initializes the PetSearch object with options and search criteria
            from the user. The user input is parsed separetely in main
            type: type of animal to search for cat/rabbit/dog
            location: where to look for a pet
            use_json: should the search results be outputted in raw JSON
            offset: setting the offset param in request
            format"""
        self.type = type
        self.location = location
        self.use_json = use_json
        self.url = 'https://q93x2sq2y7.execute-api.us-east-1.amazonaws.com/staging/pet.find'
        self.searches = 0 #num total searches (tracking if more done)
        self.offset = offset #storing prev offset
        self.end_search = False #false initially
         #making the query for the url
        self.query = {"output": "full",
                    "offset": self.offset,
                    "animal": self.type,
                    "location": self.location}
        self.response = "" #Response object from requests from server
        self.data = {} #dictionary of response

    def perform_search(self):
        """Requests the server for a search. Updates data, offset, and end_search
        fields based on the current search. Checks for error in requesting
        the search or in the returned API data.
        returns: True on a successful search, False otherwise"""
        #setting up query with the previous offset (initially 0)
        self.query["offset"] = self.offset

        #getting from server
        self.response = requests.get(self.url, params=self.query)
        #error check on get (connection error)
        if (self.response.status_code != requests.codes.ok):
            self.response.raise_for_status()

        #error check on API returned data

        self.data = json.loads(self.response.text) #dictionary

        #error code at: data.petfinder.header.status.code
        status = self.data["petfinder"]["header"]["status"]
        code = int(status["code"])
        if (code != self.PFAPI_OK): #error from API
            sys.stderr.write(f'API Error: {code} {status["message"]}\n')
            return False #bad search

        #number of hits this search = offset of this search - last offset
        self.searches = int(self.data["petfinder"]["lastOffset"]) - self.offset
        if (self.searches < self.DEFAULT_COUNT):
            self.end_search = True

        #store offset from API
        self.offset = int(self.data["petfinder"]["lastOffset"])

        return True #search done

    def get_output(self):
        """Prints gets search results either in JSON or normal format depending
        on use_json field """
        if (self.use_json):
            print(self.response.text) #raw json format
        else:
            self.json_to_normal()

    def json_to_normal(self):
        """Prints human readable text from the data dictionary of pet searches.
        data is assumed to have format:
        {  ..., "petfinder": {..., lastOffset: "...", pets: [], ...} }

        Fields from pets printed: Name, Age, Sex, Photo url, description

        NOTE: dict assumed to be valid
        (ie petfinder->header->status->code = 100)"""

        #search info and summary print
        print(f"Searching for {self.type}s in {self.location}")
        print(f"Found {self.searches} {self.type}s in {self.location}")
        print("Pets:")
        pets = self.data["petfinder"]["pets"] #pets dict

        #keys to get: age, sex, media.photos[0].url, description
        for pet in pets: #each loop will gather info on a pet and print it
            #get all the relevant fields for a pet
            name = self.get_pet_name(pet)
            age = self.get_value(pet, ["age"])
            sex = self.get_value(pet, ["sex"])
            url = self.get_value(pet, ["media", "photos", 0, "url"] )
            wrapped = self.get_pet_description(pet)

            #printing output
            print(f"Name: {name}")
            print(f"\tAge: {age}")
            print(f"\tSex: {sex}")
            print(f"\tPhoto: {url}")
            print(f"\tDescription: {wrapped}\n")


    def get_pet_description(self, pet):
        """getting description of a pet from data. Wrapping the lines with
            WRAP_TEXT
            pet: pet dictionary
            returns: string of wrapped description"""

        #formatting description text
        description = self.get_value(pet, ["description"])
        #wrapping and formatting lines
        wrapped_text = textwrap.fill(description, width=self.WRAP_TEXT, \
                    replace_whitespace=False)
        indented_wrapped_text = wrapped_text.replace('\n', "\n\t\t")
        return indented_wrapped_text

    def get_pet_name(self, pet):
        """Returns capitalized name of the pet. If none found, MISS string"""
        name = self.get_value(pet, ["name"])
        if (name != self.MISS): #capitalize
             return name.capitalize()
        return name

    def get_value(self, pet_dict, keys):
        """Looks for the value of a given keys in a nested dictionary.
        If key not found: catches KeyError and returns the default MISS string
        Also returns MISS if value for a key is null/None
        Ex: keys =  ["media", "photos", 0]
        returns: pet_dict["media"]["photos"][0]. Checking at each level
        for a valid value.

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
    """
    usage: petsearch.py [-h] -t TYPE -l LOCATION [-o OFFSET] [-j]


    Basic process:
    1) Process arguments (uses argparse)
    2) Make PetSearch object to request API server (uses requests)
    3) Format and output results (either normal or json format)
    4) If json format not used, prompt user for further searches"""

    #----(1) Process arguments----#
    #Description and help strings
    desc = "Simple Pet Finder using Oak City Labs API"
    animal_help = "Animal type. eg: dog/cat/rabbit"
    loc_help = "Location to search. eg: Raleigh,NC/Charleston,SC"
    json_help = "Print out JSON results instead of normal output"
    offset_help = "offset. sets this number as the offset for the search"
    more_search = "There could be more pets out there! Look for more? (y/n) "
    invalid_more_search = "Invalid input. Search for more pets? (y/n)"

    #building arg parse object
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument("-t", "--type", required=True, help=animal_help)
    parser.add_argument("-l", "--location", required=True, help=loc_help)
    parser.add_argument("-o", "--offset", help=offset_help, type=int, default=0)
    parser.add_argument("-j", "--json", help=json_help, action="store_true")
    args = parser.parse_args()

    #----(2) Request the server----#

    #making PetSearch object from user input
    ps = PetSearch(args.type, args.location, args.json, args.offset)

    #loop for subsequent searches
    while (True):
        #searching on server and checking for error
        if (not ps.perform_search()):
            parser.print_help(sys.stderr) #extra help message upon error
            sys.exit(1);
        #----(3) Printing output----#
        ps.get_output()
        #----(4) prompting user for further searches---#
        #prompt only if there are more to search and json opt not used
        if ((not ps.end_search) and (not ps.use_json)):
            sys.stderr.write(f"Searches done (lastOffset): {ps.offset}\n")
            sys.stderr.write(more_search) #prompting user without stdout
            user_input = input()
            while (user_input not in ['y', 'n']): #invalid input from user
                sys.stderr.write(invalid_more_search)
                user_input = input()
            if (user_input == 'n'): #user says no
                break
        else: #no more searches
            sys.stderr.write("No more results found.\n")
            break

main()
