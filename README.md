AUTHORSHIP
==========

A CherryPy web application to generate networks of co-authorship generated from PubMed search queries.  The web interface is generated with CherryPy and Kid templates.  Queries are done using the PubMed e-utilities interface and stored in a local MySQL database.

It's probably easiest to set up this app using a virutal env.  The required modules are listed in requirements.txt and can be installed with:

    virtualenv .
    source bin/activate
    pip install -r requirements.txt

It is also necessary to install and create a database and set the AUTHWEB\_USER, AUTHWEB\_PASSWD, and AUTHWEB\_DB in the authweb.db library.



License
=======
Copyright 2007 Guy Haskin Fernald

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
