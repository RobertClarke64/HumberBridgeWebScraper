# import libraries
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from twilio.rest import Client
from datetime import datetime

CONFIG_TEMPLATE = "REG_NUM=\nCOUNTRY=\nTWILIO_ACCOUNT_SID=\nTWILIO_AUTH_TOKEN=\nNUMBER_TO=\nTWILIO_NUMBER_FROM="

REG_NUM = ""
COUNTRY = ""
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
NUMBER_TO = ""
TWILIO_NUMBER_FROM = "''"


def createConfig():
    print("\tCreating config file")
    print("\tPlease fill in your registration number details")
    file = open("config", "w")
    file.write(CONFIG_TEMPLATE)
    file.close()


def checkConfig():
    global REG_NUM
    global COUNTRY
    global TWILIO_ACCOUNT_SID
    global TWILIO_AUTH_TOKEN
    global NUMBER_TO
    global TWILIO_NUMBER_FROM

    try:
        file = open("config", "r")
    except(FileNotFoundError):
        print("\tConfig file does not exist")
        createConfig()
        exit(1)

    try:
        regNumConfig = file.readline()
        countryConfig = file.readline()
        accountSidConfig = file.readline()
        authTokenConfig = file.readline()
        numberToConfig = file.readline()
        numberFromConfig = file.readline()
    except:
        raise
        print("\tConfig file in wrong format")
        createConfig()
        file.close()
        exit(1)

    file.close()

    regNum = re.search("^REG_NUM=(.+)$", regNumConfig)
    country = re.search("^COUNTRY=(.+)$", countryConfig)
    accountSid = re.search("^TWILIO_ACCOUNT_SID=(.+)$", accountSidConfig)
    authToken = re.search("^TWILIO_AUTH_TOKEN=(.+)$", authTokenConfig)
    numberTo = re.search("^NUMBER_TO=(.+)$", numberToConfig)
    numberFrom = re.search("^TWILIO_NUMBER_FROM=(.+)$", numberFromConfig)

    if(regNum is None):
        print("\tConfig file not filled in")
        createConfig()
        exit(1)

    REG_NUM = regNum.group(1)
    COUNTRY = country.group(1)
    TWILIO_ACCOUNT_SID = accountSid.group(1)
    TWILIO_AUTH_TOKEN = authToken.group(1)
    NUMBER_TO = numberTo.group(1)
    TWILIO_NUMBER_FROM = numberFrom.group(1)


def sendText(debt):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        to=NUMBER_TO,
        from_=TWILIO_NUMBER_FROM,
        body="Outstanding Humber Bridge debt: %s\n\nhttps://humbertag.com\n\n- From Robert's automated Humber Bridge toll scanner :)" %(debt))

    print(message.sid)


if __name__ == "__main__":
    checkConfig()

    urlpage = 'https://www.humbertag.com/portal/pages/info/info_home/publicHome.jsf'
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(urlpage)
    driver.execute_script("""
        document.getElementById('publicHome:lpn').value = '%s';
        document.getElementById('publicHome:lpnState').value = '%s';
        RichFaces.ajax('publicHome:searchLPN',event,{'incId':'1'} );
        return false;
    """ %(REG_NUM, COUNTRY))
    time.sleep(5)

    results = driver.find_elements_by_xpath("//*[@id='payDebtForm']")
    print('Number of results', len(results))

    if(len(results) >= 1):
        result = results[0].text
        file = open("result", "w+")
        file.write(result)
        file.close()
    else:
        file = open("error.html", "w+")
        file.write(driver.page_source)
        file.close()
        driver.quit()
        exit(1)

    driver.quit()

    debt = result.splitlines()[2]
    if(debt == "Debt Not Found."):
        print("No debt to pay")
    else:
        debtAmount = re.match("^Current debt available to pay: (.+)$", debt).group(1)
        print("Debt to pay: %s" %(debtAmount))
        sendText(debtAmount)

    file = open("timerun.txt", "a+")
    file.write(str(datetime.now().time()) + "\t\t" + debt + "\n")
    file.close()
