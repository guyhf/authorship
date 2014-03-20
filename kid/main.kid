<html xmlns="http://www.w3.org/1999/xhtml"
  xmlns:py="http://purl.org/kid/ns#">

<head>
<span py:if="any_queued and not current_query">
	<meta http-equiv="refresh" content="5"/>
</span>

<span py:replace="document('../xml/head.xml')"></span>

</head>

<body>
  <div id="container">
    <!-- Start container -->

    <div py:replace="document('../xml/pageHeader.xml')" />

    <div id="contentContainer">
      <!-- Start main content wrapper -->
	
      <div id="content">
        <!-- Start content -->
		Enter any valid Pubmed search string below. Examples:
		<UL>
		<LI>All articles with "multiple sclerosis genetics": <tt>multiple sclerosis genetics</tt></LI>
		<LI>All articles with "Doe J" as author: <tt>Doe J[au]</tt></LI>
		<LI>All articles with "Doe J" as author between June and September 2007: <tt>Doe J[au] and 2007/6/1:2007/9/1[dp]</tt></LI>
		</UL>
		Refresh this page to update status of network generation.
		<form action="search"
		      method="post"
		      accept-charset="utf-8">
		  <p><input type="text"
		         name="search_string"
		         size="40"
		         value=""
		         id="search" /> <input type="submit"
		         value="Continue to next step →" /></p>
		</form>

		<div py:if="len(formatted_queries) > 0" id="table">
			<table width="700"> 
			<tr>
				<th>Delete</th>
				<th>View</th>
				<th>Merge</th>
				<th>&nbsp;</th>
				<th>Download</th>
				<th>&nbsp;</th>
				<th>Search&nbsp;String</th>
				<th>Status</th>
				<th>Created At</th>
			</tr>
			<tr py:for="query in formatted_queries"> 
				<td>
					<span py:if="query['done_or_queued']"><font color="red"><a href="/delete/${query['query_id']}">delete</a></font></span>
					<span py:if="not query['done_or_queued']">delete</span>					
				</td>
					<td>
					<span py:if="query['done']"><a href="/webstart/${query['query_id']}">view</a></span>
					<span py:if="not query['done']">view</span>					
				</td>
					<td>
					<span py:if="not query['is_merged'] and query['done']"><a href="/merge_start/${query['query_id']}">merge</a></span>
					<span py:if="query['is_merged'] or not query['done']">merge</span>					
				</td>
				<td>
					<span py:if="query['done']"><a href="/txt/${query['query_id']}">txt.zip</a></span>
					<span py:if="not query['done']">txt.zip</span>
					</td>
					<td>					
					<span py:if="query['done']"><a href="/cytoscape/${query['query_id']}">cyto.zip</a></span>
					<span py:if="not query['done']">cyto.zip</span>
					</td>
					<td>
					<span py:if="query['done']"><a href="/pajek/${query['query_id']}">pajek.zip</a></span>
					<span py:if="not query['done']">pajek.zip</span>

				</td>
				<td><span py:content="query['search_string']"></span></td>
				<td><span py:if="query['is_processing']">

						<div id="query_status" value="${query['query_id']}">&nbsp;</div>
					</span>
					<span py:if="not query['is_processing']">
						<span py:content="query['status']"></span>
					</span>
				</td>
				<td><span py:content="query['created_at']"></span></td>
			</tr> 
			</table>
		</div>

		<font size="1">
			<span py:if="is_power"><a href="/nopower">show only my queries</a></span>
			<span py:if="not is_power"><a href="/power">show all queries</a></span>
		</font>


      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
