#!/usr/bin/env python
# encoding: utf-8
"""
networkgen.py

Created by Guy Haskin Fernald on 2007-06-06.
Copyright (c) 2007 Guy Haskin Fernald. All rights reserved.
"""

		
import sys
import os
import MySQLdb
import zipfile
import shutil
import time
from string import Template

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))

def generate_file(tmpdir, query_id, make_db_connection):
	conn = make_db_connection()
	auth_list, authors = get_authors(conn)
	num_coauthored = get_coauthorship(conn, auth_list)
	
	# make the directory
	directory = os.path.join(tmpdir, query_id)
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.mkdir(directory)
	os.mkdir(os.path.join(directory, "txt"))
	os.mkdir(os.path.join(directory, "cytoscape"))
	os.mkdir(os.path.join(directory, "pajek"))
	
	# main network file with attributes
	numcoauthored_range = make_network(directory,
										auth_list,
										num_coauthored,
										authors)
	
	(num_paper_range, impact_total_range, impact_mean_range) = make_nodeattrs(conn,
																				directory,
																				auth_list,
																				authors)
																				
	conn.close()
	
	vizmap_path = os.path.join(directory, "cytoscape", "vizmap.props")
	basefile = os.path.join(_curdir, "../lib/vizmap_base.props")
	make_vizmap_props(vizmap_path, basefile, impact_total_range, impact_mean_range, num_paper_range, numcoauthored_range)
	
	zip_txt_filename = os.path.join(directory, "%s_txt.zip" % query_id)
	zip_txt_file = zipfile.ZipFile(zip_txt_filename, "w")
	zip_txt_file.write(os.path.join(directory, "txt", "network.txt"), "%s_txt/network.txt" % query_id)
	zip_txt_file.write(os.path.join(directory, "txt", "nodeattrs.txt"), "%s_txt/nodeattrs.txt" % query_id)
	zip_txt_file.write(vizmap_path, "%s_txt/vizmap.props" % query_id)
	zip_txt_file.close()

	zip_cyto_filename = os.path.join(directory, "%s_cytoscape.zip" % query_id)
	zip_cyto_file = zipfile.ZipFile(zip_cyto_filename, "w")

	cyto_output_filepath = os.path.join(directory, "cytoscape", "network.sif")
	cyto_name_na_output_filepath = os.path.join(directory, "cytoscape", "name.na")
	cyto_numpapers_na_output_filepath = os.path.join(directory, "cytoscape", "numpapers.na")
	cyto_impacttotal_na_output_filepath = os.path.join(directory, "cytoscape", "impacttotal.na")
	cyto_impactmean_na_output_filepath = os.path.join(directory, "cytoscape", "impactmean.na")
	
	zip_cyto_file.write(cyto_output_filepath, "%s_cytoscape/network.sif" % query_id)
	zip_cyto_file.write(cyto_name_na_output_filepath, "%s_cytoscape/name.na")
	zip_cyto_file.write(cyto_numpapers_na_output_filepath, "%s_cytoscape/numpapers.na" % query_id)
	zip_cyto_file.write(cyto_impactmean_na_output_filepath, "%s_cytoscape/impactmean.na" % query_id)
	zip_cyto_file.write(cyto_impacttotal_na_output_filepath, "%s_cytoscape/impacttotal.na" % query_id)
	zip_cyto_file.write(vizmap_path, "%s_cytoscape/vizmap.props" % query_id)
	zip_cyto_file.close()

	zip_pajek_filename = os.path.join(directory, "%s_pajek.zip" % query_id)
	zip_pajek_file = zipfile.ZipFile(zip_pajek_filename, "w")

	pajek_output_filepath = os.path.join(directory, "pajek", "network.net")
	pajek_numpapers_output_filepath = os.path.join(directory, "pajek", "numpapers.vec")
	pajek_impacttotal_output_filepath = os.path.join(directory, "pajek", "impacttotal.vec")
	pajek_impactmean_output_filepath = os.path.join(directory, "pajek", "impactmean.vec")
	
	zip_pajek_file.write(pajek_output_filepath, "%s_pajek/network.net" % query_id)
	zip_pajek_file.write(pajek_numpapers_output_filepath, "%s_pajek/numpapers.vec" % query_id)
	zip_pajek_file.write(pajek_impactmean_output_filepath, "%s_pajek/impactmean.vec" % query_id)
	zip_pajek_file.write(pajek_impacttotal_output_filepath, "%s_pajek/impacttotal.vec" % query_id)
	zip_pajek_file.close()
	
	return (zip_txt_filename, zip_cyto_filename, zip_pajek_filename)

