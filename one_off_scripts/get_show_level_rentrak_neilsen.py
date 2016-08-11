import atp_classes
import sys, datetime, warnings, gc, json, time, os

# special characters in series name
reload(sys)
sys.setdefaultencoding("utf-8")

# supress warnings
warnings.filterwarnings("ignore")

rentrak = atp_classes.Rentrak()

# build targets to loop through
targets = rentrak.get_tags(search='Age Range', per_page=10000, page_num=0)
targets.append({'name':'universe','id':0})

# desired fields
fields = ["NETWORK_ID", "NETWORK_NAME", "SERIES_ID", "SERIES_NAME", "REACH_LIVE"]

# months desired
dates = ['2015-09', '2015-10', '2015-11']

data = []

for month in dates:
    start_date = datetime.datetime.strptime(month, '%Y-%m')
    end_date = start_date + datetime.timedelta(days=365 / 12)

    for target_obj in targets:
        gc.collect()

        if os.path.isfile(target_obj['name'] + '_' + month + '.json'):
            print 'Skipping because file exists: ' + target_obj['name'] + '_' + month + '.json'
            continue

        print 'Started pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        target_string = 'TAG_ID=' + str(target_obj['id']) if target_obj['id'] != 0 else ''

        report_param = dict(select_fields=fields,
                            group_fields=["SERIES_ID"],
                            dataset_filter='''NATIONAL_TIME>='{start_date}' AND NATIONAL_TIME<'{end_date}'
                                 AND NETWORK_ID=5 AND NATIONAL_CONTENT=1'''.format(
                                start_date=start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                end_date=end_date.strftime('%Y-%m-%dT%H:%M:%S')),
                            target_filter=target_string)

        report_id = rentrak.submit_report(json.dumps(report_param))['report_id']

        while rentrak.get_report_status(report_id).lower() != 'completed' and \
                        rentrak.get_report_status(report_id).lower() != 'failed':
            time.sleep(2)

        if rentrak.get_report_status(report_id).lower() == 'failed':
            raise Exception('Error while submitting report. Report generating returning status "failed"')

        print 'Finished pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        rows = rentrak.get_report_rows(report_id)

        print "starting to write to file"

        with open(target_obj['name'] + '_' + month + '.json', 'w') as outfile:
            json.dump(rows, outfile)

        print "Done with " + target_obj['name'] + '_' + month + '.json'
