#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 02:38:57 2020
@author: Kuldeep Gautam
@co-author: Surya Sai Teja also contributed to two modules, namely parseSpecification and parseSourceCodes (partially) 
for getting the textual info using BeautifulSoup.

@description: Scraper for codeforces, scraping the problem specifications, associated testcases, tags and c/cpp/python/java
source codes of accepted submissions.

@checks:
1. File creation : Done
2. Error handling (HTTP status codes) : Not required yet. Didnt face any issues.
3. Logging : Done
4. Parallelism using multiprocessing : Done but removed later
5. Adding support for headless chrome and firefox : Done
6. Retry Module : Done
7. Replacing some Xpath instances with CSS selectors: Done

@Requirements:
    1. Beautiful soup (bs4)
    2. Selenium (V3.14)
    3. Chrome/firefox webdriver (latest version compatible with the version of chrome/firefox browser in the machine)
    4. requests module

@Run:
    1. For the first run of the scraper, simply run the command specified in step-2. Else, run 'getScrapedList.py' in the 
        utility directory first to generate a 'alreadyExisting.pkl' containing the info about already scraped problems.
    2. Run this cmd for scraping: 'python cofoScraper.py <dataset-dir> <language-ID> <firefox/chrome> <true/false>'
    <dataset-dir> : Directory for storing all the scraped data
    <language-ID> : ID for the programming language submissions to be scraped
    <firefox/chrome> : Web-driver to be used
    <true/false> : Flag specifying whether the first run or not. 'true' means the first run and 'false' otherwise.
