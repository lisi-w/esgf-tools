import subprocess
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import json

DN_LIST = []
DAY = 86400
TWO_DAYS = 2 * DAY
MONTH = 28 * DAY
TEN_DAYS = 10 * DAY
FIRST = '28 days'
SECOND = '10 days'
THIRD = '2 days'
DN_EMAILS = {}

URL = "https://aims4.llnl.gov/prometheus/api/v1/query?query=probe_ssl_earliest_cert_expiry%20-%20time()"


def send_msg(message, to_email):
    msg = MIMEMultipart()
    from_email = "witham3@llnl.gov"
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Data Node SSL Certificate Expiration Update"
    body = message
    msg.attach(MIMEText(body, 'plain'))
    s = smtplib.SMTP('nospam.llnl.gov')  # llnl smtp: nospam.llnl.gov
    s.ehlo()
    s.starttls()
    text = msg.as_string()
    s.sendmail(from_email, to_email, text)
    s.quit()


def initialize(first=False):
    if first:
        notif_sent = {}
        for dn in DN_LIST:
            notif_sent[dn][FIRST] = False
            notif_sent[dn][SECOND] = False
            notif_sent[dn][THIRD] = False
        with open("notif_sent.json", "w") as ns:
            json.dump(notif_sent, ns, indent=4)
    else:
        notif_sent = json.load(open("notif_sent.json", "r"))

    return notif_sent


def get_expirations():
    retries = requests.packages.urllib3.util.retry.Retry(total=3, backoff_factor=2,
                                                         status_forcelist=[429, 500, 502, 503, 504])
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount("http://", adapter)

    expirations = {}
    try:  # put in a timeout for buffering instances
        print(".", end="", flush=True)
        resp = json.loads(http.get(URL, timeout=60))
    except Exception as x:
        print("error")

    lst = []
    for metric in resp["data"]["result"]:
        dn = metric["metric"]["instance"]
        lst.append(dn)
        exp = metric["value"][0] + int(metric["value"][1])
        date_exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        expirations[dn]['string'] = date_exp
        expirations[dn]['until'] = int(metric["value"][1])

    print(lst)
    return expirations


def notify(notifs, exps):
    for dn in exps:
        if exps[dn]['until'] < FIRST and not notifs[dn][FIRST]:
            msg = "The ssl certificate for " + dn + " will expire in less than 28 days. Expiration date: " + exps[dn]['string']
            send_msg(msg, DN_EMAILS[dn])


def main():

    # notif_sent = initialize(True)
    expirations = get_expirations()
    # notify(notif_sent, expirations)


if __name__ == '__main__':
    main()
