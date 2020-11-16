# setup-database.sh

echo 'Connecting database in container and create the initial db...'

/opt/mssql-tools/bin/sqlcmd -S localhost,1433 -U sa -P Password!123 -d master -i ./sqlfiles/createDB.sql -l 300

if [[ $? = 0 ]];
then
	echo 'Initial db created!'
	exit 0
else
	echo 'Inital db creation failed!'
	exit 1
fi
