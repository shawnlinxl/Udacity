import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import schema
import string
import csv
import codecs
import cerberus

OSM_PATH = "sample.osm"

NODES_PATH = "./csv/nodes.csv"
NODE_TAGS_PATH = "./csv/nodes_tags.csv"
WAYS_PATH = "./csv/ways.csv"
WAY_NODES_PATH = "./csv/ways_nodes.csv"
WAY_TAGS_PATH = "./csv/ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema  # Database schema

# Make sure the fields order in the csvs matches the column order in the
# sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user',
               'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# ================================================== #
#               Street Variables                     #
# ================================================== #

expected_street_names = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
                         "Trail", "Parkway", "Commons", "Broadway", "Center", "Circle", "Concourse", "Crescent",
                         "Cove", "East", "Esplanade", "Green", "Highway", "Loop", "Mews", "North", "Park", "Path",
                         "Plaza", "Promenade", "Point", "South", "Terrace", "Turnpike", "Village", "Walk", "Way",
                         "West", "Expressway", "Heights", "Alley", "Extension", "Driveway", "Bowery", "Ridge", "Roadbed",
                         "Course", "Mall", "Marketplace", "Landing", "Reservation", "Quadrangle", "Oval", "Close", "Row",
                         "Island", "Run", "Walkway", "Bayside", "Causeway"]
upper_case_letter = list(string.ascii_uppercase)
# Handles avenues named "Avenue A" etc
AlphabetAvenue = ["Avenue " + x for x in upper_case_letter]
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
# Used to update street name formats
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

print mapping_street.keys()


# ================================================== #
#               Street Formatting                    #
# ================================================== #

def need_update_street(street_name, expected, special):
    """
    Takes a street_name, some expected name types and some special
    street names as input, determines whether the street_name need
    an update.
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            for special_case in special:
                if street_name in special_case:
                    return False
            return True


def is_street_name(elem):
    """
    check if an element has attribute of street name
    """
    return (elem.attrib['k'] == "addr:street")


def update_street_name(name, mapping):
    """
    Use mapping to update nonconforming street names
    """
    if name in ["Avenuenue of the Americas", "Avenue of the Americas", "Avenue of The Americas", "Avenue of Americas"]:
        return "6th Avenue"
    elif name == 'Avenue Of Puerto Rico':
        return 'Avenue of Puerto Rico'
    mapping = dict((re.escape(k), v) for k, v in mapping.iteritems())
    pattern = re.compile("|".join(mapping.keys()))
    name = pattern.sub(lambda m: mapping[re.escape(m.group(0))], name)
    return name


def street_name(name, mapping, expected, special):
    """
    Formats street names
    """
    if need_update_street(name, expected, special):
        return update_street_name(name, mapping)
    else:
        return name

# ================================================== #
#               Zipcode Formatting                   #
# ================================================== #


def is_zip(elem):
    """
    check if an element has attribute of zip code
    """
    return (elem.attrib['k'] == "addr:postcode")


# ================================================== #
#               Output Formatting                    #
# ================================================== #

def attrib_element(element, attr_fields):
    """
    Process output for node and way
    """
    res = dict.fromkeys(attr_fields)
    for attribute in attr_fields:
        res[attribute] = element.attrib[attribute]
    return res


def attrib_secondary(element, secondary, default_tag_type):
    """
    Processs tags for node and way
    """
    res = {}
    res['id'] = element.attrib['id']
    if ":" not in secondary.attrib['k']:
        res['key'] = secondary.attrib['k']
        res['type'] = default_tag_type
    else:
        res['key'] = str(secondary.attrib['k'].split(":", 1)[1])
        res['type'] = str(secondary.attrib['k'].split(":", 1)[0])
    if is_street_name(secondary):
        res['value'] = street_name(
            secondary.attrib['v'], mapping_street, expected_street_names, [AlphabetAvenue])
    else:
        res['value'] = secondary.attrib['v']
    return res


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        node_attribs = attrib_element(element, node_attr_fields)
        for tag in element.iter("tag"):
            if problem_chars.match(tag.attrib['k']) is not None:
                continue
            else:
                tags.append(attrib_secondary(element, tag, default_tag_type))
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        way_attribs = attrib_element(element, way_attr_fields)
        for i, tag in enumerate(element.iter('nd')):
            res = {}
            res['id'] = element.attrib['id']
            res['node_id'] = tag.attrib['ref']
            res['position'] = i
            way_nodes.append(res)
        for tag in element.iter("tag"):
            if problem_chars.match(tag.attrib['k']) is not None:
                continue
            else:
                tags.append(attrib_secondary(element, tag, default_tag_type))
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
