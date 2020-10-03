from __main__ import app
from flask import request, jsonify
from modem import Modem
from sms import SMS, SMS_factory

modem = Modem()

@app.route('/modem/send_command', methods=['POST'])
def send_command():
    command = request.json.get('command', None)
    modem.send_AT_command(command)
    response = modem.get_response()
    return response, 200

@app.route('/modem/sms/all', methods=['GET'])
def get_all_sms():
    modem.send_AT_command('AT+CMGL="ALL"')
    response = modem.get_response()
    sms_list = list()
    if response.strip() == 'ERROR':
        return jsonify(message = "ERROR"), 503
    else:
        sms_list = SMS_factory(response).sms_list
    return jsonify([s.serialize() for s in sms_list]), 200

@app.route('/modem/sms/<id>', methods=['GET'])
def get_sms(id):
    modem.send_AT_command(f'AT+CMGR={id}')
    response = modem.get_response()
    if response.strip() == 'ERROR':
        return jsonify(message = "ERROR"), 503
    else:
        lines = response.split('\r\n')
        return jsonify(sms = SMS(lines[1], lines[2], id).serialize()), 200

@app.route('/modem/sms/all', methods=['DELETE'])
def delete_all_sms():
    modem.send_AT_command(f'AT+CMGD=0,4')
    response = modem.get_response()
    if response.strip() == 'OK':
        return jsonify(message = 'OK'), 200
    return jsonify(message = "ERROR"), 503

@app.route('/modem/sms/<id>', methods=['DELETE'])
def delete_sms(id):
    modem.send_AT_command(f'AT+CMGD={id}')
    response = modem.get_response()
    if response.strip() == 'OK':
        return jsonify(message = 'OK'), 200
    return jsonify(message = "ERROR"), 503

@app.route('/modem/sms', methods=['POST'])
def send_sms():
    number = request.json.get('number', None)
    text = request.json.get('text', None)
    response = modem.send_sms(number, text)
    if len(response) > 0:
        return jsonify(references = response), 200
    return jsonify(message = "ERROR"), 503