def make_db_connection():
	return MySQLdb.connect(host="localhost", user="root", passwd="", db="authorship")

authors_query = """
SELECT
	ash.author_id author_id,
	auth.last_name last_name,
	auth.initials initials,
	count(ash.article_id) num
FROM
	article art,
	authorship ash,
	author auth
WHERE
	art.id = ash.article_id
AND
	auth.id = ash.author_id
AND
	art.is_review != true
GROUP BY
	author_id
ORDER BY
      last_name, initials
"""

def get_authors(conn):
	query = authors_query
	cursor = conn.cursor()
	num = cursor.execute(query)
	index = 1

	authors_list = []
	authors = {}
	
	for row in cursor.fetchall():
		author = {}
		author_id = str(row[0])
		author['id'] = author_id
		author['index'] = index
		author['last_name'] = row[1]
		author['initials'] = row[2]
		author['num_papers'] = int(row[3])
		author['pretty_name'] = "%s %s" % (row[1], row[2])
		authors_list.append(author_id)
		authors[author_id] = author
	
	return authors_list, authors

combine_authors_query = """
update authorship set author_id = %s where author_id = %s;
"""

duplicates_query = """
select id from authorship group by article_id, author_id having count(*) > 1;
"""

delete_author_query = """
delete from author where id = %s;
"""

delete_duplicates_query = """
delete from authorship where id in (%s);
"""

def combine_authors(conn, groups):

	for group in groups:
		first_id = group[0]
		for a_id in group[1:]:
			cursor = conn.cursor()
			query_string = combine_authors_query % (first_id, a_id)
			cursor.execute(query_string)
			query_string = delete_author_query % a_id
			cursor.execute(query_string)
			cursor.close()
	cursor = conn.cursor()
	cursor.execute(duplicates_query)
	results = cursor.fetchall()
	if len(results) > 0:
		id_list_str = ",".join([str(r[0]) for r in results])
		cursor.execute(delete_duplicates_query % id_list_str)
	cursor.close()
	
num_authors_similar_query = """
select id FROM author group by last_name, first_initial having count(*) > 1;
"""	
def get_num_similar_authors(conn):
	cursor = conn.cursor()
	num = cursor.execute(num_authors_similar_query)
	cursor.close()
	return num


authors_similar_query_one = """
CREATE TEMPORARY TABLE temp_%s
SELECT last_name, first_initial FROM author group by last_name, first_initial having count(*) > 1;
"""

authors_similar_query_two = """
SELECT
  a.id id,
  a.last_name last_name,
  a.first_initial first_initial,
  a.second_initial second_initial,
  a.first_name first_name
FROM
  author a,
  temp_%s t
WHERE
  a.last_name = t.last_name
AND
  a.first_initial = t.first_initial
ORDER BY
  last_name, first_initial LIMIT %d, %d;
"""


