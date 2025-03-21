"""Gets an ORCID record"""

import requests
import datetime as dt
import re

from utils import _traverse_dict, _find_value
from citation import get_doi_record, Citation


# URL for ORCID API
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"


class Orcid():

    def __init__(self, record, citations=False):

        self.given_name = record["person"]["name"]["given-names"]["value"]
        self.family_name = record["person"]["name"]["family-name"]["value"]
        self.email = record["person"]["emails"]["email"]
        self.orcid = record["orcid-identifier"]["path"]
        self.works = [Work(work, citations=citations) for work in extract_works_section(record)]
        # self.works = extract_works_section(record)
        self.nworks = len(self.works)

    def __str__(self):
        return (f"Name: {self.family_name}, {self.given_name}\n" +
                f"email: {self.email}\n" +
                f"ORCID: {self.orcid}\n" +
                f"Works: {self.nworks}\n")

    def generate_nsf_coauthors(self):
        pass
        
    @classmethod
    def from_orcid(cls, orcid, citations=False):
        return cls(query_orcid_for_record(orcid), citations=citations)


# query ORCID for an ORCID record
def query_orcid_for_record(orcid_id):

    response = requests.get(url=requests.utils.requote_uri(ORCID_RECORD_API + orcid_id),
                          headers={'Accept': 'application/json'})
    response.raise_for_status()
    result=response.json()
    return result

# extract works section from ORCID profile
def extract_works_section(orcid_record):
    # orcid_dict=benedict.from_json(orcid_record)
    works=orcid_record['activities-summary']['works']['group']
    return works


class Work:
    """Class container for ORCID works"""

    def __init__(self, work, citations=True):
        self.doi = _get_doi(work)
        self.url = _get_url(work)
        self.type = _get_type(work)
        # self.publication_date = _get_publication_date(work)
        self.publication_date = _get_publication_date(work)
        self.journal = _get_journal(work)
        self.title = _get_title(work)
        self.bibtex = None
        if citations:
            self.citation = Citation.from_doi(self.doi)
        else:
            self.citation = None

    def __str__(self):
        return (f"Title: {self.title}\n" +
                # f"Date Published: {self.publication_date.strftime("%Y-%m")}\n" +
                f"Date Published: {self.publication_date}\n" +
                f"Journal: {self.journal}\n" +
                f"Type: {self.type}\n" +
                f"DOI: {self.doi}\n" +
                f"URL: {self.url}\n")

    def get_bibtex(self):
        """Get a bibtex citation record using the DOI"""
        if not self.bibtex:
            self.bibtex = get_doi_record(self.doi, format="bibtex")
        
    def print_bibtex(self):
        print(re.sub(r", (?=\w+\=)", ",\n    ", self.bibtex))


def _get_publication_date(work, depth=2):
    """Returns datetime representation of publication_date"""
    year = _get_publication_year(work, depth=depth)
    month = _get_publication_month(work, depth=depth)
    if year:
        return dt.datetime(year, month, 1)
    return 

def _get_publication_year(work, depth=2):
    list_of_keys = ["publication-date", "year", "value"]
    year = _find_value(work["work-summary"], list_of_keys, depth=depth, default=None)
    if year:
        return int(year)
    return

def _get_publication_month(work, depth=2):
    list_of_keys = ["publication-date", "month", "value"]
    month = _find_value(work["work-summary"], list_of_keys, depth=depth, default=1)
    if month:
        return int(month)
    return
    
def _get_doi(work, depth=2):
    list_of_keys = ["external-id-value"]
    return _find_value(work["external-ids"]["external-id"], list_of_keys, depth=depth, default=None)

def _get_url(work, depth=2):
    list_of_keys = ["external-id-url", "value"]
    return _find_value(work["external-ids"]["external-id"], list_of_keys, depth=depth, default=None)

def _get_type(work, depth=2):
    list_of_keys = ["type"]
    return _find_value(work["work-summary"], list_of_keys, depth=depth, default=None)

def _get_journal(work, depth=2):
    """Returns journal-title field"""
    list_of_keys = ["journal-title", "value"]
    return _find_value(work["work-summary"], list_of_keys, depth=depth, default=None)
    
def _get_title(work, depth=2):
    list_of_keys = ["title", "title", "value"]
    return _find_value(work["work-summary"], list_of_keys, depth=depth, default=None)

# for each work in the work section: extract title and DOI
# def extract_doi(work):
#     title = get_title(work)
#     doi = get_doi(work)
#     return doi, title

# def get_title(work):
#     return work['work-summary'][0]['title']['title']['value']

# def get_doi(work):
#     """Returns first DOI"""
#     pids = work['work-summary'][0]['external-ids']['external-id']
#     dois = [pid['external-id-value'] for pid in pids if pid['external-id-type'] == "doi"]
#     return dois[0] if dois else None    