#!/bin/bash

echo === Begin Testing FHIR_combined.py ===
LOGFILE="$(mktemp FHIR_combined_XXXXXXXXX.log)"
DATA_LOC="$(dirname $(realpath -s $0))/../../data/team_created"
echo Data: $DATA_LOC
for file in $(ls $DATA_LOC);
do
     	echo === Starting Test with $file ===
        printf "\n\n=== Starting Test with $file ===" >> $LOGFILE

	python3 $(dirname $(realpath -s $0))/../FHIR_combined.py $DATA_LOC/$file &>> $LOGFILE
	if [[ $? == 0 ]];
	then 
		echo PASSED
	else 
		echo FAILED - Check log file: $LOGFILE
	fi
done
