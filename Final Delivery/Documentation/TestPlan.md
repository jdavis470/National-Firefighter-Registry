# Test Plan

## Purpose
The purpose of this document is to inform the reader on the National Firefighter Registry project test procedure as well as the reasoning behind the test decisions that were made. In order to develop this testing strategy, the first step to be taken was to understand what high-level features were required. Next, individual test cases needed to be created to test each feature to ensure that there was complete coverage of all functionality required by this project. Lastly, a semi-automated test suite would need to be created to better facilitate integration and regression testing.

## Functional Requirements
The National Firefighter Registry had one overarching goal and that was to take an input file of FHIR patient and observation data, validate it, and insert it into a database. Additionally, we had the requirement that the format of that input file could any of the following:
  * JSON
  * XML
  * NDJSON (newline-delimited JSON)
  and contain the content of any of the following:
  * Patient resource
  * Observation resource (linked to a patient)
  * Bundle of either patients or observations (but not mixed)

These requirements were used to create a group of test cases that would validate that the National Firefighter Registry project satisfied our stakeholders goal mentioned above.

## Test Strategy
### Test Cases
The test cases that were created took the form of multiple different data files. Each of these data files were in either JSON, XML, or NDJSON format and contained Patient, Observation, or Bundles of either Patient or Observation resources.

### Similar Deployment Environment
The National Firefighter Application did not require deployment to CS 6440's HDAP system, however, we still developed and maintained a Dockerfile that would allow anyone with docker installed to pull our source code, build the docker container image, and run our project without any other environmental modifications. This allowed for easier testing as all developers were using the same environment and also allows for a more robust delivery as our stakeholders will be able to run our application as the developers did.

### Test Suite
A rudimentary shell script test suite was then created that when ran, would parse a given directory for test case data files, and then run these data files through the set of scripts that we had written for the project. Additionally, an extra script was written that would verify that the data that was supposed to be inserted into the database was in fact inserted and committed.

### Integration Testing
The test suite mentioned above had two stages that would attempt to test one of the scripts separately from the entire, end-to-end pipeline. This allowed for a more granular test against one of the scripts that we had written (the script that interacts with the FHIR server), as well as providing a test that verified the end-to-end result which involved both scripts.

### Regression Testing
This test suite served as a useful way to regression test our application. While we did not investigate or implement automated testing that would verify each and every pull request or perform nightly build and test runs, this script provided us the foundation to expand into those more mature testing strategies if the project were to continue on. Additionally, our test suite coupled with our docker deployment strategy was easy to run and use at any time by any developer which meant that we would use the passing or failing status of the test suite as a measure for whether or not pull requests should be approved.
