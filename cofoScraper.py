#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 02:38:57 2020
@author: Kuldeep Gautam
@co-author: Surya Sai Teja also contributed to two modules, namely parseSpecification and parseSourceCodes for getting the
textual info using BeautifulSoup.

@description: Scraper for codeforces, scraping the problem specifications, associated testcases, tags and c/cpp source
codes of accepted submissions.

@checks:
1. File creation : Done
2. Error handling (HTTP status codes) : Not required yet. Didnt face any issues.
3. Logging : Done
4. Parallelism using multiprocessing : Done
5. Adding support for headless chrome : Done
6. Retry Module : Done
7. Replacing Xpath instances with CSS selectors: Not done

@Requirements:
    1. Beautiful soup
    2. Selenium
    3. Chrome driver (latest version compatible with the version of chrome browser in the machine)
    4. requests module
    5. tee for logging the stdout info

@Run:
    1. Make sure to run getScrapedList.py before this to get the updated pkl of already scraped problems from CodeForces
    and ensure correct path has been mentioned for 'alreadyExisting.pkl' file in this scraper.
    2. Make sure that the path of the sub-dirs to be created in the main dir (as mentioned in line 78) is correct and 
    exist already.
    3. Change the version of the log file to be created, for every run (Changes in L.No: 378)
    4. Run this cmd for scraping: 'python cofoScraper.py | tee stdoutLogsVXX.log'
    5. Make sure to change the XX with required version of stdoutlogs depending on the run.
