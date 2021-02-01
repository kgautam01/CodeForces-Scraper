# CodeForces-Scraper
Selenium-Beautifulsoup-Python based scraper for scraping the source codes and other information associated with the problems/questions openly availabe on
[Codeforces](https://codeforces.com/) website.

## About the directories
1. **COFO** - This is a reference to our work (under review) _COFO: COdeFOrces dataset for ProgramClassification, Recognition and Tagging_ and contains a readme to provide a high level overview about the proposed dataset and related work done.

2. **Images** - It contains the images used in this repo.

3. **Utility** - It contains various utility python and bash scripts, useful while scraping the data using this scraper.

## Pre-requisites
* Python (>=3.8.5)
* Selenium (3.14)
* Beautifulsoup4 (bs4)
* requests

**All packages can be installed either using `conda`or `pip`.**

##### NOTE
 Do check the compatible versions of chrome/firefox driver with the already installed chrome/firefox browser installed in your system. This repo contains the latest versions of chrome and firefox drivers tested on Chrome browser (87.0.4280.88 (Official Build) (64-bit)) and Mozilla firefox (V84.0 (64-bit))

## Running the scripts

### Scraper
1. Run `getScrapedList.py` in the utility directory to generate a `alreadyExisting.pkl` containing the info about already scraped problems. 

2. Usage:
 `python cofoScraper.py <dataset-dir> <language-ID> <firefox/chrome> <true/false>`
`<dataset-dir>` : Directory for storing all the scraped data. This needs to be created beforehand. 
`<language-ID>` : ID for the programming language submissions to be scraped.
`<firefox/chrome>` : Web-driver to be used.
`<true/false>` : Flag specifying whether the first run or not. `true` means the first run and `false` otherwise.

3. Language-IDs (Lang-Version):
   * c.gcc11 (GNU C-11)
   * cpp.g++11 (GNU CPP-11)
   * cpp.g++14 (GNU CPP-14)
   * cpp.g++17 (GNU CPP-17)
   * python.3 (Python-3)
   * java8 (Java-8)
   * java11 (Java-11)

4. `scrapeList.pkl` denotes a subset of problems to be scraped. Codeforces API return information about a lot of problems. Using `scrapeList.pkl` will make the scraping confined to just 2.6K problems out of all of the problems.
   
### Flow of scraping
<img src="./images/scraper+tree.jpg" width=auto height=auto>

## Utility scripts
* `getScrapedList.py`
This script analyses the dataset directory and creates a pickle file `alreadyExisting.pkl`, which is consumed by the scraper to not scrape already scraped problems. Due to connectivity issues or maybe due to the driver-based issues, scraping may terminate. This script handles the scraping process in such scenarios.
**Usage:**
`python getScrapedList.py <dataset-dir>`

* `getRange.sh`
This script provides the stats on collected data. Total number of directories, total number of source codes, total number of classes and so on. Most importantly, it tells about data distribution.
**Usage:**
`bash getRange.sh <dataset-dir>`

* `getStat.sh`
This is a minimal version of the above script which focussed on just the number of directories and number of source code files in it.
**Usage:**
`bash getStat.sh <dataset-dir>`

**Make sure to create a directory with name `<dataset-dir>` in the working directory/location of your preference before using these scripts.**
