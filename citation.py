"""Gets citation from DOI"""
from typing import List, Dict, Union
import requests
import datetime as dt

from utils import _traverse_dict, _find_value

class Citation:

    def __init__(self, record: Dict):
        self.title = record.get("title")
        self.author = [Author(author) for author in record.get("author")]
        self.doi = record.get("DOI")
        self.journal = record.get("journal")
        self.issue = record.get("issue")
        self.volume = record.get("volume")
        self.publisher = record.get("publisher")
        self.url = record.get("URL")
        self.references = record.get("reference")
        self.published = _get_date_published(record)

    def __str__(self):
        return (f"Title: {self.title}\n" +
                f"Year: {self.published.year}\n" +
                f"Author: {'; '.join([author.name() for author in self.author])}\n" +
                f"Journal: {self.journal}\n" +
                f"Volume: {self.volume}\n" +
                f"Issue: {self.issue}\n" +
                f"Publisher: {self.publisher}\n" +
                f"DOI: {self.doi}\n")

    @classmethod
    def from_doi(cls, doi):
        return cls(get_doi_record(doi, format="json"))


def _get_date_published(record):
    date_parts = _traverse_dict(record, ["published", "date-parts"])[0]
    if len(date_parts) == 3:
        year, month, day = date_parts
        return dt.datetime(year, month, day)
    elif len(date_parts) == 2:
        year, month = date_parts
        return dt.datetime(year, month, 1)
    elif len(date_parts) == 1:
        year = date_parts[0]
        return dt.datetime(year, 1, 1)
    return

    
class Author:

    def __init__(self, author_info):
        """Initializes Author
        
        author_info : dict or author information from doi json
        """
        self.orcid = author_info.get("ORCID")
        self.given = author_info.get("given")
        self.family = author_info.get("family")
        self.sequence = author_info.get("sequence")
        self.affiliation = _get_author_affiliations(author_info)
        self.email = author_info.get("email", "")

    def __str__(self):
        return (f"Name: {self.family}, {self.given}\n" +
                f"Affiliation: {self._format_affiliations()}\n" +
                f"email: {self.email}\n" +
                f"ORCID: {self.orcid}\n")

    def _format_affiliations(self):
        """Returns a string of affiliations"""
        if not self.affiliation:
            return None
        if len(self.affiliation) > 1:
            return "\n" + "\n".join(self.affiliation)
        else:
            return self.affiliation[0]
                   
    def to_list(self):
        return [f"{self.family}, {self.given}", f"{self.affiliation[0]}", f"{self.email}"]

    def as_dict(self, attrs=["family", "given", "affiliation", "email"]):
        return {
            "orcid": self.orcid,
            "family": self.family,
            "given": self.given,
            "affiliation": self.affiliation[0],
            "email": self.email,
        }
    
    def name(self):
        return f"{self.family}, {self.given}"
        
    def email_from_orcid(self):
        if self.orcid != "":
            oid = self.orcid.split("/")[-1]
            self.email = Orcid(oid).email


def _get_author_affiliations(author_info):
    if author_info.get("affiliation"):
        return [af["name"] for af in author_info.get("affiliation")]
    return [None]
    

def crossref_url(doi, format="json"):
    """Retrieves a DOI record from crossref"""
    accepted_formats = {
        "json": "json",
        "bibtex": "x-bibtex",
    }
    return f"http://api.crossref.org/works/{doi}/transform/application/{accepted_formats[format]}"


def doiorg_url(doi, format="json"):
    """Retrieves a DOI record from doi.org"""
    return f"https://dx.doi.org/{doi}"


def get_doi_record(doi, format="json", source="crossref"):
    """Returns a DOI record from a source in the format specified

    Arguments
    ---------
    doi : DOI for object
    format : format to return record
    source : source of record - crossref seems to work best

    Returns
    -------
    a JSON object or bibtex string
    """
    # formats = {
    #     "citeproc": {
    #         'accept': "citeproc+json",
    #     },
    #     "bibtex": {
    #         'accept': "bibtex",
    #     },
    #     "bibliography": {
    #         "accept": "text/x-bibliography; style=apa", 
    #         "User-Agent": "mailto:youremail@email.com",
    #     },
    # }

    urls = {
        "crossref": crossref_url,
        "doi.org": doiorg_url,
        }

    try:
        url = urls[source]
    except Exception as err:
        raise KeyError(f"Unknown format {source}")

    # crossref_url(doi, format=format)
    r = requests.get(url(doi, format=format), headers=None)

    if format == "json":
        return r.json()
    elif format == "bibtex":
        return r.content.decode("utf-8")
    else:
        return r.content

