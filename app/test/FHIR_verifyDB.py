import pyodbc
import sys

sys.path.append('../')
import FHIR_insertDB
import FHIR_combined
import datetime


def connect_db(uid='sa', pwd='Password!123'):
    # connection db with credentials
    command = 'Driver={ODBC Driver 17 for SQL Server};' + 'Server=localhost,1433;' + 'Database=DFSE_FRB_WORKER;' \
              + 'UID=' + uid + ';' \
              + 'PWD=' + pwd + ';'
    conn = pyodbc.connect(command)

    return conn


def close_db(conn, cursor):
    cursor.close()
    conn.close()

    return 0


def assert_data(data_posted, cursor):
    # Execute query for patient ID on Worker table
    command = 'SELECT * FROM worker.Worker WHERE WorkerID = ' + '\'' + data_posted['id'] + '\''
    cursor.execute(command)
    worker_item = cursor.fetchone()

    # Build Dictionary from column information and query data
    worker_columns = [column[0] for column in cursor.description]
    worker_db_result = dict(zip(worker_columns, worker_item))

    # Execute query for patient ID on WorkerRace table
    command = 'SELECT * FROM worker.WorkerRace WHERE WorkerID = ' + '\'' + data_posted['id'] + '\''
    cursor.execute(command)
    workerRace_item = cursor.fetchone()
    # Build Dictionary from column information and query data
    workerRace_columns = [column[0] for column in cursor.description]
    workerRace_db_result = dict(zip(workerRace_columns, workerRace_item))

    # Verify key fields of the Worker data
    assert worker_db_result['StudyCode'] == 'NFR'
    assert worker_db_result['GenderCode'] == data_posted['gender']
    # Verify key fields of the WorkerRace data
    assert workerRace_db_result['StudyCode'] == 'NFR'
    race_code = '0000'
    # Verify other fields
    if 'address' in data_posted:
        assert worker_db_result['CurrentResidentialStreet'] == data_posted['address'][-1]['line'][0]
        assert worker_db_result['CurrentResidentialCity'] == data_posted['address'][-1]['city']
        assert worker_db_result['CurrentResidentialStateProv'] == data_posted['address'][-1]['state']
        if 'postalCode' in data_posted['address'][-1]:
            assert worker_db_result['CurrentResidentialPostalCode'] == data_posted['address'][-1]['postalCode']
        assert worker_db_result['CurrentResidentialCountry'] == data_posted['address'][-1]['country']
    if len(data_posted['name']) == 1:
        assert worker_db_result['LastName'] == data_posted['name'][-1]['family']
        if len(data_posted['name'][-1]['given']) > 1:
            assert worker_db_result['FirstName'] == data_posted['name'][-1]['given'][0]
            assert worker_db_result['MiddleName'] == data_posted['name'][-1]['given'][1]
        else:
            assert worker_db_result['FirstName'] == data_posted['name'][-1]['given'][0]
    else:
        for x in range(len(data_posted['name'])):
            if 'use' in data_posted['extension'][x]:
                if data_posted['extension'][x]['use'] == "official":
                    assert worker_db_result['LastName'] == data_posted['name'][x]['family']
                    if len(data_posted['name'][x]['given']) > 1:
                        assert worker_db_result['FirstName'] == data_posted['name'][x]['given'][0]
                        assert worker_db_result['MiddleName'] == data_posted['name'][x]['given'][1]
                    else:
                        assert worker_db_result['FirstName'] == data_posted['name'][x]['given'][0]
                elif data_posted['extension'][x]['use'] == "nickname":
                    assert worker_db_result['LastNameAlias'] == data_posted['name'][x]['family']
                    if len(data_posted['name'][x]['given']) > 1:
                        assert worker_db_result['FirstNameAlias'] == data_posted['name'][x]['given'][0]
                        assert worker_db_result['MiddleNameAlias'] == data_posted['name'][x]['given'][1]
                    else:
                        assert worker_db_result['FirstNameAlias'] == data_posted['name'][x]['given'][0]
    if 'telecom' in data_posted:
        for telecom in data_posted['telecom']:
            if telecom['system'] == 'phone' and telecom['use'] == 'mobile':
                assert worker_db_result['MobilePhoneNumber'] == telecom['value']
            elif telecom['system'] == 'email':
                assert worker_db_result['PrimaryEmailAddress'] == telecom['value']
    birthDate = datetime.datetime.strptime(data_posted['birthDate'], '%Y-%m-%d')
    assert worker_db_result['BirthMonth'] == birthDate.strftime("%m")
    assert worker_db_result['BirthDay'] == birthDate.strftime("%d")
    assert worker_db_result['Birthyear'] == birthDate.strftime("%Y")
    for x in range(len(data_posted['identifier'])):
        if data_posted['identifier'][x]['system'] == "http://hl7.org/fhir/sid/us-ssn":
            assert worker_db_result['SSN'] == data_posted['identifier'][x]['value']
    if 'extension' in data_posted:
        for x in range(len(data_posted['extension'])):
            if data_posted['extension'][x]['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                for i in range(len(data_posted['extension'][x]['extension']) - 1, -1, -1):
                    if 'valueCoding' in data_posted['extension'][x]['extension'][i].keys():
                        race_code = data_posted['extension'][x]['extension'][i]['valueCoding']['code']
                        break
            elif data_posted['extension'][x][
                'url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                for i in range(len(data_posted['extension'][x]['extension']) - 1, -1, -1):
                    if 'valueCoding' in data_posted['extension'][x]['extension'][i].keys():
                        assert worker_db_result['EthnicityCode'] == \
                               data_posted['extension'][x]['extension'][i]['valueCoding']['code']
                        break
            elif data_posted['extension'][x]['url'] == "http://hl7.org/fhir/StructureDefinition/patient-birthPlace":
                assert worker_db_result['BirthPlaceCountry'] == data_posted['extension'][x]['valueAddress']['country']
                assert worker_db_result['BirthPlaceCity'] == data_posted['extension'][x]['valueAddress']['city']
                assert worker_db_result['BirthPlaceStateProv'] == data_posted['extension'][x]['valueAddress']['state']
    assert workerRace_db_result['RaceCode'] == race_code

    # Verify DB trigger
    # Worker table
    assert worker_db_result['LastUpdatedBy'] == 'sa'
    # last update date should be today
    assert (datetime.datetime.today() - worker_db_result['LastUpdateDate']).total_seconds() < 7200
    assert worker_db_result['CreateDate'] is not None
    assert worker_db_result['CreatedBy'] is not None
    # WorkerRace table
    assert workerRace_db_result['LastUpdatedBy'] == 'sa'
    assert (datetime.datetime.today() - workerRace_db_result['LastUpdateDate']).total_seconds() < 7200
    assert workerRace_db_result['CreateDate'] is not None
    assert workerRace_db_result['CreatedBy'] is not None

    return


def usage():
    print("Usage: FHIR_insertDB.py <file_to_verify>")


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(
            "Error, you must provide exactly 1 argument for the path to the data file that will"
            "be inserted into the database.")
        usage()
        exit(1)

    inFile = sys.argv[1]
    conn = connect_db()
    exitVal = 0

    # First, clean the table (delete the table which using foreign key first!)
    conn.cursor().execute("DELETE FROM worker.WorkerRace")
    conn.cursor().commit()
    conn.cursor().execute("DELETE FROM worker.Worker")
    conn.cursor().commit()

    # Post the data
    insert_id, *_ = FHIR_combined.verify_fhir(sys.argv[1])
    returnValue = FHIR_insertDB.post_db(insert_id)
    response_data = FHIR_insertDB.get_data(insert_id)

    # Test for bundle and non-bundle case
    cursor = conn.cursor()

    # Test cases for single and bundle data
    if 'resourceType' in response_data:
        if response_data['resourceType'] == 'Bundle':
            for single_data in response_data['entry']:
                assert_data(single_data['resource'], cursor)
        elif response_data['resourceType'] == 'Patient':
            assert_data(response_data, cursor)

    close_db(conn, cursor)
    exit(exitVal)
