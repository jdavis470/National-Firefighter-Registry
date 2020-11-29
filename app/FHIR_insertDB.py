import requests
import json
import datetime
import pyodbc
import sys
import FHIR_combined


def get_data(request_data):
    """
        GETting the resource data from the FHIR server by HTTP request based on different resource type.

        Args:
            request_data: Dict type of resource data ID and its resource type.

        Returns:
            res: Dict type of response data from the server after HTTP request.
    """
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
        elif request_data['resourceType'] == 'Observation':
            headers = {'Content-Type': 'application/json'}
            url = FHIR_combined.smart_defaults['api_observation'] + '/' + request_data['id']
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
    """
        Search for the cancer observations of the patient on the FHIR server by HTTP request.

        Args:
            patient_id: String type of patient ID.

        Returns:
            observation_found: Boolean to indicate whether the cancer observation is found.
            observation_data: Dict type of the mapped observation data.
    """
    url = FHIR_combined.smart_defaults['api_base'] \
          + '/Observation?subject%3APatient=' + patient_id \
          + '&code=http://loinc.org|21861-0'
    headers = {'Content-Type': 'application/json'}
    res = requests.get(url=url, headers=headers).text
    res = json.loads(res)

    observation_data = dict()
    observation_found = False
    # when the relevant observations exist, return the required information for the database table
    if res['total'] > 0:
        sorted_entry = sorted(res['entry'], key=lambda i: datetime.datetime.strptime(handle_dates(i['resource']),
                                                                                     '%Y-%m-%dT%H:%M:%S%z'),
                              reverse=True)
        effectiveDateTime = datetime.datetime.strptime(handle_dates(sorted_entry[0]['resource']), '%Y-%m-%dT%H:%M:%S%z')
        observation_data['LastObservedMonth'] = effectiveDateTime.strftime("%m")
        observation_data['LastObservedDay'] = effectiveDateTime.strftime("%d")
        observation_data['LastObservedyear'] = effectiveDateTime.strftime("%Y")
        observation_data['DiagnosedWithCancer'] = 1
        observation_found = True
    else:
        observation_data['DiagnosedWithCancer'] = 0

    return observation_found, observation_data


def create_observation_dict(data):
    """
        Create the observation entry that maps to the database table.

        Args:
            data: Dict type of observation data getting from the FHIR server.

        Returns:
            observation_data: Dict type of the mapped observation data.
    """
    observation_data = dict()
    effectiveDateTime = datetime.datetime.strptime(handle_dates(data), '%Y-%m-%dT%H:%M:%S%z')
    observation_data['LastObservedMonth'] = effectiveDateTime.strftime("%m")
    observation_data['LastObservedDay'] = effectiveDateTime.strftime("%d")
    observation_data['LastObservedyear'] = effectiveDateTime.strftime("%Y")
    observation_data['DiagnosedWithCancer'] = 1
    return observation_data


# Note: Python 3.7 fixes this problem
# see: https://stackoverflow.com/questions/41684991/datetime-strptime-2017-01-12t141206-000-0500-y-m-dthms-fz
def handle_dates(i):
    d = i['effectiveDateTime']
    if ":" == d[-3]:
        d = d[:-3] + d[-2:]
    return d


