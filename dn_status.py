import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

DN_LIST = []
WEEK = 7
MONTH = 30
WEEK2 = 14
DAY3 = 3
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

    for metric in resp["data"]["result"]:
        dn = metric["metric"]["instance"]
        exp = metric["value"][0] + int(metric["value"][1])
        date_exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        expirations[dn] = date_exp

    return expirations


def main():

    expirations = get_expirations()

    lines = []
    for dn in expirations.keys():
        lines.append("The ssl certificate for " + dn + " will expire on " + expirations[dn])

    for email in emails:
        send_msg(lines, email)