"""

import requests
import html
import json
import pickle
from urllib.request import urlopen
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
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

# ROOT_DIR = '/home/cs20mtech01004/cofoscraper/test/testdata3'
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
        self.createDirSt(self.contestId, self.index)

        self.problemURL = 'https://codeforces.com/problemset/status/' + \
            str(self.contestId) + '/problem/' + self.index

        self.probSpecURL = 'https://codeforces.com/problemset/problem/' + \
            str(self.contestId) + '/' + self.index

        print('*' * 80)
        print("Scraping specification from {}...".format(self.probSpecURL))
        self.parseSpecification(self.probSpecURL)
        print('-' * 40)
        print("Scraping source codes from {}...".format(self.problemURL))
        self.parseDataFromHomepage(self.problemURL)
        print('*' * 80)

    def createDirSt(self, contestId, index):
        dirName = str(contestId) + '-' + index

        # Absolute Path of the main directory that would contain all the info for each sub-dir representing a problem.
        self.dirPath = os.path.join(ROOT_DIR, 'dataset', dirName)
        try:
            os.mkdir(self.dirPath)
        except Exception as warning:
            print('WARNING --> {}'.format(warning))

        # Absolute Path of the submissions folder inside each main dir containing the source codes.
        self.subDirPath = os.path.join(self.dirPath, 'submissions')
        try:
            os.mkdir(self.subDirPath)
        except Exception as warning:
            print('WARNING --> {}'.format(warning))

        # Creating tags.txt file in each main dir using Absolute Path.
        filename = os.path.join(self.dirPath, 'tags.txt')
        with open(filename, 'w') as tagFile:
            for tag in self.tags:
                tagFile.write(tag+'\n')
        return

    def get_text(self, element):
        q = ''
        for d in element:
            q += d.text
            q = html.unescape(q)
            q = q.replace('$', '')
        return q

    def parseSpecification(self, url):
        try:
            req = requests.get(url)
            time.sleep(1.5)
            soup = BeautifulSoup(req.text, 'html.parser')
            question = dict()

            # Get title and other metadata
            ref = soup.find('div', {'class': 'problem-statement'})
            question['title'] = ref.find('div', {'class': 'title'}).text
            question['input'] = ref.find(
                'div', {'class': 'input-file'}).text[5:]
            question['output'] = ref.find(
                'div', {'class': 'output-file'}).text[6:]

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
            print(
                'ERROR --> Origin: parseSpecification; URL: {} --> {}'.format(url, error))
            logging.exception(
                'Origin: parseSpecification; URL: {} - -> {}'.format(url, error))

    def parseSourceCodes(self, driver):
        # Applying filter on the form for language and accepted submissions.
        form = driver.find_element(By.CSS_SELECTOR, "form.status-filter")
        selectVerdictName = Select(
            form.find_element(By.CSS_SELECTOR, "#verdictName"))
        selectVerdictName.select_by_value("OK")

        selectLanguage = Select(form.find_element(
            By.CSS_SELECTOR, "#programTypeForInvoker"))
        selectLanguage.select_by_value(self.LANGUAGE)

        driver.find_element(
            By.CSS_SELECTOR, ".status-filter-box-content+ div input:nth-child(1)").click()
        time.sleep(0.25)

        numElements = len(
            driver.find_elements_by_css_selector('a.view-source'))
        self.subCounter += numElements
        print(
            "Number of elements on page #{}: {}".format(self.pageNo, numElements))

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
                        # print('Got subID...')
                        element.click()
                        # print('Click is working...')
                        time.sleep(0.5)
                        WebDriverWait(driver, 30).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))

                        codeFileName = ''
                        if(self.LANGUAGE == 'c.gcc11'):
                            codeFileName = subID + '.c'
                        else:
                            codeFileName = subID + '.cpp'

                        codeFileDir = os.path.join(
                            self.subDirPath, codeFileName)
                        codeElement = driver.find_elements(
                            By.XPATH, '//*[@id="facebox"]/div/div/div/pre/code/ol')

                        print("Scraping source code from element no: {}".format(elementCount+1))
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
                        # print(code)
                        with open(codeFileDir, 'w') as codeFile:
                            codeFile.write(code)
                        elementCount += 1
                        driver.find_element(
                            By.CSS_SELECTOR, "#facebox .close").click()
                        time.sleep(0.25)
                        WebDriverWait(driver, 30).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))
                    flag = 1

                except Exception as error:
                    # if attempts > 3:
                    print("Error occured while scraping element no-{}...".format(elementCount+1))
                        # print('ERROR --> Origin: parseSourceCodes; URL: {} --> {}'.format(driver.current_url, error))
                    logging.exception('Origin: parseSourceCodes; URL: {} --> Attempt #{}'.format(driver.current_url, attempts))
                    # else:
                    attempts += 1
                    driver.refresh()
                    time.sleep(1.5)
                    
                print("Number of elements scraped from the page #{}: {}".format(
                            self.pageNo, elementCount))
                print('Time taken to scrape source codes from page #{}: {:.3f} seconds'.format(
                        self.pageNo, time.time()-start))

            self.pageNo += 1
            if (self.pageNo > self.page_limit) or (self.subCounter >= 750):
                print("Returning for pageNo: {} and subCounter: {}".format(
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
            logging.warning(
                'No element on the webpage {}'.format(driver.current_url))

    def parseDataFromHomepage(self, url):
        # page limit and test cases.
        # specification from another url.
        options = Options()
        # Options.headless = True
        options.add_argument('-headless')
        driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
        # host = '127.0.0.1'
        # driver = webdriver.Remote(
        #     command_executor=f"http://{host}:4444/wd/hub",
        #     desired_capabilities=DesiredCapabilities.FIREFOX,
        #     options=options)

        driver.get(url)
        time.sleep(2)

        form = driver.find_element(By.CSS_SELECTOR, "form.status-filter")
        selectVerdictName = Select(
            form.find_element(By.CSS_SELECTOR, "#verdictName"))
        selectVerdictName.select_by_value("OK")

        selectLanguage = Select(form.find_element(
            By.CSS_SELECTOR, "#programTypeForInvoker"))
        selectLanguage.select_by_value(self.LANGUAGE)

        driver.find_element(
            By.CSS_SELECTOR, ".status-filter-box-content+ div input:nth-child(1)").click()
        time.sleep(0.25)

        # Setting the page limit to page_limit
        pageNoList = []
        pageNoList = driver.find_elements(By.CSS_SELECTOR, '.page-index a')

        if len(pageNoList) != 0:
            self.page_limit = int(pageNoList[-1].text)
            print("Page Limit: {}".format(self.page_limit))

        # Fetching the test cases from the very first submission on page.
        spec_attempts, spec_flag = 0, 0
        while spec_attempts < 3 and spec_flag == 0:
            try:
                content = driver.find_element(
                    By.XPATH, '//*[@id="pageContent"]/div[3]/div[6]/table/tbody/tr[2]/td').text
                # print("Origin: parseDataFromHomepage(); Value of content: {}".format(content))
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

                    driver.find_element(By.CSS_SELECTOR, '#facebox .close').click()
                    time.sleep(0.25)
                    WebDriverWait(driver, 30).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, '#facebox .close')))

                    spec_flag=1
                    status = self.parseSourceCodes(driver)
                    if status == "Done":
                        print("Closing all current driver instances...")
                        driver.quit()
                        return
                else:
                    print("Returning as Value of content is {}".format(content))
                    return
            except Exception as error:
                if spec_attempts >= 3:
                    print(' ERROR --> Origin: parseDataFromHomepage; URL: {} --> {}'.format(
                        driver.current_url, error))
                    logging.exception('Origin: parseDataFromHomepage; URL: {} --> {}'.format(
                        driver.current_url, error))
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
    logfile = sys.argv[1]+'logs.log'
    logging.basicConfig(
        # filename='/home/cs20mtech01004/cofoscraper/test/testlogs3.log',
        filename=logfile,
        filemode='w',
        level=logging.INFO,
        format='%(levelname)s --> %(asctime)s --> %(name)s: %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )

    apiData = urlopen('http://codeforces.com/api/problemset.problems').read()

    # JSON of fetched metadata
    jsonData = json.loads(apiData.decode('utf-8'))
    listsOfMetadata = []
    # Specify the language of the source codes to be scraped
    # language = 'cpp.g++17'
    language = sys.argv[2]

    alreadyExisting = []
    # Absolute path of alreadyExisting.pkl file
    with open('alreadyExisting.pkl', 'rb') as f:
        alreadyExisting = pickle.load(f)

    print('Length of alreadyExisting list: {}'.format(len(alreadyExisting)))

    for metaData in jsonData['result']['problems']:
        tags = metaData['tags']
        index = metaData['index']
        contestId = metaData['contestId']

        dirName = str(contestId) + '-' + index
        # if dirName not in alreadyExisting:
        if dirName in alreadyExisting:
            listsOfMetadata.append([language, contestId, index, tags])

    print('Length of updated listsOfMetadata list: {}'.format(len(listsOfMetadata)))

    # with Pool(4) as p:
    #     p.map(driverFunc, listsOfMetadata)
    #     p.terminate()
    #     p.join()
    
    print("Root Directory: {}".format(ROOT_DIR))
    print("Language-ID: {}".format(language))
    for listOfMetadata in listsOfMetadata:
        driverFunc(listOfMetadata)
    print("Scraping done successfully")
    print("Dataset is created in {}". format(ROOT_DIR))
