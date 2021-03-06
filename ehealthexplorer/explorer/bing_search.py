import json
import urllib, urllib2
from keys import BING_API_KEY
from textstat.textstat import textstat
from textblob import TextBlob

def run_bing_query(search_terms, read_min,
                                 read_max,
                                 pol_min,
                                 pol_max,
                                 sub_min,
                                 sub_max):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'
    
    # Specify how many results we wish to be returned per page.
    # Offset specifies where in the results list to start from.
    # With results_per_page = 10 and offset = 11, this would start from page 2.
    results_per_page = 20
    offset = 0
    
    # Wrap quotes around our query terms as required by the Bing API.
    # The query we will then use is stored within variable query.
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)
    
    # Construct the latter part of our request's URL.
    # Sets the format of the response to JSON and sets other properties.
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)
        
    # Setup authenticiation with the Bing servers.
    # The username MUST be a blank string, and put in your API key!
    
    username = ''

    # Create a 'password manager' which handles authentication for us.
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)
    
    # Create our results list which we'll populate.
    results = []
    
    try:
        # Prepare for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Connect to the server and read the response generated.
        response = urllib2.urlopen(search_url).read()

        # Convert the string response to a Python dictionary object.
        json_response = json.loads(response)

        # Loop through each page returned, populating our results list.
        for result in json_response['d']['results']:
            summary = result['Description']
            blobSummary = TextBlob(summary)
            read = textstat.flesch_reading_ease(summary)
            pola = float("%.2f" % blobSummary.sentiment.polarity)
            subj = float("%.2f" % blobSummary.sentiment.subjectivity)
            
            
            
            if (read_min <= read <= read_max) and (pol_min <= pola <= pol_max) and (subj <= sub_max and subj >= sub_min):
                results.append({
                    'title':result['Title'],
                    'url':result['Url'],
                    'summary':result['Description'],
                    'read':read,
                    'pola':pola,
                    'subj':subj,
                    'source':'Bing'
                    })

    except urllib2.URLError as e:
        print "Error when querying the Bing API: ", e
        
    # Return the list of results to the calling function.
    return results