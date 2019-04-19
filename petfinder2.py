
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
        self.end_search = False
         #making the query for the url
        self.query = {'output': 'full',
                    'offset': self.searches,
                    'animal': type,
                    'location': location}
        self.data = {}

    """Sets data, offset, and end_search field. Checks for error in requesting the search
        or in the returned API data"""
    def perform_search(self):
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

        #number of hits this search =
        num_hits = int(data["petfinder"]["lastOffset"]) - self.offset
        if (num_hits < DEFAULT_COUNT):
            self.end_search = True

        #set lastOffset
        self.offset = int(data["petfinder"]["lastOffset"])

    def print_output(self):
