# Based on https://gist.github.com/lfepp/0a95ba23d55894e3ddb443b494aa284a

#!/usr/bin/env python

import requests
import argparse
import json
import sys
import datetime
import pandas as pd
from collections import Counter

base_url = 'https://api.pagerduty.com'

def main():
    args = parse_args()

    headers = {
        'Authorization': 'Token token={0}'.format(args.api_key),
        'Content-type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2'
    }
    since = args.start_date.strftime("%Y-%m-%d")
    until = args.end_date.strftime("%Y-%m-%d")
    incidents = get_incidents(since, 
            until, 
            headers, 
            0, 
            args.service_id)
    report_fname = 'pagerduty_export_' + since + '.csv'
    for incident in incidents:
        get_incident_details(
            incident['id'], str(incident['incident_number']),
            incident['service']['summary'],
            report_fname,
            headers
        )

    print('Export completed successfully! Output in ' + report_fname)
    if args.freq_report:
        print("Buidling frequency report...")
        df = pd.read_csv(report_fname, header=None)
        incident_frequencies = Counter(df[4])
        frequencies = pd.DataFrame.from_dict(incident_frequencies, orient='index').reset_index()
        frequencies = frequencies.rename(columns={'index': 'event', 0: 'count'})
        freq_report_name = 'pagerduty_frequencies_' + since + '.csv'
        frequencies.to_csv(freq_report_name, index=False)
        print(f"Finished! Frequency report: {freq_report_name}")


def parse_args():
    parser = argparse.ArgumentParser(description="Builds a report based off of pagerduty .")

    parser.add_argument('-id',
            '--service_id', 
            default='',
            type=str, 
            required=False, 
            help="ID used to identify your team. Leave blank for all teams.") 
    parser.add_argument('-s', 
            '--start_date', 
            type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
            help="Start date. Formatted YYYY-MM-DD.")
    parser.add_argument('-e', 
            '--end_date', 
            type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
            help="End date. Formatted YYYY-MM-DD.")
    parser.add_argument('-api', 
            '--api_key', 
            type=str,
            help="API key.")
    parser.add_argument('-c',
            '--freq_report', 
            action='store_true',
            help="Output an additional frequency report, including incident names and their counts.")
    
    return parser.parse_args()


def get_incidents(since, until, headers, offset, service_id=None, total_incidents=[]):
    print(f"Getting incidents from {since} to {until}...")
    params = {
        'service_ids': [service_id],
        'since': since,
        'until': until,
        'offset': offset,
        'limit': 100
    }
    r = requests.get(
        '{0}/incidents'.format(base_url),
        headers=headers,
        data=json.dumps(params)
    )
    if r.json()['more']:
        total_incidents.extend(r.json()['incidents'])
        offset += 100
        return get_incidents(since, until, offset, service_id, total_incidents)
    else:
        total_incidents.extend(r.json()['incidents'])
        return total_incidents


def get_incident_details(incident_id, incident_number, service, file_name, headers):
    start_time = ''
    end_time = ''
    summary = ''
    has_details = False
    has_summary = False
    has_body = False
    output = incident_number + ',' + service + ','

    f = open(file_name, 'a')

    r = requests.get(
        '{0}/incidents/{1}/log_entries?include[]=channels'.format(
            base_url, incident_id
        ),
        headers=headers
    )

    for log_entry in r.json()['log_entries']:
        if log_entry['type'] == 'trigger_log_entry':
            if log_entry['created_at'] > start_time:
                start_time = log_entry['created_at']
                if ('summary' in log_entry['channel']):
                    has_summary = True
                    summary = log_entry['channel']['summary']
                if ('details' in log_entry['channel']):
                    has_details = True
                    details = log_entry['channel']['details']
                if ('body' in log_entry['channel']):
                    has_body = True
                    body = log_entry['channel']['body']
        elif log_entry['type'] == 'resolve_log_entry':
            end_time = log_entry['created_at']

    output += start_time + ','
    output += end_time
    if (has_summary):
        output += ',"' + summary.replace(",", "-").replace("\"", "'").replace("\n", "").replace("\r", "") + '"'
    if (has_details):
        output += ',"' + str(details).replace(",", "-").replace("\"", "'").replace("\n", "").replace("\r", "") + '"'
    if (has_body):
        output += ',"' + str(body).replace(",", "-").replace("\"", "'").replace("\n", "").replace("\r", "") + '"'
    output += '\n'
    f.write(output)


if __name__ == '__main__':
    main()


