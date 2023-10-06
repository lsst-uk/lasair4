"""
check_expire.py
"""
import os, sys, math, time, stat
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
from src import db_connect

warningfmt = """
Dear %s %s,
Your active Lasair watchlist will become inactive in about a week without action from you, and there will be no further matching of incoming alerts. To keep it active, go to https://lasair-dev.lsst.ac.uk/watchlists/%d/ then click "Settings", then "Save".
"""

inactivefmt = """
Dear %s %s,
Your active Lasair watchlist has become inactive and there will be no further matching of incoming alerts. To make it active again, go to https://lasair-dev.lsst.ac.uk/watchlists/%d/ then click "Settings", "active", then "Save".
"""


def send_email(email, message, message_html=''):
    print(email, message)
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

def set_all_expire(msl, days):
    expire = datetime.datetime.now() + datetime.timedelta(days=days)
    query = 'UPDATE watchlists SET date_expire="%s"' % str(expire)
    print(query)
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    msl.commit()

def mail_if_expire(msl, days):
    timelimit = datetime.datetime.now() + datetime.timedelta(days=days)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT wl_id, name, first_name, last_name, email, date_expire '
    query += 'FROM watchlists,auth_user WHERE auth_user.id=watchlists.user'
    cursor.execute(query)
    for row in cursor:
        if row['date_expire'] > timelimit:
            print(row['wl_id'], 'expiry is post %d days'%days)
            warning = warningfmt % (row['first_name'], row['last_name'], row['wl_id'])
            send_email(row['email'], warning, '')

def inactive_if_expire(msl, days):
    timelimit = datetime.datetime.now() + datetime.timedelta(days=days)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT wl_id, name, first_name, last_name, email, date_expire '
    query += 'FROM watchlists,auth_user WHERE auth_user.id=watchlists.user'
    cursor.execute(query)
    for row in cursor:
        if row['date_expire'] > timelimit:
            print(row['wl_id'], 'setting inactive')
            cursor2 = msl.cursor(buffered=True, dictionary=True)
            query = 'UPDATE watchlists SET active=0 WHERE wl_id=%d' % row['wl_id']
            cursor2.execute(query)
            inactive = inactivefmt % (row['first_name'], row['last_name'], row['wl_id'])
            send_email(row['email'], inactive, '')
    msl.commit()

if __name__ == "__main__":
    msl = db_connect.remote()
#    set_all_expire(msl, days)

    days = 4
    mail_if_expire(msl, days)

    days = 2
    inactive_if_expire(msl, days)
