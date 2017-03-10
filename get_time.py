import json, atp_classes as atp, time
from datetime import datetime

data = {"group_fields":["NETWORK_ID"],"dataset_filter":"NATIONAL_TIME >= '2016-08-29 06:00:00' AND NATIONAL_TIME < '2016-09-26 05:59:59' AND NATIONAL_CONTENT=1","select_fields":["NETWORK_ID","NETWORK_NAME","AD_AVERAGE_AUDIENCE_LIVE","AD_REACH_LIVE"],"target_filter":[376,377,378,379]}
r = atp.Rentrak()

rid = r.submit_report(json.dumps(data))['report_id']

print "report started at - " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

while r.get_report_status(rid).lower() != 'completed' and \
                r.get_report_status(rid).lower() != 'failed':
    time.sleep(2)

if r.get_report_status(rid).lower() == 'failed':
    raise Exception('Error while submitting report. Report generating returning status "failed"')

print "report done at - " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')