# setup-database.sh

echo 'Starting up the database...'

sleep 45s

echo 'Connecting database in container and create the initial db...'

/opt/mssql-tools/bin/sqlcmd -S localhost,1433 -U sa -P Password!123 -d master -i ./sqlfiles/DBSchemaInit.sql

echo 'Initial db created!'