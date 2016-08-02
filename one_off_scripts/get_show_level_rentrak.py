import atp_classes
import sys, datetime, warnings

#special characters in series name
reload(sys)
sys.setdefaultencoding("utf-8")

#supress warnings
warnings.filterwarnings("ignore")

rentrak = atp_classes.Rentrak()
target = 'TAG_ID=677 AND (TAG_ID=32452 OR TAG_ID=34144 OR TAG_ID=32409 OR TAG_ID=11548 OR TAG_ID=34128 OR TAG_ID=32475 OR TAG_ID=32475)'

print 'Started pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

rows = rentrak.get_show_level_by_minute('01-04-2016',target)

print 'Finished pull at ' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

print "starting to write to file"

with open('rows_minute_' + target.replace(' ', '_') + '.csv', 'w') as fout:
    fout.write('segment_start|segment_end|network_id|network_name|national_daypart_id|national_daypart_name|series_id|series_name|airing_national_start_time|reach_live|hours_live|reach_dvr_same_day|reach_live_plus_dvr_same_day|calc_exec\n')
    for row in rows:
        fout.write(str(row['segment_start']) + '|')
        fout.write(str(row['segment_end']) + '|')
        fout.write(str(row['network_id']) + '|')
        fout.write(row['network_name'] + '|')
        fout.write(str(row['national_daypart_id']) + '|')
        fout.write(row['national_daypart_name'] + '|')
        fout.write(str(row['series_id']) + '|')
        fout.write(str(row['series_name']) + '|')
        fout.write(str(row['airing_national_start_time']) + '|')
        fout.write(str(row['reach_live']) + '|')
        fout.write(str(row['hours_live']) + '|')
        fout.write(str(row['reach_dvr_same_day']) + '|')
        fout.write(str(row['reach_live_plus_dvr_same_day']) + '|')
        fout.write(str(row['calc_exec']) + '\n')

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
