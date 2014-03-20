#!/Library/Server/Web/Data/WebApps/authorship/bin/python
# encoding: utf-8

import sys
sys.path.append("../lib")
import os
import pubmed
import authwebdb
import networkgen
import thread
import threading
import time

_curdir = os.getcwd()
_filesdir = os.path.join(_curdir, "files")

def _import_articles(search_string, query_id, make_db_connection, filesdir):
	current_state = authwebdb.get_query_state(query_id)

	if current_state != authwebdb.QUERY_STATE_GENERATING:
			authwebdb.create_database_and_tables(query_id)
			authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_PROCESSING)
			pubmed.import_articles_pool(search_string, 50, make_db_connection)
			authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_GENERATING)

#			networkgen.merge_authors(query_id, make_db_connection)
#			authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_GENERATING)

	# if current_state == QUERY_STATE_GENERATING then we are restarting the generate state
	networkgen.generate_file(filesdir, query_id, make_db_connection)
	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_DONE)


def _merge_authors(search_string, query_id, make_db_connection, filesdir):
	
	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_MERGING)

	conn = make_db_connection()
	groups = networkgen.get_all_similar_authors(conn, query_id)
	networkgen.combine_authors(conn, groups)
	conn.close()
	authwebdb.set_query_merged(query_id)

	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_GENERATING)
	networkgen.generate_file(filesdir, query_id, make_db_connection)
	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_DONE)


def _generate_file(query_id, make_db_connection, filesdir):
	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_GENERATING)
	networkgen.generate_file(filesdir, query_id, make_db_connection)
	authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_DONE)

QUERY_TYPE_PROCESS  = 0
QUERY_TYPE_MERGE    = 1
QUERY_TYPE_GENERATE = 2
def authwebdb_processor(authdb_queue):
	query_id, search_string, query_type = authdb_queue.pop()
	print query_id
	print search_string
	print query_type

	if query_id != None:
		authwebdb.global_vars.authweb_app.set_current_query_id(query_id)
		make_db_connection = pubmed.db_connection_maker(query_id,
		 												authwebdb.AUTHWEB_USER,
		 												authwebdb.AUTHWEB_PASSWD)

		if query_type == authwebdb.QUERY_TYPE_PROCESS and search_string != None:
			_import_articles(search_string, query_id, make_db_connection, _filesdir)

		elif query_type == authwebdb.QUERY_TYPE_MERGE:
			_merge_authors(search_string, query_id, make_db_connection, _filesdir)

		elif query_type == authwebdb.QUERY_TYPE_GENERATE:
			_generate_file(query_id, make_db_connection, _filesdir)

		authdb_queue.completed(query_id)
		authwebdb.global_vars.authweb_app.set_current_query_id(None)

	else:
		authwebdb.clean_up_old_databases()
			

def main():
	"""docstring for main"""
	# Initialize all of our DB stuff
	authwebdb.initialize_main_db()
	authwebdb.initialize_authwebdb()
	authwebdb.initialize_mappers()
	authwebdb.initialize_app()
	
	# Start the queue
	authdb_queue_lock = thread.allocate_lock()
	authdb_queue = authwebdb.AuthDBQueue(authwebdb.global_vars.authweb_app, authdb_queue_lock, authwebdb.global_vars)
	authwebdb_processor(authdb_queue)

if __name__ == '__main__':
	main()
