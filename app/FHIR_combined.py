import requests
import json
import ndjson
import os
import xmltodict
import sys
import uuid

smart_defaults = {
    'api_base': 'https://r4.smarthealthit.org',
    'api_patient': 'https://r4.smarthealthit.org/Patient',
    'api_bundle': 'https://r4.smarthealthit.org/Bundle',
    'api_observation': 'https://r4.smarthealthit.org/Observation'
}


def convert_ndjson_to_bundle(resources):
    """
    Convert the resource data format from NDJSON into Bundle in order to upload them to the FHIR server.

    Args:
        resources: Dict type of resource data in NDJSON (Patient/Observation).

    Returns:
        bundle: Dict type of resource data in Bundle.
    """
    # bundle information
    bundle = dict()
    bundle['resourceType'] = 'Bundle'
    bundle['id'] = str(uuid.uuid4())
    bundle['type'] = 'collection'
    # resource as entry
    entry = list()
    for resource in resources:
        single_data = dict()
        single_data['resource'] = resource
        entry.append(single_data)
    bundle['entry'] = entry

    return bundle


def put_json(resource, path):
    """
        PUTing the JSON resource data into FHIR server based on different resource type.

        Args:
            resource: Dict type of resource data in JSON (Patient/Observation/Bundle).

            path (optional): String type of the resource data's file path.

        Returns:
            res_id: Dict type of resource data which uploaded to the server successfully
            (including resource ID and resource type).

            res: Dict type of response data from the server after HTTP request.
    """
    if resource['resourceType'] in ['Patient', 'Bundle', 'Observation']:
        patient_json = json.dumps(resource)
        headers = {'Content-Type': 'application/json'}
        res_id = dict()
        if resource['resourceType'] == 'Patient':
            url = smart_defaults['api_patient'] + '/' + resource['id']
            res = requests.put(url=url, headers=headers, data=patient_json).text
            res = json.loads(res)
            if path:
                print(path + ": validated, Patient: " + res['id'] + " created")
        elif resource['resourceType'] == 'Bundle':
            url = smart_defaults['api_bundle'] + '/' + resource['id']
            res = requests.put(url=url, headers=headers, data=patient_json).text
            res = json.loads(res)
            if path:
                print(path + ": validated, Bundle: " + res['id'] + " created")
        elif resource['resourceType'] == 'Observation':
            url = smart_defaults['api_observation'] + '/' + resource['id']
            res = requests.put(url=url, headers=headers, data=patient_json).text
            res = json.loads(res)
            # error handling when the data is invalid
            if 'id' in res:
                if path:
                    print(path + ": validated, Observation: " + res['id'] + " created")
            else:
                print(res['issue'][0]['severity'], ':', res['issue'][0]['diagnostics'])
        res_id['id'] = res['id']
        res_id['resourceType'] = resource['resourceType']
        return res_id, res
    else:
        raise RuntimeError("Can only handle JSON type(s) Patient and Observation.")


def put_xml(resource, path):
    """
        PUTing the XML resource data into the FHIR server based on different resource type.

        Args:
            resource: Dict type of resource data in XML (Patient/Observation/Bundle).

            path (optional): String type of the resource data's file path.

        Returns:
            res_id: Dict type of resource data which uploaded to the server successfully
            (including resource ID and resource type).

            res: Dict type of response data from the server after HTTP request.
    """
    xml_dict = xmltodict.parse(resource)
    if 'Patient' in xml_dict or 'Bundle' in xml_dict or 'Observation' in xml_dict:
        headers = {'Content-Type': 'application/xml'}
        res_id = dict()
        if 'Patient' in xml_dict:
            url = smart_defaults['api_patient'] + '/' + xml_dict['Patient']['id']['@value']
            res = requests.put(url=url, headers=headers, data=resource).text
            res = xmltodict.parse(res)
            if path:
                print(path + ": validated, Patient: " + res['Patient']['id']['@value'] + " created")
            res_id['id'] = res['Patient']['id']['@value']
            res_id['resourceType'] = 'Patient'
        elif 'Bundle' in xml_dict:
            url = smart_defaults['api_bundle'] + '/' + xml_dict['Bundle']['id']['@value']
            res = requests.put(url=url, headers=headers, data=resource).text
            res = xmltodict.parse(res)
            if path:
                print(path + ": validated, Bundle: " + res['Bundle']['id']['@value'] + " created")
            res_id['id'] = res['Bundle']['id']['@value']
            res_id['resourceType'] = 'Bundle'
        elif 'Observation' in xml_dict:
            url = smart_defaults['api_observation'] + '/' + xml_dict['Observation']['id']['@value']
            res = requests.put(url=url, headers=headers, data=resource).text
            res = xmltodict.parse(res)
            if path:
                print(path + ": validated, Observation: " + res['Observation']['id']['@value'] + " created")
            res_id['id'] = res['Observation']['id']['@value']
            res_id['resourceType'] = 'Observation'
        return res_id, res
    else:
        raise RuntimeError("Can only handle XML type(s) Patient and Observation.")


def verify_fhir(path):
    """
        Verify the format of the resource data by PUTing it into the FHIR server.

        Args:
            path: String type of the resource data's file path.

        Returns:
            res_id: Either -1 to indicate exception caught or Dict type of resource data which
            uploaded to the server successfully (including resource ID and resource type).

            res: Dict type of response data from the server after HTTP request.
    """
    try:
        filename, file_extension = os.path.splitext(path)

        if file_extension == '.ndjson':
            with open(path, encoding='utf-8') as ndjson_file:
                patients_data = ndjson.load(ndjson_file)
            ndjson_file.close()
            patients_bundle = convert_ndjson_to_bundle(patients_data)
            patient_id, res = put_json(patients_bundle, path)
            return patient_id, res

        elif file_extension == '.json':
            with open(path, encoding='utf-8') as json_data:
                patient_data = json.load(json_data)
            json_data.close()
            patient_id, res = put_json(patient_data, path)
            return patient_id, res

        elif file_extension == '.xml':
            with open(path, encoding='utf-8') as xml_file:
                patient_data = xml_file.read()
            xml_file.close()
            patient_id, res = put_xml(patient_data, path)
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


def usage():
    """
        Print out an error message when the program is called incorrectly.
    """
    print("Usage: FHIR_combined.py <file_to_verify>"
          "   or  FHIR_combined.py")


def main():
    """
        main function to call the data verification either in command line argument mode or interactive mode.
    """
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
