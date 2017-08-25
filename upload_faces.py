import os
import os.path
import cognitive_face as cf
import json
import time
from argparse import ArgumentParser

import logging
log = logging.getLogger(__name__)


_call_count = 0
def wait():
    global _call_count
    _call_count += 1
    if _call_count % 10 == 0:
        log.info('waiting 1 minute because money')
        time.sleep(60)


def all_people(pgid):
    people = []
    curr = cf.person.lists(pgid)
    wait()
    while curr:
        people.extend(curr)
        start = curr[-1]['personId']
        curr = cf.person.lists(pgid, start=start)
        wait()
    return people


def main():
    parser = ArgumentParser(description="Upload faces to the Azure Face API")
    parser.add_argument('face_dir', metavar='FACE_DIR')
    parser.add_argument('-g', '--person-group-id', metavar='PERSON_GROUP_ID', default='foo-bar-person-group-id-1')
    parser.add_argument('-c', '--config-file', metavar='CONFIG_FILE', default='azure-config.json')
    parser.add_argument('-e', '--exists', action='store_true', default=False)
    args = parser.parse_args()

    with open(args.config_file, 'r') as f:
        config = json.load(f)
    key = config['key']
    endpoint = config['endpoint']
    if endpoint[-1] != '/':
        endpoint += '/'
    cf.Key.set(key)
    cf.BaseUrl.set(endpoint)

    pgid = args.person_group_id

    if not args.exists:
        lists = cf.person_group.lists()
        wait()
        exists = any(l['personGroupId'] == pgid for l in lists)
        if exists:
            log.info('person_group_id {} already existed, continuing'.format(pgid))
        else:
            log.info('person_group_id {} does not exist, creating it now'.format(pgid))
            cf.person_group.create(pgid)
            wait()

    people = all_people(pgid)
    names = { p['name'] for p in people }

    for fname in os.listdir(args.face_dir):
        path = os.path.join(args.face_dir, fname)
        name, _ = os.path.splitext(fname)
        if name in names:
            log.info('person:{} already exists, pass'.format(name))
        else:
            log.info('creating person:' + name)
            person_id = cf.person.create(pgid, name)['personId']
            wait()
            log.info('created person:{}:{}, adding image {}'.format(name, person_id, path))
            try:
                cf.person.add_face(path, pgid, person_id)
                wait()
            except cf.util.CognitiveFaceException as e:
                if e.msg == 'No face detected in the image.':
                    log.info('no face detected in {}, pass'.format(path))
                else:
                    raise
            log.info('added image {} for person:{}:{}'.format(path, name, person_id))


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(thread)d:%(message)s')
    log.setLevel(logging.DEBUG)
    main()
