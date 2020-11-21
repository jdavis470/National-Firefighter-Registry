# setup-database.sh

# Loop courtesy of: https://github.com/microsoft/mssql-docker/issues/11

# Wait for it to be available
echo "Waiting for MS SQL to be available ⏳"
/opt/mssql-tools/bin/sqlcmd -l 30 -S localhost,1433  -U sa -P Password!123 -d master -Q "SET NOCOUNT ON SELECT \"YAY WE ARE UP\" , @@servername"
is_up=$?
while [ $is_up -ne 0 ]
do
  echo `date`
  /opt/mssql-tools/bin/sqlcmd -l 30 -S localhost,1433  -U sa -P Password!123 -d master -Q "SET NOCOUNT ON SELECT \"YAY WE ARE UP\" , @@servername"
  is_up=$?
  sleep 5
done

echo 'Connecting database in container and create the initial db...'
/opt/mssql-tools/bin/sqlcmd -S localhost,1433 -U sa -P Password!123 -d master -i ./sqlfiles/createDB.sql -l 300

