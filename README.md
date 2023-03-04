# RFJ
Web Scraping using Scrapy

### Requirements
Python 3.6 to 3.10

### Dependencies
Scrapy, Pandas, Openpyxl

### Installation
To install dependencies, run the following command:
```
pip install scrapy pandas openpyxl
```

### Run the program
To run the program, cd into the "rewardsforjustice" folder containing the scrapy.cfg file. Then, enter the following command:
```
scrapy crawl rewards
```

### Output
The program will output a JSON and XLSX file that contain the scraped data from the provided website. The filename will be in the format RWJST_YYYYMDD_hhmm.json/xlsx and will be located in the same directory.

## Recommendation
Install the program with a dedicated virtualenv as stated in the [Scrapy](https://docs.scrapy.org/en/latest/intro/install.html) documentation.
