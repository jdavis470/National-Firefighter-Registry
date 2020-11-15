# setup-database.sh

echo 'Connecting database in container and create the initial db...'

/opt/mssql-tools/bin/sqlcmd -S localhost,1433 -U sa -P Password!123 -d master -i ./sqlfiles/createDB.sql

echo 'Initial db created!'
