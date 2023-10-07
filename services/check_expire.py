"""
check_expire.py
"""
import os, sys, math, time, stat
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.append('../common')
import settings
sys.path.append('../common/src')
from src import db_connect

lasair_url = 'https://lasair-dev.lsst.ac.uk'

resources = [
    {'name':'filter',    'dbname':'myqueries',  'rid': 'mq_id'},
    {'name':'watchlist', 'dbname':'watchlists', 'rid': 'wl_id'},
    {'name':'watchmap',  'dbname':'areas',      'rid': 'ar_id'},
]

messages = {
'warning':
"""
Dear %s,
Your active Lasair %s will become inactive in about a week without action from you, and there will be no further real-time matching of incoming alerts. This is to relieve pressure on the real-time pipeline. To keep your %s active, go to %s then click "Settings", then "Save".
""",

'expired':
"""
Dear %s,
Your active Lasair %s has expired and become inactive, and there will be no further matching of incoming alerts. To make your %s active again, go to %s then click "Settings", "active", then "Save".
""",
}

def send_email(email, message, message_html=''):
    print(email, message, message_html)
#    msg = MIMEMultipart('alternative')

#    msg['Subject'] = 'Lasair: Active watchlist becoming inactive'
#    msg['From']    = 'donotreply@%s' % settings.LASAIR_URL
#    msg['To']      = email

#    msg.attach(MIMEText(message, 'plain'))
#    if len(message_html) > 0:
#        msg.attach(MIMEText(message_html, 'html'))
#    s = smtplib.SMTP('localhost')
#    s.sendmail('donotreply@%s' % settings.LASAIR_URL, email, msg.as_string())
#    s.quit()

def set_expire(msl, resource, days, rid=None):
    expire = datetime.datetime.now() + datetime.timedelta(days=days)
    query = 'UPDATE %s SET date_expire="%s"' % (resource['dbname'], str(expire))
    if rid:
        query += ' WHERE %s=%d' % (resource['rid'], rid)
    print(query)
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    msl.commit()

def check_and_send(msl, resource, message_type, days):
    timelimit = datetime.datetime.now() + datetime.timedelta(days=days)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT %s as id, name, first_name, last_name, email, date_expire ' % resource['rid'] 
    query += 'FROM %s,auth_user WHERE auth_user.id=user' % resource['dbname']
    cursor.execute(query)
    for row in cursor:
        if row['date_expire'] and row['date_expire'] < timelimit:
            rid = row['id']
            print(rid, 'expiry is post %d days'%days)
            name = '%s %s' % (row['first_name'], row['last_name'])
            rname = resource['name']

            url      = '%s/%ss/%d/' % (lasair_url, rname, rid)
            url_html = '<a href="%s">%s</a>' % (url, url)

            message_fmt = messages[message_type]
            message      = message_fmt % (name, rname, rname, url)
            message_html = message_fmt % (name, rname, rname, url_html)

            send_email(row['email'], message, message_html)

if __name__ == "__main__":
    msl = db_connect.remote()
    for r in resources:
#       set_expire(msl, r, days=10)
        check_and_send(msl, r, 'warning', days=7)
        check_and_send(msl, r, 'expired', days=0)
