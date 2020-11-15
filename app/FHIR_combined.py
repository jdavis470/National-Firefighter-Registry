import requests
import json
import ndjson
import os
import xmltodict
import sys
import uuid

smart_defaults = {
    'app_id': 'my_web_app',
    'api_base': 'https://r4.smarthealthit.org/Patient',
    'api_bundle': 'https://r4.smarthealthit.org/Bundle'
}


def convert_ndjson_to_bundle(patients):
    # bundle information
    bundle = dict()
    bundle['resourceType'] = 'Bundle'
    bundle['id'] = str(uuid.uuid4())
    bundle['type'] = 'collection'
    # patients as entry
    entry = list()
    for patient in patients:
        single_data = dict()
        single_data['resource'] = patient
        entry.append(single_data)
    bundle['entry'] = entry

    return bundle


def post_json(patient, path):
    if patient['resourceType'] == 'Patient' or patient['resourceType'] == 'Bundle':
        patient_json = json.dumps(patient)
        headers = {'Content-Type': 'application/json'}
        res_id = dict()
        if patient['resourceType'] == 'Patient':
            res = requests.post(url=smart_defaults['api_base'], headers=headers, data=patient_json).text
            res = json.loads(res)
            print(path + ": validated, Patient: " + res['id'] + " created")
        elif patient['resourceType'] == 'Bundle':
            res = requests.post(url=smart_defaults['api_bundle'], headers=headers, data=patient_json).text
            res = json.loads(res)
            print(path + ": validated, Bundle: " + res['id'] + " created")
        res_id['id'] = res['id']
        res_id['resourceType'] = patient['resourceType']
        return res_id, res
    else:
        raise RuntimeError("Can only handle JSON resourceType Patient.")


def post_xml(patient, path):
    xml_dict = xmltodict.parse(patient)
    if 'Patient' in xml_dict or 'Bundle' in xml_dict:
        headers = {'Content-Type': 'application/xml'}
        res_id = dict()
        if 'Patient' in xml_dict:
            res = requests.post(url=smart_defaults['api_base'], headers=headers, data=patient).text
            res = xmltodict.parse(res)
            print(path + ": validated, Patient: " + res['Patient']['id']['@value'] + " created")
            res_id['id'] = res['Patient']['id']['@value']
            res_id['resourceType'] = 'Patient'
        elif 'Bundle' in xml_dict:
            res = requests.post(url=smart_defaults['api_bundle'], headers=headers, data=patient).text
            res = xmltodict.parse(res)
            print(path + ": validated, Bundle: " + res['Bundle']['id']['@value'] + " created")
            res_id['id'] = res['Bundle']['id']['@value']
            res_id['resourceType'] = 'Bundle'
        return res_id, res
    else:
        raise RuntimeError("Can only handle XML type(s) Patient.")


def verify_fhir(path):
    try:
        filename, file_extension = os.path.splitext(path)

        if file_extension == '.ndjson':
            with open(path) as ndjson_file:
                patients_data = ndjson.load(ndjson_file)
            ndjson_file.close()
            patients_bundle = convert_ndjson_to_bundle(patients_data)
            patient_id, res = post_json(patients_bundle, path)
            return patient_id, res

        elif file_extension == '.json':
            with open(path) as json_data:
                patient_data = json.load(json_data)
            json_data.close()
            patient_id, res = post_json(patient_data, path)
            return patient_id, res

        elif file_extension == '.xml':
            with open(path) as xml_file:
                patient_data = xml_file.read()
            xml_file.close()
            patient_id, res = post_xml(patient_data, path)
            return patient_id, res

        else:
            print('Cannot handle this file yet')
            return -1
    except FileNotFoundError:
        print("File path: " + path + " Does not exist: ", file=sys.stderr)
        return -1
    except Exception as err:
        print("Error validating file: '" + path + "'. Error Message: {0}".format(err), file=sys.stderr)
        return -1

    return -1


def usage():
    print("Usage: FHIR_combined.py <file_to_verify>"
          "   or  FHIR_combined.py")


def main():
    if (len(sys.argv) > 2):
        print(
            "Error, if providing an argument you must provide exactly 1 argument for the path to the data file that will be verified.")
        usage()
        exit(1)

    # Command Line Argument Mode
    elif (len(sys.argv) == 2):
        returnValue = verify_fhir(sys.argv[1])

        if (returnValue == -1):
            usage()
            exit(-1)
        exit(0)


    # Interactive mode
    else:
        while (1):
            file = input("Give file path or type exit to quit: ")
            if file == 'exit':
                break
            verify_fhir(file)


if __name__ == "__main__":
    main()