def get_similar_authors(conn, start, num_to_fetch, query_id):
	begin_index = start
	cursor = conn.cursor()
	cursor.execute(authors_similar_query_one % query_id)
	cursor.fetchall()
	num = cursor.execute(authors_similar_query_two % (query_id, begin_index, num_to_fetch))
	index = 1 

	groups = []
	authors = {}
	group = None

	cur_last_name = ""
	cur_first_initial = ""
	
	num_names = 0
	for row in cursor.fetchall():
		author = {}
		author_id = str(row[0])
		last_name = row[1]
		first_initial = row[2]
		author['id'] = author_id
		author['last_name'] = last_name
		author['first_initial'] = row[2]
		author['second_initial'] = row[3]
		author['first_name'] = row[4]

		authors[author_id] = author

		if (last_name.upper() != cur_last_name.upper()) or (first_initial.upper() != cur_first_initial.upper()):
			cur_last_name = last_name
			cur_first_initial = first_initial
			if group != None:
				group_len = len(group)
				if group_len > 1:
					groups.append(group)
					num_names += group_len
			group = []

		group.append(author_id)
	
	if group != None:
		group_len = len(group)
		if group_len > 1:
			groups.append(group)
			num_names += group_len

	return groups, authors, num_names


all_authors_similar_query_one = """
CREATE TEMPORARY TABLE temp_%s
SELECT last_name, first_initial FROM author group by last_name, first_initial having count(*) > 1;
"""

all_authors_similar_query_two = """
SELECT
  a.id,
  a.last_name last_name,
  a.first_initial first_initial
FROM
  author a,
  temp_%s t
WHERE
  a.last_name = t.last_name
AND
  a.first_initial = t.first_initial
ORDER BY
  last_name, first_initial;
"""

def get_all_similar_authors(conn, query_id):
	cursor = conn.cursor()
	cursor.execute(all_authors_similar_query_one % query_id)
	cursor.fetchall()
	cursor.execute(all_authors_similar_query_two % query_id)

	groups = []
	group = None

	cur_last_name = None
	
	for row in cursor.fetchall():
		author_id = str(row[0])
		last_name = row[1]

		if last_name != cur_last_name:
			cur_last_name = last_name
			if group != None:
				if len(group) > 1:
					groups.append(group)
			group = []

		group.append(author_id)
	
	if group != None:
		if len(group) > 1:
			groups.append(group)
	
	return groups

candidate_merge_authors_query = """
SELECT
  last_name,
  first_initial
FROM
  author
GROUP BY
  last_name, first_initial
HAVING
  count(*) > 1;
"""

	
similar_authors_query = """
SELECT
  id,
  last_name,
  first_initial,
  initials
FROM
  author
WHERE
	upper(last_name) = "%s"
AND
	upper(first_initial) = "%s"
ORDER BY
  last_name, first_initial;
"""

def merge_authors(query_id, make_db_connection):
	conn = make_db_connection()
	cursor = conn.cursor()
	cursor.execute(candidate_merge_authors_query)
	author_names = cursor.fetchall()
	cursor.close()
	for (last_name, first_initial) in author_names:
		if last_name == None:
			last_name = ""
		if first_initial == None:
			first_initial = ""

		query = similar_authors_query % (last_name.upper(), first_initial.upper())

		cursor = conn.cursor()
		cursor.execute(query)
		authors = cursor.fetchall()
		cursor.close()
		
		(first_id_int, first_last_name, first_first_initial, first_initials) = authors[0]
		first_id = str(first_id_int)
		
		for row in authors[1:]:
			a_id = str(row[0])
			last_name = row[1]
			first_initial = row[2]
			initials = row[3]

			query_string = combine_authors_query % (first_id, a_id)
			cursor = conn.cursor()
			cursor.execute(query_string)
			query_string = delete_author_query % a_id
			cursor.execute(query_string)
			cursor.close()

	cursor = conn.cursor()
	cursor.execute(duplicates_query)
	results = cursor.fetchall()

	if len(results) > 0:
		id_list_str = ",".join([str(e[0]) for e in results])
		cursor.execute(delete_duplicates_query % id_list_str)

	cursor.close()

	conn.close()

artice_ids_query = """
SELECT 
	ash.article_id article_id,
	art.pubmed_id pubmed_id
FROM
	article art,
	authorship ash
WHERE
	ash.author_id=%s
AND
	art.id = ash.article_id
AND
	art.is_review != true
;
"""
def get_article_ids_for_author_id(conn, author_id):
	"""docstring for article_ids_for_author"""
	article_ids = {}
	query = artice_ids_query % author_id
	cursor = conn.cursor()
	cursor.execute(query)
	for row in cursor.fetchall():
		article_ids[str(row[0])] = True
	
	return article_ids.keys()

