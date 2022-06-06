import json
import logging
from time import sleep
import pyautogui as pag
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from http.server import HTTPServer, BaseHTTPRequestHandler, socketserver


class Server(BaseHTTPRequestHandler):
    def processPath(self):
        try:
            self.query = self.path.split('?', 1)[1]
            self.path = self.path.split('?', 1)[0]
            self.query = self.query.replace('%20', ' ').replace('%27', '\'')
        except:
            self.query = None

        if(self.path[-1] == '/'):
            self.path = self.path[:-1]

        if(self.path == ''):
            return 1

        if(self.path == '/memes'):
            return 10
        return -1

    def setHeader(self, statusCode, message, content = []):
            self.send_response(statusCode)
            self.send_header('content-type', 'text/json')
            self.end_headers()
            dictionary = {'statusCode': statusCode, 'message': message, 'content': content}
            response = json.dumps(dictionary)
            self.wfile.write(response.encode('utf-8'))

    def getMemes(self):
        if(self.query == None):
            return -1, 'No query parameters'

        dictionary = {'string': None}

        for dictKey in dictionary.keys():
            try:
                q = self.query.split('&')[0]
                if(q != self.query):
                    self.query = self.query.split('&', 1)[1]
                else:
                    self.query = None
                key = q.split('=')[0]
                value = q.split('=')[1]
                if(dictKey != key):
                    raise
                dictionary[key] = value
            except:
                return -1, f'Invalid/missing query parameter {dictKey}'

        if(self.query):
            return -1, f'Too many query parameter: {self.query}'

        memes = Memes(dictionary['string'])
        return 1, memes.memeLinks

    def do_GET(self):
        try:
            if((code := self.processPath()) != -1):

                if(code == 1):
                    self.setHeader(200, 'Access /memes')
                elif(code == 10):
                    status = self.getMemes()
                    if(status[0] == 1):
                        self.setHeader(200, 'Memes Found', status[1])
                    elif(status[0] == -1):
                        self.setHeader(400, status[1])
                else:
                    self.setHeader(501, 'How did you get here')
            else:
                self.setHeader(404, f'{self.path} path was not found')
        except Exception as e:
            print(e)
            self.setHeader(500, 'Server issue')


