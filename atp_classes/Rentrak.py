import atp_classes, requests, json, time
from datetime import timedelta, datetime


class Rentrak:
    __user_token = None
    __current_user = None

    def __init__(self, api_url=None, username=None, password=None):
        config = atp_classes.Config().get_config()

        if api_url:
            self.api_url = api_url
        else:
            self.api_url = config['api']['rentrak']['baseURL']

        if config['api']['rentrak']['auth_token'] != '':
            self.__user_token = config['api']['rentrak']['auth_token']
            self.__current_user = config['api']['rentrak']['username']
        else:
            self.login(username, password)

    def login(self, username=None, password=None):
        headers = {"Content-Type": "application/json"}

        if username and password:
            response = requests.post(self.api_url + '/auth/login', headers=headers,
                                     data=json.dumps({"user_id": username, "password": password}), verify=False)

            if response.status_code != 200:
                raise Exception('Error while logging in. ' + json.loads(response.text)['message'])
            else:
                self.__user_token = json.loads(response.text)['authtoken']
                self.__current_user = username
        else:
            config = atp_classes.Config().get_config()

            response = requests.post(self.api_url + '/auth/login', headers=headers, data=json.dumps(
                {"user_id": config['api']['rentrak']['username'], "password": config['api']['rentrak']['password']}),
                                     verify=False)

            if response.status_code != 200:
                raise Exception('Error while logging in. ' + json.loads(response.text)['message'])
            else:
                self.__user_token = json.loads(response.text)['authtoken']
                self.__current_user = config['api']['rentrak']['username']

    def logout(self):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.post(self.api_url + '/auth/logout', headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while logging out. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def search_networks(self, search):
        mapper = atp_classes.Mapper()
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/networks', params={"search": mapper.map_netowrk(search)},
                                headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting network info. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def search_tags(self, search):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/tags/', params={"search": search}, headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting tag info. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def search_endpoint(self, endpoint, search):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/{endpoint}/'.format(endpoint=endpoint),
                                params={"search": search}, headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting {endpoint} info. '.format(endpoint=endpoint) +
                            json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_all_metrics(self):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/metrics/', headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting metrics. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_reports(self):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reports/', headers=headers,
                                verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting reports. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_tags(self, per_page=10, page_num=1, search=''):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}
        params = {"search": search, "per_page": per_page, "page": page_num}

        response = requests.get(self.api_url + '/tags/', headers=headers, params=params, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting tags. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_endpoint(self, endpoint, per_page=10, page_num=1, search=''):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}
        params = {"search": search, "per_page": per_page, "page": page_num}

        response = requests.get(self.api_url + '/{endpoint}/'.format(endpoint=endpoint),
                                headers=headers, params=params, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting {endpoint}. '.format(endpoint=endpoint) +
                            json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_all_tags(self):
        page = 1
        all_tags = []
        continue_gathering = True

        while continue_gathering:
            next_tags = self.get_tags(page_num=page)
            page += 1

            if len(next_tags) == 0:
                continue_gathering = False
            else:
                all_tags += next_tags

        return all_tags

    def get_all_endpoint(self, endpoint):
        page = 1
        all_list = []
        continue_gathering = True

        while continue_gathering:
            next_results = self.get_endpoint(endpoint, page_num=page)
            page += 1

            if len(next_results) == 0:
                continue_gathering = False
            else:
                all_list += next_results

        return all_list

    def submit_report(self, data):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.post(self.api_url + '/users/' + self.__current_user + '/reports/',
                                 headers=headers, data=data, verify=False)

        if response.status_code != 202:
            raise Exception('Error while submitting report. ' + json.loads(response.text)['message'])
        else:
            location_url = response.headers['Location']
            temp_split = location_url.split('/')

            return_object = {"report_id": temp_split[-1]}

            return return_object

    def get_report_status(self, report_id):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reportqueue/' + report_id,
                                headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Error while getting report status. ' + json.loads(response.text)['message'])
        else:
            response_json = json.loads(response.text)

            if response_json.has_key('status') and response_json['status'] == "completed":
                return "Completed"
            elif response_json.has_key('status'):
                return response_json['status']
            else:
                return "Running"

    def get_report_rows(self, report_id, per_page=500):
        all_rows = []
        part_rows = []
        response = None
        page = 0
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        while not response or len(part_rows) != 0:
            response = requests.get(
                self.api_url + '/users/' + self.__current_user + '/reports/' + report_id + '/rows?page=' + str(page) +
                '&per_page=' + str(per_page), headers=headers, verify=False)

            if response.status_code != 200:
                raise Exception('Error while getting report rows. ' + json.loads(response.text)['message'])
            else:
                part_rows = json.loads(response.text)
                all_rows.extend(part_rows)
                page += 1

        return all_rows

    def delete_report(self, report_id):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.delete(self.api_url + '/users/' + self.__current_user + '/reports/' + report_id,
                                   headers=headers, verify=False)

        if response.status_code != 204:
            raise Exception('Error while deleting report. ' + json.loads(response.text)['message'])
        else:
            return "Deleted"

    def get_show_level_by_day(self, day_date, target):
        start = datetime.strptime(day_date, "%d-%m-%Y")
        end = start + timedelta(days=1)
        target_filter_string = ''

        if target != '' and target != 0:
            target_filter_string = 'TAG_ID=' + str(target) if isinstance(target, int) else target

        report_parms = dict(select_fields=["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME",
                                           "REACH_LIVE", "REACH_DVR_SAME_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY",
                                           "HOURS_LIVE", "SERIES_ID", "SERIES_NAME", "AIRING_NATIONAL_START_TIME"],
                            group_fields=["NETWORK_ID", "NATIONAL_DAYPART_ID", "SERIES_ID"],
                            dataset_filter='''NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'
                             AND NATIONAL_CONTENT = 1'''.format(
                                start_time=start.strftime('%Y-%m-%dT%H:%M:%S'),
                                end_time=end.strftime('%Y-%m-%dT%H:%M:%S')),
                            target_filter=target_filter_string)

        report_id = self.submit_report(json.dumps(report_parms))['report_id']

        while self.get_report_status(report_id).lower() != 'completed' and \
                        self.get_report_status(report_id).lower() != 'failed':
            time.sleep(2)

        if self.get_report_status(report_id).lower() == 'failed':
            raise Exception('Error while submitting report. Report generating returning status "failed"')

        rows = self.get_report_rows(report_id)

        for row in rows:
            row['segment_start'] = start.strftime('%Y-%m-%dT%H:%M:%S')
            row['segment_end'] = end.strftime('%Y-%m-%dT%H:%M:%S')

        return rows

    def get_show_level_by_hour(self, day_date, target):
        start = datetime.strptime(day_date, "%d-%m-%Y")
        end = start + timedelta(hours=1)
        target_filter_string = ''
        all_rows = []

        if target != '' and target != 0:
            target_filter_string = 'TAG_ID=' + str(target) if isinstance(target, int) else target

        while end < datetime.strptime(day_date, "%d-%m-%Y") + timedelta(days=1, hours=1):
            report_parms = dict(
                select_fields=["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME",
                               "REACH_LIVE", "REACH_DVR_SAME_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY",
                               "HOURS_LIVE", "SERIES_ID", "SERIES_NAME", "AIRING_NATIONAL_START_TIME"],
                group_fields=["NETWORK_ID", "NATIONAL_DAYPART_ID", "SERIES_ID"],
                dataset_filter='''NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'
                                 AND NATIONAL_CONTENT = 1'''.format(
                    start_time=start.strftime('%Y-%m-%dT%H:%M:%S'), end_time=end.strftime('%Y-%m-%dT%H:%M:%S')),
                target_filter=target_filter_string)

            report_id = self.submit_report(json.dumps(report_parms))['report_id']

            while self.get_report_status(report_id).lower() != 'completed' and \
                            self.get_report_status(report_id).lower() != 'failed':
                time.sleep(2)

            if self.get_report_status(report_id).lower() == 'failed':
                raise Exception('Error while submitting report. Report generating returning status "failed"')

            part_rows = self.get_report_rows(report_id)
            for part in part_rows:
                part['segment_start'] = start.strftime('%Y-%m-%dT%H:%M:%S')
                part['segment_end'] = end.strftime('%Y-%m-%dT%H:%M:%S')

            all_rows.extend(part_rows)
            start = start + timedelta(hours=1)
            end = end + timedelta(hours=1)
            print target + " : done with date: " + end.strftime('%Y-%m-%dT%H:%M:%S')

        return all_rows

    def get_show_level_by_minute(self, day_date, target, fields=[]):
        start = datetime.strptime(day_date, "%d-%m-%Y")
        end = start + timedelta(hours=1)
        target_filter_string = ''
        all_rows = []

        if target != '' and target != 0:
            target_filter_string = 'TAG_ID=' + str(target) if isinstance(target, int) else target

        if len(fields) == 0:
            fields = ["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME", "REACH_LIVE",
                      "REACH_DVR_SAME_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY", "HOURS_LIVE", "SERIES_ID", "SERIES_NAME",
                      "AIRING_NATIONAL_START_TIME", "NATIONAL_MINUTE"]

        while end < datetime.strptime(day_date, "%d-%m-%Y") + timedelta(days=1, hours=1):
            report_parms = dict(
                select_fields=fields,
                group_fields=["NETWORK_ID", "NATIONAL_MINUTE"],
                dataset_filter='''NATIONAL_MINUTE>='{start_time}' AND NATIONAL_MINUTE<'{end_time}'
                                     AND NATIONAL_CONTENT = 1'''.format(
                    start_time=start.strftime('%Y-%m-%dT%H:%M:%S'), end_time=end.strftime('%Y-%m-%dT%H:%M:%S')),
                target_filter=target_filter_string)

            report_id = self.submit_report(json.dumps(report_parms))['report_id']

            print "report submitted at - " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            while self.get_report_status(report_id).lower() != 'completed' and \
                            self.get_report_status(report_id).lower() != 'failed':
                time.sleep(2)

            print "report done at - " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            if self.get_report_status(report_id).lower() == 'failed':
                raise Exception('Error while submitting report. Report generating returning status "failed"')

            part_rows = self.get_report_rows(report_id, 1000)
            for part in part_rows:
                part['segment_start'] = datetime.strptime(part['national_minute'], '%Y-%m-%d %H:%M:%S').strftime(
                    '%Y-%m-%dT%H:%M:%S')
                part['segment_end'] = (datetime.strptime(part['national_minute'], '%Y-%m-%d %H:%M:%S') +
                                       timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S')

            all_rows.extend(part_rows)
            start = start + timedelta(hours=1)
            end = end + timedelta(hours=1)
            print target + " : done with date: " + end.strftime('%Y-%m-%dT%H:%M:%S')

        return all_rows

    def get_show_level_by_minute_array(self, day_date, target):
        start = datetime.strptime(day_date, "%d-%m-%Y")
        end = start + timedelta(days=1)
        target_filter_string = ''
        all_rows = []

        if target != '' and target != 0:
            target_filter_string = 'TAG_ID=' + str(target) if isinstance(target, int) else target

        while end < datetime.strptime(day_date, "%d-%m-%Y") + timedelta(days=1, hours=1):
            report_parms = dict(
                select_fields=["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME",
                               "HOURS_ARRAY_DVR_15_DAY", "HOURS_ARRAY_DVR_1_DAY", "HOURS_ARRAY_DVR_2_DAY",
                               "HOURS_ARRAY_LIVE", "HOURS_ARRAY_DVR_3_DAY", "HOURS_ARRAY_DVR_7_DAY",
                               "HOURS_ARRAY_DVR_SAME_DAY", "SERIES_ID", "SERIES_NAME", "AIRING_NATIONAL_START_TIME"],
                group_fields=["NETWORK_ID", "SERIES_ID"],
                dataset_filter='''NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'
                                 AND NATIONAL_CONTENT = 1'''.format(
                    start_time=start.strftime('%Y-%m-%dT%H:%M:%S'), end_time=end.strftime('%Y-%m-%dT%H:%M:%S')),
                target_filter=target_filter_string,
                array_element_length=60)

            report_id = self.submit_report(json.dumps(report_parms))['report_id']

            while self.get_report_status(report_id).lower() != 'completed' and \
                            self.get_report_status(report_id).lower() != 'failed':
                time.sleep(2)

            if self.get_report_status(report_id).lower() == 'failed':
                raise Exception('Error while submitting report. Report generating returning status "failed"')

            remove_att = ["hours_array_dvr_15_day", "hours_array_dvr_1_day", "hours_array_dvr_2_day",
                          "hours_array_live",
                          "hours_array_dvr_3_day", "hours_array_dvr_7_day", "hours_array_dvr_same_day"]
            part_rows = self.get_report_rows(report_id)
            for part in part_rows:
                part_min = part.copy()

                for att in remove_att:
                    del part_min[att]

                hours_dvr_15_array = part["hours_array_dvr_15_day"].split(',')
                hours_dvr_1_array = part["hours_array_dvr_1_day"].split(',')
                hours_dvr_2_array = part["hours_array_dvr_2_day"].split(',')
                hours_live_array = part["hours_array_live"].split(',')
                hours_dvr_3_array = part["hours_array_dvr_3_day"].split(',')
                hours_dvr_7_array = part["hours_array_dvr_7_day"].split(',')
                hours_dvr_same_array = part["hours_array_dvr_same_day"].split(',')

                for min in range(0, 60):
                    part_min['segment_start'] = (start + timedelta(minutes=min)).strftime('%Y-%m-%dT%H:%M:%S')
                    part_min['segment_end'] = (end + timedelta(minutes=(min + 1))).strftime('%Y-%m-%dT%H:%M:%S')

                    part_min["hours_dvr_15_day"] = hours_dvr_15_array[min]
                    part_min["hours_dvr_1_day"] = hours_dvr_1_array[min]
                    part_min["hours_dvr_2_day"] = hours_dvr_2_array
                    part_min["hours_live"] = hours_live_array
                    part_min["hours_dvr_3_day"] = hours_dvr_3_array
                    part_min["hours_dvr_7_day"] = hours_dvr_7_array
                    part_min["hours_dvr_same_day"] = hours_dvr_same_array

                    all_rows.extend(part_min)

            start = start + timedelta(days=1)
            end = end + timedelta(days=1)
            print target + " : done with date: " + end.strftime('%Y-%m-%dT%H:%M:%S')

        return all_rows
