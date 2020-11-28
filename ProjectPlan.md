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
Activity name: Parse patient resource in JSON format.  
Activity description: The JSON parser should be python code which accepts the FHIR patient resources in JSON format.  This input
comes in the form of a file with one or more patient resources, each representing a patient.  
Entrance criteria: Example patient resources and alignment on format for intermediate data output.  
Exit criteria: Data in some intermediate format for use with FHIR validation code and DB population.  Extracted data should match input in terms of semantics but be in the aligned intermediate format.  

### XML Parser
Activity name: Parse patient resource in XML format.  
Activity description: The XML parser should be python code which accepts the FHIR patient resources in XML format.  This input
comes in the form of a file with one or more patient resources, each representing a patient.  
Entrance criteria: Example patient resources and alignment on format for intermediate data output.  
Exit criteria: Data in some intermediate format for use with FHIR validation code and DB population.  Extracted data should match input in terms of semantics but be in the aligned intermediate format.  

### Data validation using FHIR server
Activity name: Validate extracted data.  
Activity description: The validation code should query the FHIR server to validate that the data matches the FHIR standard.  If so, should return a pass.  Otherwise, should return a fail and log an error.  
Entrance criteria: Extracted data in aligned upon intermediate format from XML & JSON parser.  
Exit criteria: Correct pass/fail depending on the validity of data.  Logs for errors if the data is invalid.  

### DB creation
Activity name: Create the database.  
Activity description: The database should be implemented in the agreed upon technology.  It should have all the fields necessary for storing the FHIR patient resource.  
Entrance criteria: Database technology to use, along with FHIR patient resource fields.  
Exit criteria: Empty database but configured for patients to be inserted.  

### DB population
Activity name: Populate the database.  
Activity description: The database should be populated with sample data from the CDC mentor.  Data will flow through the parsers, be validated, and then inserted accordingly.  
Entrance criteria: The created (empty) database along with sample patient data from the CDC mentor.  
Exit criteria: Completely populated database.  

### Data visualization
Activity name: Visualize the database.  
Activity description: A Tableau dashboard should be created which connects to the created database.  The dashboard should include the requested visualization of the number of firefighters in each fire department.  
Entrance criteria: Populated database with sample patient data.  
Exit criteria: Dashboard to visualize the number of firefighters in each fire department.  

## 3 Team

### Members

- James Davis
- Haolong Yan
- Rahul Nowlakha
- Traver Clifford
- Eric Mammoser
- Joe Kurokawa

### Team Roles
- Developer: Responsible for the creation of JSON and XML parser for the patient resource, FHIR validation code, and creation and population of SQL DB
- QA: Validate the parsers with various JSON & XML patient resource examples, testing validation code with good and bad patient resources, and validation that DB is constructed with the resulting data correctly
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
