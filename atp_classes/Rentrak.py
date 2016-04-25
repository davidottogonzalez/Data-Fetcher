import atp_classes, requests, json


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
                                     data=json.dumps({"user_id": username, "password": password}))

            if response.status_code != 200:
                raise Exception('Error while logging in. ' + json.loads(response.text)['message'])
            else:
                self.__user_token = json.loads(response.text)['authtoken']
                self.__current_user = username
        else:
            config = atp_classes.Config().get_config()

            response = requests.post(self.api_url + '/auth/login', headers=headers, data=json.dumps(
                {"user_id": config['api']['rentrak']['username'], "password": config['api']['rentrak']['password']}))

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

        response = requests.get(self.api_url + '/networks', params={"search": mapper.map_netowrk(search)}, headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting network info. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def search_tags(self, search):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/tags/', params={"search": search}, headers=headers)

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

        response = requests.get(self.api_url + '/metrics/', headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting metrics. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_reports(self):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reports/', headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting reports. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

    def get_tags(self, per_page=10, page_num=1, search=''):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}
        params = {"search": search, "per_page": per_page, "page": page_num}

        response = requests.get(self.api_url + '/tags/', headers=headers, params=params)

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
                all_tags+= next_tags

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
                                 headers=headers, data=data)

        if response.status_code != 202:
            raise Exception('Error while submitting report. ' + json.loads(response.text)['message'])
        else:
            location_url = response.headers['Location']
            temp_split = location_url.split('/')

            return_object = {"report_id":temp_split[-1]}

            return return_object

    def get_report_status(self, report_id):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reportqueue/' + report_id,
                                 headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting report status. ' + json.loads(response.text)['message'])
        else:
            response_json = json.loads(response.text)

            if response_json.has_key('status') and response_json['status'] == "completed":
                return "Completed"
            else:
                return str(response_json['pct_complete']) + "% complete"

    def get_report_rows(self, report_id):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reports/' + report_id + '/rows',
                                headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting report rows. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)