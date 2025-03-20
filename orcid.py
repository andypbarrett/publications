"""Gets an ORCID record"""

import requests


# URL for ORCID API
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"


class Orcid():

    def __init__(self, orcid):

        record = query_orcid_for_record(orcid)

        self.given_name = record["person"]["name"]["given-names"]["value"]
        self.family_name = record["person"]["name"]["family-name"]["value"]
        self.email = record["person"]["emails"]["email"]
        self.orcid = record["orcid-identifier"]["path"]
        self.works = []

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

# for each work in the work section: extract title and DOI
def extract_doi(work):
    title = get_title(work)
    doi = get_doi(work)
    return doi, title

def get_title(work):
    return work['work-summary'][0]['title']['title']['value']

def get_doi(work):
    """Returns first DOI"""
    pids = work['work-summary'][0]['external-ids']['external-id']
    dois = [pid['external-id-value'] for pid in pids if pid['external-id-type'] == "doi"]
    return dois[0] if dois else None    