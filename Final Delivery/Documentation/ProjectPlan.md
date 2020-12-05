# Project Plan


**Author**: Team 55

## 1 Introduction

Studies have shown that firefighters are more susceptible to some medical conditions than the general population such as various forms of cancer, respiratory complications, and rhabdomyolysis.  The National Firefighter Registry (NFR) is a CDC initiative to develop a national registry to track and analyze the long-term health of firefighters on a volunteer basis, with a specific emphasis on inclusion of women and minorities.  The goal of this project is to support this effort through the creation of an implementation guide for use by the Fire Records Management System (FRMS) vendors to capture the data from National Fire Incident Reporting System Casulty Forms per the FHIR standard.

## 2 Process Description

### Research
Activity name: Perform basic research.  
Activity description: Must investigate and select languages, database type, and find JSON and XML examples for patient resources.  
Entrance criteria: Project is assigned.  
Exit criteria: Language selection for project, database to use, alignment on intermediate data format for patient resource fields, and example patient resources.  

### JSON Parser
Activity name: Parse patient, observation, and bundle resource in both JSON and NDJSON format and PUT to FHIR server.  
Activity description: The JSON parser should be python code which accepts the FHIR resources in JSON and NDJSON format.  This input
comes in the form of a file with either a single resource or NDJSON collection of resources, each representing a patient or observation.  This should be PUT to the FHIR server for validation.  
Entrance criteria: Example patient, observation, and bundle resources and alignment on format for intermediate data output.  
Exit criteria: Data in some intermediate format for use with DB population.  Extracted data should match input in terms of semantics but be in the aligned intermediate format.  

### XML Parser
Activity name: Parse patient, observation, and bundle resource in XML format and PUT to FHIR server.  
Activity description: The XML parser should be python code which accepts the FHIR resources in XML format.  This input
comes in the form of a file with either a single resource or NJDSON collection of resources, each representing a patient or observation.   This should be PUT to the FHIR server for validation.  
Entrance criteria: Example patient, observation, and bundle resources and alignment on format for intermediate data output.  
Exit criteria: Data in some intermediate format for use with DB population.  Extracted data should match input in terms of semantics but be in the aligned intermediate format.  

### DB creation
Activity name: Create the database.  
Activity description: The database should be implemented in the agreed upon technology.  It should have all the fields necessary for storing the FHIR patient or observation resource.  
Entrance criteria: Database technology to use, along with FHIR patient or observation resource fields.  
Exit criteria: Empty database but configured for patients and observations to be inserted.  

### DB population
Activity name: Populate the database.  
Activity description: The database should be populated with sample data from the CDC mentor.  Data will flow through the parsers, be validated, and then inserted accordingly.  
Entrance criteria: The created (empty) database along with sample patient and observation data from the CDC mentor.  
Exit criteria: Completely populated database.  

### Data visualization
Activity name: Visualize the database.  
Activity description: A Tableau dashboard should be created which connects to the created database.  The dashboard should include the requested visualization of where the enrolled
firefighters are located.  
Entrance criteria: Populated database with sample patient and observation data.  
Exit criteria: Dashboard to visualize the location of firefighters enrolled in the registry.  

## 3 Team

### Members

- James Davis
- Haolong Yan
- Rahul Nowlakha
- Traver Clifford
- Eric Mammoser
- Joe Kurokawa

### Team Roles
- Developer: Responsible for the creation of JSON, NDJSON, and XML parser for the patient, observation, and bundle resource and creation and population of SQL DB
- QA: Validate the parsers with various JSON, NDJSON, and XML patient, observation, and bundle resource examples.  Additionally, validation that DB is constructed with the resulting data correctly
- Project Manager: Run weekly meetings, determine deliverables along with plan to create them, plan and track project progress, and develop Tableau visualization dashboard

| Member | Role |
| ------ | ---- |
| James Davis | Project Manager |
| Haolong Yan | Developer |
| Rahul Nowlakha | Developer |
| Traver Clifford | Developer |
| Eric Mammoser | QA |
| Joe Kurokawa | Developer |

## 4 Mentor Questions


## 5 Team Resources
- Architecture Diagram (v1.0) - https://drive.google.com/file/d/1AjvS8-__q-TsNvbaazzSP8Fdgf2EOPl7/view?usp=sharing 
- Gantt Chart - https://gtvault-my.sharepoint.com/:x:/g/personal/hyan88_gatech_edu/EdVXBwwxzgFMvicZgVUsn3EBbbw8Za3K7ynamXT5jPVUuw?e=5dxtbg
