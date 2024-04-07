A script for scraping electronics prices from xkom - a popular Polish electronics shop.  
  
It organizes data into separate .csv files (separated with ';') for every category in urlList dict.
Product data varies between different product types, so auxilalry parameterList array dictates what parameters should be scraped for every product. If some data is unavailable on the website, then its according field remains empty.