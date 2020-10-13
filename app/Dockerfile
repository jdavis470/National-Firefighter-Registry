# Dockerfile

FROM microsoft/mssql-server-linux

RUN apt-get install python3

RUN mkdir sqlfiles
COPY create-sql-tables/DBSchemaInit.sql ./sqlfiles/DBSchemaInit.sql
COPY create-sql-tables/setup-database.sh ./sqlfiles/setup-database.sh
COPY create-sql-tables/entrypoint.sh ./sqlfiles/entrypoint.sh

ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=Password!123
ENV PATH=${PATH}:/opt/mssql/bin:/opt/mssql-tools/bin

RUN chmod a+x ./sqlfiles/setup-database.sh
RUN chmod a+x ./sqlfiles/entrypoint.sh

EXPOSE 1433

CMD bash ./sqlfiles/entrypoint.sh > sqlOutput.txt