collaborators_query = """
SELECT
	author_id id
FROM
	authorship
WHERE
	article_id
IN
	(
	  %s
	)
AND
	author_id != %s
;"""

def get_coauthor_ids(conn, author_id):
	"""docstring for get_collaborators"""
	article_ids = get_article_ids_for_author_id(conn, author_id)
	articles_string = ",".join(article_ids)
	
	query = collaborators_query % (articles_string, author_id)
	cursor = conn.cursor()
	cursor.execute(query)
	
	return list(set([str(row[0]) for row in cursor.fetchall()]))

num_coauthored_query = """
SELECT
	count(*) num
FROM
	authorship
WHERE
	author_id = %s
AND
	article_id
IN
	(
	%s
	)
;
"""

def get_number_coauthored(conn, author_id, coauthor_id):
	"""docstring for get_number_coauthored"""
	coauthored_article_ids_string = ",".join(get_article_ids_for_author_id(conn, coauthor_id))
	query = num_coauthored_query % (author_id, coauthored_article_ids_string)
	cursor = conn.cursor()
	cursor.execute(query)
	
	row = cursor.fetchone()
	return int(row[0])

	
def get_coauthorship(conn, author_ids):
	"""docstring for get_coauthorship"""
	coauthorship = {}
	for author_id in author_ids:
		coauthorship[author_id] = {}
		for coauthor_id in get_coauthor_ids(conn, author_id):

			if coauthorship[author_id].has_key(coauthor_id):
				if not coauthorship.has_key(coauthor_id):
					coauthorship[coauthor_id] = {}
				coauthorship[coauthor_id][author_id] = coauthorship[author_id][coauthor_id]
				continue

			num = get_number_coauthored(conn, author_id, coauthor_id)
			coauthorship[author_id][coauthor_id] = num

	return coauthorship
	
articles_with_impact_query = """
SELECT
	j.impact_factor impact
FROM
	authorship ash,
	article art,
	journal_db.journal j
WHERE
	ash.author_id = %s
AND
	art.id = ash.article_id
AND
	j.id = art.journal_id
;
"""

def get_impact_factors(conn, author_id):
	"""docstring for get_impact_factors"""
	query = articles_with_impact_query % author_id
	cursor = conn.cursor()
	cursor.execute(query)
	return [row[0] for row in cursor.fetchall()]

def make_impact_factors(conn, output_total, output_mean, auth_list):
	"""docstring for make_num_coauthored"""
	output_total.write("ImpactTotal\n")
	output_mean.write("ImpactMean\n")
	for a_id in auth_list:
		impact_factors = get_impact_factors(conn, a_id)
		total = sum(impact_factors)
		mean = total/float(len(impact_factors))
		output_total.write("%s = %.2f\n" % (a_id, total))
		output_mean.write("%s = %.2f\n" % (a_id, mean))

def make_num_coauthored(conn, output, auth_list, num_coauthored, authors):
	"""docstring for make_num_coauthored"""
	output.write("NumberCoauthored\n")
	linked = {}
	for a_id in auth_list:
		linked[a_id] = {}
		coauth_list = num_coauthored[a_id].keys()
		for c_id in coauth_list:
			if c_id in auth_list:
				if not linked.has_key(c_id):
					linked[c_id] = {}
					
				if not linked[a_id].has_key(c_id) and not linked[c_id].has_key(a_id):
					linked[a_id][c_id] = True
					linked[c_id][a_id] = True
					
					output.write("%s (coauthor) %s = %d\n" % (	authors[a_id]['id'],
					 											authors[c_id]['id'],
																num_coauthored[a_id][c_id]))

def make_names(conn, output, auth_list, authors):
	"""docstring for make_num_coauthored"""
	output.write("Name\n")
	for a_id in auth_list:
		output.write("%s = %s %s\n" % (a_id, authors[a_id]['last_name'], authors[a_id]['initials']))
		