"""

import requests
import html
import json
import pickle
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os
import logging
from multiprocessing import Pool
from bs4 import BeautifulSoup
import sys
# import argparse

ROOT_DIR = sys.argv[1]

class scraper():

    def __init__(self, LANGUAGE, contestId, index, tags):
        self.page_limit = 1
        self.pageNo = 1
        self.subCounter = 0
        self.LANGUAGE = LANGUAGE
        self.contestId = contestId
        self.index = index
        self.tags = tags
        self.dirPath, self.subDirPath = '', ''
        self.problemURL = 'https://codeforces.com/problemset/status/' + \
            str(self.contestId) + '/problem/' + self.index
        self.probSpecURL = 'https://codeforces.com/problemset/problem/' + \
            str(self.contestId) + '/' + self.index

        print('*' * 80)
        self.createDirSt(self.contestId, self.index)
        print('Scraping specification from {}...'.format(self.probSpecURL))
        self.parseSpecification(self.probSpecURL)
        print('-' * 40)
        print('Scraping source codes from {}...'.format(self.problemURL))
        self.parseDataFromHomepage(self.problemURL)

    def createDirSt(self, contestId, index):
        dirName = str(contestId) + '-' + index
        self.dirPath = os.path.join(ROOT_DIR, dirName)
        try:
            os.mkdir(self.dirPath)
        except Exception as warning:
            print('WARNING --> {}'.format(warning))

        self.subDirPath = os.path.join(self.dirPath, 'submissions')
        try:
            os.mkdir(self.subDirPath)
        except Exception as warning:
            print('WARNING --> {}'.format(warning))

        filename = os.path.join(self.dirPath, 'tags.txt')
        with open(filename, 'w') as tagFile:
            for tag in self.tags:
                tagFile.write(tag+'\n')
        return

    def get_text(self, elements):
        text = ''
        for element in elements:
            text += element.text
            text = html.unescape(text)
            text = text.replace('$', '')
        return text

    def parseSpecification(self, url):
        try:
            req = requests.get(url)
            time.sleep(1.5)
            soup = BeautifulSoup(req.text, 'html.parser')
            question = dict()

            # Get title and other metadata
            ref = soup.find('div', {'class': 'problem-statement'})
            question['title'] = ref.find('div', {'class': 'title'}).text
            question['input'] = ref.find('div', {'class': 'input-file'}).text[5:]
            question['output'] = ref.find('div', {'class': 'output-file'}).text[6:]

            # Question text
            c = ref.findAll('p')
            q = self.get_text(c)
            question['problem-statement'] = q

            # Input specification
            refI = soup.find('div', {'class': 'input-specification'})
            c = refI.findAll('p')
            inp = self.get_text(c)
            question['input-specification'] = inp

            # Output specification
            refO = soup.find('div', {'class': 'output-specification'})
            c = refO.findAll('p')
            out = self.get_text(c)
            question['output-specification'] = out

            # Complete Spec
            specification = ''
            for key, value in question.items():
                specification += key+'\n'+value+'\n\n'

            filename = os.path.join(self.dirPath, 'specification.txt')
            with open(filename, 'w') as specFile:
                specFile.write(specification)
            return

        except Exception as error:
            print('ERROR --> Origin: parseSpecification; URL: {} --> {}'.format(url, error))
            logging.exception('Origin: parseSpecification; URL: {} - -> {}'.format(url, error))

    def parseSourceCodes(self, driver):
        # Applying filter on the form for language and accepted submissions.
        form = driver.find_element(By.CSS_SELECTOR, "form.status-filter")
        selectVerdictName = Select(
            form.find_element(By.CSS_SELECTOR, "#verdictName"))
        selectVerdictName.select_by_value("OK")

        selectLanguage = Select(form.find_element(
            By.CSS_SELECTOR, "#programTypeForInvoker"))
        selectLanguage.select_by_value(self.LANGUAGE)

        driver.find_element(By.CSS_SELECTOR, ".status-filter-box-content+ div input:nth-child(1)").click()
        time.sleep(0.25)

        numElements = len(driver.find_elements_by_css_selector('a.view-source'))
        print('Number of elements on page #{}: {}'.format(self.pageNo, numElements))

        if numElements > 0:
            attempts, flag = 1, 0
            while attempts <= 3 and flag == 0:
                elementCount = 0
                try:
                    print('===============Attempt-{}==============='.format(attempts))
                    print('Scraping source codes from page #{}...'.format(self.pageNo))
                    start = time.time()
                    for element in driver.find_elements_by_css_selector('a.view-source'):
                        subID = element.text
                        element.click()
                        time.sleep(0.5)
                        WebDriverWait(driver, 30).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))

                        codeFileName = ''
                        if self.LANGUAGE == 'c.gcc11':
                            codeFileName = subID + '.c'
                        elif self.LANGUAGE == 'python.3':
                            codeFileName = subID + '.py'
                        elif self.LANGUAGE == 'java8':
                            codeFileName = subID + '-8.java'
                        elif self.LANGUAGE == 'java11':
                            codeFileName = subID + '-11.java'
                        else:
                            codeFileName = subID + '.cpp'

                        codeFileDir = os.path.join(self.subDirPath, codeFileName)
                        codeElement = driver.find_elements(
                            By.XPATH, '//*[@id="facebox"]/div/div/div/pre/code/ol')

                        print('Scraping source code from element no: {}'.format(elementCount+1))
                        for li in codeElement:
                            code = ''
                            doc = li.get_attribute('innerHTML')
                            soup = BeautifulSoup(doc, 'html.parser')
                            init = soup.findAll('li')
                            for ele in init:
                                spans = ele.findAll('span')
                                codeLine = ''
                                for span in spans:
                                    for word in span:
                                        codeLine += word
                                code += codeLine + '\n'

                        with open(codeFileDir, 'w') as codeFile:
                            codeFile.write(code)
                        elementCount += 1
                        driver.find_element(By.CSS_SELECTOR, "#facebox .close").click()
                        time.sleep(0.25)
                        WebDriverWait(driver, 30).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))
                    flag = 1

                except Exception as error:
                    print('Error occured while scraping element no-{}...'.format(elementCount+1))
                    logging.exception('Origin: parseSourceCodes; URL: {} --> Attempt #{}'.format(
                        driver.current_url, attempts))
                    attempts += 1
                    driver.refresh()
                    time.sleep(1.5)

                print('Number of elements scraped from the page #{}: {}'.format(self.pageNo, elementCount))
                print('Time taken to scrape source codes from page #{}: {:.3f} seconds'.format(
                    self.pageNo, time.time()-start))
                self.subCounter += elementCount

            self.pageNo += 1
            if (self.pageNo > self.page_limit) or (self.subCounter >= 750):
                print('Returning for pageNo: {} and subCounter: {}'.format(
                    self.pageNo, self.subCounter))
                return "Done"

            else:
                url = 'http://codeforces.com/problemset/status/' + str(self.contestId) + '/problem/' \
                    + self.index + '/page/' + \
                    str(self.pageNo)+'?order=BY_PROGRAM_LENGTH_ASC'

                driver.get(url)
                time.sleep(1.5)
                return self.parseSourceCodes(driver)
        else:
            print('WARNING --> No element on the webpage {}'.format(driver.current_url))
            logging.warning('No element on the webpage {}'.format(driver.current_url))

    # Getting page limit and test cases.
    def parseDataFromHomepage(self, url):
        browser = sys.argv[3]
        # For firefox driver
        if browser == 'firefox':
            options = firefoxOptions()
            options.add_argument('-headless')
            driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
        # For chrome driver
        else: 
            options = chromeOptions()
            options.headless = True
            driver = webdriver.Chrome(executable_path='./chromedriver', options=options)

        driver.get(url)
        time.sleep(2)

        try:
            # Select Accepted submissions
            form = driver.find_element(By.CSS_SELECTOR, "form.status-filter")
            selectVerdictName = Select(
                form.find_element(By.CSS_SELECTOR, "#verdictName"))
            selectVerdictName.select_by_value("OK")

            # Select programming language
            selectLanguage = Select(form.find_element(
                By.CSS_SELECTOR, "#programTypeForInvoker"))
            selectLanguage.select_by_value(self.LANGUAGE)

        except Exception as error:
            logging.exception('Origin: parseDataFromHomepage; URL: {} --> {}'.format(
                driver.current_url, error))
            print("No such element exception raised. Closing driver instance...")
            driver.close()
            return

        driver.find_element(By.CSS_SELECTOR, ".status-filter-box-content+ div input:nth-child(1)").click()
        time.sleep(0.25)

        # Setting the page limit to page_limit
        pageNoList = []
        pageNoList = driver.find_elements(By.CSS_SELECTOR, '.page-index a')

        if len(pageNoList) != 0:
            self.page_limit = int(pageNoList[-1].text)
            print('Number of pages to be scraped: {}'.format(self.page_limit))

        # Fetching the test cases from the very first submission on page.
        spec_attempts, spec_flag = 1, 0
        while spec_attempts <= 3 and spec_flag == 0:
            try:
                content = driver.find_element(By.XPATH, '//*[@id="pageContent"]/div[3]/div[6]/table/tbody/tr[2]/td').text
                if content != 'No items':
                    filename = 'testcases.txt'
                    filepath = os.path.join(self.dirPath, filename)
                    driver.find_element_by_css_selector('a.view-source').click()
                    time.sleep(0.5)
                    WebDriverWait(driver, 40).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))

                    with open(filepath, 'w') as file:
                        for testcase in driver.find_elements(By.XPATH, '//*[@id="facebox"]/div/div/div/div/div'):
                            file.write(testcase.text+'\n')
                    print('Created testcases.txt...')

                    driver.find_element(
                        By.CSS_SELECTOR, '#facebox .close').click()
                    time.sleep(0.25)
                    WebDriverWait(driver, 30).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))
                    spec_flag = 1
                    status = self.parseSourceCodes(driver)
                    if status == "Done":
                        print('Closing all current driver instances...')
                        driver.quit()
                        return
                else:
                    print('Closing driver instance as value of content is --{}--'.format(content))
                    driver.close()
                    return

            except Exception as error:
                if spec_attempts > 3:
                    print('ERROR --> Origin: parseDataFromHomepage; URL: {} - -> Attempt  # {}'.format(
                          driver.current_url, spec_attempts))
                    logging.exception('Origin: parseDataFromHomepage; URL: {} --> Attempt #{}'.format(
                        driver.current_url, spec_attempts))
                    print('Closing driver instance as max limit of attempts reached in parseDataFromHomepage...')
                    driver.close()
                    return
                else:
                    spec_attempts += 1
                    driver.refresh()
                    time.sleep(1.5)

def driverFunc(listOfMetadata):
    language = listOfMetadata[0]
    contestId = listOfMetadata[1]
    index = listOfMetadata[2]
    tags = listOfMetadata[3]
    _ = scraper(language, contestId, index, tags)
    return

if __name__ == "__main__":
    #sys.argv[1] - data dir
    #sys.argv[2] - language-id
    #sys.argv[3] - chrome/firefox
    #sys.argv[4] - true/false
    logfile = sys.argv[1]+'logs.log'
    logging.basicConfig(
        filename=logfile,
        filemode='a',
        level=logging.INFO,
        format='%(levelname)s --> %(asctime)s --> %(name)s: %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )
    apiData = urlopen('http://codeforces.com/api/problemset.problems').read()
    # JSON of fetched metadata
    jsonData = json.loads(apiData.decode('utf-8'))
    listsOfMetadata = []
    language = sys.argv[2]
    alreadyExisting = []

    # alreadyExisting.pkl file in current working directory
    if sys.argv[4] == 'false':
        with open('alreadyExisting.pkl', 'rb') as f:
            alreadyExisting = pickle.load(f)
        print('Length of alreadyExisting list: {}.'.format(len(alreadyExisting)))

    # scrapeList.pkl file in current working directory
    with open('scrapeList.pkl', 'rb') as f:
        scrapeList = pickle.load(f)
    print('Length of scrapeList: {}.'.format(len(scrapeList)))

    for metaData in jsonData['result']['problems']:
        tags = metaData['tags']
        index = metaData['index']
        contestId = metaData['contestId']
        dirName = str(contestId) + '-' + index
        if sys.argv[4] == 'false':
            # If not the first time run
            if dirName not in alreadyExisting and dirName in scrapeList:
                listsOfMetadata.append([language, contestId, index, tags])
        else:
            # For the first run
            if dirName in scrapeList:
                listsOfMetadata.append([language, contestId, index, tags])
    
    if language == 'c.gcc11':
        lang = 'GNU C11'
    elif language == 'cpp.g++11':
        lang = 'GNU C++11'
    elif language == 'cpp.g++14':
        lang = 'GNU C++14'
    elif language == 'cpp.g++17':
        lang = 'GNU C++17'
    elif language == 'python.3':
        lang = 'Python-3'
    elif language == 'java8':
        lang = 'Java-8'
    elif language == 'java11':
        lang = 'Java-11'
    else:
        lang = 'Not Specified.'

    print('Length of updated listsOfMetadata list: {}.'.format(len(listsOfMetadata)))
    print('Root Directory: {}.'.format(ROOT_DIR))
    print('Language-ID: {}.'.format(language))
    print('Programming Language: {}.'.format(lang))
    print('Webdriver: {}.'.format(sys.argv[3].capitalize()))
    for listOfMetadata in listsOfMetadata:
        driverFunc(listOfMetadata)

    print('Scraping done successfully.')
    print('Dataset is created in {}.'.format(ROOT_DIR))
