# News and Sentiment Extractor
# By: Justin Serowik
# https://github.com/jserowik
import re
import os
import csv
import glob
import requests
import datetime

import nltk
import pandas as pd
import pandas_datareader.data as web
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup
from goose import Goose
from matplotlib import style
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tag import pos_tag

# Function to scrape text from news feed (Reuters by default)
def scrape(feed, used, excep, split1, split2, urlName, nameF):
    arrLinks = []
    req = requests.get('http://feeds.reuters.com/reuters/businessNews')
    soupRss = BeautifulSoup(req.text, "html5lib")
    # Checks list of already queried links 
    logrFile = open(used,"r")
    usedLinks = [line.strip() for line in logrFile]
    logrFile.close()
    # Extracts links from inital feed, excluding non-news
    for link in soupRss.find_all('guid'):
        arrLinks.append(str(link.getText()
            .replace('?feedType=RSS&feedName=businessNews', '')))
    # Store currently extracted links as not to repeat
    log_file = open(used,"w")
    for item in arrLinks:
        log_file.write(str(item)+"\n")
    log_file.close()
    # Extracts stripped news content with timestamp, omitting used links
    for item in arrLinks:
        fileName = str(item.rsplit('/', split1)[split2])
        if any(fileName in s for s in usedLinks):
            print fileName +" has been extracted."
        else:
            extractedText = Extractor(extractor='ArticleExtractor', url=urlName+fileName)
            print fileName + ": New"
            write_file = open("extractedFiles/"+nameF+fileName+".txt","w")
            write_file.write(str(datetime.date.today())+"\n")
            write_file.write(str(extractedText.getText().encode("utf-8")))
            write_file.close()

# Function for Sentiment analysis on extracted text
def sentAnalysis(pathOpt, targetFile):
    arr = []
    arrRate = []
    arrSent = []
    logrFile = open(pathOpt + targetFile)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')    
    data = logrFile.read()
    logrFile.close()
    # Split text by sentences and get sentiment score for each sentence
    sent = tokenizer.tokenize(data)
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(data)
    # Process text to remove newline symbol
    for line in sent:
        arrSent.append(str(line.replace('\n', '')))
    # Get sentence sentiment score and attach it to entities in sentence
    for sent in arrSent:
        nounLn = []
        taggedSent = pos_tag(sent.split())
        propernouns = [word for word,pos in taggedSent if pos == 'NNP']
        ss = sid.polarity_scores(sent)
        score = re.findall(r'\d+\.{0,1}\d*', str(ss))
        aScore = float(score[2])-float(score[0])
        propernouns.insert(0, aScore)
        for item in propernouns:
            if type(item) is str:
                nounLn.append(re.sub('[".,]', '', item))
            else:
                nounLn.append(item)
        arr.append(nounLn)
    # Output Entities with sentiment scores to csv file
    with open('output.csv', 'rb') as csv_file:
        reader = csv.reader(csv_file)
        outA = dict(reader)
    csv_file.close()
    # Make sure not to overwrite values in output file
    for it in arr:
        scIt = it[0]
        for item in it[1:]:
            if item not in outA:
                outA[item] = scIt
            else:
                outA[item] = float(outA[item]) + scIt
    print outA
    with open("output.csv", "wb") as fout:
        writer = csv.writer(fout)
        for key, val in outA.items():
            writer.writerow([key, val])
    fout.close()

# Function for managing and reading files
def readFile():
    path = 'extractedFiles/'
    optionRead = True
    while optionRead:
        print ("""
        1. Read example file
        2. Read specified file
        3. List files
        4. Change default file path
        5. Return to previous menu
        """)
        optionRead = raw_input("Enter input: ")
        if optionRead == "1": 
            sentAnalysis(path, "example.txt")
        elif optionRead == "2":
            fileTar = raw_input("Enter file name: ")
            sentAnalysis(path, fileTar)
        elif optionRead == "3":
            for filename in glob.glob(os.path.join(path, '*.txt')):
                print(filename.rsplit('/', 1)[-1])
        elif optionRead == "4":
            path = raw_input("Enter new file path: ")
        elif optionRead == "5":
            optionRead = False 
        elif optionRead != "":
          print("\n Not Valid Choice Try again")

# Displays menu
menu = True
while menu:
    print ("""
    Input the number corresponding to the menu option:
    1. Extract News
    2. Read File
    3. Exit/Quit
    """)
    menu = raw_input("Enter input: ") 
    if menu == "1": 
      scrape("http://feeds.reuters.com/reuters/businessNews","usedReuter.txt",
          'http://www.reuters.com',1,-1,"http://www.reuters.com/article/","reuters_")
    elif menu == "2":
        readFile()
    elif menu== "3":
      print("Goodbye")
      menu= False 
    elif menu != "":
      print("\n Not Valid Choice Try again") 