def make_num_papers(conn, output, auth_list, authors):
	"""docstring for make_num_coauthored"""
	output.write("NumPapers\n")
	for a_id in auth_list:
		output.write("%s = %d\n" % (a_id, authors[a_id]['num_papers']))

# def make_sif_file(conn, output, auth_list, num_coauthored, authors):
# 	"""docstring for make_sif_file"""
# 	linked = {}
# 	for a_id in auth_list:
# 		linked[a_id] = {}
# 		coauth_list = num_coauthored[a_id].keys()
# 		for c_id in coauth_list:
# 			if c_id in auth_list:
# 				if not linked.has_key(c_id):
# 					linked[c_id] = {}
# 					
# 				if not linked[a_id].has_key(c_id) and not linked[c_id].has_key(a_id):
# 					linked[a_id][c_id] = True
# 					linked[c_id][a_id] = True
# 					
# 					output.write("%s coauthor %s\n" % (	authors[a_id]['id'],
# 					 									authors[c_id]['id']))
# 
def make_network(directory, auth_list, num_coauthored, authors):
	"""docstring for make_network"""
	
	txt_output_filepath = os.path.join(directory, "txt", "network.txt")
	txt_output = open(txt_output_filepath, "w")
	txt_output.write("AuthorID1\tRelationship\tAuthorID2\tNumberCoauthored\n")
	
	cyto_output_filepath = os.path.join(directory, "cytoscape", "network.sif")
	cyto_output = open(cyto_output_filepath, "w")
	
	cyto_ea_output_filepath = os.path.join(directory, "cytoscape", "numcoauthored.ea")
	cyto_ea_output = open(cyto_ea_output_filepath, "w")
	cyto_ea_output.write("NumCoauthored\n")
	
	pajek_top_output_filepath = os.path.join(directory, "pajek", "network.net")
	pajek_top_output = open(pajek_top_output_filepath, "w")
	pajek_top_output.write("/* authorship network generated at %s */\r\n" % time.asctime())
	pajek_top_output.write("*Vertices %d\r\n" % len(auth_list))
	
	pajek_bottom_output_filepath = os.path.join(directory, "pajek", "network_bottom.net")
	pajek_bottom_output = open(pajek_bottom_output_filepath, "w")
	pajek_bottom_output.write("*Arcs\r\n")

	min_num = sys.maxint
	max_num = -(sys.maxint - 1)
	linked = {}
	for a_id in auth_list:
		linked[a_id] = {}
		pajek_top_output.write("%s \"%s, %s\"\r\n" %
							(authors[a_id]['id'],
							authors[a_id]['last_name'],
							authors[a_id]['initials']))
		coauth_list = num_coauthored[a_id].keys()
		for c_id in coauth_list:
			if c_id in auth_list:
				if not linked.has_key(c_id):
					linked[c_id] = {}
				if not linked[a_id].has_key(c_id) and not linked[c_id].has_key(a_id):
					linked[a_id][c_id] = True
					linked[c_id][a_id] = True
					
					num = num_coauthored[a_id][c_id]
					
					min_num = min(num, min_num)
					max_num = max(num, max_num)
					
					txt_output.write("%s\tcoauthor\t%s\t%s\n" % (authors[a_id]['id'],
					 										 	authors[c_id]['id'],
															 	num))
																
					cyto_output.write("%s coauthor %s\n" % (	authors[a_id]['id'],
																		authors[c_id]['id']))
																		
					cyto_ea_output.write("%s (coauthor) %s = %d\n" % (	authors[a_id]['id'],
					 															authors[c_id]['id'],
																				num_coauthored[a_id][c_id]))
					pajek_bottom_output.write("%s %s %d w %d\r\n" %
												(authors[a_id]['id'],
												authors[c_id]['id'],
												num_coauthored[a_id][c_id],
												num_coauthored[a_id][c_id]))
	pajek_top_output.close()
	pajek_bottom_output.close()
	
	
	pajek_top_output = open(pajek_top_output_filepath, "a")
	pajek_top_output.write(open(pajek_bottom_output_filepath, "r").read())
	
	pajek_top_output.close()
	pajek_bottom_output.close()
	os.remove(pajek_bottom_output_filepath)

	txt_output.close()
	cyto_ea_output.close()
	cyto_output.close()
	
	return (min_num, max_num)

