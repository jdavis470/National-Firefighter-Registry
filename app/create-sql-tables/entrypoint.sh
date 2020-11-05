# entrypoint.sh

echo 'Starting clean database...'
/opt/mssql/bin/sqlservr &

echo 'Sleeping 10 seconds to allow database to finish starting up...'
sleep 10

echo 'Setuping up the FireFighter table...'
./sqlfiles/setup-database.sh 

echo 'Database is setup.'
wait
