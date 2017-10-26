
# coding: utf-8

# In[39]:


from bs4 import BeautifulSoup
import requests
import re

# Returns an array of links to all of the indexed pages on the inspection reports website that contain restaurants.
def getRestaurantPages():
    database = requests.get('http://il.healthinspections.us/champaign/search.cfm?searchType=letter&srchLetter=').text
    soup = BeautifulSoup(database, 'html5lib')
    links = soup.find_all('a')
    newLinks = []
    for i in range(len(links)):
        links[i] = links[i].get('href')
    for i in range(len(links) - 1):
        # The only links that lead to the pages we want to scrape begin with "search"
        if links[i][0:6] == 'search':
            newLinks.append('http://il.healthinspections.us/champaign/' + links[i])
    return newLinks

# Takes a link from the array described above, and for each restaurant
# on that page, returns an array of arrays, each of which contains
# the restaurant's name, address, and the link to its page on the site.
def getPageInfo(link):
    database = requests.get(link).text
    soup = BeautifulSoup(database, 'html5lib')
    # All of the restaurants on a page are stored in a table.
    tableOfPlaces = soup.find('table')
    # All of the names occur within bold tags.
    tableOfNames = tableOfPlaces.find_all('b')
    for i in range(len(tableOfNames)):
        tableOfNames[i] = tableOfNames[i].text
    # All of the addresses occur within a "div" tag.
    tableOfAddrs = tableOfPlaces.find_all('div')
    for i in range(len(tableOfAddrs)):
        tableOfAddrs[i] = tableOfAddrs[i].text
    # All of the links occur within an "a" tag.
    tableOfLinks = tableOfPlaces.find_all('a')
    cleanLinks = []
    for i in range(len(tableOfLinks)):
        tableOfLinks[i] = tableOfLinks[i].get('href')
        # All of the links to a restaurant begin with "estab".
        if tableOfLinks[i][0:5] == 'estab':
            cleanLinks.append(tableOfLinks[i])
    # There is always one bold-tagged text element at the beginning and at the end of the
    # array that isn't a restaurant name.
    cleanNames = tableOfNames[1:len(tableOfNames) - 1]
    returnArray = []
    for i in range(len(cleanLinks)):
        # We append the link we would like to go to for each restaurant, as opposed to the
        # link stub that the page contains.
        returnArray.append([cleanNames[i], tableOfAddrs[i], 'http://il.healthinspections.us/champaign/'
                            + cleanLinks[i]])
    return returnArray

# Takes a link to the page containing an inspection report for a restaurant, and returns
# a dictionary with important info about that particular report.
def getReportInfo(reportLink):
    report = requests.get(reportLink).text
    soup = BeautifulSoup(report, 'html5lib')
    # Almost all data associated with the report, including
    # the data we want to scrape, occurs within "td" tags.
    test = soup.find_all('td')
    # Tells whether we want to store a score value in score1.
    check = True
    # Tells whether we want to store the next value as the date.
    checkDate = False
    # Empty string in which we will store the date when we find it.
    date = ''
    # Empty string for the raw score on the inspection report.
    score1 = ''
    # Empty string for the adjusted score on the inspection report.
    score2 = ''
    # Empty string for a representation of the number of critical violations.
    critical = ''
    # Empty string for a representation of the number of repeated violations.
    repeats = ''
    for element in test:
        if checkDate:
            rawText = element.text
            # The date occurs at the end of this string, and has length 8.
            rawText = rawText[len(rawText) - 8:len(rawText)]
            date = rawText
            # Once we find the date, we do not want to keep storing new text in date.
            checkDate = False
        if element.find(text=re.compile('SCORE')):
            # check is true at the first occurrence of score, which is the raw score.
            if check:
                score1 = element.text
                check = not check
            # check becomes false before the second occurrence of score, which is the adjusted score.
            else:
                score2 = element.text
        if element.find(text=re.compile('Date')):
            # If we find the word "Date" the next "td" element will contain the actual date.
            checkDate = True
        if element.find(text=re.compile('CRITICAL X')):
            critical = element.text
        if element.find(text=re.compile('REPEATS X')):
            repeats = element.text
    # For the scores, critical violations, and repeat violations, the number to
    # represent them is the last number in the string.
    return {"DATE": date, "SCORE1": score1.split(" ")[-1], "SCORE2": score2.split(" ")[-1],
                        "CRITICAL": critical.split(" ")[-1], "REPEATS": repeats.split(" ")[-1]}

# Takes a link to a restaurant, and returns an array, which
# contains a dictionary for each of that restaurant's inspection reports.
def reportArray(link):
    database = requests.get(link).text
    soup = BeautifulSoup(database, 'html5lib')
    # All inspection report links are within an "a" tag.
    links = soup.find_all('a')
    for i in range(len(links)):
        links[i] = links[i].get('href')
    # The first two links always do not lead to an inspection report.
    trueLinks = links[2:]
    reportsData = []
    for i in range(len(trueLinks)):
        string = trueLinks[i]
        upper = len(string)
        # There are two extraneous characters at the beginning of each of the
        # inspection report link stubs.
        linkAppend = string[2:upper]
        # We append the link stub to the rest of the link that will lead
        # to the actual page that contains the report information.
        reportInfoLink = 'http://il.healthinspections.us' + linkAppend
        reportsData.append(getReportInfo(reportInfoLink))
    return reportsData

# Primary function that returns a dictionary mapping the names of restaurants
# on Green Street to an array as returned by the previous function.
def scrapeReports():
    pageLinks = getRestaurantPages()
    dictOfInfo = {}
    for pageLink in pageLinks:
        # Gets the info about a restaurant.
        namesAddrsLinks = getPageInfo(pageLink)
        for i in range(len(namesAddrsLinks)):
            # If the restaurant's address contains "Green  ST", it's one of the
            # ones that we want to scrape.
            if not (namesAddrsLinks[i][1].find('Green  ST') == -1):
                dictOfInfo[namesAddrsLinks[i][0]] = namesAddrsLinks[i][2]
    dictOfReportInfo = {}
    for rest in dictOfInfo:
        # For each restaurant we want to scrape info from, this maps
        # the restaurant's name to its array of reports.
        dictOfReportInfo[rest] = reportArray(dictOfInfo[rest])
    return dictOfReportInfo

print(scrapeReports())
