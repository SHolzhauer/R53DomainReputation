import requests
import multiprocessing
import logging
import logmatic
from Domain import Domain
from AWSinteractors import R53

# Create logger
logger = logging.getLogger()
logger.handlers = []
handler = logging.StreamHandler()
handler.setFormatter(logmatic.JsonFormatter())
logger.addHandler(handler)
logger.propagate = False
logger.setLevel(logging.INFO)


def main():

    try:
        r53 = R53()
        r53_domains = r53.get_domains()
    except Exception:
        logger.error("Failed to retrieve domains", exc_info=True)

    # Get the required files
    # Get the csv file and write it to a local file
    try:
        resp = requests.get("https://urlhaus.abuse.ch/downloads/csv/")
    except Exception:
        logger.error("Failed to retrieve urlhaus", exc_info=True)
    else:
        with open("urlhaus.csv", "w") as f:
            f.write(resp.content)

    # Get the file and write it to a local file
    try:
        resp = requests.get(
            "https://mirror1.malwaredomains.com/files/justdomains")
    except Exception:
        logger.error("Failed to retrieve malwaredomains", exc_info=True)
    else:
        with open("justdomains.txt", "w") as f:
            f.write(resp.content)

    pool = multiprocessing.Pool(processes=8)
    pool.map(handle_domain, r53_domains)


def handle_domain(domain):
    d = Domain(domain)
    d.get_reputation()
    if d.reputation != 100:
        logger.info("Failed domain", extra={
            'score': '{}/100'.format(d.reputation),
            'domain': '{}'.format(d.domain),
            'marks': '{}'.format(d.marks)
        })


if __name__ == "__main__":
    main()
