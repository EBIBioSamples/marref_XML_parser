'''
Convert MarRef XML from https://gitlab.com/uit-sfb/MarineMetagenomicPortal/raw/master/content/_marApp-data/MarDB_2017-08-11.xml
into bioschemas JSON-LD

presumed structure is html, body, records, record

Potentially not taking:
envmaterialenvo url becuase found '/gaz/' issue just taking curie
geolocnamegazenvo url because link could be cleaner?
any attributes ending in 'missing' although these would be stripped automatically by biosamples
genus, family, order, class, phylum, kingdom





'''

from bs4 import BeautifulSoup
import requests, sys, csv, re, json

def record2jsonld(record):
	record_dict = {}
	for attribute in record.children: #iterate through all the tags in each sample
		# if attribute.name is not None and attribute.name[-7:] != 'missing' and attribute.string is not None:
		if attribute.name is not None and attribute.name[-7:] != 'missing':
			record_dict[attribute.name] = attribute.string
			if attribute.name == 'mmpid':
				record_dict['mmpid_url'] = attribute['url']

			# print(attribute.item)

			# TODO add ability to look inside attributes for items and extract them.

				


	biosampleaccession = record_dict.get('biosampleaccession')
	mmpid = record_dict.get('mmpid')
	url = record_dict.get('mmpid_url')
	description = record_dict.get('comments')
	gaz = record_dict.get('geolocnamegazenvo')




	# print(record_dict)
	# print(record_dict.get('assembly'))



def souper(input_xml):
	with open(input_xml) as fin:
		soup = BeautifulSoup(fin, "lxml")
		tag = soup.findAll('record')
		for record in tag:
			# print(record.prettify())
			record2jsonld(record)
			sys.exit()


if __name__ == '__main__':

	input_xml = 'trunc_MarDB_2017-08-11.xml'
	souper(input_xml)

	# TODO use JSONencoder to build a class for JSONLD build.

