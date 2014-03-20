<?xml version="1.0" encoding="UTF-8"?>
<jnlp codebase="${url['codebase']}" href="${query_id}.jnlp">
  <security>
    <all-permissions />
  </security>
  <information>
    <title>Cytoscape Webstart</title>
    <vendor>Cytoscape Collaboration</vendor>
    <homepage href="http://cytoscape.org" />
    <offline-allowed />
  </information>
  <resources>
    <j2se version="1.5+" max-heap-size="1024M" />
    <!--All lib jars that cytoscape requires to run should be in this list-->
    <jar href="cytoscape.jar" />
    <jar href="lib/activation.jar" />
    <jar href="lib/biojava-1.4.jar" />
    <jar href="lib/colt.jar" />
    <jar href="lib/coltginy.jar" />
    <jar href="lib/com-nerius-math-xform.jar" />
    <jar href="lib/commons-cli-1.x-cytoscape-custom.jar" />
    <jar href="lib/concurrent.jar" />
    <jar href="lib/cytoscape-cruft-obo.jar" />
    <jar href="lib/cytoscape-geom-rtree.jar" />
    <jar href="lib/cytoscape-geom-spacial.jar" />
    <jar href="lib/cytoscape-graph-dynamic.jar" />
    <jar href="lib/cytoscape-graph-fixed.jar" />
    <jar href="lib/cytoscape-render-export.jar" />
    <jar href="lib/cytoscape-render-immed.jar" />
    <jar href="lib/cytoscape-render-stateful.jar" />
    <jar href="lib/cytoscape-task.jar" />
    <jar href="lib/cytoscape-util-intr.jar" />
    <jar href="lib/ding.jar" />
    <jar href="lib/fing.jar" />
    <jar href="lib/freehep-base.jar" />
    <jar href="lib/freehep-graphics2d.jar" />
    <jar href="lib/freehep-graphicsio-gif.jar" />
    <jar href="lib/freehep-graphicsio-pdf.jar" />
    <jar href="lib/freehep-graphicsio-ps.jar" />
    <jar href="lib/freehep-graphicsio-svg.jar" />
    <jar href="lib/freehep-graphicsio-swf.jar" />
    <jar href="lib/freehep-graphicsio.jar" />
    <jar href="lib/giny.jar" />
    <jar href="lib/glf.jar" />
    <jar href="lib/jaxb-api.jar" />
    <jar href="lib/jaxb-impl.jar" />
    <jar href="lib/jdom.jar" />
    <jar href="lib/jhall.jar" />
    <jar href="lib/jnlp.jar" />
    <jar href="lib/jsr173_1.0_api.jar" />
    <jar href="lib/junit.jar" />
    <jar href="lib/looks-1.1.3.jar" />
    <jar href="lib/phoebe.jar" />
    <jar href="lib/piccolo.jar" />
    <jar href="lib/piccolox.jar" />
    <jar href="lib/swing-layout-1.0.1.jar" />
    <jar href="lib/tclib.jar" />
    <jar href="lib/violinstrings-1.0.2.jar" />
    <jar href="lib/wizard.jar" />
    <jar href="lib/xercesImpl.jar" />
    <!--These are the plugins you wish to load, edit as necessary.-->
    <jar href="plugins/AutomaticLayout.jar" />
    <jar href="plugins/biopax.jar" />
    <jar href="plugins/browser.jar" />
    <jar href="plugins/cPath.jar" />
    <jar href="plugins/CytoscapeEditor.jar" />
    <jar href="plugins/exesto.jar" />
    <jar href="plugins/filter.jar" />
    <jar href="plugins/GraphMerge.jar" />
    <jar href="plugins/linkout.jar" />
    <jar href="plugins/ManualLayout.jar" />
    <jar href="plugins/psi_mi.jar" />
    <jar href="plugins/quick_find.jar" />
    <jar href="plugins/SBMLReader.jar" />
    <jar href="plugins/TableImport.jar" />
    <jar href="plugins/yeast-context.jar" />
    <jar href="plugins/yLayouts.jar" />
  </resources>
  <!--This starts-up Cytoscape, specify your plugins to load, and other command line arguments.  Plugins not specified here will not be loaded.-->
  <application-desc main-class="cytoscape.CyMain">
    <argument>-p</argument>
    <argument>csplugins.layout.LayoutPlugin</argument>
    <argument>-p</argument>
    <argument>org.mskcc.biopax_plugin.plugin.BioPaxPlugIn</argument>
    <argument>-p</argument>
    <argument>browser.AttributeBrowserPlugin</argument>
    <argument>-p</argument>
    <argument>org.cytoscape.coreplugin.cpath.plugin.CPathPlugIn</argument>
    <argument>-p</argument>
    <argument>cytoscape.editor.CytoscapeEditorPlugin</argument>
    <argument>-p</argument>
    <argument>filter.cytoscape.CsFilter</argument>
    <argument>-p</argument>
    <argument>GraphMerge.GraphMerge</argument>
    <argument>-p</argument>
    <argument>linkout.LinkOutPlugin</argument>
    <argument>-p</argument>
    <argument>ManualLayout.ManualLayoutPlugin</argument>
    <argument>-p</argument>
    <argument>org.cytoscape.coreplugin.psi_mi.plugin.PsiMiPlugIn</argument>
    <argument>-p</argument>
    <argument>csplugins.quickfind.plugin.QuickFindPlugIn</argument>
    <argument>-p</argument>
    <argument>sbmlreader.SBMLReaderPlugin</argument>
    <argument>-p</argument>
    <argument>edu.ucsd.bioeng.coreplugin.tableImport.TableImportPlugin</argument>
    <argument>-p</argument>
    <argument>yfiles.YFilesLayoutPlugin</argument>
    <argument>-N</argument>
    <argument>${url['network_sif']}</argument>
    <argument>-n</argument>
    <argument>${url['name_na']}</argument>
    <argument>-n</argument>
    <argument>${url['numpapers_na']}</argument>
    <argument>-n</argument>
    <argument>${url['impacttotal_na']}</argument>
    <argument>-n</argument>
    <argument>${url['impactmean_na']}</argument>
    <argument>-e</argument>
    <argument>${url['numcoauthored_ea']}</argument>
    <argument>--vizmap</argument>
    <argument>${url['vizmap_props']}</argument>
    <argument>-P</argument>
    <argument>defaultVisualStyle=authorship</argument>
  </application-desc>
</jnlp>
