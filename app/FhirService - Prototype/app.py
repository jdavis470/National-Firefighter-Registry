from flask import Flask, request, redirect, session

import logging
from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest
import fhirclient.models.patient as p
import fhirclient.models.humanname as hn


app = Flask(__name__)
# app setup
smart_defaults = {
    'app_id': 'my_web_app',
    'api_base': 'http://hapi.fhir.org/baseDstu3',
}
def _save_state(state):
    session['state'] = state

def _get_smart():
    state = session.get('state')
    if state:
        return client.FHIRClient(state=state, save_func=_save_state)
    else:
        return client.FHIRClient(settings=smart_defaults, save_func=_save_state)

def _get_patient(smart, id):
    res = p.Patient.read(id, smart.server)
    res = smart.human_name(res.name[0])
    return res

def _post_patient(smart):
    #smart.server.post_json = {"resourceType": "Patient","name": [{"use": "official","family": "Smith","given": ["Jack"],"suffix": ["Jr."]}],"gender": "male","birthDate": "1985-06-12"}
    patient1 = p.Patient();
    name = hn.HumanName()
    name.given = ['Peter']
    name.family = 'Parker'
    patient1.name = [name]
    res = patient1.create(smart.server)
    return res

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/patient/<id>', methods=['GET'])
def getPatient(id):
    if request.method == 'GET':
        smart = _get_smart()
        pres = _get_patient(smart, id)
        return pres
    else:
        return "this is not right"

@app.route('/patient', methods=['POST'])
def createPatient():
    if request.method == 'POST':
        smart = _get_smart()
        res = _post_patient(smart)
        return res
    else:
        return "this is not right"


