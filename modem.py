import serial
import subprocess
import threading
import time

import pdu

import binascii

class Modem():
    def __init__(self):
        self._new_response_available = False
        self._serial_port = self.get_serial_port()
        self._receiver_thread = threading.Thread(target=self.receiver_method)
        self._receiver_thread.start()
        self.configure_modem()

    def get_serial_port(self):
        return serial.Serial(
            port=self.get_port(),
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0
        )

    def get_port(self):
        proc1 = subprocess.Popen(['ls', '-l', '/dev'], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', 'USB'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
        out, err = proc2.communicate()
        return '/dev/' + out.decode('utf-8').strip().split(' ')[-1]

    def configure_modem(self):
        self._serial_port.write(('ATE0\r').encode())
        self.get_response()
        self._serial_port.write(('AT+CMGF=0\r').encode())
        self.get_response()
        self._serial_port.write(('AT+CSCS="UCS2"\r').encode())
        self.get_response()

    def receiver_method(self):
        prev_in_waiting = 0
        while True:
            try:
                in_waiting = self._serial_port.inWaiting()
                if (in_waiting > 0):
                    if in_waiting == prev_in_waiting:
                        data = self._serial_port.read(in_waiting).decode()
                        self.response = data
                    prev_in_waiting = in_waiting
            except:
                pass
            time.sleep(0.1)

    def send_AT_command(self, command, cr=True):
        try:
            self._new_response_available = False
            if cr == True:
                return self._serial_port.write((command + '\r').encode())
            else:
                return self._serial_port.write((command).encode())
        except serial.serialutil.SerialException:
            print('SerialException')
            self._serial_port = self.get_serial_port()
            self.configure_modem()
            self.response = 'ERROR'

    def get_response(self):
        attempts_amount = 50
        attempt = 0
        while(not self._new_response_available and attempt < attempts_amount):
            time.sleep(0.1)
            attempt += 1
        if self._new_response_available:
            self._new_response_available = False
            return self._response
        else:
            return None

    def send_sms(self, number, text):
        sms = pdu.encodeSmsSubmitPdu(number, text)
        result = list()
        references = []
        for s in sms:
            pdu_string = binascii.hexlify(s.data).decode('ascii')
            ctrlz = b'\x1a'.decode()
            self.send_AT_command(f'AT+CMGS={s.tpduLength}')
            r1 = self.get_response()
            self.send_AT_command(f'{pdu_string}{ctrlz}', cr=False)
            r2 = self.get_response()
            response = self.get_response()
            if response is not None and response.split('\r\n')[-2].strip() == 'OK':
                references.append(response.split('\r\n')[1].split(' ')[1])
                result.append(True)
            else:
                result.append(False)
                #break
        if all(x for x in result):
            return references
        else:
            return []

    @property
    def response(self):
        return self._response
    
    @response.setter
    def response(self, value):
        self._response = value
        self._new_response_available = True

    def serial_port_is_open(self):
        return self._serial_port.is_open()

    def close(self):
        self._serial_port.close()