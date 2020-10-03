# pip3 install python-gsmmodem
# from gsmmodem import pdu
from datetime import datetime
import pdu

class SMS(object):
    def __init__(self, line1, line2, id=None):
        self.sms = pdu.decodeSmsPdu(line2)
        self.sms['id'] = int(line1.split(',')[0].split(' ')[1])

    def serialize(self):
        result = {}
        for key, value in self.sms.items():
            if isinstance(self.sms[key], str):
                result[key] = str(value)
            if isinstance(self.sms[key], int):
                result[key] = int(value)
            if isinstance(self.sms[key], datetime):
                result[key] = str(value)
        return result

class SMS_factory():
    def __init__(self, modem_response):
        lines = modem_response.split('\r\n')
        self.sms_list = list()
        for i in range(len(lines)):
            if i % 3 != 0:
                continue
            if lines[i+1] != 'OK':
                try:
                    self.sms_list.append(SMS(lines[i+1], lines[i+2]))
                except:
                    pass