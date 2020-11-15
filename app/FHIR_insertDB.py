import requests
import json
import datetime
import pyodbc
import sys
import FHIR_combined


# https://r4.smarthealthit.org/Observation?subject%3APatient=7e1f4334-1a53-41a7-b07f-f0203bb55733&code=http://loinc.org|8302-2


def get_data(request_data):
    # id needed to get data, file extension needed for case handling
    if 'resourceType' and 'id' in request_data:
        # handle json case
        if request_data['resourceType'] == 'Patient':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_patient'] + '/' + request_data['id']
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


def search_observation(patient_id):
    # url for testing
    # url = 'https://r4.smarthealthit.org/Observation/_search?subject%3APatient=7e1f4334-1a53-41a7-b07f-f0203bb55733&code=http://loinc.org|8302-2'
    url = FHIR_combined.smart_defaults['api_base'] \
          + '/Observation?subject%3APatient=' + patient_id \
          + '&code=http://loinc.org|21861-0'
    headers = {'Content-Type': 'application/json'}
    res = requests.get(url=url, headers=headers).text
    res = json.loads(res)

    observation_data = dict()
    observation_found = False
    if res['total'] > 0:
        sorted_entry = sorted(res['entry'], key=lambda i: datetime.datetime.strptime(i['resource']['effectiveDateTime'], '%Y-%m-%dT%H:%M:%S%z'), reverse=True)
        effectiveDateTime = datetime.datetime.strptime(sorted_entry[0]['resource']['effectiveDateTime'], '%Y-%m-%dT%H:%M:%S%z')
        observation_data['LastObservedMonth'] = effectiveDateTime.strftime("%m")
        observation_data['LastObservedDay'] = effectiveDateTime.strftime("%d")
        observation_data['LastObservedyear'] = effectiveDateTime.strftime("%Y")
        observation_data['DiagnosedWithCancer'] = 1
        observation_found = True
    else:
        observation_data['DiagnosedWithCancer'] = 0

    return observation_found, observation_data


def map_data(data):
    tb_Worker = dict()
    tb_WorkerRace = dict()
    # TODO: mapping other resources to db
    # mapping data from patient resources
    # improvement: check the 'period' of the data field to find the most recent one
    if data['resourceType'] == 'Patient':
        # map key fields for table Worker
        tb_Worker['WorkerID'] = data['id']
        tb_Worker['StudyCode'] = '0000'
        tb_Worker['GenderCode'] = data['gender']

        # map key fields for table WorkerRace
        tb_WorkerRace['WorkerID'] = data['id']
        tb_WorkerRace['StudyCode'] = '0000'
        tb_WorkerRace['RaceCode'] = '0000'

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
        for x in range(len(data['identifier'])):
            if data['identifier'][x]['system'] == "http://hl7.org/fhir/sid/us-ssn":
                tb_Worker['SSN'] = data['identifier'][x]['value']
        if 'extension' in data:
            for x in range(len(data['extension'])):
                if data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                    for i in range(len(data['extension'][x]['extension']) - 1, -1, -1):
                        if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                            tb_Worker['EthnicityCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                            break
                elif data['extension'][x]['url'] == "http://hl7.org/fhir/StructureDefinition/patient-birthPlace":
                    tb_Worker['BirthPlaceCountry'] = data['extension'][x]['valueAddress']['country']
                    tb_Worker['BirthPlaceCity'] = data['extension'][x]['valueAddress']['city']
                    tb_Worker['BirthPlaceStateProv'] = data['extension'][x]['valueAddress']['state']
                elif data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                    for i in range(len(data['extension'][x]['extension']) - 1, -1, -1):
                        if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                            tb_WorkerRace['RaceCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                            break

        # search for cancer observation of the patient
        observation_found, observation_data = search_observation(data['id'])
        tb_Worker['DiagnosedWithCancer'] = observation_data['DiagnosedWithCancer']
        if observation_found:
            tb_Worker['LastObservedMonth'] = observation_data['LastObservedMonth']
            tb_Worker['LastObservedDay'] = observation_data['LastObservedDay']
            tb_Worker['LastObservedyear'] = observation_data['LastObservedyear']

    else:
        print('Cannot handle this resource type yet')

    return tb_Worker, tb_WorkerRace


def connect_db(uid='sa', pwd='Password!123'):
    # connection db with credentials
    command = 'Driver={ODBC Driver 17 for SQL Server};' + 'Server=localhost,1433;' + 'Database=DFSE_FRB_WORKER;' \
              + 'UID=' + uid + ';' \
              + 'PWD=' + pwd + ';'
    conn = pyodbc.connect(command)
    cursor = conn.cursor()

    # cursor is used as sql query
    return conn, cursor


def close_db(conn, cursor):
    cursor.close()
    conn.close()

    return 0


def insert_table(cursor, table, tableName):
    # generate query command for insertion
    command_fields = 'INSERT INTO worker.' + tableName + ' ('
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
    command = 'SELECT * FROM worker.' + tableName
    cursor.execute(command)
    count = 0

    print('All data in table', tableName, ': ')
    for row in cursor:
        print(row)
        count += 1
    print('Total in table', tableName, ': ', count)
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
            for j in range(len(list_Worker)):
                if list_Worker[j]:
                    insert_table(cursor, list_Worker[j], 'Worker')
            for i in range(len(list_WorkerRace)):
                if list_WorkerRace[i]:
                    insert_table(cursor, list_WorkerRace[i], 'WorkerRace')

            # check if the insertion is succeed
            check_table_insertion(cursor, 'Worker')
            check_table_insertion(cursor, 'WorkerRace')

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
        # ignore second return value which is for testing
        # post data to FHIR server
        data_posted, *_ = FHIR_combined.verify_fhir(sys.argv[1])
        if isinstance(data_posted, dict):
            # FHIR server data retrieval and SQL database insertion
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
                data_id, *_ = FHIR_combined.verify_fhir(file)
                if isinstance(data_id, dict):
                    returnValue = post_db(data_id)
