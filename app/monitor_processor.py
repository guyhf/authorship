import sys
import os
sys.path.append("../lib")
from sqlalchemy import *
from sqlalchemy.orm import create_session, relation, mapper
import MySQLdb
import authwebdb
import time
from cherrypy import config

COMMAND = "./processor_start.sh"

def main():
	"""docstring for main"""

	config.update("config.ini")
	time_interval = config.get('processor.timeout')
	
	db = create_engine("mysql://%s:%s@localhost/%s" % (authwebdb.AUTHWEB_USER, authwebdb.AUTHWEB_PASSWD, authwebdb.AUTHWEB_DB))
	db.echo = False
	metadata = MetaData(db)

	auth_app_table = Table('auth_app', metadata, autoload=True)
	mapper(authwebdb.AuthApp, auth_app_table)
	
	auth_query_table = Table('auth_query', metadata, autoload=True)
	mapper(authwebdb.AuthQuery, auth_query_table, order_by=auth_query_table.created_time)

	session = create_session()

	query_auth_app = session.query(authwebdb.AuthApp)
	authapp = query_auth_app.selectfirst()
	cur_id = authapp.current_query_id

	

	if cur_id != None:
		query_auth_query = session.query(authwebdb.AuthQuery)
		current_query = query_auth_query.get_by(query_id = cur_id)

		
		if current_query.state == authwebdb.QUERY_STATE_PROCESSING:

			conn = MySQLdb.connect(user=authwebdb.AUTHWEB_USER, passwd=authwebdb.AUTHWEB_PASSWD, db=cur_id)
			cursor = conn.cursor()
			query_string = "select count(*) from article;"
			cursor.execute(query_string)
			first_num = int(cursor.fetchone()[0])
			cursor.close()
		
			time.sleep(time_interval)
			
			conn = MySQLdb.connect(user=authwebdb.AUTHWEB_USER, passwd=authwebdb.AUTHWEB_PASSWD, db=cur_id)
			cursor = conn.cursor()
			query_string = "select count(*) from article;"
			cursor.execute(query_string)
			second_num = int(cursor.fetchone()[0])
			cursor.close()
			conn.close()
			
			if first_num == second_num:
				print "Restarting process."
				os.system("cd %s ; %s > /dev/null 2>&1 &" % (os.getcwd(), COMMAND))
		else:
			time.sleep(time_interval)
	else:
		time.sleep(time_interval)

if __name__ == '__main__':
	main()
