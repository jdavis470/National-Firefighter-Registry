# entrypoint.sh

echo 'starting database setup'
./sqlfiles/setup-database.sh &
/opt/mssql/bin/sqlservr