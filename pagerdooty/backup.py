#!/usr/bin/env python

import json
import os
import yaml

from hammock import Hammock


CONFIG_FILE_NAME = 'pd.conf.yml'
REQUIRED_CONFIG_KEYS = ['pagerduty_account', 'pagerduty_token']
DATA_DIR = 'data'
USER_PATH = 'users'
SERVICE_PATH = 'services'
SCHEDULE_PATH = 'schedules'
DEFAULT_PAGINATION_LIMIT = 100

EXCLUDED_FIELDS = {
    'user': [],
    'service': ["incident_counts", "last_incident_timestamp", "status"],
    'schedule': ["today"],
}


def _load_config(file_name):
    try:
        with open(file_name, 'r') as stream:
            config = yaml.load(stream)
    except:
        print "WARNING: config file {} does not exist".format(file_name)
        config = {}

    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            val = os.environ.get(key.upper())
            if val is not None:
                config[key] = val
            else:
                raise Exception('Required config value "{}" not found in {} or as environment variable {}!'
                                .format(key, CONFIG_FILE_NAME, key.upper()))
    return config


def _init_pagerduty(config_file_name):
    config = _load_config(config_file_name)
    headers = {
        'Authorization': 'Token token={0}'.format(config['pagerduty_token']),
        'Content-Type': 'application/json',
    }
    pager_duty_client = Hammock('https://{}.pagerduty.com/api/v1/'.format(config['pagerduty_account']), headers=headers)
    return pager_duty_client


def _depaginate(func, key, limit=DEFAULT_PAGINATION_LIMIT, *args, **kwargs):
    offset = 0
    contents = []
    while True:
        content = func(*args, params={'limit': limit, 'offset': offset}, **kwargs).content
        content = json.loads(content)
        data = content[key]
        contents += data
        if content['offset'] >= content['total']:
            break
        offset += limit
    return contents


def create_dirs(base_dir, dirs):
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)

    for dir in dirs:
        path = os.path.join(base_dir, dir)
        if not os.path.isdir(path):
            os.mkdir(path)


def dump_object_file(object_type, obj, base_dir=DATA_DIR):
    file_name = os.path.join(base_dir, object_type, generate_file_name(obj))

    with open(file_name, 'w') as f:
        f.write(json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))


def strip_fields(obj, fields):
    for field in fields:
        del obj[field]
    return obj


def generate_file_name(data_object):
    return "{}-{}.json".format(data_object['name'], data_object['id']).lower().replace(' ', '')


def main():
    print "Initialising PagerDuty client..."
    pager_duty_client = _init_pagerduty(CONFIG_FILE_NAME)

    print "Creating user, service, schedule dirs..."
    create_dirs(DATA_DIR, [USER_PATH, SERVICE_PATH, SCHEDULE_PATH])

    users = _depaginate(pager_duty_client.users.GET, 'users')
    for user in users:
        print "Creating file for user: {} {}".format(user['name'], user['id'])
        user = strip_fields(user, EXCLUDED_FIELDS['user'])
        dump_object_file(USER_PATH, user)

    services = _depaginate(pager_duty_client.services.GET, 'services')
    for service in services:
        print "Creating file for service: {} {}".format(service['name'], service['id'])
        service = strip_fields(service, EXCLUDED_FIELDS['service'])
        dump_object_file(SERVICE_PATH, service)

    schedules = _depaginate(pager_duty_client.schedules.GET, 'schedules')
    for schedule in schedules:
        print "Creating file for schedule: {} {}".format(schedule['name'], schedule['id'])
        schedule = strip_fields(schedule, EXCLUDED_FIELDS['schedule'])
        dump_object_file(SCHEDULE_PATH, schedule)


if __name__ == "__main__":
    main()
