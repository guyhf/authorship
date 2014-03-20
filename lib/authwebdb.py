#!/usr/bin/env python
# encoding: utf-8
"""
authwebdb.py

Created by Guy Haskin Fernald on 2007-06-19.
Copyright (c) 2007 Guy Haskin Fernald. All rights reserved.
"""

import sys
import os
import unittest
from sqlalchemy import *
from sqlalchemy.orm import create_session, relation, mapper
import MySQLdb
import string
import random
import time
import pubmed
import shutil
import getopt

_curdir = os.getcwd()
_filesdir = os.path.join(_curdir, "files")

AUTHWEB_USER   = "authweb"
AUTHWEB_PASSWD = "authweb"
AUTHWEB_DB     = "authweb"

QUERY_STATE_QUEUED     = 0
QUERY_STATE_PROCESSING = 1
QUERY_STATE_GENERATING = 2
QUERY_STATE_MERGING    = 3
QUERY_STATE_DONE       = 4

QUERY_TYPE_PROCESS  = 0
QUERY_TYPE_MERGE    = 1
QUERY_TYPE_GENERATE = 2

class Global:

	def __init__(self):
		db               = None
		metadata         = None
		verbose          = False
		conn             = None
		session          = None
		query            = None
		query_auth_queue = None
		query_auth_app   = None
		authweb_app      = None

global_vars = Global()

class AuthDBQueue(object):
	def __init__(self, auth_app, lock, global_vars):
		self.auth_app = auth_app
		self.lock = lock
	
	def pop(self):
		self.lock.acquire()
		auth_queue = global_vars.query_auth_queue.order_by(AuthQueue.query_number).first()
		
		if auth_queue == None:
			self.lock.release()
			return None, None, None
			
		query_id   = auth_queue.query_id
		query_type = auth_queue.query_type

		auth_query = global_vars.query.filter(AuthQuery.query_id == query_id).first()
		if auth_query:
			search_string = auth_query.search_string
		else:
			search_string = None
		self.lock.release()
		return query_id, search_string, query_type
		
	def completed(self, query_id):
		"""docstring for unshift"""
		self.lock.acquire()
		auth_queue = global_vars.query_auth_queue.filter_by(query_id = query_id).first()
		global_vars.session.delete(auth_queue)
		global_vars.session.flush()
		self.lock.release()
	
	def push(self, query_id, query_type):
		"""docstring for push"""
		self.lock.acquire()
		auth_queue = AuthQueue()
		auth_queue.query_id = query_id
		auth_queue.query_type = query_type
		auth_queue.query_number = self.auth_app.increment()
		global_vars.session.add(auth_queue)
		global_vars.session.flush()
		self.lock.release()
		
	def get_position(self, query_id):
		"""docstring for get_position"""
		self.lock.acquire()
		entries = global_vars.query_auth_queue.filter().order_by(AuthQueue.query_number).all()
		total = len(entries)
		pos = 1
		found = False
		for entry in entries:
			if entry.query_id == query_id:
				found = True
				break
			else:
				pos += 1
		self.lock.release()
		
		if not found:
			return 0, 0
		
		return total, pos
	

	
def initialize_authwebdb():
	"""docstring for initialize_authwebdb"""
	global_vars.db, global_vars.metadata = initialize_database(AUTHWEB_DB, AUTHWEB_USER, AUTHWEB_PASSWD)
	global_vars.session = create_session()

def initialize_main_db():
	"""docstring for initialize_authwebdb"""
	global_vars.conn = MySQLdb.connect(user= "root", passwd = "")

def connect_to_main_db():
	"""docstring for connect_to_main_db"""
	conn = MySQLdb.connect(user= "root", passwd = "")
	return conn

def initialize_mappers():
	auth_query_table = Table('auth_query', global_vars.metadata, autoload=True)
	mapper(AuthQuery, auth_query_table, order_by=auth_query_table.c.created_time)
	global_vars.query = global_vars.session.query(AuthQuery)
	auth_queue_table = Table('auth_queue', global_vars.metadata, autoload=True)
	mapper(AuthQueue, auth_queue_table)
	global_vars.query_auth_queue = global_vars.session.query(AuthQueue)
	auth_app_table = Table('auth_app', global_vars.metadata, autoload=True)
	mapper(AuthApp, auth_app_table)
	global_vars.query_auth_app = global_vars.session.query(AuthApp)

def initialize_all():
	initialize_main_db()
	initialize_authwebdb()
	initialize_mappers()

def verbose(string):
	if global_vars.verbose: print string

def create_database(dbname, user, passwd):
	"""initialize sql alchemy connection to db"""
	conn = connect_to_main_db()
	cursor = conn.cursor()
	query_string = "drop database if exists %s" % dbname
	print query_string
	cursor.execute(query_string)
	conn.commit()
	query_string = "create database %s" % dbname
	print query_string
	cursor.execute(query_string)
	conn.commit()
	cursor.close()
	conn.close()

