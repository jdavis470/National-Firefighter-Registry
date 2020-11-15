#!/bin/bash

echo === Begin Testing FHIR_combined.py ===
LOGFILE="$(mktemp FHIR_combined_XXXXXXXXX.log)"
DATA_LOC="$(dirname $(realpath -s $0))/data/team_created"
echo Data: $DATA_LOC
for file in $(find $DATA_LOC -maxdepth 1 -not -type d);
do
     	echo === Starting Test with $file ===
        printf "\n\n=== Starting Test with $file ===" >> $LOGFILE

	python3 $(dirname $(realpath -s $0))/../FHIR_combined.py $file &>> $LOGFILE
	if [[ $? == 0 ]];
	then 
		echo PASSED
	else 
		echo FAILED - Check log file: $LOGFILE
	fi
done

echo === Begin Testing FHIR_insertDB.py ===
LOGFILE="$(mktemp FHIR_insertDB_XXXXXXXXX.log)"
DATA_LOC="$(dirname $(realpath -s $0))/data/team_created"
echo Data: $DATA_LOC
for file in $(find $DATA_LOC -maxdepth 1 -not -type d);
do
     	echo === Starting Test with $file ===
        printf "\n\n=== Starting Test with $file ===" >> $LOGFILE

	python3 $(dirname $(realpath -s $0))/FHIR_verifyDB.py $file &>> $LOGFILE
	if [[ $? == 0 ]];
	then 
		echo PASSED
	else 
		echo FAILED - Check log file: $LOGFILE
	fi
done
