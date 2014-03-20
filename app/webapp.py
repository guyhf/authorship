"""
webapp.py

Created by Guy Haskin Fernald on 2007-06-18.
Copyright (c) 2007 Guy Haskin Fernald. All rights reserved.
"""

import sys
sys.path.append("../lib")
import os
import glob
import cherrypy
import kid
import string
import random
import pubmed
import authwebdb
import time
import thread
import threading
import Queue
import networkgen
import traceback
from cherrypy.lib.static import serve_file

_curdir = os.getcwd()
_filesdir = os.path.join(_curdir, "files")
_mergePerPage = 100

templates = {}
filenames = glob.glob("../kid/*.kid")

for filename in filenames:
	root_path = os.path.split(filename)[1]
	root_name = os.path.splitext(root_path)[0]
	content = open(filename).read()
	templates[root_name] = content

def get_template(root_name):
	"""docstring for get_template"""
	try:
		return templates[root_name]
	except:
		return ""



class AuthwebApp(object):
	"""docstring for AuthwebApp"""
	_cp_config = { 'tools.sessions.on': True ,
	'tools.sessions.storage_type' : "file",
	'tools.sessions.storage_path' : "../sessions/",
	'tools.sessions.timeout' : 10080
	}
	
	
	def __init__(self, authdb_queue):
		self.authdb_queue = authdb_queue
		self.baseURL = cherrypy.config.get('server.baseURL')
	
	def setup(self):
		"""docstring for setup"""
		pass

	def _start_download(self):
		"""docstring for _start_download"""
		pms = cherrypy.session.get('pubmed_search')
		query_id = authwebdb.make_query_id()
		authwebdb.create_auth_query(query_id, cherrypy.session.id, pms.search_string, pms.count, cherrypy.request.remote.ip)
		self.authdb_queue.push(query_id, authwebdb.QUERY_TYPE_PROCESS)
	
	def _query_state_pp(self, query):
		if query.state == authwebdb.QUERY_STATE_DONE:
			return "Done"
		elif query.state == authwebdb.QUERY_STATE_GENERATING:
			return "Generating"
		elif query.state == authwebdb.QUERY_STATE_MERGING:
			return "Merging"
		elif query.state == authwebdb.QUERY_STATE_QUEUED:
			total_queue, queue_position = self.authdb_queue.get_position(query.query_id)
			return "Queued(%d)" % queue_position
		else:
			num_downloaded = authwebdb.query_num_downloaded(query.query_id)
			return "%d/%d" % (num_downloaded, query.total_count)

	@cherrypy.expose
	def index(self):
		return self.start()

	@cherrypy.expose
	def start(self):
		
		power_user = cherrypy.session.get('power', False)
		if power_user:
			queries = authwebdb.get_query_list_all()
		else:
			queries = authwebdb.get_query_list(cherrypy.session.id)
		formatted_queries = []
		any_queued = False
		for query in queries:
			q = {}
			q['state'] = query.state
			q['query_id'] = query.query_id
			q['search_string'] = query.search_string
			q['done'] = query.state == authwebdb.QUERY_STATE_DONE
			q['is_merged'] = query.is_merged
			q['done_or_queued'] = (query.state == authwebdb.QUERY_STATE_DONE) or (query.state == authwebdb.QUERY_STATE_QUEUED)
			q['is_processing'] = query.state == authwebdb.QUERY_STATE_PROCESSING
			if query.state == authwebdb.QUERY_STATE_QUEUED:
				any_queued = True
			q['status'] = self._query_state_pp(query)
			q['created_at'] =  time.strftime("%D, %I:%M:%S %p",time.localtime(query.created_time))
			formatted_queries.append(q)
		is_power = cherrypy.session.get('power', False)
		main_template = kid.Template(source=get_template('main'),
										formatted_queries=formatted_queries,
										current_query=authwebdb.global_vars.authweb_app.current_query_id(),
										any_queued=any_queued,
										is_power=is_power)
		main_page = main_template.serialize()
		page = []
		page.append(main_page)
		# Returns to the CherryPy server the page to render
		return page

	@cherrypy.expose
	def query_status(self):
		status = "None"
		if authwebdb.global_vars.authweb_app.current_query_id():
			query = authwebdb.query(authwebdb.global_vars.authweb_app.current_query_id())
			status = self._query_state_pp(query)
		return status
		
	@cherrypy.expose
	def delete(self, query_id):
		"""docstring for delete"""
		authwebdb.drop_database(query_id)
		authwebdb.drop_auth_query(query_id)
		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)

	@cherrypy.expose
	def txt(self, query_id):
		"""docstring for delete"""
		zip_filename = os.path.join(_filesdir, "%s/%s_txt.zip" % (query_id, query_id))
		return serve_file(zip_filename, "application/x-download", "attachment")

	@cherrypy.expose
	def cytoscape(self, query_id):
		"""docstring for delete"""
		zip_filename = os.path.join(_filesdir, "%s/%s_cytoscape.zip" % (query_id, query_id))
		return serve_file(zip_filename, "application/x-download", "attachment")

	@cherrypy.expose
	def pajek(self, query_id):
		"""docstring for delete"""
		zip_filename = os.path.join(_filesdir, "%s/%s_pajek.zip" % (query_id, query_id))
		return serve_file(zip_filename, "application/x-download", "attachment")

	@cherrypy.expose
	def alive(self):
		"""docstring for alive"""
		
		# try a couple of DB transactions to make sure we are up and running

		try:
			conn = pubmed.db_connection_maker(authwebdb.AUTHWEB_DB, authwebdb.AUTHWEB_USER, authwebdb.AUTHWEB_PASSWD)()
			cursor  = conn.cursor()
			cursor.execute("select * from auth_app limit 1;")
			row     = cursor.fetchone()
			conn.close()
			query = authwebdb.get_query_list_first()
		except:
			traceback.print_exc()
			return "NOTOK"

		return "OK"

	@cherrypy.expose
	def power(self):
		cherrypy.session['power'] = True
		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)
		
	@cherrypy.expose
	def nopower(self):
		cherrypy.session['power'] = False
		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)
		
	@cherrypy.expose
	def search(self, search_string):
		templ_str = get_template('search_result')
		
		pms = pubmed.PubmedSearch(search_string,1)
		cherrypy.session['pubmed_search'] = pms

		pms.do_search()
		
		template = kid.Template(source=templ_str, search_string=search_string, num_found=pms.count)
		page_string= template.serialize()

		page = []
		page.append(page_string)

		return page


	@cherrypy.expose
	def webstart(self, query_id):
		templ_str = get_template('webstart')
		url = {}
		url['codebase'] = cherrypy.request.base + "/files/"
		url['network_sif'] = cherrypy.request.base + "/files/%s/cytoscape/network.sif" % query_id
		url['name_na'] = cherrypy.request.base + "/files/%s/cytoscape/name.na" % query_id
		url['numpapers_na'] = cherrypy.request.base + "/files/%s/cytoscape/numpapers.na" % query_id
		url['impacttotal_na'] = cherrypy.request.base + "/files/%s/cytoscape/impacttotal.na" % query_id
		url['impactmean_na'] = cherrypy.request.base + "/files/%s/cytoscape/impactmean.na" % query_id
		url['numcoauthored_ea'] = cherrypy.request.base + "/files/%s/cytoscape/numcoauthored.ea" % query_id
		url['vizmap_props'] = cherrypy.request.base + "/files/%s/cytoscape/vizmap.props" % query_id
		
		template = kid.Template(source=templ_str, url=url, query_id=query_id)

		filepath = os.path.join(_filesdir, "%s.jnlp" % query_id)
		output = open(filepath, "w")
		output.write(template.serialize())
		output.close()
		
		url = "/files/%s.jnlp" % query_id

		raise cherrypy.HTTPRedirect("%s%s" % (self.baseURL, url))


	@cherrypy.expose
	def generate_network_pre(self):
		pms = cherrypy.session.get('pubmed_search', None)
		templ_str = get_template('generate_network_pre')
		
		template = kid.Template(source=templ_str, search_string=pms.search_string, num_found=pms.count)
		page_string= template.serialize()

		page = []
		page.append(page_string)

		return page

	@cherrypy.expose
	def merge_start(self, query_id):

		conn = pubmed.db_connection_maker(query_id, authwebdb.AUTHWEB_USER, authwebdb.AUTHWEB_PASSWD)()
		num_authors = networkgen.get_num_similar_authors(conn)
		conn.close()

		if num_authors == 0:
			state = 0
			templ_str = get_template('merge_none')
			authwebdb.set_query_merged(query_id)
		else:
			templ_str = get_template('merge_start')

		template = kid.Template(source=templ_str, num_authors=num_authors, query_id=query_id, merge_per_page=_mergePerPage)
		page_string= template.serialize()
		page = []
		page.append(page_string)

		return page

	@cherrypy.expose
	def merge(self, query_id, start_str):
		start = int(start_str)

		conn = pubmed.db_connection_maker(query_id, authwebdb.AUTHWEB_USER, authwebdb.AUTHWEB_PASSWD)()
		groups, authors, num_here = networkgen.get_similar_authors(conn, start, _mergePerPage, query_id)
		conn.close()
		
		if len(groups) > 0:
			templ_str = get_template('merge')
			template = kid.Template(source=templ_str, groups=groups, authors=authors, query_id=query_id, start=start, num_merge=num_here)
		else:
			templ_str = get_template('combine_start')
			template = kid.Template(source=templ_str, query_id=query_id)

		page_string= template.serialize()

		page = []
		page.append(page_string)

		return page

	@cherrypy.expose
	def merge_aggregate(self, *args, **kwds):

		start_str = kwds['start']
		start = int(start_str)
		num_merge_str = kwds['num_merge']
		num_merge = int(num_merge_str)
		query_id = kwds['query_id']
		num_groups = int(kwds['num_groups'])

		groups_to_combine = set()
		for i in range(num_groups):
			do_combine = kwds["do_combine%d" % i]
			combine_group = kwds["combine%d" % i]
			if do_combine:
				groups_to_combine.add(tuple(combine_group))
		
		merge_groups = cherrypy.session.get('merge_groups', set())
		merge_groups.update(tuple(groups_to_combine))
		cherrypy.session['merge_groups'] = merge_groups
		new_start = start + num_merge
		raise cherrypy.HTTPRedirect("%s/merge/%s/%d" % (self.baseURL, query_id, new_start))

	@cherrypy.expose
	def combine(self, *args, **kwds):
		query_id = kwds['query_id']
		merge_groups_set = cherrypy.session.get('merge_groups', set())
		merge_groups = list(merge_groups_set)

		conn = pubmed.db_connection_maker(query_id, authwebdb.AUTHWEB_USER, authwebdb.AUTHWEB_PASSWD)()
		authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_MERGING)
		networkgen.combine_authors(conn, merge_groups)
		conn.close()

		authwebdb.set_query_merged(query_id)
		
		self.authdb_queue.push(query_id, authwebdb.QUERY_TYPE_GENERATE)
		authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_QUEUED)			

		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)

	@cherrypy.expose
	def combineall(self, query_id):

		self.authdb_queue.push(query_id, authwebdb.QUERY_TYPE_MERGE)
		authwebdb.set_query_state(query_id, authwebdb.QUERY_STATE_QUEUED)		

		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)



	@cherrypy.expose
	def generate_network_start(self):
		pms = cherrypy.session.get('pubmed_search', None)
		
		# maybe create database for this search
		self._start_download()
		raise cherrypy.HTTPRedirect("%s/" % self.baseURL)


def main():

	# Update the global CherryPy configuration
	cherrypy.config.update("config.ini")

	# Initialize all of our DB stuff
	authwebdb.initialize_main_db()
	authwebdb.initialize_authwebdb()
	authwebdb.initialize_mappers()
	authwebdb.initialize_app()

	# Start the uploading queue
	authdb_queue_lock = thread.allocate_lock()
	authdb_queue = authwebdb.AuthDBQueue(authwebdb.global_vars.authweb_app, authdb_queue_lock, authwebdb.global_vars)

	authweb_app = AuthwebApp(authdb_queue)
	authweb_app.setup()

	# mount the application on the '/' base path
	cherrypy.tree.mount(authweb_app, '/', config = "application.ini")

	# Start CherryPy 
	cherrypy.engine.start()
	cherrypy.engine.block()


if __name__ == '__main__':
	main()