def grant_privileges(dbname, user, passwd):
	"""initialize sql alchemy connection to db"""
	conn = connect_to_main_db()
	cursor = conn.cursor()
	query_string = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s'" % (dbname, user, passwd)
	cursor.execute(query_string)
	conn.commit()
	cursor.close()
	conn.close()


def drop_database(dbname):
	"""initialize sql alchemy connection to db"""
	conn = connect_to_main_db()
	cursor = conn.cursor()
	cursor.execute("drop database if exists %s;" % dbname)
	conn.commit()
	cursor.close()
	conn.close()
	directory = os.path.join(_filesdir, dbname)
	if os.path.exists(directory):
		shutil.rmtree(directory)
	jnlp_filename = os.path.join(_filesdir, "%s.jnlp" % dbname)
	if os.path.exists(jnlp_filename):
		os.remove(jnlp_filename)

def drop_auth_query(query_id):
	auth_query = global_vars.query.filter_by(query_id=query_id).first()
	global_vars.session.delete(auth_query)
	global_vars.session.flush()
	
def initialize_database(dbname, user, passwd):
	"""initialize sql alchemy connection to db"""
	db = create_engine("mysql://%s:%s@localhost/%s" % (user, passwd, dbname))
	db.echo = False
	metadata = MetaData(db)
	return (db, metadata)

class AuthQuery(object):
	pass

class AuthQueue(object):
	pass

class AuthApp(object):
	pass

# this class is to encapsulate the instance of the AuthApp, so it can do the
# SQLAlchemy session management and saving.

class AuthwebApp(object):
	"""docstring for AuthwebApp"""
	def __init__(self, auth_app):
		self.auth_app = auth_app
		self.auth_app.current_query_id = None

	def set_current_query_id(self, current_query_id):
		"""docstring for increment"""
		self.auth_app.current_query_id = current_query_id
		global_vars.session.add(self.auth_app)
		global_vars.session.flush()
		return self.auth_app.current_query_id

	def current_query_id(self):
		"""docstring for increment"""
		global_vars.session.refresh(self.auth_app)
		return self.auth_app.current_query_id
	
	def increment(self):
		"""docstring for increment"""
		self.auth_app.query_count += 1
		global_vars.session.add(self.auth_app)
		global_vars.session.flush()
		return self.auth_app.query_count
	

query_id_chars = string.ascii_letters + string.digits
def make_query_id():
	"""docstring for make_query_id"""
	return "authweb_" + ''.join([random.choice(query_id_chars) for i in range(20)])
	
def create_authweb_tables():
	"""docstring for create_authweb_tables"""
	auth_query_table = Table('auth_query', global_vars.metadata, 
	    Column('query_id', String(128), primary_key = True),
	    Column('session_id', String(128)),
	    Column('search_string', String(256)),
	    Column('total_count', Integer, nullable = False),
	    Column('state', Integer, default = 0),
	    Column('created_time', Integer, nullable = False),
	    Column('is_merged', Boolean, default = False),
	    Column('ip_address', String(128), nullable = False)
	)
	auth_query_table.create()
	auth_queue_table = Table('auth_queue', global_vars.metadata, 
	    Column('query_id', String(128), primary_key = True),
	    Column('query_number', Integer, nullable = False),
	    Column('query_type', Integer, nullable = False)
	)
	auth_queue_table.create()
	auth_app_table = Table('auth_app', global_vars.metadata,
	    Column('app_id', Integer, Sequence('app_id_sequence'), primary_key = True),
	    Column('current_query_id', String(128)),
	    Column('query_count', Integer, default = 0)
	)
	auth_app_table.create()

	
def drop_authweb_tables():
	"""drop table table_name"""
	global_vars.metadata.drop_all()
	global_vars.db.dispose()
	drop_database(AUTHWEB_DB)

def database_exists(database_name):
	"""docstring for database_exists"""
	query_string = "select schema_name from information_schema.schemata where schema_name='%s';" % database_name
	conn = connect_to_main_db()
	cursor = conn.cursor()
	num = cursor.execute(query_string)
	cursor.close()
	conn.close()
	return num == 1
	

create_authorship_tables_query = open("../sql/create_authorship_tables.sql").read().strip()

def create_database_and_tables(query_id):
	"""docstring for fname"""
	create_database(query_id, AUTHWEB_USER, AUTHWEB_PASSWD)
	grant_privileges(query_id, AUTHWEB_USER, AUTHWEB_PASSWD)
	conn = MySQLdb.connect(user=AUTHWEB_USER, passwd=AUTHWEB_PASSWD, db=query_id)
	cursor = conn.cursor()
	for subquery in create_authorship_tables_query.split(';'):
		print subquery
		subquery = subquery.strip()
		if not len(subquery) > 0:
			continue
		cursor.execute(subquery)
	conn.commit()
	cursor.close()
	conn.close()


