# Research
## Thrid Party Library Choices 

For this project we heavily relied on third party libraries in Python for processing data and insertion of data into the database. 
During our validation step, we decided to Post jsons and xmls directly to the FHIR server using basic http requests
using the requests library (https://requests.readthedocs.io/en/master/). We decided to not use a fhir client such as 
Fhircleint.py from Smart Health IT(https://github.com/smart-on-fhir/client-py). Since we already had a json or xml file, 
converting it to Patient objects using the client was an uncessary step since we can post that json direclty to the FHIR server. 
Also, when it comes to Database insertion, there is no need for a Patient Object class since you can get the posted data directly 
from the server in either json or xml format.

In order to handle formats outside of json such as xml and ndjson, we implemented the use of 
xmltodict library (https://pypi.org/project/xmltodict/) as well as ndjson library (https://pypi.org/project/ndjson/).
Both libraries take in respective data formats and convert them to Python codable dictionaries. We chose these libraries
because they were easy to use and widely adopted libraries publicly.  

Finally, in order to make the database connection in to MS SQL server, we use the pyodbc (https://pypi.org/project/pyodbc/)
to connect to the database to make insert and update statements. This was a straight forward choice because pyodbc is a 
simple library that is widely adopted. 