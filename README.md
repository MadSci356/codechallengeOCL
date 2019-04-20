# codechallengeOCL

## Pet Search

This script performs a search against a REST API to find pets of a certain type
and from a certain location.

`usage: petsearch.py [-h] --type ANIMAL_TYPE --location LOCATION [--json]`

#### Work description

Initially this code was written procedurally. (the old script is in the scripts folder)
I decided to make it object oriented because it might more flexible and easier to use.

#### Adding more formatted text
If more fields need to be parsed, `get_value()` can be used directly to access them.
If the values need modification (ex: capitalizing names), can write a separate function
that uses `get_value()`. The final formatted prints take place in `json_to_normal()`.

The OO approach was better for handling subsequent searches for pets if prompted by the user.

#### Subsequent searches
When a search is complete, the user is prompted:
`There could be more pets out there! Look for more? (y/n)` to either continue or stop searching.
The prompt will keep occurring until either the returned number of searches is < 25 or
if the server returns a error status.

#### Issue with prompting and output redirection
If the output is redirected to a file with something like:
`./petsearch.py -l apex,nc -t cat > output.txt`

Here, the prompts to the user will be redirected as well. So once a search finishes,
terminal will be waiting for a user response for subsequent searches but won't
display the prompt to enter "y/n". I don't know how to fix that quite yet,
but will modify it I find/think of something.

**EDIT**: fixed this issue by printing the prompts to `stderr` stream.

#### Other
Runs in Python 3

Nonstandard libraries used: requests

#### Things I (re)learned during the project:
- Python doesn't yell at for you doing this: `["string", "another string", 598]`
- how good the requests library is
- so many pets!

#### Estimated time spent: 10 hours
