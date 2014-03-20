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

		Some authors are listed under multiple names.  You can automatically merge all of them or you can choose which
		ones you want to merge manually.  An author is considered similar if the first initial and last name are same, such as:
		<UL>
				<LI>Smith, J and Smith, JE</LI>
		</UL>
			
		There are <B>${num_authors}</B> groups of authors that look similar:
		<UL>
			<LI><a href="/combineall/${query_id}">Merge all automatically</a></LI>
			<LI><a href="/merge/${query_id}/0">Merge manually (hand pick ${merge_per_page} per page)</a></LI>
		</UL>
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
