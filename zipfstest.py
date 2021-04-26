#Necessary imports
import requests
import re
from bs4 import BeautifulSoup
from collections import Counter
from langdetect import detect
import matplotlib.pyplot as plt
import math
from requests.exceptions import MissingSchema, InvalidURL
import pandas as pd

#Parsing function where a URL is passed as a parameter
def parseSite(url):
    #Requests the raw HTML text and assigns it to 'html'
    html = requests.get(url).text
    #Using BeutifulSoul's HTML parser to parse/sieve through the raw HTML text
    soup = BeautifulSoup(html, "html.parser")

    #Initialize a Counter object (a subclass of dict that provides the frequencies for each word)
    count = Counter()

    #Going through the soup 'html'
    for word in soup.findAll('html'):
        #Utilizes the re module's sub methods to clean up the words (made lowercase) by replacing the regex pattern with ""  
        text = re.sub("[^\w0-9 ]", "",
        word.get_text().lower())
    
		#Checks to see if the word is in a particular language
        if detect(text) == 'es':
          #Inserts the word into count (Counter object)
          count.update(text.split(" "))

	#Removing the key that is just a blank space	  
    del count['']
    
    #Returns the Counter object
    return count

#Function that takes URL as an argument and generates a chart from the Counter object returned by parseSite
def generateChart(url):
    #Try-Catch that'll redirect the user if the URL is invalid or missing a schema (i.e. https)
    try:
        word_count = parseSite(url)

    except (InvalidURL, MissingSchema):
        #We will redirect here
        return f'URL {url} is invalid'

    #Converting the Counter object to a dictionary so that we can better use the keys and values
    #To make plot and scatter chart
    hash = dict(word_count.most_common(15))

    #Calls this  function to return a formatted string containing the similarity percentage of hash
    percent = percentageCount(hash)

    #If the url string has a normal schema, make url into a substring of itself
    if '//' in url:
        url = url[url.rindex('//') + 2 : len(url)]

    #Making a line and scatter plot using hash's keys and values
    plt.plot(list(hash.keys()),list(hash.values()), color = 'k', linestyle = '-.')
    plt.scatter(list(hash.keys()),list(hash.values()), color = 'r', marker = '.')
    plt.title(f'Zipf\'s Results for \'{url}\'')
    plt.ylabel('Number of Occurances')
    plt.xlabel('Word Rank')
    plt.legend(['Zipf\'s line', 'Words'], loc= 'upper right')
    #plt.savefig(f'Zipf\'s Law for {url}')

    #Labeling the scatter points with the number of occurances for that particular word
    #enumerate is used so i can be a number (for the X, Y coordinates) and txt can be the values from
    #the 'hash' dictionary
    for i, txt in enumerate(list(hash.values())):
        plt.annotate(f' {txt} \n #{i+1}', (list(hash.keys())[i], list(hash.values())[i]))

    zplot = plt
    
    zplot.show()
    
    #Formatting the percent properly with the '%' sign
    percent = f'{percent}%'

    return percent

#Function that'll calculate a percentage on the similarity to a pure zipf's chart
def percentageCount(hash):
    #Setting zvalues to the hash values converted to a list
    zvalues = list(hash.values())
    #Getting the most frequent word
    mostFreqWord = zvalues[0]

    #These will be used when returning the finals percentage
    percentSum = 0
    zipfPerfectPercent = 0

    #Iterating through the sorted top 15 words from the site
    #0(N) time algorithm that'll return the similarity percentage of the frequecies
    for i in range(0, len(zvalues) - 1):
        
        zdifference = (mostFreqWord // (2 + i))

        curr = math.floor((zvalues[1 + i] / mostFreqWord) * 100)

        #This increments by 100 each time so we can compare how similar the word freqs
        #in the 'hash' are to the perfect zipf's chart
        zipfPerfectPercent += 100

        #Calculates the percent difference between the ideal zipf's division (zdifference) and the division 
        #between the most frequent word and the current word (curr)
        
        if(curr < zdifference):
            theDiff = (100 - (abs(curr - zdifference) / zdifference) * 100.0)
            percentSum += theDiff

        elif (zdifference < curr):
           theDiff = (100 - (abs(zdifference - curr) / curr) * 100.0)
           percentSum += theDiff

        else:
            #100% match so percentSum is incremented by 100 in tandem with zipfPerfectPercent
            percentSum += 100

    #Rounding the final percent to 2 decimal points
    return round(((percentSum / zipfPerfectPercent) * 100), 2)



print(generateChart(url = 'https://elpais.com/'))

