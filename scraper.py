import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# CONFIG_TEMPLATE = "SMTP_SERVER=\nSMTP_PORT=\nEMAIL_ADDRESS_FROM=\nPASSWORD=\nEMAIL_ADDRESS_TO="
CONFIG_TEMPLATE = "REG_NUM=\nCOUNTRY="

SMTP_SERVER = ""
SMTP_PORT = 0
EMAIL_ADDRESS = ""
PASSWORD = ""
EMAIL_TO = ""

REG_NUM = ""
COUNTRY = ""


def checkWebPage():
    URL = "https://www.humbertag.com/portal/pages/info/info_home/publicHome.jsf"
    # page = requests.get(URL)
	page = requests.post(URL, data=dict(
    	"publicHome"="publicHome",
    	"publicHome:lpn"=REG_NUM,
		"publicHome:lpnState"=COUNTRY
	));

    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='web-scraper')
    results = results.prettify()

    file = open("receivedPage.html", "w+")
    file.write(results)
    file.close()


def createConfig():
    print("\tCreating config file")
    print("\tPlease fill in your registration number details")
    file = open("config", "w")
    file.write(CONFIG_TEMPLATE)
    file.close()


def checkConfig():
    global REG_NUM
	global COUNTRY

    try:
        file = open("config", "r")
    except(FileNotFoundError):
        print("\tConfig file does not exist")
        createConfig()
        exit(1)

    try:
        regNumConfig = file.readline()
		countryConfig = file.readline()
    except:
        raise
        print("\tConfig file in wrong format")
        createConfig()
        file.close()
        exit(1)

    file.close()

    regNum = re.search("^REG_NUM=(.+)$", regNumConfig)
	country = re.search("^COUNTRY=(.+)$", countryConfig)

    if(regNum is None):
        print("\tConfig file not filled in")
        createConfig()
        exit(1)

	REG_NUM = regNum.group(1)
	COUNTRY = country.group(1)
	

def sendEmail():
    s = smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT)
    s.starttls()
    s.login(EMAIL_ADDRESS, PASSWORD)

    msg = MIMEMultipart()       # create a message

    # add in the actual person name to the message template
    message = "<p>UoN SU Jobs page has changed: <a href=\"https://www.su.nottingham.ac.uk/jobs/\">Visit Page</a></p>"

    # setup the parameters of the message
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = "UoN SU Jobs site changed"

    # add in the message body
    msg.attach(MIMEText(message, 'html'))

    # send the message via the server set up earlier.
    s.send_message(msg)

    del msg

    s.quit()


if __name__ == "__main__":
    checkConfig()

    checkWebPage()

    file = open("timerun.txt", "a+")
    file.write(str(datetime.now().time()) + "\n")
    file.close()

    print("End of program")
