from flask import Flask, render_template, url_for, request
import requests
from xml.etree import ElementTree

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home.html", name="Sales")


@app.route('/ledgerStatement', methods=['POST'])
def led_statement():
    ledger = request.form['ledger']
    from_dt = request.form['fromDate']
    to_dt = request.form['toDate']
    payload = get_payload(from_dt,to_dt,ledger)
    print(payload)
    xml = ElementTree.fromstring(get_data(payload))
    dates = []
    ledgers = []
    vtypes = []
    debits = []
    credits = []
    VchNos =[]
    for date in xml.findall("DSPVCHDATE"):
        dates.append(date.text)
    for led in xml.findall("DSPVCHLEDACCOUNT"):
        ledgers.append(led.text)
    for vtype in xml.findall("DSPVCHTYPE"):
        vtypes.append(vtype.text)
    for dr in xml.findall("DSPVCHDRAMT"):
        debits.append(dr.text if dr.text != None else "0")
    for cr in xml.findall("DSPVCHCRAMT"):
        credits.append(cr.text if cr.text != None else "0")
    for vchNo in xml.findall("DSPEXPLVCHNUMBER"):
        VchNos.append(vchNo.text)
    return render_template("ledgerstatement.html", name=ledger, from_dt=from_dt, to_dt=to_dt, dt=dates,nos=VchNos,led=ledgers,vtype=vtypes,dr=debits,cr=credits)


def get_data(payload):
    req = requests.post(url="http://localhost:9000", data=payload)
    res = req.text.encode("UTF-8")
    print(res)
    return res


def get_payload(fromdate, todate, ledger):
    xml = "<ENVELOPE><HEADER><VERSION>1</VERSION><TALLYREQUEST>EXPORT</TALLYREQUEST><TYPE>DATA</TYPE>"
    xml += "<ID>LedgerVouchers</ID></HEADER><BODY><DESC><STATICVARIABLES>"
    xml += "<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT><LEDGERNAME>"+ledger+"</LEDGERNAME><EXPLODEVNUM>YES</EXPLODEVNUM></STATICVARIABLES><TDL>"
    xml += "<TDLMESSAGE><REPORT Name='LedgerVouchers' ISMODIFY='Yes'><SET>SVFROMDATE:"+"'"+fromdate+"'"+"</SET>"
    xml += "<SET>SVTODATE:"+"'"+todate+"'"+"</SET></REPORT></TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>"
    return xml


if __name__ == "__main__":
    app.run(debug=True)
