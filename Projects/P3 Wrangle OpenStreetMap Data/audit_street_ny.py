import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import string

OSMFILE = "C:/Users/Lenovo/Documents/GitHub/new-york_new-york.OSM"
LOGFILE = "log.txt"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Broadway", "Center", "Circle", "Concourse", "Crescent",
            "Cove", "East", "Esplanade", "Green", "Highway", "Loop", "Mews", "North", "Park", "Path",
            "Plaza", "Promenade", "Point", "South", "Terrace", "Turnpike", "Village", "Walk", "Way",
            "West", "Expressway", "Heights", "Alley", "Extension", "Driveway", "Bowery", "Ridge", "Roadbed",
            "Course", "Mall", "Marketplace", "Landing", "Reservation", "Quadrangle", "Oval", "Close", "Row",
            "Island", "Run", "Walkway", "Bayside", "Causeway"]

mapping_street = {"St": "Street",
                  "St.": "Street",
                  "st": "Street",
                  "street": "Street",
                  "Steet": "Street",
                  "Rd.": "Road",
                  "ROAD": "Road",
                  "Rd": "Road",
                  "Dr.": "Drive",
                  "Dr": "Drive",
                  "drive": "Drive",
                  "Ave": "Avenue",
                  "Ave.": "Avenue",
                  "AVE.": "Avenue",
                  "Ave,": "Avenue",
                  "avenue": "Avenue",
                  "avene": "Avenue",
                  "Avene": "Avenue",
                  "ave": "Avenue",
                  "avene": "Avenue",
                  "Aveneu": "Avenue",
                  "Blvd": "Boulevard",
                  "boulevard": "Boulevard",
                  "Blv.": "Boulevard",
                  "Cir": "Circle",
                  "Cres": "Crescent",
                  "Cv": "Cove",
                  "Ct": "Court",
                  "Hwy": "Highway",
                  "Pkwy": "Parkway",
                  "Pky": "Parkway",
                  "Plz": "Plaza",
                  "Prom": "Promenade",
                  "Pt": "Point",
                  "Tpke": "Turnpike",
                  "N": "North",
                  "S": "South",
                  "E": "East",
                  "W": "West"}

expected_street_names = list(mapping_street.keys()) + expected

upper_case_letter = list(string.ascii_uppercase)
# Handles avenues named "Avenue A" etc
AlphabetAvenue = ["Avenue " + x for x in upper_case_letter]
other = ['Avenue Of The Americas', 'Avenue of the Americas',
         "Fort Hamilton", "Prospect Park Southwest"]


def audit_street_type(street_types, street_name, special):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected_street_names:
            for special_case in special:
                if street_name in special_case:
                    return None
            return street_type + ":" + street_name
            # street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile, logfile):
    osm_file = open(osmfile, "r")
    log_file = open(logfile, "w")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    output = audit_street_type(street_types, tag.attrib[
                                               'v'], [AlphabetAvenue, other])
                    if output is not None:
                        log_file.writelines(output + '\n')
    osm_file.close()
    log_file.close()
    return street_types


def test():
    st_types = audit(OSMFILE, LOGFILE)

if __name__ == '__main__':
    test()
