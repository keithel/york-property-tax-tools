# york-property-tax-tools
A set of python tools to fetch and extract property tax bills for York, Maine, USA


## Running
pip install -r requirements.txt

```
python york_prop_tax.py [OPTION]... [COMMAND]
OPTIONS:
   -y, --year=TAX_YEAR          Tax year to work with
   -s, --search=SEARCH_QUERY    A search query used fo find the desired property
                                tax bill page.

COMMANDS:
   url  Print the URL to the current tax year's taxes. url is the default
        command if unspecified.
   get  Fetch and output property taxes for the year given (or current year if
        not specified). If no name or address specified, will output all
        property tax bills.
```
