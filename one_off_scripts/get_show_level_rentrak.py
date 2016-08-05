import atp_classes
import sys, datetime, warnings

#special characters in series name
reload(sys)
sys.setdefaultencoding("utf-8")

#supress warnings
warnings.filterwarnings("ignore")


#build targets to loop through
targets = [
    {'name':'A18-49',
     'definition':'TAG_ID = 3623'},
    {'name': 'F18-49',
     'definition': 'TAG_ID = 3641'},
    {'name': 'M18-49',
     'definition': 'TAG_ID = 3632'}
]

# desired fields
fields = ["NETWORK_ID", "NETWORK_NAME", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME", "SERIES_ID", "SERIES_NAME",
          "AIRING_NATIONAL_START_TIME", "AVERAGE_AUDIENCE_DVR_15_DAY", "AVERAGE_AUDIENCE_DVR_1_DAY",
          "AVERAGE_AUDIENCE_DVR_2_DAY", "AVERAGE_AUDIENCE_DVR_3_DAY", "AVERAGE_AUDIENCE_DVR_7_DAY",
          "AVERAGE_AUDIENCE_DVR_SAME_DAY", "AVERAGE_AUDIENCE_LIVE", "HOURS_DVR_15_DAY", "HOURS_DVR_1_DAY",
          "HOURS_DVR_2_DAY", "HOURS_DVR_3_DAY", "HOURS_DVR_7_DAY", "HOURS_DVR_SAME_DAY", "HOURS_LIVE",
          "MEETS_THRESHOLD_DVR_15_DAY", "MEETS_THRESHOLD_DVR_1_DAY", "MEETS_THRESHOLD_DVR_2_DAY", "MEETS_THRESHOLD_DVR_3_DAY",
          "MEETS_THRESHOLD_DVR_7_DAY", "MEETS_THRESHOLD_DVR_SAME_DAY", "MEETS_THRESHOLD_LIVE", "MEETS_THRESHOLD_LIVE_PLUS_DVR_15_DAY",
          "MEETS_THRESHOLD_LIVE_PLUS_DVR_1_DAY", "MEETS_THRESHOLD_LIVE_PLUS_DVR_2_DAY", "MEETS_THRESHOLD_LIVE_PLUS_DVR_3_DAY",
          "MEETS_THRESHOLD_LIVE_PLUS_DVR_7_DAY", "MEETS_THRESHOLD_LIVE_PLUS_DVR_SAME_DAY", "RATING_DVR_15_DAY", "RATING_DVR_1_DAY",
          "RATING_DVR_2_DAY", "RATING_DVR_3_DAY", "RATING_DVR_7_DAY", "RATING_DVR_SAME_DAY", "RATING_LIVE", "REACH_DVR_15_DAY",
          "REACH_DVR_1_DAY", "REACH_DVR_2_DAY", "REACH_DVR_3_DAY", "REACH_DVR_7_DAY", "REACH_DVR_SAME_DAY", "REACH_LIVE",
          "REACH_LIVE_PLUS_DVR_15_DAY", "REACH_LIVE_PLUS_DVR_1_DAY", "REACH_LIVE_PLUS_DVR_2_DAY", "REACH_LIVE_PLUS_DVR_3_DAY",
          "REACH_LIVE_PLUS_DVR_7_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY", "REACH_PCT_DVR_15_DAY", "REACH_PCT_DVR_1_DAY",
          "REACH_PCT_DVR_2_DAY", "REACH_PCT_DVR_3_DAY", "REACH_PCT_DVR_7_DAY", "REACH_PCT_DVR_SAME_DAY", "REACH_PCT_LIVE",
          "REACH_PCT_LIVE_PLUS_DVR_15_DAY", "REACH_PCT_LIVE_PLUS_DVR_1_DAY", "REACH_PCT_LIVE_PLUS_DVR_2_DAY",
          "REACH_PCT_LIVE_PLUS_DVR_3_DAY", "REACH_PCT_LIVE_PLUS_DVR_7_DAY", "REACH_PCT_LIVE_PLUS_DVR_SAME_DAY", "CALC_EXEC"]

rentrak = atp_classes.Rentrak()

for target_obj in targets:
    target = target_obj['definition']

    print 'Started pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    rows = rentrak.get_show_level_by_minute('01-04-2016',target,fields)

    print 'Finished pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    print "starting to write to file"

    with open('rows_minute_' + target_obj['name'] + '_' + target.replace(' ', '_') + '.csv', 'w') as fout:
        fout.write('segment_start|segment_end')

        for field in fields:
            fout.write('|' + field.lower())

        fout.write('\n')

        for row in rows:
            fout.write(str(row['segment_start']) + '|')
            fout.write(str(row['segment_end']))

            for field in fields:
                fout.write('|' + str(row[field.lower()]))

            fout.write('\n')

    # with open('rows_minute_' + target.replace(' ', '_') + '.csv', 'w') as fout:
    #     fout.write('segment_start|segment_end|network_id|network_name|national_daypart_id|national_daypart_name|series_id|series_name|airing_national_start_time|hours_live|hours_dvr_1_day|hours_dvr_2_day|hours_dvr_3_day|hours_dvr_7_day|hours_dvr_15_day|hours_dvr_same_day|calc_exec\n')
    #     for row in rows:
    #         fout.write(str(row['segment_start']) + '|')
    #         fout.write(str(row['segment_end']) + '|')
    #         fout.write(str(row['network_id']) + '|')
    #         fout.write(row['network_name'] + '|')
    #         fout.write(str(row['national_daypart_id']) + '|')
    #         fout.write(row['national_daypart_name'] + '|')
    #         fout.write(str(row['series_id']) + '|')
    #         fout.write(str(row['series_name']) + '|')
    #         fout.write(str(row['airing_national_start_time']) + '|')
    #         fout.write(str(row['hours_live']) + '|')
    #         fout.write(str(row['hours_dvr_1_day']) + '|')
    #         fout.write(str(row['hours_dvr_2_day']) + '|')
    #         fout.write(str(row['hours_dvr_3_day']) + '|')
    #         fout.write(str(row['hours_dvr_7_day']) + '|')
    #         fout.write(str(row['hours_dvr_15_day']) + '|')
    #         fout.write(str(row['hours_dvr_same_day']) + '|')
    #         fout.write(str(row['calc_exec']) + '\n')

    print target + " : done with " + str(len(rows))
