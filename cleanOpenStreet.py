#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys,re
import pprint
import codecs
import json
from collections import defaultdict
from shape_element import shape_element


"""
Initializing Global Variables and regular expressions
to be used later in the program
"""

OSM_FILE = "singapore.osm"
OUTPUT_FILE = "output.osm"

k = 15

street_type_re_number = re.compile(r'\b\S+[0-9]+?$', re.IGNORECASE)
number = re.compile(r'[0-9]+$',re.IGNORECASE)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

singapore_list = ['Singapore', 'Changi Village', 'Singapore', 'Sembawang', 'Ang Mo Kio', 'Changi Village', 'Singapore', '01-169 Singapore', 'Woodlands Spectrum II', 'Holland Village']
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd"   : "Road",
            "Dr"   : "Drive",
            "Rd." : "Road",
            "Jl"  : "Jalan",
            "Jl." : "Jalan",
            "Jln." : "Jalan",
            "Jln" : "Jalan",
            "Cresent" : "Crescent"
            }

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def count_tags(filename):
        """
        Code to count tags of each kind
        """
        tags = {}
        tags_set = set()
        context = ET.iterparse(filename, events=("start", "end"))
        context = iter(context)
        event, root = context.next()
        
        for event,elem in context:
            if not elem.tag in tags:
                tags[elem.tag] = 1
                print tags
            else:
                tags[elem.tag] = tags[elem.tag] + 1
                #print elem.tag
                
            root.clear()
            elem.clear()

            
        return tags

def is_street(tag):
    """
    to find if tag attribute is street
    """
    
    return tag.attrib['k'] == "addr:street"

def is_city(tag):
    """
    to find if tag attribute is city
    """
    
    return tag.attrib['k'] == "addr:city"

def is_post_code(tag):
    """
    to find if tag attribute is postal code
    """
    
    return tag.attrib['k'] == "addr:postcode"



def is_singapore(elem):
    """
    to check if the name of the city is singapore

    """

    
    for tag in elem.iter("tag"):
        if is_city(tag):
            if tag.attrib['v'] in singapore_list:
                return True
            else:
                return False
            

    return True
    
def audit_city(osmfile):
    """
    In the data I found cities other than singapore is present
    this function is to determine the unique city names and unique postal codes
    that are not that are not matching 6 digit postal code standated of singapore

    """

    
    osm_file_name = open(osmfile,"r")
    street_types = defaultdict(set)
    #street_types = set()
    #context = ET.iterparse(osm_file_name, events=("start", "end"))
    context = ET.iterparse(osm_file_name, events=("start",))
    context = iter(context)
    event, root = context.next()
    city = set()
    post = []
    
    for event,elem in context:
        shape_element(elem)
        if elem.tag == "node" or elem.tag == "way":
            #print elem.attrib['changeset']
            city_now = ""
            
            for tag in elem.iter("tag"):
                if is_city(tag):
                    city.add(tag.attrib['v'])
                    city_now = tag.attrib['v']
                    #audit_street_type(street_types, tag.attrib['v'])
                if is_post_code(tag):
                    m = number.match(tag.attrib['v']) 
                    if city_now == 'Singapore' or city_now == 'singapore' or city_now == 'Holland Village' or city == 'Sembawang':
                        if m:
                            pass
                        else:
                            post.append(tag.attrib['v'])
                        if len(tag.attrib['v'])  != 6:
                            post.append(tag.attrib['v'])
                
        else:
             elem.clear()
        root.clear()
              
    print "strange postal codes"
    print post

    
    return city

def audit_street(osmfile):

    """
    TO look into different street types

    """

    
    osm_file_name = open(osmfile,"r")
    street_types = defaultdict(set)
    #street_types = set()
    #context = ET.iterparse(osm_file_name, events=("start", "end"))
    context = ET.iterparse(osm_file_name, events=("start",))
    context = iter(context)
    event, root = context.next()
    
    for event,elem in context:
        if elem.tag == "node" or elem.tag == "way":
        
           
            for tag in elem.iter("tag"):
                
                if is_street(tag):
                    
                   
                    street_types[tag.attrib['v']].add(tag.attrib['v'])
                    
        else:
             elem.clear()
        root.clear()
         
    return street_types


def create_small_file():
    """
    To create a small file to do initial analysis

    """

    
    with open(OUTPUT_FILE, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        for i, element in enumerate(get_element(OSM_FILE)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')
        print "File created"
        

def create_json(file_in, pretty = False):

    """
    This function creates a new json file to be exported into MongoDB

    """

    
    context = ET.iterparse(file_in, events=("start",))
    context = iter(context)
    event, root = context.next()
    file_out = "{0}.json".format(file_in)
    data = []
    
    with codecs.open(file_out, "w") as fo:
        
        for _, element in context:
            el = shape_element(element)  #Shape element definition is present in another file names shape_element.py
            if el:
                #data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
                del el
            
            
            element.clear()
            root.clear()
            
    print "Json file created"
    
    return data

if __name__ == "__main__":
    
    street_types = audit_street(OUTPUT_FILE)
    print street_types
    city = audit_city(OUTPUT_FILE)
    print city
    create_json(OSM_FILE, True)
    
                
