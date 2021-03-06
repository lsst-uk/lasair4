from django.db import models

# A watchlist is owned by a user and given a name and description
# Only active watchlists are run against the realtime ingestion
# The prequel_where can be used to select which candidates are compared with the watchlist
from django.contrib.auth.models import User

# When a watchlist is run against the database, ZTF candidates may be matched to cones
# We also keep the objectId of that candidate and distance from the cone center
# If the same run happens again, that candidate will not go in again to the same watchlist.

class WatchlistCones(models.Model):
    """WatchlistCones.
    """

    cone_id = models.AutoField(primary_key=True)
    wl      = models.ForeignKey('Watchlists', models.DO_NOTHING, blank=True, null=True)
    name    = models.CharField(max_length=32, blank=True, null=True)
    ra      = models.FloatField(blank=True, null=True)
    decl    = models.FloatField(blank=True, null=True)
    radius  = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'watchlist_cones'

class Watchlists(models.Model):
    """Watchlists.
    """

    wl_id         = models.AutoField(primary_key=True)
    user          = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    name          = models.CharField(max_length=256, blank=True, null=True)
    description   = models.CharField(max_length=4096, blank=True, null=True)
    active        = models.IntegerField(blank=True, null=True)
    public        = models.IntegerField(blank=True, null=True)
    radius        = models.FloatField(blank=True, null=True)
    timestamp     = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'watchlists'

    def __str__(self):
        return self.user.first_name +' '+ self.user.last_name +': '+ self.name

class Areas(models.Model):
    """Areas.
    """

    ar_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.CharField(max_length=4096, blank=True, null=True)
    moc = models.TextField(blank=True, null=True)
    mocimage = models.TextField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    timestamp     = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'areas'

    def __str__(self):
        return self.user.first_name +' '+ self.user.last_name +': '+ self.name

class Myqueries(models.Model):
    """Myqueries.
    """

    mq_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.CharField(max_length=4096, blank=True, null=True)
    selected = models.CharField(max_length=4096, blank=True, null=True)
    conditions = models.CharField(max_length=4096, blank=True, null=True)
    tables = models.CharField(max_length=4096, blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    topic_name = models.CharField(max_length=256, blank=True, null=True)
    real_sql = models.CharField(max_length=4096, blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'myqueries'

    def __str__(self):
        return self.user.first_name +' '+ self.user.last_name +': '+ self.name

class Annotators(models.Model):
    topic = models.CharField(primary_key=True, max_length=32)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
#    owner = models.IntegerField()
    username = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    url = models.CharField(max_length=1024, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'annotators'

    def __str__(self):
        return self.user.first_name +' '+ self.user.last_name +': ' + self.topic
