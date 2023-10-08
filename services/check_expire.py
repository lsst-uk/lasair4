"""
Expiration warnings and deactivation for active resources 
    where a resource is a filter, watchlist, or watchmap
    Checks one or all resources for expiration nearer than DAYS days
    and if it finds them does action that can be email warning, 
    or expiration plus email confirmation.
    The action is taken of the expiration is less than DAYS in the future
    By default all resources are checked, or just one type of resource,
    or just one specific resource of given id (rid).

Usage:
    check_expire.py <action> <days> [<resource>] [<rid>]
    check_expire.py list

Options:
      <action>: (set|warning|expiration)
        set: Choose set to set expiration for some days in the future
        warning: Choose warning to send email of upcoming expiration 
        expiration: Choose expiration to send email and deactivate
      <days>: Days is number of days ahead for expiration
      Optional: <resource>: choose filter|watchlist|watchmap to run on only one kind of resource
      Optional: <rid> choose id for resource to run only on that

"""
import os, sys, math, time, stat
import datetime, docopt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.append('../common')
import settings
sys.path.append('../common/src')
from src import db_connect

# What we should call the resource, then the database name of it, then the name of the identifier
resources = {
    'filter':    {'dbname':'myqueries',  'rid': 'mq_id'},
    'watchlist': {'dbname':'watchlists', 'rid': 'wl_id'},
    'watchmap':  {'dbname':'areas',      'rid': 'ar_id'},
}

# The emails we can send out
messages = {
'warning':
"""
Dear %s,
Your active Lasair %s will become inactive in about a week without action from you, and there will be no further real-time matching of incoming alerts. This is to relieve pressure on the real-time pipeline. To keep your %s active, go to %s then click "Settings", then "Save".
""",

'expiration':
"""
Dear %s,
Your active Lasair %s has expired and become inactive, and there will be no further matching of incoming alerts. To make your %s active again, go to %s then click "Settings", "active", then "Save".
""",
}

def send_email(email, message, message_html=''):
    print(email, message, message_html)
#    msg = MIMEMultipart('alternative')

#    msg['Subject'] = 'Lasair: Active resource becoming inactive'
#    msg['From']    = 'donotreply@%s' % settings.LASAIR_URL
#    msg['To']      = email

#    msg.attach(MIMEText(message, 'plain'))
#    if len(message_html) > 0:
#        msg.attach(MIMEText(message_html, 'html'))
#    s = smtplib.SMTP('localhost')
#    s.sendmail('donotreply@%s' % settings.LASAIR_URL, email, msg.as_string())
#    s.quit()

def list_resources(msl):
    """
    List all the active resources
    """
    global resources
    now = datetime.datetime.now()
    cursor = msl.cursor(buffered=True, dictionary=True)
    for rname,resource in resources.items():
        print('Active ', rname)
        query = 'SELECT %s as id, name, first_name, last_name, email, date_expire ' % resource['rid'] 
        query += 'FROM %s,auth_user WHERE auth_user.id=user AND active>0 ' % resource['dbname']
        query += 'ORDER BY  date_expire'
        cursor.execute(query)
        for row in cursor:
            name = '[%s %s]' % (row['first_name'], row['last_name'])
            until = row['date_expire'] - now
            print('   %5d expires %.1f daysAhead %s %s' % (row['id'], until.days, name, row['name']))

def set_expire(msl, resource, daysAhead, rid=None):
    """
    Set the given resource expiration dates in the future
    if the resource id (rid) is None, it does all of them
    """
    expire = datetime.datetime.now() + datetime.timedelta(days=daysAhead)
    query = 'UPDATE %s SET date_expire="%s"' % (resource['dbname'], str(expire))
    if rid:
        query += ' WHERE %s=%s' % (resource['rid'], rid)
    print(query)
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    msl.commit()

def make_inactive(msl, resource, rid):
    """
    The actual teeth of the thing. Switches the given resource to inactive.
    """
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'UPDATE %s SET active=0 where %s=%s'
    query = query % (resource['dbname'], resource['rid'], rid)
    print(query)
    cursor.execute(query)
    msl.commit()

def check_and_action(msl, rname, resource, action, daysAhead, rid=None):
    """
    Check all the given resources for a warning message of for actual expiration.
    if the resource id (rid) is None, it does all of them
    """
    if rid:
        print('Checking expiration for %s with %s, rid=%s' % (rname, action, rid))
    else:
        print('Checking expiration for %s with %s, rid=All' % (rname, action))
    timelimit = datetime.datetime.now() + datetime.timedelta(days=daysAhead)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT %s as id, name, first_name, last_name, email, date_expire ' % resource['rid'] 
    query += 'FROM %s,auth_user WHERE auth_user.id=user AND active>0 ' % resource['dbname']
    if rid:
        query += 'AND id=%s' % rid
    cursor.execute(query)
    for row in cursor:
        if row['date_expire'] and row['date_expire'] < timelimit:
            rid = row['id']
            print(rid, 'expiry is post %d daysAhead'%daysAhead)
            name = '%s %s' % (row['first_name'], row['last_name'])

            url      = '%s/%ss/%d/' % (settings.LASAIR_URL, rname, rid)
            url_html = '<a href="%s">%s</a>' % (url, url)

            message_fmt = messages[action]
            message      = message_fmt % (name, rname, rname, url)
            message_html = message_fmt % (name, rname, rname, url_html)

            send_email(row['email'], message, message_html)
            if message == 'expiration':
                make_inactive(msl, resource, rid)

if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    action = args['<action>']
    rname  = args['<resource>']
    rid    = args['<rid>']
    
    print(args)
    msl = db_connect.remote()

    if args['list']:
        list_resources(msl)
        sys.exit()

    daysAhead   = int(args['<days>'])

    if action == 'set':
        if not rname:
            for  rname,resource in resources.items():
                set_expire(msl, resource, daysAhead, rid=rid)
        elif rname in resources:
            set_expire(msl, resources[rname], daysAhead, rid=rid)
        else:
            print('Resource name %s not recognised, must be in %s' % (rname, resources.keys()))

    elif action == 'warning' or action == 'expiration':
        if not rname:
            for  rname,resource in resources.items():
                check_and_action(msl, rname, resource, action, daysAhead)
        elif rname in resources:
            check_and_action(msl, rname, resources[rname], action, daysAhead, rid)
        else:
            print('Resource name %s not recognised, must be in %s' % (rname, resources.keys()))

    else:
        print('Action %s not recognised, must be in list|set|warning|expiration' % action)
