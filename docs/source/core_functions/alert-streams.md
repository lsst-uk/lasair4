## Alert Streams

The Lasair broker can send immediate “push” notifications when your active query/filter sees and interesting alert. Here is how to make that happen with email notification. First make sure you are logged in to your Lasair account (top left of screen, then go to create new stored query. This page is about how to get email alerts from your active query; the process is very similar for Kafka alerts, except that you will fetch the results by machine instead of by email. See article Reading a Kafka Stream.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig1.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig1.png)

Fill in the form as shown here. Name and description, then check the “email” box, and fill in the SELECT as

objects.objectId, objects.latestrmag, jdnow()-objects.jdmax as since

check the “objects” table, and fill in the WHERE as

objects.latestrmag < 12

Then click “Create Query”

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig2.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig2.png)

Nothing will happen immediately. You can run the query in the usual way from the web browser, but you will have to wait for some alerts to arrive before your active query will be triggered. Once that happens, you will get an email at the address you used to create your account. Something like the message shown here. Note that the attributes you chose above are reported (objectId, latestrmag, since), together with the UTC time at which the alert was triggered.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig3.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig3.png)

In addition to the email, the webserver holds the last 1000 alerts that went to this channel. The link is in your list of queries.

[![](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig4.png)](https://lasair-ztf.lsst.ac.uk/lasair/static/cookbook/realtimealerts/fig4.png)

Click on that link and it will show you a page like this one.

## Smart Watchlists

By providing Kafka streams, Lasair provides a machine-readable packet of data that can cause action at your site. See the FAQ article on how to create a stream using the Lasair web environment. This page is about how to read it on your side. There is a [blog post](https://roywilliams.github.io/writing/streaming_data.html) about why Kafka is a good way to deal with streaming data.

*   We recommend [Confluent Kafka](https://pypi.org/project/confluent-kafka/), the python install being "pip install confluent\_kafka".
*   You will be connecting to kafka.lsst.ac.uk on port 9092
*   For coding details, please see the [accompanying notebook](https://colab.research.google.com/drive/1sV-JGzzVdZrP86P1tGu-naUQcMSSXAi7?usp=sharing).

You will need to understand two concepts: Topic and GroupID. The Topic is a string to identify which stream of alerts you want, which derives from the name of a Lasair streaming query. For example, the query defined [here](https://lasair-ztf.lsst.ac.uk/query/2/) is named "SN-like candidates", and its output collected [here](https://lasair-ztf.lsst.ac.uk/streams/lasair_2SN-likecandidates/). Its Kafka topic is "lasair\_2SN-likecandidates". The GroupID tells Kafka where to start delivery to you. It is just a string that you can make up, for example "Susan3456". The Kafka server remembers which GroupIds it has seen before, and which was the last alert it delivered. When you start your code again with the same GroupID, you only get alerts that arrived since last time you used that GroupId. If you use a new GroupID, you get the alerts from the start of the Kafka cache, which is about 7 days.


