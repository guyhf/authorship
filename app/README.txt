CO-AUTHORSHIP NETWORKS

This is an application to generate networks of co-authorship.  It works by sending queries to NCBI's pubmed database, inserting the data into a local MySQL database, and then calculating the relationships to make network files.  It generates files for Cytoscape, Pajek, and text files and can be read by spreadsheet programs.

INSTALLATION

The code is written in Python and requires the following components:

	MySQLdb
	Cherrypy
	SQLAlchemy
	Threadpool
	
a working version of MySQL is needed as well of course.

USAGE

Once you have installed all the necessary components you can setup your system with:

% ./authwebctl.sh init

You can then start|stop|restart the system with:

% ./authwebctl.sh start
% ./authwebctl.sh restart
% ./authwebctl.sh stop

