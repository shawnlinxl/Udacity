import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import string

OSMFILE = "C:/Users/Lenovo/Documents/GitHub/new-york_new-york.OSM"
LOGFILE = "zip_log.txt"


def audit_zipcode(zipcode):
    if len(zipcode) != 5:
        return zipcode


def is_zip(elem):
    """
    check if an element has attribute of zip code
    """
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile, logfile):
    osm_file = open(osmfile, "r")
    log_file = open(logfile, "w")
    zipset = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip(tag):
                    zipcode = audit_zipcode(tag.attrib['v'])
                    if zipcode is not None:
                        log_file.write(zipcode + '\n')
    osm_file.close()
    log_file.close()
    return zipset


def test():
    zip_types = audit(OSMFILE, LOGFILE)
    print zip_types


if __name__ == '__main__':
    test()
