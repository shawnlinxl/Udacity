import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import string

OSMFILE = "sample.osm"


def audit_zipcode(zipset,zipcode):
    if len(zipcode) != 5:
        zipset.add(zipcode)

def is_zip(elem):
    """
    check if an element has attribute of zip code
    """
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    zipset = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip(tag):
                    audit_zipcode(zipset, tag.attrib['v'])
    osm_file.close()
    return zipset

def test():
    zip_types = audit(OSMFILE)
    print zip_types


if __name__ == '__main__':
    test()