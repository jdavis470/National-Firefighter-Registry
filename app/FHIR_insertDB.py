import requests
import json
import datetime
import pyodbc
import sys
import FHIR_combined


def get_data(request_data):
    # id needed to get data, file extension needed for case handling
    if 'file_extension' and 'id' in request_data:
        # handle json case
        if request_data['file_extension'] == '.json':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_base'] + '/' + request_data['id']
            res = requests.get(url=url, headers=headers).text
            res = json.loads(res)
            return res
        else:
            print('Cannot handle this file yet')
            return 0
    elif 'file_extension' and 'id' in request_data['Patient']:
        if request_data['file_extension'] == '.xml':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_base'] + '/' + str(request_data['Patient']['id']['@value'])
            res = requests.get(url=url, headers=headers).text
            res = json.loads(res)
            return res
        else:
            print('Cannot handle this file yet')
            return 0

    else:
        print('file extension and id should be provided to get data')
        return 0


def map_data(data):
    tb_Worker = dict()
    tb_WorkerRace = dict()
    # TODO: mapping other resources to db
    # mapping data from patient resources
    # improvement: check the 'period' of the data field to find the most recent one
    if data['resourceType'] == 'Patient':
        # map for table Worker
        for x in range(len(data['identifier'])):
            if data['identifier'][x]['use'] == "official":
                tb_Worker['WorkerID'] = data['identifier'][x]['value']
        tb_Worker['StudyCode'] = 'NFR'
        tb_Worker['GenderCode'] = data['gender']
        tb_Worker['CurrentResidentialStreet'] = data['address'][-1]['line'][0]
        tb_Worker['CurrentResidentialCity'] = data['address'][-1]['city']
        tb_Worker['CurrentResidentialStateProv'] = data['address'][-1]['state']
        tb_Worker['CurrentResidentialPostalCode'] = data['address'][-1]['postalCode']
        tb_Worker['CurrentResidentialCountry'] = data['address'][-1]['country']
        if len(data['name']) == 1:
            tb_Worker['LastName'] = data['name'][-1]['family']
            if len(data['name'][-1]['given']) > 1:
                tb_Worker['FirstName'] = data['name'][-1]['given'][0]
                tb_Worker['MiddleName'] = data['name'][-1]['given'][1]
            else:
                tb_Worker['FirstName'] = data['name'][-1]['given'][0]
        else:
            for name in data['name']:
                if name['use'] == "official":
                    tb_Worker['LastName'] = name['family']
                    if len(name['given']) > 1:
                        tb_Worker['FirstName'] = name['given'][0]
                        tb_Worker['MiddleName'] = name['given'][1]
                    else:
                        tb_Worker['FirstName'] = name['given'][0]
                elif name['use'] == "nickname":
                    tb_Worker['LastNameAlias'] = name['family']
                    if len(name['given']) > 1:
                        tb_Worker['FirstNameAlias'] = name['given'][0]
                        tb_Worker['MiddleNameAlias'] = name['given'][1]
                    else:
                        tb_Worker['FirstNameAlias'] = name['given'][0]
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
        for x in range(len(data['identifier'])):
            if data['identifier'][x]['system'] == "http://hl7.org/fhir/sid/us-ssn":
                tb_Worker['SSN'] = data['identifier'][x]['value']
        for x in range(len(data['extension'])):
            if data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                for i in range(len(data['extension'][x]['extension'])-1, -1, -1):
                    if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                        tb_Worker['EthnicityCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                        break
        for x in range(len(data['extension'])):
            if data['extension'][x]['url'] == "http://hl7.org/fhir/StructureDefinition/patient-birthPlace":
                tb_Worker['BirthPlaceCountry'] = data['extension'][x]['valueAddress']['country']
                tb_Worker['BirthPlaceCity'] = data['extension'][x]['valueAddress']['city']
                tb_Worker['BirthPlaceStateProv'] = data['extension'][x]['valueAddress']['state']

        # map for table WorkerRace
        tb_WorkerRace['WorkerID'] = data['id']
        tb_WorkerRace['StudyCode'] = '0000'
        for x in range(len(data['extension'])):
            if data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                for i in range(len(data['extension'][x]['extension'])-1, -1, -1):
                    if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                        tb_WorkerRace['RaceCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                        break
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
        command_fields += key + ','
        command_values += '\'' + value + '\','

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

    return


def post_db(data_posted):
    # get data from FHIR server by ID
    data_received = get_data(data_posted)
    # map server data to db fields
    tb_Worker, tb_WorkerRace = map_data(data_received)

    # connect local db server (docker db should be on)
    conn, cursor = connect_db()
    # db insertion
    insert_table(cursor, tb_WorkerRace, 'WorkerRace')
    insert_table(cursor, tb_Worker, 'Worker')

    # check if the insertion is succeed
    check_table_insertion(cursor, 'WorkerRace')
    check_table_insertion(cursor, 'Worker')

    # close db connection
    close_db(conn, cursor)

    return 0


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
            # post data to FHIR server
            data_posted = FHIR_combined.verify_fhir(file)

            # FHIR server data retrieval and SQL database insertion
            returnValue = post_db(data_posted)
