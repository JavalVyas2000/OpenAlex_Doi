"""
This is the file which has the openAlex works,
and is used to access the bibtex and ris formats
for the given Doi string.
"""
import base64
import requests

class Works:
    """
    A class representing a scholarly work.

    Attributes:
        oaid (str): The OpenAlex identifier of the work.
        data (dict): The JSON data for the work obtained from the OpenAlex API.
    """

    def __init__(self, oaid):
        """
        Constructs a new Works object.

        Args:
            oaid (str): The OpenAlex identifier of the work.
        """
        self.oaid = oaid
        self.req = requests.get(f'https://api.openalex.org/works/{oaid}')
        self.data = self.req.json()

    def bibtex(self):
        """
        Returns the BibTeX string for the work.

        Returns:
            str: The BibTeX string.
        """
        _authors = [au['author']['display_name'] for au in self.data['authorships']]
        if len(_authors) == 1:
            authors = _authors[0]
        else:
            authors = ', '.join(_authors[0:-1]) + ' and' + _authors[-1]

        title = self.data['title']

        volume = self.data['biblio']['volume']

        issue = self.data['biblio']['issue']
        if issue is None:
            issue = ', '
        else:
            issue = ', ' + issue

        pages = '-'.join([self.data['biblio']['first_page'], self.data['biblio']['last_page']])
        year = self.data['publication_year']
        seq = (
            f'author = {authors},'
            f'title = {title},'
            f'volume = {volume},'
            f'number = {issue},'
            f'pages = {pages},'
            f'year = {year},'
            f'doi = "{self.data["doi"]}",'
            f'url = "{self.oaid}",'
            f'DATE_ADDED = {self.data["updated_date"]}'
        )
        return seq
    def ris(self):
        """
        Returns the ris  for the work.

        Returns:
            html: The ris string.
        """
        fields = []
        if self.data['type'] == 'journal-article':
            fields += ['TY  - JOUR']
        else:
            raise Exception("Unsupported type {self.data['type']}")

        for author in self.data['authorships']:
            fields += [f'AU  - {author["author"]["display_name"]}']

        fields += [f'PY  - {self.data["publication_year"]}']
        fields += [f'TI  - {self.data["title"]}']
        fields += [f'JO  - {self.data["host_venue"]["display_name"]}']
        fields += [f'VL  - {self.data["biblio"]["volume"]}']

        if self.data['biblio']['issue']:
            fields += [f'IS  - {self.data["biblio"]["issue"]}']


        fields += [f'SP  - {self.data["biblio"]["first_page"]}']
        fields += [f'EP  - {self.data["biblio"]["last_page"]}']
        fields += [f'DO  - {self.data["doi"]}']
        fields += ['ER  -']

        ris = '\n'.join(fields)
        ris64 = base64.b64encode(ris.encode('utf-8')).decode('utf8')
        uri = (f'<pre>{ris}<pre><br>'
               f'<a href="data:text/plain;base64,{ris64}" download="ris">Download RIS</a>')
        return uri
