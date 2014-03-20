<html xmlns="http://www.w3.org/1999/xhtml"
  xmlns:py="http://purl.org/kid/ns#">

<head>
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

		Some authors are listed under multiple names.  The following authors look similar.  Please de-select any authors which should not be combined and click 'Combine' to combine them.  You will then be brought to the next page of authors.
		
			<p>
			<form action="/merge_aggregate" method="post" accept-charset="utf-8">
			<input type="hidden" name="query_id" value="${query_id}"/>
			<input type="hidden" name="num_groups" value="${len(groups)}"/>
			<input type="hidden" name="num_merge" value="${num_merge}"/>
			<input type="hidden" name="start" value="${start}"/>
			<table> 
			<tr>
				<th>Combine?</th>
				<th>Authors</th>
			</tr>
			<tr py:for="i in range(len(groups))">
			<td>
				<input type="radio"
				  name="do_combine${i}"
				  value="True" CHECKED="YES"/> Yes
				<input type="radio"
				  name="do_combine${i}"
				  value="False"/> No
			</td>
			<td>
				<table>
				<tr py:for="a_id in groups[i]">
				<td><input type="checkbox" name="combine${i}" value="${a_id}" CHECKED="YES"/></td>
				<td>${authors[a_id]['last_name']}</td>
				<td>${authors[a_id]['first_initial']}</td>
				<td>${authors[a_id]['second_initial']}</td>
				<td>${authors[a_id]['first_name']}</td>
				</tr>
				</table>
			</td>
			</tr>
			</table>
			<input type="submit" value="Continue"/>
			</form>
			</p>
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
