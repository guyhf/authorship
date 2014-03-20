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


		Your search <tt>"${search_string}"</tt> returned ${num_found} articles.  You may refine your search below.
		
			<p><form action="/search" method="post" accept-charset="utf-8"><input type="text" name="search_string" value="${search_string}" id="search"/><input type="submit" value="Refine Search"/></form> <form action="/generate_network_pre" method="post" accept-charset="utf-8"> <input type="submit" value="Continue to next step  →"/></form></p>
		
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
