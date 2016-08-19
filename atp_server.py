from flask import Flask, url_for, redirect, json, request, make_response
import atp_classes
import time, os

app = Flask(__name__)
config = atp_classes.Config()
app.secret_key = config.get_config()['session_secret']
cache = atp_classes.Cache()
app_db = atp_classes.AppDB()
teradata_db = atp_classes.TeradataDB()
rentrak_api = atp_classes.Rentrak()
app_login = atp_classes.AppLogin(app)


@app.route('/')
@app.route('/<path:path>')
@app_login.required_login
def index(path=None):
    if path and path[-4:] == '.ico':
        return make_response(open('static/favicon.ico').read())
    else:
        return make_response(open('static/index.html').read())


@app.route('/handleLogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = atp_classes.User.find_user_by_username(json.loads(request.data)['username'])
        if user and atp_classes.User.validate_login(user.password, json.loads(request.data)['password']):
            user_obj = atp_classes.User(str(user._id), user.username)
            app_login.log_user_in(user_obj)
            return json.dumps({"status": 'success'})
        return json.dumps({"status": 'failed'})
    return redirect(url_for('login_form', next=request.args.get("next")))


@app.route('/login/')
def login_form():
    if app_login.current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return make_response(open('static/index.html').read())


@app.route('/isUserAuthenticated/')
def is_user_authenticated():
    if app_login.current_user.is_authenticated:
        return json.dumps({"status": True, "username": app_login.current_user.username})
    else:
        return json.dumps({"status": False})


@app.route('/isUserAdmin/')
def is_user_admin():
    if app_login.current_user.is_authenticated and app_login.current_user.is_admin():
        return json.dumps({"status": True})
    else:
        return json.dumps({"status": False})


@app.route('/logout/')
def logout():
    app_login.log_user_out()
    return redirect('/')


@app.route('/queryWithParams/', methods=['POST'])
@app_login.required_login
@cache
def query_with_params():
    form_params = json.loads(request.data)['params']
    query_string = '''
        SELECT sdf.deal_id, sdf.deal_name, p.property_name, dhc.property_cd, sdf.brdcast_week_id, sdf.brand_id,
        b.brand_name, sdf.advertiser_id, a.advertiser_name, sdf.AIR_DTTM, sdf.UNIT_LENGTH, sdf.ISCII_CD

        FROM sales_detail_fact sdf
        JOIN brand b on (sdf.brand_id = b.brand_id and sdf.src_sys_id = b.src_sys_id)
        JOIN advertiser a on (sdf.advertiser_id = a.advertiser_id and sdf.src_sys_id = a.src_sys_id)
        JOIN deal_header_curr dhc on (sdf.deal_id = dhc.deal_id and sdf.src_sys_id = dhc.src_sys_id)
        JOIN property p on (dhc.property_cd = p.property_cd and dhc.src_sys_id = p.src_sys_id)

        WHERE sdf.src_sys_id = 1030
        AND brdcast_week_id >= {st_week_id}
        AND brdcast_week_id <= {end_week_id}
        AND business_type_cd = 'CURRENT_CONTRACTS'
        ''' \
        .format(st_week_id=form_params['st_week_id'], end_week_id=form_params['end_week_id'])

    if form_params['adv_id'] != '':
        query_string += '''
        AND sdf.advertiser_id = {adv_id}
        '''.format(adv_id=form_params['adv_id'])

    if form_params['brand_id'] != '':
        query_string += '''
        AND sdf.brand_id = {brand_id}
        '''.format(brand_id=form_params['brand_id'])

    if form_params['deal_id'] != '':
        query_string += '''
        AND sdf.deal_id = {deal_id}
        '''.format(deal_id=form_params['deal_id'])

    print query_string

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/findAdvertisers/', methods=['POST'])
@app_login.required_login
@cache
def find_advertisers():
    search = json.loads(request.data)['search']
    brand_id = json.loads(request.data)['brand_id']
    deal_id = json.loads(request.data)['deal_id']

    query_string = '''
        SELECT adv.ADVERTISER_ID, adv.ADVERTISER_NAME
        FROM ADVERTISER adv
        JOIN SALES_DETAIL_FACT sdf
        ON adv.ADVERTISER_ID = sdf.ADVERTISER_ID
        WHERE LOWER(ADVERTISER_NAME) LIKE LOWER('{search}%')
        AND sdf.SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

    if brand_id != '':
        query_string += '''
        AND sdf.BRAND_ID = '{brand_id}'
        '''.format(brand_id=brand_id)

    if deal_id != '':
        query_string += '''
        AND sdf.DEAL_ID = '{deal_id}'
        '''.format(deal_id=deal_id)

    query_string += '''
        GROUP BY adv.ADVERTISER_ID, adv.ADVERTISER_NAME
        '''

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/findBrands/', methods=['POST'])
@app_login.required_login
@cache
def find_brands():
    search = json.loads(request.data)['search']
    adv_id = json.loads(request.data)['adv_id']
    deal_id = json.loads(request.data)['deal_id']

    query_string = '''
        SELECT b.BRAND_ID, b.BRAND_NAME
        FROM BRAND b
        JOIN SALES_DETAIL_FACT sdf
        ON b.BRAND_ID = sdf.BRAND_ID
        WHERE LOWER(BRAND_NAME) LIKE LOWER('{search}%')
        AND sdf.SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

    if adv_id != '':
        query_string += '''
        AND sdf.ADVERTISER_ID = '{adv_id}'
        '''.format(adv_id=adv_id)

    if deal_id != '':
        query_string += '''
        AND sdf.DEAL_ID = '{deal_id}'
        '''.format(deal_id=deal_id)

    query_string += '''
        GROUP BY b.BRAND_ID, b.BRAND_NAME
        '''

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/findDeals/', methods=['POST'])
@app_login.required_login
@cache
def find_deals():
    search = json.loads(request.data)['search']
    brand_id = json.loads(request.data)['brand_id']
    adv_id = json.loads(request.data)['adv_id']

    query_string = '''
        SELECT DISTINCT DEAL_NAME, DEAL_ID
        FROM sales_detail_fact
        WHERE LOWER(DEAL_NAME) LIKE LOWER('{search}%')
        AND SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

    if brand_id != '':
        query_string += '''
        AND BRAND_ID = '{brand_id}'
        '''.format(brand_id=brand_id)

    if adv_id != '':
        query_string += '''
        AND ADVERTISER_ID = '{adv_id}'
        '''.format(adv_id=adv_id)

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/getRentrakData/', methods=['POST'])
@app_login.required_login
@cache
def get_report_data():
    network_search = json.loads(request.data)['network']
    start_timestamp = json.loads(request.data)['start_time']
    end_timestamp = json.loads(request.data)['end_time']
    metrics = json.loads(request.data)['metrics']

    # currently gets first result. eventually need to have user disambiguate
    network = rentrak_api.search_networks(network_search)[0]

    report_parms = dict(select_fields=["NETWORK_NAME", "NETWORK_ID"] + metrics,
                        group_fields=["NETWORK_ID"],
                        dataset_filter="NETWORK_ID={net_id} AND NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'".format(
                            net_id=network['id'], start_time=start_timestamp, end_time=end_timestamp),
                        array_element_length=1)

    report_id = rentrak_api.submit_report(json.dumps(report_parms))['report_id']

    while rentrak_api.get_report_status(report_id).lower() != 'completed' and \
            rentrak_api.get_report_status(report_id).lower() != 'failed':
        time.sleep(2)

    if rentrak_api.get_report_status(report_id).lower() == 'failed':
        raise Exception('Error while submitting report. Report generating returning status "failed"')

    rows = rentrak_api.get_report_rows(report_id)

    return json.dumps(rows)


@app.route('/getRentrakGridData/', methods=['POST'])
@app_login.required_login
@cache
def get_report_grid_data():
    networks_list = json.loads(request.data)['networks']
    start_timestamp = json.loads(request.data)['start_time']
    end_timestamp = json.loads(request.data)['end_time']
    target = json.loads(request.data)['target']

    network_query_string = ''
    for network in networks_list:
        if network_query_string == '':
            network_query_string += '(NETWORK_ID=' + str(network['id'])
        else:
            network_query_string += ' OR NETWORK_ID=' + str(network['id'])
    network_query_string += ')'

    target_filter_string = ''
    if target != '':
        target_filter_string = 'TAG_ID=' + str(target['id'])

    report_parms = dict(select_fields=["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME",
                                       "REACH_LIVE", "REACH_DVR_SAME_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY",
                                       "HOURS_LIVE"],
                        group_fields=["NETWORK_ID", "NATIONAL_DAYPART_ID"],
                        dataset_filter="{net_string} AND NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'".format(
                            net_string=network_query_string, start_time=start_timestamp, end_time=end_timestamp),
                        target_filter=target_filter_string)

    report_id = rentrak_api.submit_report(json.dumps(report_parms))['report_id']

    while rentrak_api.get_report_status(report_id).lower() != 'completed' and \
            rentrak_api.get_report_status(report_id).lower() != 'failed':
        time.sleep(2)

    if rentrak_api.get_report_status(report_id).lower() == 'failed':
        raise Exception('Error while submitting report. Report generating returning status "failed"')

    rows = rentrak_api.get_report_rows(report_id)

    return json.dumps(rows)


@app.route('/getRentrakShowGridData/', methods=['POST'])
@app_login.required_login
@cache
def get_report_show_grid_data():
    network_id = json.loads(request.data)['network_id']
    daypart_id = json.loads(request.data)['daypart_id']
    start_timestamp = json.loads(request.data)['start_time']
    end_timestamp = json.loads(request.data)['end_time']
    target = json.loads(request.data)['target']

    target_filter_string = ''
    if target != '':
        target_filter_string = 'TAG_ID=' + str(target['id'])

    report_parms = dict(select_fields=["NETWORK_NAME", "NETWORK_ID", "NATIONAL_DAYPART_ID", "NATIONAL_DAYPART_NAME",
                                       "REACH_LIVE", "REACH_DVR_SAME_DAY", "REACH_LIVE_PLUS_DVR_SAME_DAY",
                                       "HOURS_LIVE", "SERIES_ID", "SERIES_NAME", "AIRING_NATIONAL_START_TIME"],
                        group_fields=["NETWORK_ID", "NATIONAL_DAYPART_ID", "SERIES_ID"],
                        dataset_filter='''NETWORK_ID = {net_id} AND NATIONAL_TIME>='{start_time}' AND NATIONAL_TIME<'{end_time}'
                         AND NATIONAL_DAYPART_ID = {dpart_id} AND NATIONAL_CONTENT = 1'''.format(
                            net_id=network_id, start_time=start_timestamp, end_time=end_timestamp,
                            dpart_id=daypart_id, target_filter=target_filter_string))

    report_id = rentrak_api.submit_report(json.dumps(report_parms))['report_id']

    while rentrak_api.get_report_status(report_id).lower() != 'completed' and \
            rentrak_api.get_report_status(report_id).lower() != 'failed':
        time.sleep(2)

    if rentrak_api.get_report_status(report_id).lower() == 'failed':
        raise Exception('Error while submitting report. Report generating returning status "failed"')

    rows = rentrak_api.get_report_rows(report_id)

    return json.dumps(rows)


@app.route('/getMetrics/')
@app_login.required_login
def get_metrics():
    return json.dumps(rentrak_api.get_all_metrics(), default=atp_classes.JSONHandler.JSONHandler)


@app.route('/findTags/', methods=['POST'])
@app_login.required_login
@cache
def get_tags():
    search_term = json.loads(request.data)['search']
    return json.dumps(rentrak_api.search_endpoint('tags', search_term), default=atp_classes.JSONHandler.JSONHandler)


@app.route('/admin/getUsers/')
@app_login.required_login
@app_login.required_admin
def get_users():
    users_list = []

    for user in app_db.get_collection('users'):
        user["password"] = ''
        users_list.append(user)

    return json.dumps(users_list, default=atp_classes.JSONHandler.JSONHandler)


@app.route('/admin/updateUser/', methods=['POST'])
@app_login.required_login
@app_login.required_admin
def update_user():
    form_user = json.loads(request.data)['updateUser']
    form_user['password'] = atp_classes.User.generate_hash(form_user['password'])

    return json.dumps(app_db.update_collection('users', form_user),
                      default=atp_classes.JSONHandler.JSONHandler)


@app.route('/admin/addUser/', methods=['POST'])
@app_login.required_login
@app_login.required_admin
def add_user():
    form_user = json.loads(request.data)['addUser']
    form_user['password'] = atp_classes.User.generate_hash(form_user['password'])

    return json.dumps(app_db.add_to_collection('users', form_user),
                      default=atp_classes.JSONHandler.JSONHandler)


@app.route('/admin/removeUser/', methods=['POST'])
@app_login.required_login
@app_login.required_admin
def remove_user():
    form_user = json.loads(request.data)['removeUser']

    if app_db.remove_from_collection('users', form_user) > 0:
        return json.dumps({"status": True})
    else:
        return json.dumps({"status": False})


@app.route('/test/')
@app_login.required_login
def test():
    return json.dumps(rentrak_api.get_endpoint('dayparts'))


@app.errorhandler(Exception)
def handle_exceptions(err):
    err_message = str(err)

    if len(err_message) > 150:
        err_message = err_message[:150] + '...'

    return make_response(err_message, 500)


if __name__ == '__main__':
    app.run(debug=False, host=config.get_config()['host'], threaded=False,
            port=int(os.getenv('PORT', config.get_config()['port'])))
