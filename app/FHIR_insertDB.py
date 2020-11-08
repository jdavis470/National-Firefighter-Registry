import requests
import json
import datetime
import pyodbc
import sys
import FHIR_combined


def get_data(request_data):
    # id needed to get data, file extension needed for case handling
    if 'resourceType' and 'id' in request_data:
        # handle json case
        if request_data['resourceType'] == 'Patient':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_base'] + '/' + request_data['id']
            res = requests.get(url=url, headers=headers).text
            res = json.loads(res)
            return res
        elif request_data['resourceType'] == 'Bundle':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_bundle'] + '/' + request_data['id']
            res = requests.get(url=url, headers=headers).text
            res = json.loads(res)
            return res
        else:
            print('Cannot handle this resource type yet')
            return 0
    else:
        print('resource type and id should be provided to get data')
        return -1


def map_data(data):
    tb_Worker = dict()
    tb_WorkerRace = dict()
    # TODO: mapping other resources to db
    # mapping data from patient resources
    # improvement: check the 'period' of the data field to find the most recent one
    if data['resourceType'] == 'Patient':
        # map for table Worker
        tb_Worker['WorkerID'] = data['id']
        tb_Worker['StudyCode'] = '0000'
        tb_Worker['GenderCode'] = data['gender']
        if 'address' in data:
            tb_Worker['CurrentResidentialStreet'] = data['address'][-1]['line'][0]
            tb_Worker['CurrentResidentialCity'] = data['address'][-1]['city']
            tb_Worker['CurrentResidentialStateProv'] = data['address'][-1]['state']
            if 'postalCode' in data['address'][-1]:
                tb_Worker['CurrentResidentialPostalCode'] = data['address'][-1]['postalCode']
            tb_Worker['CurrentResidentialCountry'] = data['address'][-1]['country']
        tb_Worker['LastName'] = data['name'][-1]['family']
        if len(data['name'][-1]['given']) > 1:
            tb_Worker['FirstName'] = data['name'][-1]['given'][0]
            tb_Worker['MiddleName'] = data['name'][-1]['given'][1]
        else:
            tb_Worker['FirstName'] = data['name'][-1]['given'][0]
        if 'telecom' in data:
            for telecom in data['telecom']:
                if telecom['system'] == 'phone' and telecom['use'] == 'mobile':
                    tb_Worker['MobilePhoneNumber'] = telecom['value']
                elif telecom['system'] == 'email':
                    tb_Worker['PrimaryEmailAddress'] = telecom['value']
        # tb_Worker['BirthDate'] = data['birthDate']
        birthDate = datetime.datetime.strptime(data['birthDate'], '%Y-%m-%d')
        tb_Worker['BirthMonth'] = birthDate.strftime("%m")
        tb_Worker['BirthDay'] = birthDate.strftime("%d")
        tb_Worker['Birthyear'] = birthDate.strftime("%Y")

        # map for table WorkerRace
        tb_WorkerRace['WorkerID'] = data['id']
        tb_WorkerRace['StudyCode'] = '0000'
        tb_WorkerRace['RaceCode'] = '0000'

    else:
        print('Cannot handle this resource type yet')

    return tb_Worker, tb_WorkerRace

def connect_db():
    # connection db with credentials
    # improvement: make credentials as parameters
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server=localhost,1433;'
                          'Database=FIREFIGHTER;'
                          'UID=sa;'
                          'PWD=Password!123;')
    cursor = conn.cursor()

    # cursor is used as sql query
    return conn, cursor


def close_db(conn, cursor):
    cursor.close()
    conn.close()

    return 0


def insert_table(cursor, table, tableName):
    # generate query command for insertion
    command_fields = 'INSERT INTO dbo.' + tableName + ' ('
    command_values = 'SELECT '

    # mapping data for the command
    for key, value in table.items():
        insert_value = value.replace('\'', '\'\'')
        command_fields += key + ','
        command_values += '\'' + insert_value + '\','

    command_fields = command_fields[:-1] + ') '
    command_values = command_values[:-1] + ';'
    command = command_fields + command_values

    # execute insertion
    cursor.execute(command)
    cursor.commit()
    print('Data is inserted to table', tableName, ':', command_values[7:-1])

    return command


def check_table_insertion(cursor, tableName):
    # get all data from the table as checking
    command = 'SELECT * FROM FIREFIGHTER.dbo.' + tableName
    cursor.execute(command)

    print('All data in table', tableName, ': ')
    for row in cursor:
        print(row)

    return 0


def post_db(data_posted):
    # get data from FHIR server by ID
    data_received = get_data(data_posted)

    if isinstance(data_received, dict):
        list_Worker = list()
        list_WorkerRace = list()

        # retrieve single data from bundle type
        if data_received['resourceType'] == 'Bundle':
            if 'entry' in data_received:
                for resource_data in data_received['entry']:
                    if 'resource' in resource_data:
                        # map server data to db fields
                        tb_Worker, tb_WorkerRace = map_data(resource_data['resource'])
                        if tb_Worker:
                            list_Worker.append(tb_Worker)
                        if tb_WorkerRace:
                            list_WorkerRace.append(tb_WorkerRace)
        else:
            tb_Worker, tb_WorkerRace = map_data(data_received)
            if tb_Worker:
                list_Worker.append(tb_Worker)
            if tb_WorkerRace:
                list_WorkerRace.append(tb_WorkerRace)

        # process further if the mapped tables are not empty
        if len(list_Worker) > 0 or len(list_WorkerRace) > 0:
            # connect local db server (docker db should be on)
            conn, cursor = connect_db()
            # db insertion
            for i in range(len(list_WorkerRace)):
                if list_WorkerRace[i]:
                    insert_table(cursor, list_WorkerRace[i], 'WorkerRace')
            for j in range(len(list_Worker)):
                if list_Worker[j]:
                    insert_table(cursor, list_Worker[j], 'Worker')

            # check if the insertion is succeed
            check_table_insertion(cursor, 'WorkerRace')
            check_table_insertion(cursor, 'Worker')

            # close db connection
            close_db(conn, cursor)
        else:
            print('no data is inserted to the database')
        return 0
    else:
        print('failed to retrieve data from FHIR server')
        return -1


def usage():
    print("Usage: FHIR_insertDB.py <file_to_verify>"
          "   or  FHIR_insertDB.py")


if __name__ == "__main__":
    if (len(sys.argv) > 2):
        print(
            "Error, if providing an argument you must provide exactly 1 argument for the path to the data file that will be verified.")
        usage()
        exit(1)

    # Command Line Argument Mode
    elif (len(sys.argv) == 2):
        data_posted = FHIR_combined.verify_fhir(sys.argv[1])
        returnValue = post_db(data_posted)

        if (returnValue != 0):
            usage()

        exit(returnValue)

    # Interactive mode
    else:
        while (1):
            file = input("Give file path or type exit to quit: ")
            if file == 'exit':
                break
            else:
                # post data to FHIR server
                data_posted = FHIR_combined.verify_fhir(file)

                if isinstance(data_posted, dict):
                    # FHIR server data retrieval and SQL database insertion
                    returnValue = post_db(data_posted)
