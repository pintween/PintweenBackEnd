#!/usr/bin/python3
#import pywikibot
import os
import re
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from datetime import datetime



"""Define functions to parse the page."""


def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')


def surrounded_by_strings(tag):
    return (isinstance(tag.next_element, NavigableString)
            and isinstance(tag.previous_element, NavigableString))


def has_six_characters(css_class):
    return css_class is not None and len(css_class) == 6

"""Return True if this string is the only child of its parent tag."""
def is_the_only_string_within_a_tag(s):
    return (s == s.parent.string)


"""Return string after stripping out the tags"""
def strip_html_tag(input_string):
    return re.sub('<[^<]+?>', '', input_string)


""" Return Bool to check location information is available
    if not, Pintween skip thme at this moment
"""
def has_location_info(s):
    loc_info = s.find_all('span',  class_='noprint listing-coordinates')
    return (len(loc_info) > 0)

""" Return category string with two cases
    if there are h2 & h3 tags simoultaneously
    it concatenates them, and return it.
    if only h2 is avaialble, it returns h2
    if h3 exists, shouldn't be less than the h2 line number
"""
def get_category_string(poi_candidate):
     category_string = ""
     h2_line = 0
     h3_line = 0
     if poi_candidate.sourceline > 0:
         h2_line = poi_candidate.find_previous("h2").sourceline
         h3_line = poi_candidate.find_previous("h3").sourceline

     if h3_line > h2_line:
         category_string = strip_html_tag(str(poi_candidate.find_previous("h2").contents[0]))  \
                            + "::" \
                            + strip_html_tag(str(poi_candidate.find_previous("h3").contents[0]))

     if h2_line > h3_line:
         category_string = strip_html_tag(str(poi_candidate.find_previous("h2").contents[0]))
     return (category_string)


def get_previous_thumbimage_url(poi_candidate, poi_name):
     poi_image_url = ""
     image_block = poi_candidate.find_previous(class_='thumbimage')
     caption_block = poi_candidate.find_previous(class_='thumbcaption')
     caption_string = caption_block.contents[1]
     if poi_name == caption_string:
         poi_image_url = image_block.get('src')
         return poi_image_url
     else:
         poi_image_url = "pintween_data_not_available"
         return poi_image_url


def get_text_after_check_isNone(content_text):
    poi_data_text = ""
    if content_text is None:
       poi_data_text = "pintween_data_not_available"
       return poi_data_text
    else:
       poi_data_text = content_text.text
       return poi_data_text



"""Define variables to parse the page and prepare the files"""

# open cralwed file
crawled_filename = "en.wikivoyage.org_Da_Nang_1210_2019_165947.txt"
pintween_file_crawled = open(crawled_filename, "r")

# create new file to save parsed output
parsed_output_filename = "en.wikivoyage.org_Da_Nang_1210_2019_165947" \
                         + "_parsed_output.txt"
pintween_file_parsed_output = open(parsed_output_filename, "w+")


"""
Define 4 lines of the each file to process the header with following info
1. wikivoyage url
2. country
3. city
4. sub city section
"""


"""Begin to get BeautifulSoup html parser.
   Read the crawled file and read it with html parser
"""
soup = BeautifulSoup(pintween_file_crawled.read(), 'html.parser')


"""
   primary value for POI is location info to pick up POIs.
   if there are no loc info,  we skip it this time.
   It should begin with tag having loc info

   Structure {}
   1.  dashline for new poi
   2.  source line number
   3.  poi place name
   4.  latitude
   5.  longitude
   6.  description;  there are some cases it is not avaialble;
       if so set it to the flag equal to pintween_data_not_available
   7.  image url; get url if image caption eqaul to the poi name
       so only for a few cases image url is avaialble; other than that
       set it to pintween_data_not_available
   8.  address (optional)
   9.  phone number(optional)

"""


#<bdi class="vcard">
bdi_vcard_output = soup.find_all('bdi',  class_='vcard')
numOfPOI = 0

for poi_candidate in bdi_vcard_output:
   if has_location_info(poi_candidate):
       dashline_for_newpoi = "\n ------------------------------------------- "  + str(poi_candidate.sourceline)
       category_name = get_category_string(poi_candidate)
       poi_name = poi_candidate.find('span',  class_='fn org listing-name')
       latitude_value = poi_candidate.find('abbr',  class_='latitude')
       longitude_value = poi_candidate.find('abbr',  class_='longitude')

       listing_content_text = poi_candidate.find('bdi',  class_='note listing-content')
       poi_description = ""
       poi_description = get_text_after_check_isNone(listing_content_text)

       listing_address_output = poi_candidate.find('bdi', class_='adr listing-address street-address')
       listing_phone_output = poi_candidate.find('bdi', class_='tel listing-phone')
       poi_address = ""
       poi_address = get_text_after_check_isNone(listing_address_output)
       poi_phone = ""
       poi_phone = get_text_after_check_isNone(listing_phone_output)

       poi_image_url = get_previous_thumbimage_url(poi_candidate, poi_name.b.string)
       pintween_file_parsed_output.writelines([ dashline_for_newpoi,     \
                                                "\n",                    \
                                                category_name,           \
                                                "\n",                    \
                                                poi_name.b.string,       \
                                                "\n",                    \
                                                latitude_value.string,   \
                                                "\n",                    \
                                                longitude_value.string,  \
                                                "\n",                    \
                                                poi_description,         \
                                                "\n",                    \
                                                poi_image_url,           \
                                                "\n",                    \
                                                poi_address,             \
                                                "\n",                    \
                                                poi_phone])
       numOfPOI += 1



"""What if it is empty file. Handle this case.  City itself is a POI"""
if numOfPOI < 1:
    poi_name = soup.title.string
    latitude_value = soup.find('abbr',  class_='latitude')
    longitude_value = soup.find('abbr',  class_='longitude')
    poi_description = "url_address"
    pintween_file_parsed_output.writelines([ poi_name.b.string,       \
                                             "\n",                    \
                                             latitude_value.string,   \
                                             "\n",                    \
                                             longitude_value.string,  \
                                             "\n",                    \
                                             poi_description])

"""Make sure to close the opened files"""
pintween_file_parsed_output.close()
pintween_file_crawled.close()

