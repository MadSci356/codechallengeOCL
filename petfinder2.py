
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
        self.end_search = False
         #making the query for the url
        self.query = {'output': 'full',
                    'offset': self.offset,
                    'animal': type,
                    'location': location}
        self.data = {}

    def perform_search(self):
        """Sets data, offset, and end_search field. Checks for error
            in requesting the search or in the returned API data"""
        #getting from url
        response = requests.get(self.url, params=self.query)

        #error check on get (connection error)
        if (response.status_code != requests.codes.ok):
            response.raise_for_status()

        #error check on API returned data
        self.data = json.loads(response.text) #dictionary
        status = data["petfinder"]["header"]["status"]
        code = int(status["code"])
        if (code != PFAPI_OK): #error from API
            print(f'Err: {code} {status["message"]}')
            parser.parse_args(["-h"]) #extra help message
            sys.exit(1);

        #number of hits this search = offset of this search - last
        self.num_hits = int(data["petfinder"]["lastOffset"]) - self.offset
        if (self.num_hits < DEFAULT_COUNT):
            self.end_search = True

        #store offset from API
        self.offset = int(data["petfinder"]["lastOffset"])

    def get_output(self):
        if (self.json): #raw json format
            return str(self.data)
        else:
            self.json_to_normal()

    def json_to_normal(self):
        """Prints human readable text from the data dictionary of pet searches.
        data is assumed to have format:
        {  ..., "petfinder": {..., lastOffset: "...", pets: [], ...} }

        Fields printed: Name, Age, Sex, Photo url, description

        NOTE: dict assumed to be valid (ie petfinder->header->status-> = 100)"""

        #search info and summary
        print(f"Searching for {self.type} in {self.location}")

        print(f"Found {self.hits} {self.type} in {self.location}")
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

            #formatting description text
            description = get_value(pet, "description")
            #wrapping and formatting lines
            wrapper = TextWrapper(width=WRAP_TEXT, subsequent_indent='\t\t', \
            replace_whitespace=False)
            wrapped = "\n".join(wrapper.wrap(description))

            #printing output
            output = "Name: {} \n\t" + "Age: {} \n\t" + "Sex: {} \n\t" + \
                    "Photo: {}\n\t" + "Description: {}\n\t"
            print(output.format(name, age, sex, url, wrapped))


    def get_value(pet_dict, key):
        """Looks for the value of a given key in the dictionary.
        If key not found: catches KeyError and returns the default MISS string
        Returns MISS if value for a key is null/None
        pet_dict: dictonary to search
        key: lookup key for the dictionary
        returns: string of the value if found, else return MISS string"""

        value = ""
        try:
            value = pet_dict[key]
        except KeyError: #key missing
            return MISS

        #key exists but check if val is null or of len 0
        if (value == None or len(value) == 0):
            return MISS
        return value
def main():
