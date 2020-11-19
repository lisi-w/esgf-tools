import subprocess
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import json
import time

DN_LIST = ['esgf.apcc21.org', 'aims3.llnl.gov', 'esg.camscma.cn', 'esgf-data1.diasjp.net', 'esgf-node.llnl.gov', 'crd-esgf-drc.ec.gc.ca', 'esgf.nci.org.au', 'esg.camscma.cn', 'esgf-data2.diasjp.net', 'esgf-nimscmip6.apcc21.org', 'esgf-data3.diasjp.net', 'esgf-data3.diasjp.net', 'crd-esgf-drc.ec.gc.ca', 'esgf.nci.org.au', 'esgf-node.llnl.gov', 'esgf-data1.llnl.gov', 'esgf-data1.llnl.gov', 'esgf-nimscmip6.apcc21.org', 'esgf.nci.org.au', 'esgf-data1.diasjp.net', 'esgf-data2.diasjp.net', 'esgf.apcc21.org', 'aims3.llnl.gov', 'esgf.nci.org.au', 'esgf-data2.llnl.gov', 'esgf-data2.llnl.gov', 'esg.pik-potsdam.de', 'esgf1.dkrz.de', 'esgf-node.ipsl.upmc.fr', 'acdisc.gesdisc.eosdis.nasa.gov', 'esgf-data1.ceda.ac.uk', 'esg1.umr-cnrm.fr', 'esgf-ictp.hpc.cineca.it', 'esg.pik-potsdam.de', 'gpm1.gesdisc.eosdis.nasa.gov', 'dpesgf03.nccs.nasa.gov', 'esg-dn1.nsc.liu.se', 'esg-dn1.nsc.liu.se', 'data.meteo.unican.es', 'esgf-data3.ceda.ac.uk', 'gpm1.gesdisc.eosdis.nasa.gov', 'esgf2.dkrz.de', 'esgf-data.dkrz.de', 'vesg.ipsl.upmc.fr', 'esgf.nccs.nasa.gov', 'esgf-data1.ceda.ac.uk', 'esgf.ichec.ie', 'esgf-node.ipsl.upmc.fr', 'esg-cccr.tropmet.res.in', 'esgf-ictp.hpc.cineca.it', 'esg.pik-potsdam.de', 'esg-dn1.nsc.liu.se', 'dataserver.nccs.nasa.gov', 'esgf.nccs.nasa.gov', 'acdisc.gesdisc.eosdis.nasa.gov', 'esgf-node.cmcc.it', 'esgf1.dkrz.de', 'esgf2.dkrz.de', 'esgf-cnr.hpc.cineca.it', 'esgf-data3.ceda.ac.uk', 'esgf-cnr.hpc.cineca.it', 'esg1.umr-cnrm.fr', 'esgf-data2.ceda.ac.uk', 'esgf-dev.bsc.es', 'esg-dn2.nsc.liu.se', 'esgf-index1.ceda.ac.uk', 'dpesgf03.nccs.nasa.gov', 'data.meteo.unican.es', 'esgf.bsc.es', 'esg.pik-potsdam.de', 'esg-dn1.nsc.liu.se', 'esgf.bsc.es', 'dataserver.nccs.nasa.gov', 'esgf-dev.bsc.es', 'esg-cccr.tropmet.res.in', 'vesg.ipsl.upmc.fr', 'esgf-node.cmcc.it', 'esg-dn2.nsc.liu.se', 'esgf-index1.ceda.ac.uk', 'esgf-data.dkrz.de', 'esgf-data2.ceda.ac.uk', 'cordexesg.dmi.dk', 'cordexesg.dmi.dk', 'esgf.dwd.de', 'esgf.dwd.de', 'esgdata.gfdl.noaa.gov', 'esgf.rcec.sinica.edu.tw', 'esgf.rcec.sinica.edu.tw', 'esgf-node2.cmcc.it', 'noresg.nird.sigma2.no', 'noresg.nird.sigma2.no', 'cmip.fio.org.cn', 'cmip.fio.org.cn', 'esgf-node2.cmcc.it', 'esgf.ichec.ie', 'esgf-data.ucar.edu', 'esgf-data.ucar.edu', 'dist.nmlab.snu.ac.kr', 'dist.nmlab.snu.ac.kr', 'esgdata.gfdl.noaa.gov', 'esgdata.gfdl.noaa.gov', 'esgdata.gfdl.noaa.gov', 'cmip.bcc.cma.cn', 'cmip.bcc.cma.cn', 'esg.lasg.ac.cn', 'esg.lasg.ac.cn']
DAY = 86400
TWO_DAYS = 2 * DAY
MONTH = 28 * DAY
TEN_DAYS = 10 * DAY
FIRST = '28 days'
SECOND = '10 days'
THIRD = '2 days'
DN_EMAILS = {}
i = 0
for dn in DN_LIST:
    DN_EMAILS[dn] = "elysiawitham@gmail.com"
    if (i % 2) == 0:
        DN_EMAILS[dn] = "ames4@llnl.gov"
    i += 1

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
            notif_sent[dn] = {}
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
        resp = json.loads(http.get(URL, timeout=60).text)
    except Exception as x:
        print("error: " + str(x))
        exit(1)

    for metric in resp["data"]["result"]:
        dn = metric["metric"]["instance"]
        expirations[dn] = {}
        exp = metric["value"][0] + float(metric["value"][1])
        date_exp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        expirations[dn]['string'] = date_exp
        expirations[dn]['until'] = float(metric["value"][1])

    return expirations


def notify(notifs, exps):
    for dn in exps:
        if exps[dn]['until'] < TWO_DAYS and not notifs[dn][THIRD]:
            msg = "The ssl certificate for " + dn + " will expire in less than 2 days. Expiration date: " + exps[dn]['string']
            send_msg(msg, DN_EMAILS[dn])
            notifs[dn][THIRD] = True
        elif exps[dn]['until'] < TEN_DAYS and not notifs[dn][SECOND]:
            msg = "The ssl certificate for " + dn + " will expire in less than 10 days. Expiration date: " + exps[dn]['string']
            send_msg(msg, DN_EMAILS[dn])
            notifs[dn][SECOND] = True
        elif exps[dn]['until'] < MONTH and not notifs[dn][FIRST]:
            msg = "The ssl certificate for " + dn + " will expire in less than 28 days. Expiration date: " + exps[dm]['string']
            send_msg((msg, DN_EMAILS[dn]))
            notifs[dn][FIRST] = True
    return notifs


def main():

    notif_sent = initialize()
    expirations = get_expirations()
    notifs = notify(notif_sent, expirations)
    with open("notif_sent.json", "w") as ns:
        json.dump(notifs, ns, indent=4)


if __name__ == '__main__':
    main()