class SeleniumInstance:
    def __init__(self, wait : int = 5, loggingLevel = logging.INFO):
        """
        Driver Initialization
        """

        logging.basicConfig(level=loggingLevel, format='[%(asctime)s] - [%(levelname)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.debug('SeleniumInstance class initialization')

        self.typesDict = {
            "ID": "id",
            "XPath": "xpath",
            "Link": "link text",
            "PartialLink": "partial link text",
            "Name": "name",
            "Tag": "tag name",
            "Class": "class name",
            "CSS": "css selector"
        }
        self.wait = wait
        logging.info('Opening Chrome browser')

        self.driver = uc.Chrome()
        self.driver.maximize_window()

    def findElem(self, element : str, type : str, name : str, mode : int = 1):
        """
        Finds a specified element and returns it in case of sucess
        """

        selection = None
        while(True):
            try:
                selection = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((self.typesDict[type], element)))
                logging.debug(f'"{name}" element was found')
                return(selection)
            except:
                logging.error(f'"{name}" element was not found')
                if(mode == 2):
                    logging.warning('Continuing without the element')
                    return(None)
                response = pag.confirm(text=f'Could not find "{name}" element', title='Element Not Found', buttons=['Continue', 'Retry', 'Cancel'])
                if(response == 'Continue'):
                    logging.warning('Continuing without the element')
                    return(None)
                elif(response == 'Retry'):
                    logging.info('Retrying to find the element')
                    pass
                else:
                    logging.warning('Quitting the script')
                    exit(0)

    def clickElem(self, element : str, type : str, name : str, mode : int = 1):
        """
        Clicks on the provided element
        """

        element = self.findElem(element, type, name, mode)
        if(element != None):
            while(True):
                try:
                    element.click()
                    logging.debug(f'"{name}" element was clicked')
                    return(True)
                except:
                    logging.error(f'Could not click on "{name}" element')
                    if(mode == 2):
                        logging.warning('Continuing without clicking on the element')
                        return(False)
                    response = pag.confirm(text=f'Could not click on "{name}" element', title='Element Non Clickable', buttons=['Continue', 'Retry', 'Cancel'])
                    if(response == 'Continue'):
                        logging.warning('Continuing without clicking on the element')
                        return(False)
                    elif(response == 'Retry'):
                        logging.info('Retrying to click on the element')
                        pass
                    else:
                        logging.warning('Quitting the script')
                        exit(0)
        else:
            logging.warning(f'Skipping over "{name}" element')

    def writeElem(self, element : str, type : str, name : str, text : str, mode : int = 1):
        """
        Writes the provided text in the provided element
        """

        element = self.findElem(element, type, name, mode)
        if(element != None):
            while(True):
                try:
                    element.clear()
                    element.send_keys(text)
                    logging.debug(f'"{name}" element was written in')
                    return(True)
                except:
                    logging.error(f'Could not write in "{name}" element')
                    if(mode == 2):
                        logging.warning('Continuing without writting in the element')
                        return(False)
                    response = pag.confirm(text=f'Could not write in "{name}" element', title='Element Non Writable', buttons=['Continue', 'Retry', 'Cancel'])
                    if(response == 'Continue'):
                        logging.warning('Continuing without writting in the element')
                        return(False)
                    elif(response == 'Retry'):
                        logging.info('Retrying to write in the element')
                        pass
                    else:
                        logging.warning('Quitting the script')
                        exit(0)
        else:
            logging.warning(f'Skipping over "{name}" element')
            return False

    def selectElem(self, element : str, type : str, name : str, value : str, mode : int = 1):
        """
        Select the provided value in the provided element
        """

        element = self.findElem(element, type, name, mode)
        if(element != None):
            while(True):
                try:
                    Select(element).select_by_value(value)
                    logging.debug(f'Value "{value}"" was selected in "{name}" element')
                    return(True)
                except:
                    logging.error(f'Could not select value "{value}" in "{name}" element')
                    if(mode == 2):
                        logging.warning('Continuing without selecting a value in the element')
                        return(False)
                    response = pag.confirm(text=f'Could not select value "{value}" in "{name}" element', title='Value Non Selectable', buttons=['Continue', 'Retry', 'Cancel'])
                    if(response == 'Continue'):
                        logging.warning('Continuing without selecting the value in the element')
                        return(False)
                    elif(response == 'Retry'):
                        logging.info('Retrying to select the value in the element')
                        pass
                    else:
                        logging.warning('Quitting the script')
                        exit(0)
        else:
            logging.warning(f'Skipping over selecting value "{value}" in "{name}" element')


class Memes:
    def __init__(self, text, waitTime : int = 5, preset : int = 1, loggingLevel = logging.INFO):
        """
        Memes Initialization
        """

        logging.basicConfig(level=loggingLevel, format='[%(asctime)s] - [%(levelname)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.debug('Memes class initialization')
        self.si = SeleniumInstance(wait = waitTime, loggingLevel = loggingLevel)
        self.driver = self.si.driver
        self.text = text
        self.getMemes()
        self.driver.quit()

    def getMemes(self):
        self.driver.get('https://imgflip.com/automeme')
        sleep(3)
        self.si.writeElem('am-text', 'ID', 'Meme Text', self.text, 2)
        sleep(3)

        self.memeLinks = list()
        for i in range(7):
            self.si.clickElem('//button[contains(text(), "Generate Meme")]', 'XPath', 'Generate Meme', 2)
            sleep(2)
            try:
                link = self.si.findElem('link', 'Class', 'Image Link', 2).get_attribute("value")
                self.memeLinks.append(link)
            except:
                pass
            if(i == 6): break
            self.si.clickElem('//button[contains(text(), "Make another")]', 'XPath', 'Make another', 2)
            sleep(1)
            self.driver.switch_to.alert.accept()
            self.driver.switch_to.default_content()
            sleep(1)
            self.si.clickElem(f'//tr[@class="am-prediction"][{i + 2}]', 'XPath', f'Prediction {i + 2}', 2)
            sleep(1)


if __name__ == '__main__':
    #si = SeleniumInstance()
    httpd = HTTPServer(('0.0.0.0', 40404), Server)
    httpd.serve_forever()