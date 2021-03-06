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
        AND sdf.advertiser_id = {ad_id}
        AND sdf.brand_id = {brand_id}
        AND sdf.deal_id = {deal_id}
        AND brdcast_week_id >= {st_week_id}
        AND brdcast_week_id <= {end_week_id}
        AND business_type_cd = 'CURRENT_CONTRACTS'
        ''' \
        .format(ad_id=form_params['ad_id'], brand_id=form_params['brand_id'], deal_id=form_params['deal_id'],
                st_week_id=form_params['st_week_id'], end_week_id=form_params['end_week_id'])

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

    query_string = '''
        SELECT ADVERTISER_ID, ADVERTISER_NAME
        FROM ADVERTISER
        WHERE LOWER(ADVERTISER_NAME) LIKE LOWER('{search}%')
        AND SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/findBrands/', methods=['POST'])
@app_login.required_login
@cache
def find_brands():
    search = json.loads(request.data)['search']

    query_string = '''
        SELECT BRAND_ID, BRAND_NAME
        FROM BRAND
        WHERE LOWER(BRAND_NAME) LIKE LOWER('{search}%')
        AND SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

    results = teradata_db.execute_query(query_string)

    if not isinstance(results, list):
        raise Exception(results)

    return json.dumps(results)


@app.route('/findDeals/', methods=['POST'])
@app_login.required_login
@cache
def find_deals():
    search = json.loads(request.data)['search']

    query_string = '''
        SELECT DISTINCT DEAL_NAME, DEAL_ID
        FROM sales_detail_fact
        WHERE LOWER(DEAL_NAME) LIKE LOWER('{search}%')
        AND SRC_SYS_ID = 1030
        ''' \
        .format(search=search)

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
                            net_id=network['id'], start_time=start_timestamp, end_time=end_timestamp))

    report_id = rentrak_api.submit_report(json.dumps(report_parms))['report_id']

    while rentrak_api.get_report_status(report_id) != 'Completed':
        time.sleep(2)

    rows = rentrak_api.get_report_rows(report_id)

    return json.dumps(rows)


@app.route('/getMetrics/')
@app_login.required_login
def get_metrics():
    return json.dumps(rentrak_api.get_all_metrics(), default=atp_classes.JSONHandler.JSONHandler)


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


@app.errorhandler(Exception)
def handle_exceptions(err):
    err_message = str(err)

    if len(err_message) > 150:
        err_message = err_message[:150] + '...'

    return make_response(err_message, 500)


if __name__ == '__main__':
    app.run(debug=False, host=config.get_config()['host'], threaded=False,
            port=int(os.getenv('PORT', config.get_config()['port'])))