# AUTHWEB_IMPACTTOTALLABELCOLOR1-5
# AUTHWEB_AUTHORSHIPNUMPAPERSIZE1-6
# AUTHWEB_NUMCOAUTHOREDLINETYPE1-6
# AUTHWEB_IMPACTMEANCOLOR1-7 - maybe can yse the same?

def linspace(xmin, xmax, N):
	if N==1: return xmax
	dx = (xmax-xmin)/(N-1)
	return [xmin + dx * idx for idx in range(N)]

def add_vars_to_dict(dictionary, basename, indices, values):
	for i in indices:
		varname = "%s%d" % (basename, i)
		dictionary[varname] = values[i-1]

def make_vizmap_props(filepath, basefile, impact_total_range, impact_mean_range, num_paper_range, numcoauthored_range):
	dictionary = {}
	
	min_val, max_val = impact_total_range
	values = linspace(min_val, max_val, 5)
	add_vars_to_dict(dictionary, "AUTHWEB_IMPACTTOTALLABELCOLOR", range(1,6), values)
	
	min_val, max_val = impact_mean_range
	values = linspace(min_val, max_val, 7)
	add_vars_to_dict(dictionary, "AUTHWEB_IMPACTMEANCOLOR", range(1,8), values)
	
	min_val, max_val = num_paper_range
	values = linspace(min_val, max_val, 6)
	add_vars_to_dict(dictionary, "AUTHWEB_AUTHORSHIPNUMPAPERSIZE", range(1,7), values)
	
	min_val, max_val = numcoauthored_range
	values = linspace(min_val, max_val, 6)
	add_vars_to_dict(dictionary, "AUTHWEB_NUMCOAUTHOREDLINETYPE", range(1,7), values)
	
	base_string = open(basefile).read()
	base_template = Template(base_string)
	
	output = open(filepath, "w")
	output.write(base_template.substitute(dictionary))
	output.close()

