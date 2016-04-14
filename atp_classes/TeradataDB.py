import atp_classes, re, platform, os
import jaydebeapi, jpype
import teradata, time, sys, subprocess, json


class TeradataDB:
    is_executing = False

    def __init__(self, host=None, port=None, username=None, password=None, database=None, auth_mech=None):
        config = atp_classes.Config()
        self.host = host or config.get_config()['database']['dataWarehouse']['host']
        self.username = username or config.get_config()['database']['dataWarehouse']['username']
        self.password = password or config.get_config()['database']['dataWarehouse']['password']

    def execute_query(self, query_string):
        result_rows = []

        if platform.mac_ver()[0] != '':
            udaExec = teradata.UdaExec(appName="DataFetcher", version="1.0", logConsole=False)

            with udaExec.connect(method="odbc", system=self.host, username=self.username, password=self.password)as conn:
                with conn.cursor() as cur:
                    try:
                        print "executing query"

                        # Execute query
                        cur.execute(query_string)

                        print "done executing query"

                        # Get column names
                        columns = cur.description

                        # Fetch table results
                        for row in cur:
                            result_obj = {}
                            for index, val in enumerate(columns):
                                # Remove characters and dot which precedes column name for key values
                                result_obj[re.sub(r'.*[.]', '', val[0])] = str(row[index]).strip()
                            result_rows.append(result_obj)
                    except Exception, e:
                        return e

            conn.close()
        else:
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))

                while self.is_executing:
                    time.sleep(2)

                self.is_executing = True

                subprocess.call([sys.executable, os.path.join(current_dir, 'TeradataDB.py'), query_string], env=os.environ.copy())

                with open("jdbc_results.json") as json_file:
                    result_rows = json.load(json_file)

                self.is_executing = False
            except Exception, e:
                self.is_executing = False
                return e

        return result_rows

    def jdbc_execute_query(self, query_string):
        result_rows = []

        if not jpype.isJVMStarted():
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            jar = r'{lib_path_gss}{java_sep}{lib_path_jdbc}'.format(lib_path_gss=os.path.join(current_dir,"lib",'tdgssconfig.jar'),
                                                                    java_sep=os.pathsep,
                                                                    lib_path_jdbc=os.path.join(current_dir,'lib','terajdbc4.jar'))
            args='-Djava.class.path=%s' % jar

            if 'JVM_PATH' in os.environ:
                jvm_path = os.environ['JVM_PATH']
            else:
                jvm_path = jpype.getDefaultJVMPath()

            jpype.startJVM(jvm_path, args)

        conn = jaydebeapi.connect('com.teradata.jdbc.TeraDriver','jdbc:teradata://{url}/USER={user},PASSWORD={password}'
                                  .format(url=self.host, user=self.username, password=self.password))
        cur = conn.cursor()
        print "executing query"

        # Execute query
        cur.execute(query_string)

        print "done executing query"

        # Get column names
        columns = cur.description

        # Fetch table results
        for row in cur.fetchall():
            result_obj = {}
            for index, val in enumerate(columns):
                # Remove characters and dot which precedes column name for key values
                result_obj[re.sub(r'.*[.]', '', val[0])] = str(row[index]).strip()
            result_rows.append(result_obj)

        cur.close()
        conn.close()

        return result_rows

if __name__ == '__main__':
    teradata_db = TeradataDB()

    print sys.argv[1]
    results = teradata_db.jdbc_execute_query(sys.argv[1])

    with open('jdbc_results.json', 'w') as outfile:
        json.dump(results, outfile)
