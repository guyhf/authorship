<html xmlns="http://www.w3.org/1999/xhtml"
  xmlns:py="http://purl.org/kid/ns#">

<head>
<span py:replace="document('../xml/head.xml')"></span>
<meta py:if="num_downloaded != total_count" http-equiv="refresh" content="5" />
</head>

<body>
  <div id="container">
    <!-- Start container -->

    <div py:replace="document('../xml/pageHeader.xml')" />

    <div id="contentContainer">
      <!-- Start main content wrapper -->

      <div id="content">
        <!-- Start content -->
		<p>Generating network...</p>
		<p><center>Downloading articles...   ${num_downloaded}/${total_count} downloaded.</center></p>
		<p py:if="num_downloaded != total_count">(page will refresh automatically in 5 seconds)</p>
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