def make_nodeattrs(conn, directory, auth_list, authors):
	"""docstring for make_nodeattrs"""

	txt_na_output_filepath = os.path.join(directory, "txt", "nodeattrs.txt")
	txt_na_output = open(txt_na_output_filepath, "w")
	
	cyto_name_na_output_filepath = os.path.join(directory, "cytoscape", "name.na")
	cyto_name_na_output = open(cyto_name_na_output_filepath, "w")

	cyto_numpapers_na_output_filepath = os.path.join(directory, "cytoscape", "numpapers.na")
	cyto_numpapers_na_output = open(cyto_numpapers_na_output_filepath, "w")

	cyto_impacttotal_na_output_filepath = os.path.join(directory, "cytoscape", "impacttotal.na")
	cyto_impacttotal_na_output = open(cyto_impacttotal_na_output_filepath, "w")

	cyto_impactmean_na_output_filepath = os.path.join(directory, "cytoscape", "impactmean.na")
	cyto_impactmean_na_output = open(cyto_impactmean_na_output_filepath, "w")
	
	pajek_numpapers_output_filepath = os.path.join(directory, "pajek", "numpapers.vec")
	pajek_numpapers_output = open(pajek_numpapers_output_filepath, "w")
	
	pajek_impacttotal_output_filepath = os.path.join(directory, "pajek", "impacttotal.vec")
	pajek_impacttotal_output = open(pajek_impacttotal_output_filepath, "w")
	
	pajek_impactmean_output_filepath = os.path.join(directory, "pajek", "impactmean.vec")
	pajek_impactmean_output = open(pajek_impactmean_output_filepath, "w")

	# There seems to be a bug in Cytoscape 2.4.1 where the first line of imported text attr data is ignored.
	# Writing the header line twice is a workaround.
	txt_na_output.write("AuthorID\tName\tNumPapers\tImpactTotal\tImpactMean\n")
	txt_na_output.write("AuthorID\tName\tNumPapers\tImpactTotal\tImpactMean\n")

	cyto_name_na_output.write("Name\n")
	cyto_numpapers_na_output.write("NumPapers\n")
	cyto_impacttotal_na_output.write("ImpactTotal\n")
	cyto_impactmean_na_output.write("ImpactMean\n")
	
	pajek_numpapers_output.write("*Vertices %d\r\n" % len(auth_list))
	pajek_impacttotal_output.write("*Vertices %d\r\n" % len(auth_list))
	pajek_impactmean_output.write("*Vertices %d\r\n" % len(auth_list))

	numpapers_min = sys.maxint
	numpapers_max = -(sys.maxint - 1)
	
	impacttotal_min = sys.maxint
	impacttotal_max = -(sys.maxint - 1)
	
	impactmean_min = sys.maxint
	impactmean_max = -(sys.maxint - 1)
	
	for a_id in auth_list:
		name = "%s %s" % (authors[a_id]['last_name'], authors[a_id]['initials'])
		num_papers =  authors[a_id]['num_papers']
		impact_factors = get_impact_factors(conn, a_id)
		total = sum(impact_factors)
		mean = total/float(len(impact_factors))
		impact_total = "%.2f" % total
		impact_mean = "%.2f" % mean
		
		numpapers_min = min(numpapers_min, int(num_papers))
		numpapers_max = max(numpapers_max, int(num_papers))
		
		impacttotal_min = min(impacttotal_min, float(impact_total))
		impacttotal_max = max(impacttotal_max, float(impact_total))
		
		impactmean_min = min(impactmean_min, float(impact_mean))
		impactmean_max = max(impactmean_max, float(impact_mean))
		
		txt_na_output.write("%s\t%s\t%d\t%s\t%s\n" % (a_id, name, num_papers, impact_total, impact_mean))
		cyto_name_na_output.write("%s = %s %s\n" % (a_id, authors[a_id]['last_name'], authors[a_id]['initials']))
		cyto_numpapers_na_output.write("%s = %d\n" % (a_id, authors[a_id]['num_papers']))
		cyto_impactmean_na_output.write("%s = %.2f\n" % (a_id, mean))
		cyto_impacttotal_na_output.write("%s = %.2f\n" % (a_id, total))
		pajek_numpapers_output.write("%d\r\n" % authors[a_id]['num_papers'])
		pajek_impactmean_output.write("%.2f\r\n" % mean)
		pajek_impacttotal_output.write("%.2f\r\n" % total)

	txt_na_output.close()
	cyto_name_na_output.close()
	cyto_numpapers_na_output.close()
	cyto_impactmean_na_output.close()
	cyto_impacttotal_na_output.close()
	return ((numpapers_min, numpapers_max), (impacttotal_min, impacttotal_max), (impactmean_min, impactmean_max))


# IMPACTTOTALLABELCOLOR1

def main():
	"""docstring for main"""
	pass
	# conn = make_db_connection()
	# auth_list, authors = get_authors(conn, 100)
	# num_coauthored = get_coauthorship(conn, auth_list)
	# output = open("../test.sif", "w")
	# make_sif_file(conn, output, auth_list, num_coauthored, authors)
	# output.close()
	# output = open("../num_coauthored.ea", "w")
	# make_num_coauthored(conn, output, auth_list, num_coauthored, authors)
	# output.close()
	# output = open("../names.na", "w")
	# make_names(conn, output, auth_list, authors)
	# output.close()
	# output = open("../num_papers.na", "w")
	# make_num_papers(conn, output, auth_list, authors)
	# output.close()
	# 51 = open("../impact_total.na", "w")
	# output_mean = open("../impact_mean.na", "w")
	# make_impact_factors(conn, output_total, output_mean, auth_list)
	# output_total.close()
	# output_mean.close()

if __name__ == '__main__':
	main()


