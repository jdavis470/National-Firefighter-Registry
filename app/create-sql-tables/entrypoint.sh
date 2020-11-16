# entrypoint.sh

echo 'Starting clean database...'
/opt/mssql/bin/sqlservr &

echo 'Setuping up the FireFighter table...'
./sqlfiles/setup-database.sh 

wait
