import atp_classes, requests, json


class Rentrak:
    __user_token = None
    __current_user = None

    def __init__(self, api_url=None, username=None, password=None):
        if api_url:
            self.api_url = api_url
        else:
            config = atp_classes.Config().get_config()
            self.api_url = config['api']['rentrak']['baseURL']

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

    def search_networks(self, search):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/networks', params={"search": search}, headers=headers)

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

    def get_reports(self):
        headers = {"Content-Type": "application/json", "Authorization": "RAP " + self.__user_token}

        response = requests.get(self.api_url + '/users/' + self.__current_user + '/reports/', headers=headers)

        if response.status_code != 200:
            raise Exception('Error while getting reports. ' + json.loads(response.text)['message'])
        else:
            return json.loads(response.text)

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