def map_data(data, path):
    """
        Map the resource data to our database tables.

        Args:
            data: Dict type of resource data getting from the FHIR server.

            path: String type of source file path.

        Returns:
            tb_Worker: Dict type of the mapped data to the database table 'Worker'.

            tb_WorkerRace: Dict type of the mapped data to the database table 'WorkerRace'.
    """
    tb_Worker = dict()
    tb_WorkerRace = dict()
    # mapping data from patient resources
    if data['resourceType'] == 'Patient':
        # map the Worker ID
        tb_Worker['WorkerID'] = data['id']
        tb_WorkerRace['WorkerID'] = data['id']

        # map key fields for table Worker
        # StudyCode fixes as 'NFR'
        tb_Worker['StudyCode'] = 'NFR'
        # GenderCode read from gender field in patient FHIR standard
        tb_Worker['GenderCode'] = data['gender']
        # Source file is the path the file was read in from 
        tb_Worker['SourceFile'] = path
        tb_Worker['ImportCode'] = 'NFR_Script'

        # map key fields for table WorkerRace
        tb_WorkerRace['StudyCode'] = 'NFR'
        tb_WorkerRace['RaceCode'] = '0000'
        tb_WorkerRace['SourceFile'] = path
        tb_WorkerRace['ImportCode'] = 'NFR_Script'

        # For address we read in the most recent address in the patient FHIR standard
        if 'address' in data:
            tb_Worker['CurrentResidentialStreet'] = data['address'][-1]['line'][0]
            tb_Worker['CurrentResidentialCity'] = data['address'][-1]['city']
            tb_Worker['CurrentResidentialStateProv'] = data['address'][-1]['state']
            if 'postalCode' in data['address'][-1]:
                tb_Worker['CurrentResidentialPostalCode'] = data['address'][-1]['postalCode']
            tb_Worker['CurrentResidentialCountry'] = data['address'][-1]['country']
        # Mapping logic for name:
        # If only one name provided, use it as their primary name (not alias)
        # else >1 name provided check to see if use exists
        # If it does, look for official (primary) and nickname (alias)
        # If primary name wasn't found, set it to the last value in name array
        if len(data['name']) == 1:
            tb_Worker['LastName'] = data['name'][-1]['family']
            if len(data['name'][-1]['given']) > 1:
                tb_Worker['FirstName'] = data['name'][-1]['given'][0]
                tb_Worker['MiddleName'] = data['name'][-1]['given'][1]
            else:
                tb_Worker['FirstName'] = data['name'][-1]['given'][0]
        else:
            for name in data['name']:
                if 'use' in name:
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
            if 'FirstName' not in tb_Worker:
                tb_Worker['LastName'] = data['name'][-1]['family']
                if len(data['name'][-1]['given']) > 1:
                    tb_Worker['FirstName'] = data['name'][-1]['given'][0]
                    tb_Worker['MiddleName'] = data['name'][-1]['given'][1]
                else:
                    tb_Worker['FirstName'] = data['name'][-1]['given'][0]
        # Phone number and email are both found in telecom section of patient FHIR data standard
        if 'telecom' in data:
            for telecom in data['telecom']:
                if telecom['system'] == 'phone' and telecom['use'] == 'mobile':
                    tb_Worker['MobilePhoneNumber'] = telecom['value']
                elif telecom['system'] == 'email':
                    tb_Worker['PrimaryEmailAddress'] = telecom['value']
        # We read in Birth Data and break it into Month, Day, Year
        birthDate = datetime.datetime.strptime(data['birthDate'], '%Y-%m-%d')
        # Database table will convert them into birthDate automatically
        tb_Worker['BirthMonth'] = birthDate.strftime("%m")
        tb_Worker['BirthDay'] = birthDate.strftime("%d")
        tb_Worker['Birthyear'] = birthDate.strftime("%Y")
        # We read SSN from identifier section of FHIR Patient standard
        for x in range(len(data['identifier'])):
            if data['identifier'][x]['system'] == "http://hl7.org/fhir/sid/us-ssn":
                tb_Worker['SSN'] = data['identifier'][x]['value']
        if 'extension' in data:
            for x in range(len(data['extension'])):
                # We read in us-core-ethinicy extention for paitent ethnicity
                if data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                    for i in range(len(data['extension'][x]['extension']) - 1, -1, -1):
                        if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                            tb_Worker['EthnicityCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                            break
                # We read in patient-birthPlace extention for paitent birth place
                elif data['extension'][x]['url'] == "http://hl7.org/fhir/StructureDefinition/patient-birthPlace":
                    tb_Worker['BirthPlaceCountry'] = data['extension'][x]['valueAddress']['country']
                    tb_Worker['BirthPlaceCity'] = data['extension'][x]['valueAddress']['city']
                    tb_Worker['BirthPlaceStateProv'] = data['extension'][x]['valueAddress']['state']
                # We read in us-core-race extention for paitent race
                elif data['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                    for i in range(len(data['extension'][x]['extension']) - 1, -1, -1):
                        if 'valueCoding' in data['extension'][x]['extension'][i].keys():
                            tb_WorkerRace['RaceCode'] = data['extension'][x]['extension'][i]['valueCoding']['code']
                            break

        # search for cancer observation of the patient
        observation_found, observation_data = search_observation(data['id'])
        tb_Worker['DiagnosedWithCancer'] = observation_data['DiagnosedWithCancer']
        if observation_found:
            # We update last patient observation date if cancer observation found
            tb_Worker['LastObservedMonth'] = observation_data['LastObservedMonth']
            tb_Worker['LastObservedDay'] = observation_data['LastObservedDay']
            tb_Worker['LastObservedyear'] = observation_data['LastObservedyear']
        # determine if this is an update or an insert,
        tb_Worker['isUpdate'] = False

    elif data['resourceType'] == 'Observation':
        # find the patient attached to the observation
        subjectId = data['subject']['reference'].split('/')[1]
        observation_data = create_observation_dict(data)
        tb_Worker['WorkerID'] = subjectId
        tb_Worker['DiagnosedWithCancer'] = observation_data['DiagnosedWithCancer']
        tb_Worker['LastObservedMonth'] = observation_data['LastObservedMonth']
        tb_Worker['LastObservedDay'] = observation_data['LastObservedDay']
        tb_Worker['LastObservedyear'] = observation_data['LastObservedyear']
        tb_Worker['isUpdate'] = True
    else:
        print('Cannot handle this resource type yet')

    return tb_Worker, tb_WorkerRace


def connect_db(uid='sa', pwd='Password!123'):
    """
        Connect to the database with specific credentials.

        Args:
            uid: String type of user id, by default system administrator.

            pwd: String type of password, by default system administrator.

        Returns:
            conn: the connection String to the database.

            cursor: the cursor for the connection.
    """
    # connection db with credentials
    command = 'Driver={ODBC Driver 17 for SQL Server};' + 'Server=localhost,1433;' + 'Database=DFSE_FRB_WORKER;' \
              + 'UID=' + uid + ';' \
              + 'PWD=' + pwd + ';'
    conn = pyodbc.connect(command)
    cursor = conn.cursor()

    # cursor is used as sql query
    return conn, cursor


def close_db(conn, cursor):
    """
        Close the database connection.

        Args:
            conn: the connection String to the database.

            cursor: the cursor for the connection.
    """
    cursor.close()
    conn.close()

    return 0


def insert_table(cursor, table, tableName):
    """
        Insert a new entry to the database table.

        Args:
            cursor: the cursor for the database connection.

            table: Dict type of mapped resource data that inserts to the table.

            tableName: String type of target table name.

        Returns:
            command: String type of the insertion command.
    """
    # generate query command for insertion
    command_fields = 'INSERT INTO worker.' + tableName + ' ('
    command_values = 'SELECT '

    # mapping data for the command
    for key, value in table.items():
        if key == 'isUpdate':
            continue
        if isinstance(value, str):
            # if the insertion value has quotation marks, they need to
            # replace with double quotation marks to be a valid command
            insert_value = value.replace('\'', '\'\'')
        else:
            insert_value = str(value)
        command_fields += key + ','
        command_values += '\'' + insert_value + '\','

    command_fields = command_fields[:-1] + ') '
    command_values = command_values[:-1] + ';'
    command = command_fields + command_values

    # execute and commit insertion
    cursor.execute(command)
    cursor.commit()
    print('Data is inserted to table', tableName, ':', command_values[7:-1])

    return command


def check_table_insertion(cursor, tableName):
    """
        Debug function to print out the entries on the database tables.

        Args:
            cursor: the cursor for the database connection.

            tableName: String type of target table name.
    """
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


def update_table(cursor, table, tableName):
    """
        Update the existing entry on the database table.

        Args:
            cursor: the cursor for the database connection.

            table: Dict type of mapped resource data that updates the table.

            tableName: String type of target table name.

        Returns:
            command: String type of the update command.
    """
    # generate query command for insertion
    command = 'UPDATE worker.' + tableName + ' SET '
    command_values = ''
    command_condition = ' WHERE WorkerID = \'' + table['WorkerID'] + '\';'
    for key, value in table.items():
        if key == 'WorkerID' or key == 'isUpdate':
            continue
        if isinstance(value, str):
            insert_value = value.replace('\'', '\'\'')
        else:
            insert_value = str(value)
        command_line = key + '=\'' + insert_value + '\','
        command_values += command_line
    command_values = command_values[:-1]
    command = command + command_values + command_condition

    # execute insertion
    try:
        cursor.execute(command)
        cursor.commit()
        print('Data is updated to table', tableName, ':', command_values + ' on Worker with Id: ' + table['WorkerID'])
    except Exception as e:
        print("did not find the Worker to attach this observation on: " + e)
        return
    return command


def post_db(data_posted, path):
    """
        Perform the data insertion/update on our database tables.

        Args:
            data_posted: Dict type of resource data ID and its resource type for the data insertion/update.

            path: String type of source file path.
    """
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
                        tb_Worker, tb_WorkerRace = map_data(resource_data['resource'], path)
                        if tb_Worker:
                            list_Worker.append(tb_Worker)
                        if tb_WorkerRace:
                            list_WorkerRace.append(tb_WorkerRace)
        else:
            # map the response data into our database table fields
            tb_Worker, tb_WorkerRace = map_data(data_received, path)
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
                    if list_Worker[j]['isUpdate'] is True:
                        update_table(cursor, list_Worker[j], 'Worker')
                    else:
                        insert_table(cursor, list_Worker[j], 'Worker')
            for i in range(len(list_WorkerRace)):
                if list_WorkerRace[i]:
                    insert_table(cursor, list_WorkerRace[i], 'WorkerRace')

            # check if the insertion is succeed (DEBUG Printout)
            # check_table_insertion(cursor, 'Worker')
            # check_table_insertion(cursor, 'WorkerRace')

            # close db connection
            close_db(conn, cursor)
        else:
            print('no data is inserted to the database')
        return 0
    else:
        print('failed to retrieve data from FHIR server')
        return -1


def usage():
    """
        Print out an error message when the program is called incorrectly.
    """
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
            returnValue = post_db(data_posted, sys.argv[1])

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
                    returnValue = post_db(data_id, file)