def create_auth_query(query_id, session_id, search_string, total_count, ip_address):
	"""docstring for create_auth_query"""
	auth_query = AuthQuery()
	auth_query.query_id = query_id
	auth_query.session_id = session_id
	auth_query.search_string = search_string
	auth_query.total_count = total_count
	auth_query.state = QUERY_STATE_QUEUED
	auth_query.created_time = int(time.time())
	auth_query.is_merged = False
	auth_query.ip_address = ip_address
	global_vars.session.add(auth_query)
	global_vars.session.flush()


def query_num_downloaded(database_name):
	"""docstring for query_num_downloaded"""
	query_string = "select count(*) from %s.article_data;" % database_name
	conn = connect_to_main_db()
	cursor = conn.cursor()
	cursor.execute(query_string)
	row = cursor.fetchone()
	cursor.close()
	conn.close()
	return row[0]



def query(query_id):
	"""docstring for query_num_downloaded"""
	query = global_vars.query.filter_by(query_id=query_id).first()
	global_vars.session.refresh(query)
	return query
	
def get_query_list(session_id):
	"""docstring for get_query_list"""
	query_list = global_vars.query.filter(AuthQuery.session_id==session_id)
	for q in query_list:
		global_vars.session.refresh(q)
	return query_list

def get_query_list_all():
	"""docstring for get_query_list"""
	query_list = global_vars.query.filter()
	for q in query_list:
		global_vars.session.refresh(q)
	return query_list

def get_query_list_first():
	"""docstring for get_query_list"""
	query = global_vars.query.first()
	if query != None:
		global_vars.session.refresh(query)
	return query


# Set the state of the auth_query: 0=Queued, 1=Processing, 2=Done, ...
def set_query_state(query_id, state):
	"""docstring for set_query_state"""
	auth_query = global_vars.query.filter_by(query_id=query_id).first()
	auth_query.state = state
	global_vars.session.add(auth_query)
	global_vars.session.flush()
	
def set_query_merged(query_id):
	"""docstring for set_query_merged"""
	auth_query = global_vars.query.filter_by(query_id=query_id).first()
	auth_query.is_merged = True
	global_vars.session.add(auth_query)
	global_vars.session.flush()
	


# Set the state of the auth_query: 0=Queued, 1=Processing, 2=Done
def get_query_state(query_id):
	"""docstring for set_query_state"""
	auth_query = global_vars.query.filter_by(query_id=query_id).first()
	if auth_query == None:
		return None
	return auth_query.state

# By default delete queries older than a month
def clean_up_old_databases(aged_in_seconds = 60 * 60 * 24 * 30):
	"""docstring for clean_up_old_databases"""
	a_while_ago =  time.time() - aged_in_seconds
	auth_queries = global_vars.query.filter(AuthQuery.created_time < a_while_ago)
	for auth_query in auth_queries:
		drop_auth_query(auth_query.query_id)
		if database_exists(auth_query.query_id):
			drop_database(auth_query.query_id)

def clean_up_all_databases():
	"""docstring for clean_up_old_databases"""
	return clean_up_old_databases(0)

def create_everything():
	initialize_main_db()
	create_database(AUTHWEB_DB, AUTHWEB_USER, AUTHWEB_PASSWD)
	grant_privileges(AUTHWEB_DB, AUTHWEB_USER, AUTHWEB_PASSWD)
	grant_privileges(pubmed.JOURNAL_DB, AUTHWEB_USER, AUTHWEB_PASSWD)
	initialize_authwebdb()
	create_authweb_tables()

def create_app():
	# Create app and initialize query count to 0
	auth_app = AuthApp()
	global_vars.session.add(auth_app)
	global_vars.session.flush()


def initialize_app():
	# Create app and initialize query count to 0
	global_vars.authweb_app = AuthwebApp(global_vars.query_auth_app.first())
	

def create_and_initialize_app():
	# Create app and initialize query count to 0
	create_app()
	initialize_app()

def drop_everything():
	initialize_all()
	clean_up_all_databases()
	drop_authweb_tables()

def test():
	initialize_all()
	create_database_and_tables("authweb_guytest", "My Search", 21, "192.168.0.1")


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "h", ["help"])
		except getopt.error, msg:
			 raise Usage(msg)
		# more code, unchanged
		for o, a in opts:
			if o in ("-h", "--help"):
				print "python authwebdb.py drop|create"
				sys.exit(0)
		if len(args) > 0:
			if args[0] == "drop":
				drop_everything()
			elif args[0] == "create":
				create_everything()
				initialize_mappers()
				initialize_authwebdb()
				create_and_initialize_app()
			else:
				raise Usage, "must use 'drop' or 'create' argument"
		else:
			raise Usage, "must use 'drop' or 'create' argument"
		
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, "for help use --help"
		return 2

if __name__ == "__main__":
    sys.exit(main())
