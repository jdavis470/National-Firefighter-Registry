# Dockerfile

FROM microsoft/mssql-server-linux

RUN mkdir sqlfiles
COPY DBSchemaInit.sql ./sqlfiles/DBSchemaInit.sql
COPY setup-database.sh ./sqlfiles/setup-database.sh
COPY entrypoint.sh ./sqlfiles/entrypoint.sh

ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=Password!123
ENV PATH=${PATH}:/opt/mssql/bin:/opt/mssql-tools/bin

RUN chmod a+x ./sqlfiles/setup-database.sh
RUN chmod a+x ./sqlfiles/entrypoint.sh
CMD bash ./sqlfiles/entrypoint.sh
