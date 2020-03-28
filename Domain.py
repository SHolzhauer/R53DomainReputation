import requests
import csv
import logging
import logmatic

curated_lists = [
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
    'http://sysctl.org/cameleon/hosts',
    'https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt',
    'https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt',
    'https://hosts-file.net/ad_servers.txt'
]
logger = logging.getLogger()
logger.handlers = []
handler = logging.StreamHandler()
handler.setFormatter(logmatic.JsonFormatter())
logger.addHandler(handler)
logger.propagate = False
logger.setLevel(logging.INFO)


class Domain:

    def __init__(self, domain):
        self._obj = domain
        self.domain = domain['Name']
        self.reputation = 100
        self.marks = []

    def get_reputation(self):

        self._check_abuse_dot_ch()
        self._check_malwaredomains_dot_com()

    def _check_abuse_dot_ch(self):
        """Make sure the domain is not in urlhaus.abuse.ch/downloads/csv/"""

        # Read through the file with csv reader
        with open("urlhaus.csv") as csvfile:
            read = csv.reader(csvfile, delimiter=',')
            for row in read:
                if len(row) > 3 and self.domain in row[3]:
                    # Domain is in the list retract reputation points and
                    # add the remark to the domain
                    self.reputation -= 10
                    self.marks.append("Domain found in urlhaus: {}".format(
                        row
                    ))

    def _check_malwaredomains_dot_com(self):
        # See if the domain is in the list
        for line in open("justdomains.txt", "r"):
            if self.domain in line:
                # Domain is in the list retract reputation points and
                # add the remark to the domain
                self.reputation -= 10
                self.marks.append("Domain found on malwaredomains.com")

    def check_virus_total(self):
        """Verify the domain is not reported to be malicious by VirusTotal"""
        pass
