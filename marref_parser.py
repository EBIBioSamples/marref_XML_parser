"""
Convert MarRef XML from https://gitlab.com/uit-sfb/MarineMetagenomicPortal/raw/master/content/_marApp-data/MarDB_2017-08-11.xml
into bioschemas JSON-LD

presumed structure is html, body, records, record

Potentially not taking:
envmaterialenvo url becuase found '/gaz/' issue just taking curie
geolocnamegazenvo url because link could be cleaner?
any attributes ending in 'missing' although these would be stripped automatically by biosamples
genus, family, order, class, phylum, kingdom
"""
import os, shutil
from bs4 import BeautifulSoup, Tag
import requests, sys, csv, re, json

output_folder = './bioschemas'

mapping_field = {
    'identifier': ['biosampleaccession', 'mmpid'],
    'name': 'fullscientificname',
    'url': 'mmpid_url',
    'description': 'comments',
    'dataset': ['bioprojectaccession', 'genbankaccession', 'silvaaccessionssu',
                'silvaaccessionlsu', 'uniprotaccession', 'assemblyaccession',
                'ncbirefseqaccession', 'ncbirefseqaccession'],
    'additionalProperty': [
        {
            'name': 'Run Id',
            'value': 'runid',
        },
        {
            'name': 'Collection Time',
            'value': 'collectiontime'
        },
        {
            'name': 'Geographic Location (GAZ)',
            'value': 'geolocnamegaz',
            'valueReference': [{
                'name': 'geolocnamegaz',
                'codeValue': 'geolocnamegazenvo',
                'url': 'geolocnamegazenvo_url'
            }]
        },
        {
            'name': 'Organism',
            'value': 'organism',
            'valueReference': [{
                'name': 'organism',
                'url': 'ncbitaxonidentifier_url'
            }]
        }
    ]
}


def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def record2jsonld(record):
    record_dict = {}
    for attribute in record.children:  # iterate through all the tags in each sample
        # if attribute.name is not None and attribute.name[-7:] != 'missing' and attribute.string is not None:
        if isinstance(attribute, Tag):
            name = attribute.name
            if not name.endswith('missing'):
                url = None
                if 'url' in attribute.attrs:
                    url = attribute.attrs['url']
                value = attribute.string
                record_dict[name] = value
                if url is not None:
                    field_name = "{}_url".format(name)
                    record_dict[field_name] = url
            # attr_children = [c for c in attribute.children if isinstance(c, Tag)]
            # if attribute.name is not None and attribute.name[-7:] != 'missing':
            #     record_dict[attribute.name] = attribute.string
            #     if attribute.name == 'mmpid':
            #         record_dict['mmpid_url'] = attribute['url']

        # print(attribute.item)

        # TODO add ability to look inside attributes for items and extract them.

    # biosampleaccession = record_dict.get('biosampleaccession')
    # mmpid = record_dict.get('mmpid')
    # name = record_dict.get('fullscientificname')
    # url = record_dict.get('mmpid_url')
    # description = record_dict.get('comments')
    # datasets = [
    #     record_dict.get("bioprojectaccession"),
    #     record_dict.get("genbankaccession"),
    #     record_dict.get("silvaaccessionssu"),
    #     record_dict.get("silvaaccessionlsu"),
    #     record_dict.get("uniprotaccession"),
    #     record_dict.get("assemblyaccession"),
    #     record_dict.get("ncbirefseqaccession"),
    # ]
    # gaz = record_dict.get('geolocnamegazenvo')

    jsonld = dict()
    jsonld['@context'] = 'http://schema.org'
    jsonld['@type'] = ['BioChemEntity', 'Sample']
    for key, value in mapping_field.items():
        if key == 'additionalProperty':
            add_properties = list()
            for prop in value:
                pv = record_dict.get(prop.get('value', None))
                if pv is not None:
                    add_prop = dict()
                    add_prop['@type'] = 'PropertyValue'
                    add_prop['name'] = prop.get('name', None)
                    add_prop['value'] = pv
                    if 'valueReference' in prop:
                        codes = list()
                        for cc in prop.get('valueReference', []):
                            cat_code = dict()
                            cat_code['@type'] = 'CategoryCode'
                            cat_code['name'] = record_dict.get(cc.get('name', None), None)
                            cat_code['codeValue'] = record_dict.get(cc.get('code_value', None), None)
                            cat_code['url'] = record_dict.get(cc.get('url', None), None)
                            codes.append(cat_code)
                        add_prop['valueReference'] = codes
                    add_properties.append(add_prop)

            jsonld['additionalProperty'] = add_properties
        else:
            if isinstance(value, list):
                jsonld[key] = [record_dict.get(v) for v in value]
            else:
                jsonld[key] = record_dict.get(value)
    # jsonld['identifier'] = ["biosamples:{}".format(biosampleaccession), "mmp.ref:{}".format(mmpid)]
    # jsonld['name'] = name
    # jsonld['description'] = description
    # jsonld['url'] = url
    # jsonld['dataset'] = datasets
    return jsonld


# print(record_dict)
# print(record_dict.get('assembly'))


def souper(input_xml):
    with open(input_xml, encoding="utf-8") as fin:
        soup = BeautifulSoup(fin, "lxml")
        tag = soup.findAll('record')
        for record in tag:
            # print(record.prettify())
            jsonld = record2jsonld(record)
            mmp_id = [_id for _id in jsonld['identifier'] if _id.startswith('MMP')][0]
            filename = os.path.join(output_folder, "{}.json".format(mmp_id))
            with open(filename, 'w') as fout:
                json.dump(jsonld, fout, indent=2)


if __name__ == '__main__':
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    input_xml = 'MarRef_2017-08-11.xml'
    souper(input_xml)
    print("Finished")

# TODO use JSONencoder to build a class for JSONLD build.
