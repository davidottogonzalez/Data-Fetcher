import teradata
import atp_classes, re


class TeradataDB:

    def __init__(self, host=None, port=None, username=None, password=None, database=None, auth_mech=None):
        config = atp_classes.Config()
        self.host = host or config.get_config()['database']['dataWarehouse']['host']
        self.username = username or config.get_config()['database']['dataWarehouse']['username']
        self.password = password or config.get_config()['database']['dataWarehouse']['password']

    def execute_query(self, query_string):
        result_rows = []
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
        return result_rows
