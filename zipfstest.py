#Necessary imports
import requests
import re
import pytesseract
from bs4 import BeautifulSoup
from collections import Counter
from langdetect import detect
from datetime import date
from PIL import Image
import matplotlib.pyplot as plt
import os
import time, stat
import PyPDF2
from requests.exceptions import MissingSchema, InvalidURL

global alphanumeric 
alphanumeric = "[^\w0-9 ]"

#ZipfsSite object that stores the url, hash, and the last modified date of the site or file (if it exists)
class ZipfSite:
    def __init__(self, url, hash, last_modified):

        self.url = url
        self.hash = hash
        self.last_modified = last_modified

    def __str__(self):
        return self.url


#Parsing function where a URL is passed as a parameter
def parseSite(url):
    #Requests the raw HTML text and assigns it to 'html'
    html = requests.get(url)
    #Using BeutifulSoul's HTML parser to parse/sieve through the raw HTML text
    if 'Last-Modified' in html.headers:
        #Making modified a global variable so generateChart can access it without doing a requests call again
        global modified
        modified = html.headers['Last-Modified']

    soup = BeautifulSoup(html.text, "html.parser")

    #Initialize a Counter object (a subclass of dict that provides the frequencies for each word)
    count = Counter()

    #Going through the soup 'html'
    for word in soup.findAll('html'):
        #Utilizes the re module's sub methods to clean up the words (made lowercase) by replacing the regex pattern with ""
        text = re.sub(alphanumeric, "", word.get_text().lower())
        #Checks to see if the word is in a particular language
        if (detect(text) == 'en'):
            #Inserts the word into count (Counter object)
            count.update(text.split(" "))

#Removing the key that is just a blank space
    del count['']
    #Returns the Counter object
    return count

#This function parses files instead of URL
def parseFile(file):

    #Getting the filename and extension by splitting text
    fileName, extension = os.path.splitext(file)

    #Getting the statistics of the given file
    fileStatsObject = os.stat(file)

    global modified

    #getting the global modified date
    modified = time.ctime(fileStatsObject[stat.ST_MTIME])

    hasDigits = re.compile('\d')

    count = Counter()
    
    #If the extension is a .txt, .doc, or docx file, proceed
    #with parsing in this manner
    if extension == '.txt' or extension == '.docx' or extension == '.doc':

        with open(file) as f:
            #Using a list comprehension to get the individual words, instead of lines of words
            word_list = [word for line in f for word in line.split()]

            for line in word_list:
                #Using regex to remove non-alphabet letters
                text = re.sub(alphanumeric, "", line.lower())

                if (bool(hasDigits.search(text)) == False and len(text) > 0):
                    #Inserts the word into count (Counter object)
                    count.update(text.split(" "))

    #In the case the file is a pdf
    elif extension == '.pdf':

        #This string will be used to store the extracted text from each page of the PDF
        stringBuilder = ''

        #Creating a PDF file object
        pdfFileObject = open(file, 'rb')

        #Creating a PDF reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObject)

        #For-Loop that'll go through all the pages of the PDF
        #so all words can be put into the Counter object
        for i in range(0, pdfReader.numPages):

            #Each individual page of the PDF
            pageObject = pdfReader.getPage(i)

            #The extracted text is put into the string variable created above
            stringBuilder += ''.join(pageObject.extractText())

        #Closing the PDF file object since we have no more use for it
        pdfFileObject.close()
        #For-Loop to get all the individual words of the PDF
        for line in stringBuilder.split():

            text = re.sub(alphanumeric, "", line.lower())

            if (bool(hasDigits.search(text)) == False and len(text) > 0):
                count.update(text.split(" "))

    #In the case an image containing text is passed through 
    elif extension == '.png' or extension == '.jpeg' or extension == '.jpg':
        #Python-tesseract is an optical character recognition (OCR) tool for python. 
        #It will recognize and “read” the text embedded in images.
        stringBuilder = pytesseract.image_to_string(Image.open(f'{file}'))

        for line in stringBuilder.split():

            text = re.sub(alphanumeric, "",
                line.lower())

            if(bool(hasDigits.search(text)) == False and len(text) > 0):
                count.update(text.split(" "))

    #redirect if count is empty (when Django phase begins)

    return count


#Function that takes URL as an argument and generates a chart from the Counter object returned by parseSite
def generateChart(url, ftype='url'):
    #if ftype is set to 'url', then we know the parameter being passed is a URL
    if ftype == 'url':
        #Try-Catch that'll redirect the user if the URL is invalid or missing a schema (i.e. https)
        try:
            word_count = parseSite(url)

        except (InvalidURL, MissingSchema):
            #We will redirect here
            return f'URL {url} is invalid'
    #In the case it's a File instead of a URL
    else:
        word_count = parseFile(url)

    #Converting the Counter object to a dictionary so that we can better use the keys and values
    #To make plot and scatter chart
    if len(word_count) >= 201:
        hash = dict(word_count.most_common(201))
    else:
        hash = dict(word_count.most_common(len(word_count)))

    #Calls this function to return a formatted string containing the similarity percentage of hash
    percent = percentageCount(hash)

    #If the url string has a normal schema, make url into a substring of itself
    if '//' in url:
        url = url[url.rindex('//') + 2:len(url)]

        if url[len(url) - 1] == '/':
            url = url[:-1]

    todayDate = date.today()
    #Making a line and scatter plot using hash's keys and values
    plt.xlim(0, 24)
    plt.plot(list(hash.keys()), list(hash.values()), color='k', linestyle='-.')
    plt.scatter(list(hash.keys()), list(hash.values()), color='r', marker='.')
    plt.title(f'Zipf\'s Results for \'{url}\' \n {todayDate}')
    plt.ylabel('Number of Occurances')
    plt.xlabel('Word Rank')
    plt.legend(['Zipf\'s line', 'Words'], loc='upper right')
    #plt.savefig(f'Zipf\'s Law for {url}')

    #Labeling the scatter points with the number of occurances for that particular word
    #enumerate is used so i can be a number (for the X, Y coordinates) and txt can be the values from
    #the 'hash' dictionary
    for i, txt in enumerate(list(hash.values())):
        plt.annotate(f' {txt} \n #{i+1}',
                     (list(hash.keys())[i], list(hash.values())[i]))

    zplot = plt
    zplot.show()

    #Formatting the percent properly with the '%' sign
    percent = f'{percent}%'

    #Checks if the modified variable actually exists
    if 'modified' in globals():
        objecty = ZipfSite(url, hash, modified)
    else:
        objecty = ZipfSite(url, hash, 'N/A')

    print(objecty.last_modified)

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

    #Iterating through the sorted top 200 words from the site
    #0(N) time algorithm that'll return the similarity percentage of the frequecies
    for i in range(0, len(zvalues) - 1):

        zdifference = (mostFreqWord / (2 + i))
        current = zvalues[1 + i]
        #This increments by 100 each time so we can compare how similar a perfect zipf's chart would be to the actual zipf's chart
        zipfPerfectPercent += 100

        #Calculates the percent difference between the ideal zipf's division (zdifference) and the division between the most frequent word/(2+i) and the current word (current)
        theDiff = ((zdifference / current) * 100)
        percentSum += theDiff

    #Rounding the final percent to 2 decimal points
    return round((percentSum / zipfPerfectPercent) * 100, 2)

print(generateChart(url='https://en.wikipedia.org/wiki/Albania', ftype='url'))

print(generateChart(url='great_gatsby.txt', ftype='file'))

print(generateChart(url='poem.jpeg', ftype = 'file'))