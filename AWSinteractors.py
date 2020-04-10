import multiprocessing
import boto3
import logging
import logmatic
from datetime import datetime

logger = logging.getLogger()
logger.handlers = []
handler = logging.StreamHandler()
handler.setFormatter(logmatic.JsonFormatter())
logger.addHandler(handler)
logger.propagate = False
logger.setLevel(logging.INFO)


def get_domains(hz):
    client = boto3.client('route53')
    domains = []
    try:
        # Get the domains for the Hosted zone
        response = client.list_resource_record_sets(
            HostedZoneId='{}'.format(hz['Id'])
        )
        domains += response['ResourceRecordSets']
        # As long as there are more domains to be retrieved go get them
        while response['IsTruncated']:
            try:
                nrn = response['NextRecordName']
            except KeyError:
                nrn = ''
            try:
                nrt = response['NextRecordType']
            except KeyError:
                nrt = ''

            response = client.list_resource_record_sets(
                HostedZoneId='{}'.format(hz['Id']),
                StartRecordName='{}'.format(nrn),
                StartRecordType='{}'.format(nrt)
            )

            domains += response['ResourceRecordSets']
    except Exception:
        logger.warning("Failed to retrieve domains", exc_info=True)
    else:
        logger.info("Retrieved {} domains".format(len(domains)))
    return domains


class R53:
    """Route53 interaction class"""

    def __init__(self):
        self._client = boto3.client('route53')

    def get_domains(self):
        hzs = self._get_hosted_zones()
        all_domains = []

        print(datetime.now())
        pool = multiprocessing.Pool(processes=4)
        try:
            ret = pool.map(get_domains, hzs)
        except Exception:
            logger.error("Failed to run multiprocessing", exc_info=True)
        else:
            for x in ret:
                all_domains = all_domains + x
        logger.info("Retrieved {} domains".format(
            len(all_domains)
        ))
        print(datetime.now())

        return all_domains

    def _get_hosted_zones(self):
        hostedzones = []
        # Get the hosted zone's in the current account
        try:
            response = self._client.list_hosted_zones()
        except Exception:
            logger.error("Failed to retrieve hosted zones", exc_info=True)
        else:
            hostedzones += response['HostedZones']
            while response['IsTruncated']:
                # Get the hosted zone's in the current account
                try:
                    response = self._client.list_hosted_zones(
                        Marker='{}'.format(response['NextMarker'])
                    )
                except Exception:
                    logger.error("Failed to retrieve hosted zones",
                                 exc_info=True)
                else:
                    hostedzones += response['HostedZones']

        logger.info("Retrieved {} hosted zones".format(
            len(hostedzones)
        ))
        return hostedzones


class CWL:
    """Cloudwatch Logs interaction class"""

    def __init__(self):
        self._client = ""
