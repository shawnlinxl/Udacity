#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET # Parse XML
import random # To generate random sample

random.seed(100) # Fix seed for replicable sampling
proportion = 0.005 # Sample proportion of total

OSM_FILE = "C:/Users/Lenovo/Documents/GitHub/new-york_new-york.osm" # Input file to be sampled
SAMPLE_FILE = "sample.osm" # Output Sampled File


def get_element(XML_file, tags):
    context = iter(ET.iterparse(XML_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n')

    # Randomly writes a proportion of top level elements
    for element in get_element(OSM_FILE, tags = ['node','way','relation']):
        if random.random() < proportion:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')