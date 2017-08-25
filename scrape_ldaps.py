import re
import sys
from string import ascii_lowercase
from queue import Queue
from threading import Thread, Lock
from requests import Session
from argparse import ArgumentParser

import logging
log = logging.getLogger(__name__)

ldap_re = re.compile('([a-z0-9]+)&nbsp;&lt;(?:A|&#065;)(?:T|&#084;)&gt;&nbsp;carleton&nbsp;(?:\.|&#046;)&nbsp;edu')

def mk_url(last_name_prefix):
    return 'https://apps.carleton.edu/campus/directory/?last_name=' + last_name_prefix

def main():
    parser = ArgumentParser(description="Scrape LDAP's from Stalkernet")
    parser.add_argument('nthreads', metavar='NTHREADS', type=int, help='Maximum number of concurrent outstanding requests. Be careful with this. More than 10 is a bad idea.')
    args = parser.parse_args()

    q = Queue()
    lock = Lock()

    def worker():
        s = Session()
        while True:
            prefi = q.get()
            log.info(prefi)
            try:
                for x in ascii_lowercase:
                    prefix = prefi + x
                    resp = s.get(mk_url(prefix))
                    resp.raise_for_status()
                    doc = resp.text
                    if 'Showing the first 100' in doc:
                        log.info('{} > 100'.format(prefix))
                        q.put(prefix)
                    ldaps = ldap_re.findall(doc)
                    log.info('{}: {}'.format(prefix, len(ldaps)))
                    with lock:
                        for ldap in ldaps:
                            print(ldap, flush=True)
            except Exception as e:
                log.exception(e)
                q.put(prefi)
                break
            finally:
                q.task_done()

    for _ in range(args.nthreads):
        Thread(target=worker, daemon=True).start()

    q.put('')
    q.join()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(thread)d:%(message)s')
    log.setLevel(logging.DEBUG)
    main()
