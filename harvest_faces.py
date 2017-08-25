import os
import sys
import glob
import mimetypes
import urllib
from threading import Thread
from queue import Queue
from requests import Session
from argparse import ArgumentParser

import logging
log = logging.getLogger(__name__)

def mk_url(ldap):
    return 'https://apps.carleton.edu/stock/ldapimage.php?id=' + ldap

def main():
    parser = ArgumentParser(description="Download Stalkernet images corresponding to LDAP's from stdin")
    parser.add_argument('nthreads', metavar='NTHREADS', type=int, help='Maximum number of concurrent outstanding requests.')
    parser.add_argument('dest', metavar='DEST', help='Destination directory.')
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    os.chdir(args.dest)

    q = Queue()

    def worker():
        while True:
            ldap = q.get()
            try:
                if not any(not x.endswith('.part') for x in glob.iglob(ldap + '.*')):
                    log.info(ldap + '...')
                    tmp, headers = urllib.request.urlretrieve(mk_url(ldap), ldap + '.part')
                    typ = mimetypes.guess_extension(headers['Content-Type'])
                    assert typ is not None
                    os.rename(tmp, ldap + typ)
                    log.info('...' + ldap)
            except Exception as e:
                log.exception(e)
                q.put(ldap)
                break
            finally:
                q.task_done()

    for _ in range(args.nthreads):
        Thread(target=worker, daemon=True).start()

    for line in sys.stdin:
        q.put(line.strip())

    q.join()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(thread)d:%(message)s')
    log.setLevel(logging.DEBUG)
    main()
