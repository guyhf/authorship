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

		You have selected all of the authors, click "Combine" to continue.
		
			<p>
			<form action="/combine" method="post" accept-charset="utf-8">
			<input type="hidden" name="query_id" value="${query_id}"/>

			<input type="submit" value="Combine"/>
			</form>
			</p>
      </div><!-- End content -->
    </div><!-- End main content wrapper -->

    <div py:replace="document('../xml/footer.xml')" />

  </div><!-- End container -->
</body>
</html>
