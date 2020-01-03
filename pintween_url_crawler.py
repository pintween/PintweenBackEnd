
#!/usr/bin/python3
#import pywikibot
import os
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime


# url list creation by city
# request the text by city
"""
create file_name by city url
"""
url_list_file_name = "pintween_wikivoyage_url_list.txt"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))



"""
Python multi-line comments
"""
def create_filename(url):
   url_words = url.split("/")
   url_header_word = ""

   for block in url_words:
       if block == "https:":
          # do nothing
          continue
       elif block == "wiki":
          # do nothing
          continue
       elif block == "":
          # do nothing
          continue
       else:
          url_header_word += block + "_"

   now = datetime.now()
   date_time = now.strftime("%m%d_%Y_%H%M%S")
   file_name_withURL = url_header_word + "_" + date_time  + ".txt"

   return file_name_withURL




"""
fetch URLs from wikivoyage
"""
with open(url_list_file_name) as openfileobject:
    for wikivoyage_url in openfileobject:
        print(wikivoyage_url)
        wikivoyage_page = requests.get(wikivoyage_url.rstrip())
        if wikivoyage_page.status_code == 200:
           file_name_withURL = create_filename(wikivoyage_url.rstrip())
           pintween_file_name = os.path.join(THIS_FOLDER, file_name_withURL)
           pintween_file_crawled = open(pintween_file_name, "wb+")
           pintween_file_crawled.write(wikivoyage_page.content)
           pintween_file_crawled.close()
           print("the URL cralwed successfully: " + wikivoyage_url)
        else:
           print("Error to fetch the URL: " + wikivoyage_url + "Error Code: " + str(wikivoyage_page.status_code))

        # Wait for 10 seconds
        print("waiting 60 seconds ...")
        time.sleep(60)

