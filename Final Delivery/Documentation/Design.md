# Design Document

## Project Scope
At a high level, this project has objectives of taking an input file of FHIR patient and observation data, validating it, and inserting it into a database.  A Tableau
frontend will be used to connect to the database and enable a simple visualization of the firefighters enrolled in the database.

## Project Requirements
The input file formats supported shall include:
  1) JSON
  2) XML
  3) NDJSON (newline-delimited JSON)

The content of the input files supported shall include:
  1) Patient resource
  2) Observation resource (linked to a patient)
  3) Bundle of either patients or observations (but not mixed)

The database fields were provided as part of a SQL create script provided by the CDC NIOSH.  These shall be populated using FHIR patient and observation resource elements.

## Project Architecture
![Figure 1](../../collateral/architecture.png)

Figure 1 shows the design architecture of our project.  The first two steps are the "Process Input" step and the "Pass Input Files" step.  As input can come in a variety of 
file formats, we are using a few libraries to handle this.  JSON is handled by the json lib, NDJSON is handled by the ndjson lib, and XML is handled by the xmltodict lib.  

The next step is the HTTP PUT of the data to the FHIR server. This process involves forming our own HTTP request to the FHIR server using the requests lib.  For the NDJSON 
data, we are dealing with multiple resources so to reduce the number of HTTP requests, we form this into a bundle and POST it that way.  

After performing the PUT, we can do an HTTP GET and request the data from the FHIR server that we just PUT, but specifying that we want the return to be JSON formatted.  This 
again uses the requests lib.  

The final step in our data pipeline is to take the response data from the HTTP GET and process it, pulling out the fields (and processing them as necessary) to be able to insert
these into the SQL database.  We used the pyodbc library for this purpose.  After this point, our code execution is complete and the user is able to use any of their preferred
methods to interact with the SQL database to perform queries.  

## Design Decisions
Throughout the design process, we made several architectural decision which we would like to provide the rationale for.  First, our design used a FHIR server for two
purposes: 
  1) Validate that the input FHIR data is valid per FHIR V4.0.0 R4
  2) Handle conversion of JSON/XML data to a common format

Validation of data could have been achieved by writing code to perform FHIR resource validation instead of performing an HTTP PUT to the FHIR server.  However, this would
have to be maintained over time, whereas if we leverage the FHIR server directly it will be maintained on its own.  

Secondly, we wished to support both JSON and XML input formats, but we only wanted to write the database insertion code to support one data format because the structure of
XML and JSON is slightly different.  This simpifies our code, but requires a way to convert JSON and XML to a common data format.  Initially we considered other python
libraries to do this conversion, but we realized that if we do an HTTP GET and request the same FHIR resource we just executed an HTTP PUT with, we would be ablet to request
it in either JSON or XML format.  Therefore, we can do an HTTP PUT of XML data then an HTTP GET requesting that same data in JSON format, effectively using the FHIR server to
perform the data conversion for us.

Another design decision was to use HTTP POST or HTTP PUT for the patient resource.  For the FHIR server we are using (SMARTHealthIT), performing an HTTP POST of a patient
with a resource ID that already exists creates a new patient with a different ID.  However, performing an HTTP PUT of a patient with a resource ID that already exists will
replace that patient with the patient in the HTTP PUT.  This subtle difference is important for us, because we need to read in both a patient resource and an observation
resource with a reference to the patient ID.  If a patient is created with a different ID than the ID it has in the input file for the patient resource (and thus the input
file for the observation resource), then it causes a problem for linking this observation to the correct patient.  There are a number of ways to solve this problem.  

First one can use an HTTP PUT, which ensures that the patient ID in the FHIR server is the same as that contained in the input file since it will overwrite a patient.  The
benefit of this is in simplicity: it's a single change of POST to PUT.  However, there are two key downsides.  The first is that the FHIR server could overwrite an existing
patient.  Since we are only using this for validation/conversion purposes, this is not an issue for us.  Secondly, the behavior for an HTTP PUT can be configured differently
on FHIR servers, so if a FHIR server was used with different behavior (such as returning an error if the patient ID already exists), then we would not be able to rely on this
behavior.  However, for us this is not an issue.

As an alternative, we could find a way to store the original ID and the new ID.  This could be done by adding a field to the database and storing the ID from the input file
(which is needed to link to the observation resource), while also keeping the field containing the new ID.  When doing a POST of the observation, we could do a DB query to
find the new ID from the old ID and do a substitution before POSTing. A similar approach would be to use the old ID as an identifier when POSTing to the FHIR server.  These
solutions are slightly more complex, so we opted for the simpler solution detailed previously.  However, if the behavior chagnes then these are viable alternatives.

Finally, we were faced with a challenge of handling the sequencing of observation data and patient data.  In a FHIR server, there is a requirement that the observation
subject's reference ID (referring to a patient) exists in the FHIR server when trying to POST the observation.  As a result, patient data has to be PUT/POSTED before the
observation is.  Since we are relying on validation of the FHIR data via the FHIR server, we are requiring that the order of data read in is patient and then observation.
This means that a patient resource read in results in a creation of a new entry in the DB, while a read in of observation data results in an update of an existing entry.  In
theory, this could be changed if we did not rely on the FHIR server for validation purposes.  For example, if we validated the data ourselves, we could do a SQL query for the
reference ID for the patient to see if it exists in the database.  If not (as would be the case if the observation is read in before a patient) then we could create an entry
with the reference ID but the rest of the patient fields left empty.  Then, we could perform an update to the DB when reading in the patient data if the ID already existed.
In this way, there is more flexibility of data read order if dealing with many data files of different resource types without an easy way to sort them.  However, this would
require significantly more complexity: we would have to perform our own validation of the FHIR data, and then both patient and observation read ins would need to support a
create (if the patient ID doesn't exist in the DB), or an update (if the patient ID already exists).

