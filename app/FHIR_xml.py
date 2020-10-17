import requests
import xmltodict

smart_defaults = {
    'app_id': 'my_web_app',
    'api_base': 'https://r4.smarthealthit.org/Patient',
}

def verify_fhir(path):
    try:
        with open(path) as xml_file:
            patient_data = xml_file.read()
        xml_file.close()
        xml_dict = xmltodict.parse(patient_data)
        if xml_dict['Patient']:
            headers = {'Content-Type': 'application/xml'}
            res = requests.post(url=smart_defaults['api_base'], headers=headers, data=patient_data).text
            res = xmltodict.parse(res)
            print(path + ": This validation was right, Patient: " + res['Patient']['id']['@value'] + " created")
            return res
        else:
            print("Cannot handle this type yet")
        return
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            print("FHIR server validation error")
        pass
    except FileNotFoundError:
        print ("File path: " + path + " Does not exist")
        pass
    except Exception:
        print (path + ": This validation was wrong")

def main():
    while (1) :
        file = input("Give file path or type exit to quit: ")
        if file == 'exit':
            break
        verify_fhir(file)

if __name__ == "__main__":
    main()