# Making a Lasair Filter

The Lasair database has information about objects and candidates. Each candidate is a detection made by the telescope, and the collection of detections of a given star is an object. Queries are written with the SQL language, that is built in three pieces through the Lasair web interface:

*   WHAT you are selecting (“Select Attributes”)
*   WHICH tables to use, and
*   CONDITIONS on what you are selecting (“Where”).

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig1.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig1.png)

This example query looks for objects within the Orion Nebula. Once you have logged in to Lasair, you can create a query from the /myquery page, shown at left. Write a name and description, then keep the query inactive and not public (first 2 green boxes). The “select attributes” box has autocomplete for the possible attributes, which are also listed in detail at the /schema page. In this case we chose the object identifier objectId, and the number of good candidates, ncandgp. Select only the objects table – meaning no joins. The “where” box has the square degree of the sky which is the Orion Nebula. Then click “Create query”.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig2.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig2.png)

Now we can run the query. Go to the page /objlist and find your saved query, then click on its name (green box). The form fields above are now filled in with the details

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig3.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig3.png)

In addition to the saved query, we can add an additional constraint (green box), where we restrict to objects that have had a detection in the last 10 days. Now click “Run filter”.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig4.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig4.png)

The results appear, as a table with the columns as specified in the “select attributes” part of the query. The actual SQL that runs against the database is shown. You can see (red boxes) an execution time limit of 300 seconds, the “recent” events constraint written as objects.jdmax $gt; JDNOW() - 10.00000, and a limit of 1000 results. If more, there will be a link to the next page of results. Notice that the objectId is a link

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig5.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig5.png)

This is the information page for a Lasair object. You can see the light curve (top left) and sky locations for the candidates. There is a wealth of information (see this page). In particular, you can click on the “Simbad” link, which fetches information about this source.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig6.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/query/fig6.png)

The Simbad database tells us that the star we selected is a Variable Star of Orion type.

