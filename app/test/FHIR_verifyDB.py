import pyodbc
import sys
sys.path.append('../')
import FHIR_insertDB
import FHIR_combined
import datetime

def connect_db():
    # connection db with credentials
    # improvement: make credentials as parameters
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server=localhost,1433;'
                          'Database=FIREFIGHTER;'
                          'UID=sa;'
                          'PWD=Password!123;')

    # cursor is used as sql query
    return conn


def close_db(conn, cursor):
    cursor.close()
    conn.close()

    return 0


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

    # First, clean the table
    conn.cursor().execute("DELETE FROM Worker")
    conn.cursor().commit()
    conn.cursor().execute("DELETE FROM WorkerRace")
    conn.cursor().commit()

    # Post the data
    data_posted = FHIR_combined.verify_fhir(sys.argv[1])
    returnValue = FHIR_insertDB.post_db(data_posted)

    # Execute query for patient ID on Worker table
    cursor = conn.cursor()
    cursor.execute('SELECT StudyCode,GenderCode,CurrentResidentialStreet,CurrentResidentialCity,CurrentResidentialStateProv,'
                   'CurrentResidentialPostalCode,CurrentResidentialCountry,LastName,FirstName,MiddleName,MobilePhoneNumber,'
                   'PrimaryEmailAddress,BirthMonth,BirthDay,Birthyear FROM Worker WHERE WorkerID = ' + data_posted['id'])
    worker_item = cursor.fetchone()

    # Build Dictionary from column information and query data
    worker_columns = [column[0] for column in cursor.description]
    worker_db_result = dict(zip(worker_columns, worker_item))

    # Execute query for patient ID on WorkerRace table
    cursor.execute('SELECT StudyCode,RaceCode FROM WorkerRace WHERE WorkerID = ' + data_posted['id'])
    workerRace_item = cursor.fetchone()
    # Build Dictionary from column information and query data
    workerRace_columns = [column[0] for column in cursor.description]
    workerRace_db_result = dict(zip(workerRace_columns, workerRace_item))

    # Verify the Worker data
    assert worker_db_result['StudyCode'] == '0000'
    assert worker_db_result['GenderCode'] == data_posted['gender']
    assert worker_db_result['CurrentResidentialStreet'] == data_posted['address'][-1]['line'][0]
    assert worker_db_result['CurrentResidentialCity'] == data_posted['address'][-1]['city']
    assert worker_db_result['CurrentResidentialStateProv'] == data_posted['address'][-1]['state']
    assert worker_db_result['CurrentResidentialPostalCode'] == data_posted['address'][-1]['postalCode']
    assert worker_db_result['CurrentResidentialCountry'] == data_posted['address'][-1]['country']
    assert worker_db_result['LastName'] == data_posted['name'][-1]['family']
    if len(data_posted['name'][-1]['given']) > 1:
        assert worker_db_result['FirstName'] == data_posted['name'][-1]['given'][0]
        assert worker_db_result['MiddleName'] == data_posted['name'][-1]['given'][1]
    else:
        assert worker_db_result['FirstName'] == data_posted['name'][-1]['given']
    for telecom in data_posted['telecom']:
        if telecom['system'] == 'phone' and telecom['use'] == 'mobile':
            assert worker_db_result['MobilePhoneNumber'] == telecom['value']
        elif telecom['system'] == 'email':
            assert worker_db_result['PrimaryEmailAddress'] == telecom['value']
    birthDate = datetime.datetime.strptime(data_posted['birthDate'], '%Y-%m-%d')
    assert worker_db_result['BirthMonth'] == birthDate.strftime("%m")
    assert worker_db_result['BirthDay'] == birthDate.strftime("%d")
    assert worker_db_result['Birthyear'] == birthDate.strftime("%Y")

    # Verify the WorkerRace data
    assert workerRace_db_result['StudyCode'] == '0000'
    assert workerRace_db_result['RaceCode'] == '0000'

    close_db(conn, cursor)
    exit(exitVal)