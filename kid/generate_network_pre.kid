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
		<p>Generate Network.  This could take a while:</p>

		<blockquote>
			${search_string} : ${num_found}
		</blockquote>
		
		<form action="generate_network_start" method="get" accept-charset="utf-8">
			<p><input type="submit" value="Generate Network &rarr;"/></p>
		</form>
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
