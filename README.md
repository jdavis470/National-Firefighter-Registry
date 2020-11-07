# National Firefighter Registry

## Team 55 Members
James Davis (jdavis470)
Haolong Yan (hyan88)
Rahul Nowlakha (rnowlakha3)
Robert Clifford (rclifford6)
Joe Kurokawa (jkurokawa3)

## Background
Studies have shown that firefighters are more susceptible to some medical conditions than the general population such as various forms of cancer, respiratory complications, and rhabdomyolysis. The National Firefighter Registry (NFR) is a CDC initiative to develop a national registry to track and analyze the long-term health of firefighters on a volunteer basis, with a specific emphasis on inclusion of women and minorities. The goal of this project is to support this effort through the creation of an implementation guide for use by the Fire Records Management System (FRMS) vendors to capture the data from National Fire Incident Reporting System Casulty Forms per the FHIR standard.

## Starting the Docker environment
1) Clone the repository 
2) CD into /National-Firefighter-Registry/app
3) (Skip if you have previously done this) Install the appropriate Docker version for your system: https://docs.docker.com/get-docker/ 
5) To build the docker image, type and run the following: docker build -t ff_env .
6) To start the environment, type and run the following: docker run -p 80:1433 ff_env
