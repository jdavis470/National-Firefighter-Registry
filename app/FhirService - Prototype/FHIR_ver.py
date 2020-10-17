from fhirclient.models.fhirabstractbase import FHIRValidationError
from fhirclient import client
import fhirclient.models.patient as p
import json

smart_defaults = {
    'app_id': 'my_web_app',
    'api_base': 'http://hapi.fhir.org/baseDstu3',
}

def verify_fhir(path, smart):
    try:
        with open(path) as json_data:
            patient_data = json.load(json_data)
            json_data.close()
        if patient_data['resourceType'] == 'Patient' :
            patient = p.Patient(patient_data)
            res = patient.create(smart.server)
            print(path + ": This validation was right, Patient: " + res['id'] + " created")
        else:
            print("Dont handle type '" + patient_data['resourceType'] + "' yet")
        return
    except FHIRValidationError:
        print (path + ": This validation was wrong")
        pass
    except FileNotFoundError:
        print ("File path: " + path + " Does not exist")

def main():
    smart = client.FHIRClient(settings=smart_defaults)
    while (1) :
        file = input("Give file path or type exit to quit: ")
        if file == 'exit':
            break
        verify_fhir(file, smart)

if __name__ == "__main__":
    main()