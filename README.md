# codechallengeOCL

## Pet Search

This script performs a search against a REST API to find pets of a certain type
and from a certain location.

`usage: petsearch.py [-h] -t TYPE -l LOCATION [-o OFFSET] [-j]
`

#### Work description

Initially this code was written procedurally (the old script in `/scripts`).
I decided to make it object oriented because it might be more flexible and easier to use.

#### Adding more formatted text
If more fields need to be parsed, `get_value()` can be used directly to access them.
If the values need modification (ex: capitalizing names), can write a separate function
that uses `get_value()`. The final formatted prints take place in `json_to_normal()`.

The OO approach was better for handling subsequent searches for pets if prompted by the user.

#### Subsequent searches
There are two options for this:

1. After a search, user will be prompted:

`> There could be more pets out there! Look for more? (y/n) ` to either continue or stop searching.
The prompt will reoccur after each search until either the returned number of searches is < 25 or
if the server returns an error status.

**Note**: Cannot use -j/--json option with this feature.

2. Use the `-o/--offset` to print the next 25 searches from the given offset.

Example: `/petsearch.py -l apex,nc -t cat -o 1500`
will print search results from 1500 to 1525 of cats in Apex, NC

#### Prompting and output redirection
If the output is redirected to a file with something like:
`./petsearch.py -l apex,nc -t cat > output.txt`

Only prompts to the user for more searches will be displayed in terminal. output.txt will have the formatted output.

#### Other
Runs in Python 3

Nonstandard libraries used: requests

#### Things I (re)learned during the project:
- Python doesn't yell at for you doing this: `["string", "another string", 598]`
- how good the requests library is
- so many pets!

#### Estimated time spent: 9-10 hours
