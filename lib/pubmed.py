#!/usr/bin/env python
# encoding: utf-8
"""
pubmed.py

Created by Guy Haskin Fernald on 2007-05-30.
Copyright (c) 2007 Guy Haskin Fernald. All rights reserved.
"""

import sys
import os
import re
import datetime
import urllib
import MySQLdb
from StringIO import StringIO
from xml.dom import minidom
import time
import thread
import threading
import traceback
import timeit


JOURNAL_DB = "journal_db"

debug_on = False
def debug(out_string):
    """docstring for _debug"""
    if debug_on:
        sys.stderr.write("(%s): %s\n" % (datetime.datetime.now().strftime("%F %r"), out_string))


def latin1_to_ascii (unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
        something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
        This function makes a best effort to convert Latin-1 characters into 
        ASCII equivalents. It does not just strip out the Latin-1 characters.
        All characters in the standard 7-bit ASCII range are preserved. 
        In the 8th bit range all the Latin-1 accented letters are converted 
        to unaccented equivalents. Most symbol characters are converted to 
        something meaningful. Anything not converted is deleted.
    """
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C',
        0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
        0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
        0xdd:'Y', 0xde:'th', 0xdf:'ss',
        0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
        0xe6:'ae', 0xe7:'c',
        0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
        0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
        0xf0:'th', 0xf1:'n',
        0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
        0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
        0xfd:'y', 0xfe:'th', 0xff:'y',
        0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 
        0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        0xd7:'*', 0xf7:'/'
        }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r

class PubmedSearch(object):
    """docstring for PubmedSearch"""
    
    # do not include review articles
    
    Pubmed_Search_URL = "http://www.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s%%20not%%20%%22Review%%22&retmode=xml&retstart=%d&retmax=1"
    
    def __init__(self, search_string, index):
        super(PubmedSearch, self).__init__()
        self.search_string = search_string
        self.index = index
    

    def do_search(self):
        """docstring for _do_search"""
        url_string = self.Pubmed_Search_URL % (urllib.quote(self.search_string), self.index)
        debug("search_url_string = '%s'" % url_string)
        downloaded = False
        while not downloaded:
            try:
                xmlsock = urllib.urlopen(url_string)
                xmldoc = minidom.parse(xmlsock).childNodes[1]
                downloaded = True
            except:
                print "Error: couldn't download url: '%s'" % url_string
                traceback.print_exc()
        elts = {}
        for elt in xmldoc.childNodes:
            if elt.nodeType == elt.ELEMENT_NODE:
                elts[elt.tagName] = elt
        
        try:
            self.count = int(elts['Count'].firstChild.data)
            self.retmax = int(elts['RetMax'].firstChild.data)
            self.retstart = int(elts['RetStart'].firstChild.data)
        except:
            print "Error couldn't get elts from data."
            traceback.print_exc()
            return None
        
        self.id_list = []
        for e in elts['IdList'].childNodes:
            if e.nodeType == e.ELEMENT_NODE:
                self.id_list.append(str(e.firstChild.data))

        debug("count = %d" % self.count)
        debug("retmax = %d" % self.retmax)
        debug("retstart = %d" % self.retstart)
        debug("id_list = %s" % ",".join(self.id_list))

        try:
            return self.id_list[0]
        except:
            return None


        
class PubmedFetch(object):
    """docstring for PubmedSearch"""
        
    Pubmed_Fetch_URL = "http://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml"
    
    def __init__(self, id_string):
        super(PubmedFetch, self).__init__()
        self.id_string = id_string
    
    def do_fetch(self):
        """docstring for _do_fetch"""
        url_string = self.Pubmed_Fetch_URL % self.id_string
        debug("fetch_url_string = '%s'" % url_string)
        data = None
        try:
            xmlsock = urllib.urlopen(url_string)
            data = xmlsock.read()
        except Error:
            data = ""
        return data

class PubmedArticle(object):
    """docstring for PubmedArticle"""
    def __init__(self, xmldoc):
        super(PubmedArticle, self).__init__()
        self.xmldoc = xmldoc
        self.is_review = None
        self.year = None
        self.month = None
        self.issn = None
        self.journal_name = None
        self.pubmed_id = None
        self._do_parse()


    def _hasYearAndMonth(self, elements):
        
        if len(elements) <= 0:
            return False
            
        element = elements[0]
        
        if element == None:
            return False

        year_elts = element.getElementsByTagName("Year")
        month_elts = element.getElementsByTagName("Month")
        
        if len(year_elts) <= 0:
            return False
        
        if len(month_elts) <= 0:
            return False

        return year_elts[0] != None and month_elts[0] != None

    def _do_parse(self):
        """docstring for _do_parse"""
        # assign MedlineCitation and PubmedData
        try:
            set_elts = [e for e in self.xmldoc.childNodes if e.nodeType == e.ELEMENT_NODE]
            elts = [e for e in set_elts[0].childNodes if e.nodeType == e.ELEMENT_NODE]
        except:
            raise "Error processing XML for article"

        medline_doc = elts[0]
        pubmed_doc  = elts[1]

        ## Get the TITLE

        title_uni = medline_doc.getElementsByTagName("Article")[0].getElementsByTagName("ArticleTitle")[0].childNodes[0].data

        self.title = latin1_to_ascii(title_uni)

        ## Get the Date
        date_elts = medline_doc.getElementsByTagName("PubDate")
        if not self._hasYearAndMonth(date_elts):
            date_elts = medline_doc.getElementsByTagName("ArticleDate")
            if not self._hasYearAndMonth(date_elts):
                date_elts = pubmed_doc.getElementsByTagName("PubMedPubDate")
                if not self._hasYearAndMonth(date_elts):
                    date_elts = medline_doc.getElementsByTagName("DateCreated")
                    if not self._hasYearAndMonth(date_elts):
                        raise "No Year or Month for entry: %s" % self
        
        date_elt = date_elts[0]
        self.year = int(date_elt.getElementsByTagName("Year")[0].firstChild.data)
        self.month = str(date_elt.getElementsByTagName("Month")[0].firstChild.data)
        
        
        ## Get ISSN
        try:
            self.issn = str(medline_doc.getElementsByTagName("ISSN")[0].firstChild.data)
        except:
            self.issn = None
        
        ## Get Journal Name, JournalID, PubMedID

        try:
            self.journal_name = latin1_to_ascii(medline_doc.getElementsByTagName("MedlineTA")[0].firstChild.data)
        except:
            raise "No Journal name for entry: %s" % self

        ## get PubmedID
        try:
            article_id_list = pubmed_doc.getElementsByTagName("ArticleIdList")
            article_ids = [a for a in article_id_list[0].childNodes if a.nodeType == a.ELEMENT_NODE]
            pubmed_id_uni = [a for a in article_ids if a.attributes["IdType"].value == "pubmed"][0].firstChild.data
            self.pubmed_id = latin1_to_ascii(pubmed_id_uni)
        except:
            raise "No PubmedID for entry: %s" % self
        
        ## Check for Review
        pubtypes_doc = medline_doc.getElementsByTagName("Article")[0].getElementsByTagName("PublicationTypeList")[0]
        pubtypes = [str(e.childNodes[0].data) for e in pubtypes_doc.childNodes if e.nodeType == e.ELEMENT_NODE]
        
        
        self.is_review = False
        for t in pubtypes:
            if re.match("review", t.lower()):
                self.is_review = True
                
        ## Look up authors, authors will be a list of tuples (LastName, Forename, Initials)
        self.authors = []
        author_list_elts = medline_doc.getElementsByTagName("AuthorList")

        if author_list_elts != None and len(author_list_elts) > 0:
            author_list_doc = author_list_elts[0]
            author_list = [e for e in author_list_doc.childNodes if e.nodeType == e.ELEMENT_NODE]
        else:
            author_list = []

        for author in author_list:
            try:
                last_name = author.getElementsByTagName("LastName")[0].firstChild.data
            except:
                last_name = None

            try:
                fore_name = author.getElementsByTagName("ForeName")[0].firstChild.data
            except:
                try:
                    fore_name = author.getElementsByTagName("FirstName")[0].firstChild.data
                except:
                    fore_name = None

            try:
                initials = author.getElementsByTagName("Initials")[0].firstChild.data
            except:
                initials = None

            if last_name == None or fore_name == None or initials == None:
                continue

            self.authors.append((latin1_to_ascii(last_name),latin1_to_ascii(fore_name),latin1_to_ascii(initials)))


    def __str__(self):
        """docstring for __str__"""
        string_rep = """
        Title: '%s'
        Review: %s
        Year: %d
        Month: %s
        ISSN: %s
        Journal: %s
        Pubmed ID: %s
"""
        return latin1_to_ascii(string_rep % (self.title, self.is_review, self.year, self.month, self.issn, self.journal_name, self.pubmed_id))


    
def article_insert(cursor, article, journal_id, data_id):
    """docstring for article_insert"""
    values = (  MySQLdb.escape_string(article.title),
                article.year,
                MySQLdb.escape_string(article.month),
                MySQLdb.escape_string(article.pubmed_id),
                journal_id,
                article.is_review and 1 or 0,
                data_id)

    query_str = """INSERT into article values(NULL, '%s', %d, '%s', '%s', %d, %d, %d);"""
    query = query_str % values
    cursor.execute(query)
    cursor.execute("""SELECT LAST_INSERT_ID();""")
    row = cursor.fetchone()
    article_id = int(row[0])

    for (last, first, initials) in article.authors:
        author_id = author_lookup(cursor, last, first, initials)
        if author_id == None:
            if len(last) > 0 and len(first) > 0:
                author_id = author_insert(cursor, last, first, initials)
        authorship_insert(cursor, article_id, author_id)
    
def author_lookup(cursor, last, first, initials):
    """docstring for author_lookup(conn, last, first, initials)"""
    ## Now get authors and possible insert them if necessary while updating the authorship table
    ## Match authors by queries:
    ## 1. lastname only
    ## 2. lastname and initial
    ## 3. lastname firstname
    ## 4. lastname firstname initial
    ## if still not present then insert the author

    first_initial = ""
    second_initial = ""

    if len(initials) > 0:
        first_initial = initials[0]

    if len(initials) > 1:
        second_initial = initials[1]

    query = """SELECT id from author where upper(last_name) = '%s'  and upper(initials) = '%s'""" % (MySQLdb.escape_string(last.upper()), MySQLdb.escape_string(initials.upper()))
    cursor.execute(query)
    rows = cursor.fetchall()
    nrows = len(rows)
    
    if nrows == 1:
        return int(rows[0][0])
    else:
        return None

def author_insert(cursor, last, first, initials):
    """docstring for author_lookup(conn, last, first, initials)"""

    initials_quoted = "NULL"
    first_initial_quoted = "NULL"
    second_initial_quoted = "NULL"

    if len(initials) == 0:
        initials = first[0].upper()

    if len(initials) > 0:
        initials_quoted = "'%s'" % MySQLdb.escape_string(initials)
        first_initial_quoted = "'%s'" % MySQLdb.escape_string(initials[0])

    if len(initials) > 1:
        second_initial_quoted = "'%s'" % MySQLdb.escape_string(initials[1])
    
    last_quoted = "'%s'" % MySQLdb.escape_string(last)
    first_quoted = "'%s'" % MySQLdb.escape_string(first)

    values = (last_quoted, first_quoted, initials_quoted, first_initial_quoted, second_initial_quoted)
    query = """INSERT into author values (NULL, %s, %s, %s, %s, %s);""" % values
    cursor.execute(query)
    cursor.execute("SELECT LAST_INSERT_ID();")
    row = cursor.fetchone()
    author_id = int(row[0])
    
    return author_id

    
def authorship_insert(cursor, article_id, author_id):
    """docstring for authorship_insert"""
    if article_id is not None and author_id is not None:
        query = """SELECT count(*) from authorship where article_id=%d and author_id=%d;""" % (article_id, author_id)

        cursor.execute(query)
        row = cursor.fetchone()
        num = row[0]

        if num == 0:
            query = """INSERT into authorship values(NULL, %d, %d);""" % (article_id, author_id)
            cursor.execute(query)



def article_download_and_import(conn, db_lock, search_string, count, unknown_journal_id):
    """docstring for article_import"""
    
    
    # Do the pubmed search
    pms = PubmedSearch(search_string, count)
    id_string = pms.do_search()
    pmf = PubmedFetch(id_string)
    data = pmf.do_fetch()
    
    # Make sure that we can parse it
    try:
        xmldoc = minidom.parse(StringIO(str(data)))
    except:
        xmldoc = None

    if xmldoc == None:
        return None
    
    try:
        article = PubmedArticle(xmldoc.childNodes[1])
    except:
        return None
    
    # the data is good.  insert data into article_data and continue
    
    cursor=conn.cursor()
    db_lock.acquire()
    cursor.execute("""START TRANSACTION;""")
    cursor.execute("""INSERT INTO article_data VALUES (NULL, %s);""", (data,) )
    nres=cursor.execute("""SELECT LAST_INSERT_ID();""")
    row = cursor.fetchone()
    data_id = int(row[0])
    cursor.execute("""COMMIT;""")
    
    try:
        xmldoc = minidom.parse(StringIO(str(data)))
    except:
        xmldoc = None

    if xmldoc == None:
        return None
        
    article = PubmedArticle(xmldoc.childNodes[1])

    journal_name = article.journal_name
    query = """SELECT id from %s.journal where name='%s'""" % (JOURNAL_DB, journal_name)
    journal_id = cursor.execute(query)
    jids = [row[0] for row in cursor.fetchall()]

    if len(jids) != 1:
        issn = article.issn
        query = """SELECT id from %s.journal where issn='%s'""" % (JOURNAL_DB, issn)
        cursor.execute(query)
        jids = [row[0] for row in cursor.fetchall()]
    
    if len(jids) == 0:
        similar_name = journal_name.replace(' ', '%')
        query = """SELECT id from %s.journal where upper(name) like '%s'""" % (JOURNAL_DB, similar_name.upper())
        cursor.execute(query)
        jids = [row[0] for row in cursor.fetchall()]
        
    if len(jids) == 0:
        jids = [unknown_journal_id]

    journal_id = int(jids[0])
    
    cursor.execute("START TRANSACTION;")
    article_insert(cursor, article, journal_id, data_id)
    cursor.execute("COMMIT;")
    cursor.close()
    conn.close()
    db_lock.release()
    return data_id
    


class ArticleDownloader(threading.Thread):
    """docstring for ArticleDownloader"""
    def __init__(self, conn, lock, search_string, index, unknown_journal_id):
        super(ArticleDownloader, self).__init__()
        self.conn = conn
        self.lock = lock
        self.search_string = search_string
        self.index = index
        self.unknown_journal_id = unknown_journal_id
    
    def run(self):
        """docstring for run"""
        done = False
        while not done:
            try:
                article_download_and_import(self.conn,
                                            self.lock,
                                            self.search_string,
                                            self.index,
                                            self.unknown_journal_id)
            except:
                print "Error in article_download_and_import: '%s', '%d'" % (self.search_string, self.index)
                traceback.print_exc()
                
            else:
                done = True

        self.lock.acquire()
        global download_count
        download_count += 1
        global available_threads
        available_threads += 1
        self.lock.release()

    

def release_thread(request, data_id):
    """docstring for dosomething"""
    request.lock.acquire()
    global available_threads
    available_threads += 1
    request.lock.release()
    
def import_articles_pool(search_string, pool_size, make_db_connection):

    pms = PubmedSearch(search_string, 0)
    pms.do_search()
    total_count = pms.count

    lock = thread.allocate_lock()
    db_lock = thread.allocate_lock()
    conn = make_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id from %s.journal where issn='9999-9999';" % JOURNAL_DB)
    row = cursor.fetchone()
    unknown_journal_id = row[0]
    cursor.close()
    conn.close()

    global download_count
    download_count = 0
    index = 0
    global available_threads
    available_threads = pool_size
    
    while download_count < total_count:
        
        lock.acquire()
        if (index < total_count) and (available_threads > 0):
            available_threads -= 1
            lock.release()
            this_conn = make_db_connection()
            
            article_downloader = ArticleDownloader(this_conn, db_lock, search_string, index, unknown_journal_id)
            article_downloader.start()
            index += 1
            
        else:
            lock.release()
            time.sleep(1)



# TODO move db_connection_maker to authwebdb
def db_connection_maker(name, user, passwd):
    return lambda: MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=name)

def import_articles_test(search_string, pool_size):
    make_db_function = db_connection_maker("authorship", "root", "")
    import_articles_pool(search_string, pool_size, make_db_function)
    
def main():
    t = timeit.Timer('import_articles_test("Montalban",75)', "from __main__ import import_articles_test")
    print t.timeit(1)

if __name__ == '__main__':
    main()
