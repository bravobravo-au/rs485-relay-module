'''
BSD 2-Clause License

Copyright (c) 2024, bravobravo-au https://github.com/bravobravo-au/rs485-relay-module

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

rs485-relay-module for MODBUS relays from eletechsup 
Documentation from https://485io.com/eletechsup/23IOA08_23IOB16_23IOC24_23IOD32_23IOE48.rar
MQTT support for rs485-relay-module
'''

import json
from json.decoder import JSONDecodeError
import random
import time
import datetime
import configparser
import argparse
from paho.mqtt import client as mqtt_client
from multipleModuleManager import MultipleModuleManager
import re
import logging
import subprocess
import sqlite3
import sys
import math

from parsers import *

def on_mqtt_message(client, userdata, msg):
    logger.debug(f'''Incoming MQTT topic {msg.topic} and message: {msg.payload.decode('utf-8')}''')


    if msg.topic == mqtt_device_status_request_topic:
        logger.debug(f'''Got MQTT message on topic {msg.topic}''')
        msgPayload = msg.payload.decode("utf-8")
        
        inputAddresses = None
        outputAddresses = None
        modulesModbusAddressList = modules.getModbusAddresses()
        try:
            jsonMessage = json.loads( msg.payload.decode("utf-8") )
        except JSONDecodeError:
            jsonMessage = {}

        if 'modulesModbusAddress' in jsonMessage:
            modulesModbusAddressList = [jsonMessage['modulesModbusAddress']]
        if 'inputAddresses' in jsonMessage:
            inputAddresses = jsonMessage['inputAddresses']
        if 'outputAddresses' in jsonMessage:
            outputAddresses = jsonMessage['outputAddresses']

        modulesList = []
        for modbusAddress in modulesModbusAddressList:
            if inputAddresses is None:
                inputs = modules.getInputs( modbusAddress )
            else:
                inputs = modules.getInputs( modbusAddress,inputAddresses)

            if outputAddresses is None:
                outputs = modules.getOutputs( modbusAddress )
            else:
                outputs = modules.getOutputs( modbusAddress, outputAddresses)

            inputList = []

            if inputs is not None and len(inputs) > 0:
                for input in inputs:
                    inputList.append( f'''{{"number": "{input['number']}", "value": "{input['value']}", "lastChanged": "{input['lastchangestr']}"}}''')
            outputList = []

            if outputs is not None and len(outputs) > 0:
                for output in outputs:
                    outputList.append( f'''{{"number": "{output['number']}", "value": "{output['value']}", "lastChanged": "{output['lastchangestr']}"}}''')

            inputStr = ",".join(inputList)
            outputStr = ",".join(outputList)
            modulesList.append( f'''"modbusAddress":{modbusAddress},"inputs":[{inputStr}],"outputs":[{outputStr}]''')
        modulesStr = ",".join(modulesList)

        message = f'''{{"Modules": [{{{modulesStr}}}] }}'''

        scheduledOutputs = []
        query = f'''SELECT
                                    *
                            FROM
                                    scheduledEvents;
                            '''
        cur.execute( query )
        rows = cur.fetchall()

        if len( rows ) > 0:
            for scheduledEvent in rows:
                logger.info(f'''timestamp: {scheduledEvent['timestamp']} createdAt: {scheduledEvent['createdAt']} MODBUS_ADDR: {scheduledEvent['MODBUS_ADDR']} MODBUS_IO: {scheduledEvent['MODBUS_IO']} with Value: {scheduledEvent['outputState']}''')
                scheduledOutputs.append( f'''{{"timestamp": {scheduledEvent['timestamp']}, "timestampStr": "{datetime.datetime.fromtimestamp(scheduledEvent['timestamp'],datetime.UTC).strftime("%Y-%m-%d-%H:%M:%S.%f")}", "createdAt": {scheduledEvent['createdAt']}, "MODBUS_ADDR": {scheduledEvent['MODBUS_ADDR']}, "MODBUS_IO": {scheduledEvent['MODBUS_IO']}, "value": {scheduledEvent['outputState']} }}''' )

            scheduledOutputs = ",".join( scheduledOutputs )
            message = f'''{{"Modules": [{{{modulesStr}}}], "ScheduledOutputs": [{scheduledOutputs}]}}'''

        client.publish(mqtt_device_status_response_topic, message, qos=mqtt_qos )
        return

    if msg.topic == mqtt_hexiaecimal_control_topic:
        jsonMessage = json.loads( msg.payload.decode("utf-8") )
        keepCurrent = False
        if 'keepCurrent' in jsonMessage:
            keepCurrent = jsonMessage['keepCurrent']
        if 'Output' in jsonMessage and 'modbusaddress' in jsonMessage and 'value' in jsonMessage:
            modules.updateOutputsByHexStr( jsonMessage['modbusaddress'], jsonMessage['Output'],outputValue=jsonMessage['value'],keepCurrent=keepCurrent)

    for commandConfig in commandConfigs:
        if msg.topic == commandConfig['MQTT_TOPICS']:
            commandList = commandConfig['COMMAND'].split(" ")
            execute = subprocess.run( commandList )
            returnCode = execute.returncode
            logger.info(commandConfig['LOG_MESSAGE'] % {
                                                            'command': commandConfig['COMMAND'],
                                                            'message': msg.payload.decode("utf-8"),
                                                            'topic': msg.topic, 'returncode': returnCode
                                                        })
            return

    logger.debug( f'''gpioConfigs: {gpioConfigs}''')
    for gpioConfig in gpioConfigs:
        if msg.topic in gpioConfig['MQTT_TOPICS'] and gpioConfig['GPIO_TYPE'] == 'OUTPUT':
            logger.debug( f'''Found GPIO Config {gpioConfig}''')
            functionName = "PARSER_" + gpioConfig['MQTT_PARSER']
            value = globals()[ functionName ]( msg, gpioConfig )

            modules.updateOutput(gpioConfig['MODBUS_ADDR'],gpioConfig['MODBUS_IO'],value)

            logger.info(gpioConfig['LOG_MESSAGE'] % { 
                                                        'address': gpioConfig['MODBUS_ADDR'],
                                                        'output': gpioConfig['MODBUS_IO'], 
                                                        'value': value, 
                                                        'message': msg.payload.decode("utf-8"), 
                                                        'topic': msg.topic 
                                                        })
            jsonMessage = json.loads( msg.payload.decode("utf-8") )
            if 'DelayActionTime' in jsonMessage and 'DelayAction' in jsonMessage:
                actionTime = convertValueToTimestamp( jsonMessage['DelayActionTime'] )
                logger.debug(f'''Got MQTT message DelayActionTime: {jsonMessage['DelayActionTime']} and DelayAction: {jsonMessage['DelayAction']} scheduled for: {actionTime}''')

                deleteQuery = f'''DELETE FROM scheduledEvents WHERE MODBUS_ADDR=? AND MODBUS_IO=?;'''

                if 'DelayActionTime' in jsonMessage and isinstance(jsonMessage['DelayActionTime'],list) and next(iter(jsonMessage['DelayActionTime'].values())) < 0:
                    cur.execute(deleteQuery,(gpioConfig['MODBUS_ADDR'],gpioConfig['MODBUS_IO']))
                    db.commit()

                if actionTime > 0:
                    nowObj = datetime.datetime.now(datetime.UTC)

                    #Remove any existing scheduled events
                    cur.execute(deleteQuery,(gpioConfig['MODBUS_ADDR'],gpioConfig['MODBUS_IO']))

                    query = f'''INSERT INTO scheduledEvents (MODBUS_ADDR,
                                                                MODBUS_IO,
                                                                createdAt,
                                                                timestamp,
                                                                outputState)
                                                        VALUES (
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?);'''

                    logger.debug(f'''MODBUS_ADDR: {gpioConfig['MODBUS_ADDR']} MODBUS_IO: {gpioConfig['MODBUS_IO']} createdAt: {nowObj.timestamp()}, timestamp: {actionTime} outputState: {jsonMessage['DelayAction']} ''')
                    cur.execute(query, (gpioConfig['MODBUS_ADDR'],gpioConfig['MODBUS_IO'],nowObj.timestamp(),actionTime,jsonMessage['DelayAction'],))

                    db.commit()
            return

def gpio_input_callback(modbusAddress, input, state):
    nowObj = datetime.datetime.now(datetime.UTC)
    for gpioConfig in gpioConfigs:
        if gpioConfig['MODBUS_ADDR'] == modbusAddress and gpioConfig['MODBUS_IO'] == input and gpioConfig['GPIO_TYPE'] == 'INPUT':
            value = BOOL_ONOFFSTRING(state).lower()
            message = gpioConfig['MQTT_MESSAGE']. \
                    replace('{MODBUSADDRESS}', str(modbusAddress)). \
                    replace('{INPUT}', str(input)). \
                    replace('{STATE}', value). \
                    replace('{UTCTIMESTAMP}', str(nowObj.timestamp())).\
                    replace('{UPDATEDAT}', nowObj.strftime("%Y-%m-%d-%H:%M:%S.%f")
                    )
            client.publish(gpioConfig['MQTT_TOPICS'][0], message, qos=gpioConfig['MQTT_QOS'] )
            
            for arrayIndex,vi in enumerate(virtualInputs):
                if vi['MODBUS_ADDR'] == modbusAddress and vi['MODBUS_IO'] == input:

                    if value == 'off':
                        inputData = modules.getInput(gpioConfig['MODBUS_ADDR'],gpioConfig['MODBUS_IO'])
                        holdDurationTimeDelta = inputData['lastOff'] - inputData['lastOn']
                        if holdDurationTimeDelta > datetime.timedelta(seconds=0.5):
                            #here we go
                            message = vi['MQTT_HOLD_MESSAGE']. \
                                        replace('{MODBUSADDRESS}', str(modbusAddress)). \
                                        replace('{INPUT}', str(input)). \
                                        replace('{STATE}', value). \
                                        replace('{UTCTIMESTAMP}', str(nowObj.timestamp())). \
                                        replace('{UPDATEDAT}', nowObj.strftime("%Y-%m-%d-%H:%M:%S.%f")). \
                                        replace('{HOLDTIME}',str(holdDurationTimeDelta.total_seconds()))
                                        
                            client.publish(vi['MQTT_HOLD_TOPICS'][0],message, qos=gpioConfig['MQTT_QOS'] )
                            

                    query = f'''INSERT INTO virtualInputEvents (MODBUS_ADDR,
				                                MODBUS_IO,
                                				MQTT_TOPICS,
                      			                MQTT_MESSAGE,
				                                timestamp,
				                                state,
                                				type,
								                arrayIndex)
							VALUES (
								?,
								?,
								?,
				                ?,
								?,
								?,
								?,
								?
								);'''
                    cur.execute(query, (vi['MODBUS_ADDR'],vi['MODBUS_IO'],json.dumps({"MQTT_TOPICS": vi['MQTT_TOPICS']}),vi['MQTT_MESSAGE'],nowObj.timestamp(),vi['GPIO_PIN_STATE'],vi['GPIO_TYPE'],arrayIndex))
                    db.commit()
                    break
            logger.info(gpioConfig['LOG_MESSAGE'] % {
                                                     'message': message,
                                                     'topic': gpioConfig['MQTT_TOPICS']
                                                     })

def on_mqtt_connect(client, userdata, flags, rc, properties):
    global mqtt_connected

    if rc == 0:
        mqtt_connected = True

        if mqtt_startup_message and mqtt_startup_topic:
            client.publish(
                                topic=mqtt_startup_topic,
                                payload=mqtt_startup_message % ( {'datetimenow': datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S") } ),
                                qos=mqtt_qos,
                                retain=mqtt_retain,
                        )
        if mqtt_device_status_request_topic is not None and mqtt_device_status_request_topic != '':
            client.subscribe( mqtt_device_status_request_topic )

        if mqtt_hexiaecimal_control_topic is not None and mqtt_hexiaecimal_control_topic != '':
            client.subscribe( mqtt_hexiaecimal_control_topic )

        for cmnd in commandConfigs:
            client.subscribe( cmnd['MQTT_TOPICS'] )
        for gpio in gpioConfigs:
            if gpio['GPIO_TYPE'] == 'OUTPUT':
                client.subscribe( gpio['MQTT_TOPICS'] )
    else:
        mqtt_connected = False

def on_mqtt_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False

def mqtt_connect(mqtt_host,mqtt_port,mqtt_connected,client):
    if mqtt_connected == False:
        client.connect(
                        mqtt_host,
                        port=mqtt_port,
                        keepalive=60,
                    )
        client.loop(5)

def sqliteSetup():
    db = sqlite3.connect("file::memory:?cache=shared")
    db.row_factory =  dict_factory
    cur = db.cursor()

    cur.execute('''CREATE TABLE virtualInputEvents (
				MODBUS_ADDR INTEGER NOT NULL,
				MODBUS_IO INTEGER NOT NULL,
				MQTT_TOPICS TEXT NOT NULL,
                MQTT_MESSAGE TEXT NOT NULL,
				timestamp FLOAT NOT NULL,
				state TEXT NOT NULL,
				type TEXT NOT NULL,
				arrayIndex INTEGER NOT NULL
				);''')
    db.commit()
    cur.execute('''CREATE TABLE scheduledEvents (
                                MODBUS_ADDR INTEGER NOT NULL,
                                MODBUS_IO INTEGER NOT NULL,
                                createdAt FLOAT NOT NULL,
                                timestamp FLOAT NOT NULL,
                                outputState TEXT NOT NULL
                                );''')

    db.commit()
    return cur,db

def initialise(modbusaddresses,DELAY):
    global mqtt_connected, mqtt_startup_message, mqtt_startup_topic, mqtt_qos, mqtt_retain, mqtt_device_status_request_topic, mqtt_device_status_response_topic, mqtt_hexiaecimal_control_topic, commandConfigs, gpioConfigs, virtualInputs
    '''
    Configs for running shell commands
    '''
    commandConfigs = []
    
    '''
    GPIO configuration
    '''
    gpioConfigs = []
    

    '''
    Virtual Input configuration
    '''
    virtualInputs = []


    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use default config.ini")
    parser.add_argument("--debug", help="print debugging to console")
    args = parser.parse_args()

    config = configparser.ConfigParser(interpolation=None)
    if args.config:
        config.read(args.config)
    else:
        config.read('config.ini')

    if 'LOGFILE_NAME' in config['DEFAULT']:
        logfile_name                    = config['DEFAULT']['LOGFILE_NAME']
    else:
       logfile_name                    = None

    if args.debug is not None and args.debug == 'DEBUG':
        logging.basicConfig(filename=logfile_name, format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(filename=logfile_name, format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    mqtt_host                           = config['DEFAULT']['MQTT_HOST']
    mqtt_port                           = int(config['DEFAULT']['MQTT_PORT'])
    mqtt_client_name                    = config['DEFAULT']['MQTT_CLIENT_NAME']
    mqtt_username                       = config['DEFAULT']['MQTT_USERNAME']
    mqtt_password                       = config['DEFAULT']['MQTT_PASSWORD']
    mqtt_loop_delay                     = float(config['DEFAULT']['MQTT_LOOP_DELAY'])
    mqtt_qos                            = int(config['DEFAULT']['MQTT_QOS'])
    mqtt_retain                         = int(config['DEFAULT']['MQTT_RETAIN'])
    mqtt_connected                      = False
    mqtt_startup_message                = config['DEFAULT']['MQTT_STARTUP_MESSAGE']
    mqtt_startup_topic                  = config['DEFAULT']['MQTT_STARTUP_TOPIC']
    mqtt_device_status_request_topic	= config['DEFAULT']['MQTT_DEVICE_STATUS_REQUEST_TOPIC']
    mqtt_device_status_response_topic	= config['DEFAULT']['MQTT_DEVICE_STATUS_RESPONSE_TOPIC']
    mqtt_hexiaecimal_control_topic	    = config['DEFAULT']['MQTT_HEXADECIMAL_CONTROL_TOPIC']
    device_name                         = config['DEFAULT']['RS485_DEVICE']
    baud_rate                           = config['DEFAULT']['RS485_BAUD_RATE']


    client = mqtt_client.Client(   client_id='',
                        clean_session=True,
                        userdata=None,
                        transport='tcp',
                        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2
                        )
    if mqtt_username not in [None,''] and mqtt_password not in [None,'']:
        client.username_pw_set(username=mqtt_username, password=mqtt_password)

    client.on_message=on_mqtt_message
    client.on_connect=on_mqtt_connect
    client.on_disconnect=on_mqtt_disconnect

    mqtt_connect(mqtt_host=mqtt_host,mqtt_port=mqtt_port,mqtt_connected=mqtt_connected,client=client)

    for section in config.sections():
        sectiontype                     = config[section]['TYPE']

        if sectiontype == 'COMMAND':
            mqtt_topics                 = json.loads( config[section]['MQTT_TOPICS'] )['MQTT_TOPICS'][0]
            log_message                 = config[section]['LOG_MESSAGE']
            command                     = config[section]['COMMAND']
            logger.debug('Added command processor for command:%(command)s on MQTT topic:%(topic)s' % ( {
                                                                            'command': command,
                                                                            'topic': mqtt_topics,
                                                                            }
                                                                            )
                                                                        )
            commandConfigs.append( {
                'COMMAND'       : command,
                'MQTT_TOPICS'   : mqtt_topics,
                'LOG_MESSAGE'   : log_message,
            } )
            client.subscribe( mqtt_topics )

        if sectiontype in ['GPIO','VIRTUALINPUT']:
            mqtt_topics                 = json.loads( config[section]['MQTT_TOPICS'] )['MQTT_TOPICS']

            if 'MQTT_HOLD_TOPICS' in json.loads( config[section]['MQTT_TOPICS'] ):
                mqtt_hold_topics            = json.loads( config[section]['MQTT_TOPICS'] )['MQTT_HOLD_TOPICS']
            else:
                mqtt_hold_topics            = []

            if 'MQTT_HOLD_MESSAGE' in config[section]:
                mqtt_hold_message       = config[section]['MQTT_HOLD_MESSAGE'] 
            else:
                mqtt_hold_message       = None

            gpio_type                   = config[section]['GPIO_TYPE']
            mqtt_parser                 = None
            mqtt_parser_arg1            = None
            mqtt_message                = None
            gpio_pin_state              = False
            mqtt_retain                 = bool(config[section]['MQTT_RETAIN'])
            mqtt_qos                    = int(config[section]['MQTT_QOS'])
            log_message                 = config[section]['LOG_MESSAGE']

            if gpio_type == 'OUTPUT':
                mqtt_parser             = config[section]['MQTT_PARSER']
                mqtt_parser_arg1        = config[section]['MQTT_PARSER_ARG1']
                for mqtt_topic in mqtt_topics:
                    client.subscribe( 
                            mqtt_topic,
                            )
                    logger.debug( f'''Added configuration for Modbus Address {config[section]['MODBUS_ADDR']} Output {config[section]['MODBUS_IO']} on MQTT topic {mqtt_topic}''' )

            if gpio_type == 'INPUT' or sectiontype == 'VIRTUALINPUT':
                mqtt_message            = config[section]['MQTT_MESSAGE']

            gpioData = {
                            'MQTT_TOPICS':          mqtt_topics,
                            'MQTT_HOLD_TOPICS':     mqtt_hold_topics,
                            'GPIO_TYPE':            gpio_type,
                            'MQTT_PARSER':          mqtt_parser,
                            'MQTT_PARSER_ARG1':     mqtt_parser_arg1,
                            'MQTT_MESSAGE':         mqtt_message,
                            'MQTT_HOLD_MESSAGE':    mqtt_hold_message,
                            'GPIO_PIN_STATE':       gpio_pin_state,
                            'LOG_MESSAGE':          log_message,
                            'MQTT_QOS':             mqtt_qos,
                            'MQTT_RETAIN':          mqtt_retain,
                            'MODBUS_ADDR':          int(config[section]['MODBUS_ADDR']),
                            'MODBUS_IO':            int(config[section]['MODBUS_IO']),
                            }
            if sectiontype == 'VIRTUALINPUT':
                virtualInputs.append( gpioData )
            else:
                gpioConfigs.append( gpioData )
            logger.debug( 'Added configuration for %s' % ( gpioData ) )

    modules = MultipleModuleManager(port=device_name, desiredbaudrate=baud_rate, modbusaddresses=modbusaddresses, inputchangecallback=gpio_input_callback)
    return logger, virtualInputs, gpioConfigs, commandConfigs, client, modules

def loopScheduledEvents(cur,db,logger):
    query = f'''SELECT COUNT(*) AS numberShortPressEvents FROM scheduledEvents WHERE timestamp < {datetime.datetime.now(datetime.UTC).timestamp()};'''
    cur.execute( query )
    rows = cur.fetchall()
    if rows[0]['numberShortPressEvents'] > 0:
        logger.debug(f'''There are {rows[0]['numberShortPressEvents']} scheduled events to process''')
        query = f'''SELECT
                            *
                    FROM
                            scheduledEvents
                    WHERE 
                            timestamp < {datetime.datetime.now(datetime.UTC).timestamp()};

                    '''
        cur.execute( query )
        rows = cur.fetchall()
        logger.debug(f'''now: {datetime.datetime.now(datetime.UTC).timestamp()} rows: {rows}''')
        for scheduledEvent in rows:
            logger.info(f'''Ran scheduled event for MODBUS_ADDR: {scheduledEvent['MODBUS_ADDR']} MODBUS_IO: {scheduledEvent['MODBUS_IO']} with Value: {scheduledEvent['outputState']}''')
            modules.updateOutput(scheduledEvent['MODBUS_ADDR'],scheduledEvent['MODBUS_IO'],scheduledEvent['outputState'])
            query = f'''DELETE FROM
                                scheduledEvents
                            WHERE
                                MODBUS_ADDR='{scheduledEvent['MODBUS_ADDR']}'
                                AND MODBUS_IO='{scheduledEvent['MODBUS_IO']}'
                                AND createdAt='{scheduledEvent['createdAt']}'
                                AND timestamp='{scheduledEvent['timestamp']}'
                            '''
            cur.execute( query )
            db.commit()

def loopVirtualEvents(cur,db,logger):
    query = f'''SELECT COUNT(*) AS numberShortPressEvents FROM virtualInputEvents;'''
    cur.execute( query )
    rows = cur.fetchall()
    if rows[0]['numberShortPressEvents'] > 0:
        logger.debug(f'''Found {rows[0]['numberShortPressEvents']} virtualInputEvents''')
        query = f'''SELECT 
                            MODBUS_ADDR, 
                            MODBUS_IO, 
                            type, 
                            MQTT_TOPICS,
                            MQTT_MESSAGE,
                            state,
                            arrayIndex,
                            COUNT(*) as number 
                    FROM 
                            virtualInputEvents 
                    GROUP BY 
                            MODBUS_ADDR, 
                            MODBUS_IO, 
                            type, 
                            MQTT_TOPICS;
                    '''
        cur.execute( query )
        rows = cur.fetchall()
        for inputDevice in rows:
            query = f'''SELECT 
                            state,
                            ( ((julianday('now') - 2440587.5) * 86400.0) - timestamp ) AS age
                        FROM
                            virtualInputEvents
                        WHERE
                            MODBUS_ADDR='{inputDevice['MODBUS_ADDR']}'
                            AND MODBUS_IO='{inputDevice['MODBUS_IO']}'
                            AND type='{inputDevice['type']}'
                            AND MQTT_TOPICS='{inputDevice['MQTT_TOPICS']}'
                        ORDER BY
                            timestamp DESC;'''
            cur.execute( query )
            results = cur.fetchall()
            completed = True
            numberShortPressEvents = 0
            for res in results:
                if res['age'] <= 0.30:
                    completed = False
                    break
                numberShortPressEvents += 1

            if completed is True:
                if numberShortPressEventsToString(numberShortPressEvents, res['state']) is not None:
                    numberShortPresses = math.floor(numberShortPressEvents / 2)
                    if numberShortPresses == 0:
                        numberShortPresses = 1
                    topicsList = json.loads(inputDevice['MQTT_TOPICS'])['MQTT_TOPICS']
                    nowObj = datetime.datetime.now(datetime.UTC)
                    
                    #set state here
                    virtualInputs[ inputDevice['arrayIndex'] ]['GPIO_PIN_STATE'] = not(virtualInputs[ inputDevice['arrayIndex'] ]['GPIO_PIN_STATE'] )
                    client.publish( 
                                topicsList[numberShortPresses - 1],
                                inputDevice['MQTT_MESSAGE']. \
                                        replace('{MODBUSADDRESS}', str(inputDevice['MODBUS_ADDR'])). \
                                        replace('{INPUT}', str(inputDevice['MODBUS_IO'])). \
                                        replace('{STATE}', BOOL_ONOFFSTRING(virtualInputs[ inputDevice['arrayIndex'] ]['GPIO_PIN_STATE'])).lower(). \
                                        replace('{utctimestamp}', str(nowObj.timestamp())). \
                                        replace('{updatedat}', nowObj.strftime("%Y-%m-%d-%H:%M:%S.%f")),
                                qos=1,
                                    )
                    logger.info(f'''Published a virtual input event to MQTT topic: {topicsList[numberShortPresses - 1]} for MODBUS_ADDR: {inputDevice['MODBUS_ADDR']} and MODBUS_IO: {inputDevice['MODBUS_IO']}''') 
                query = f'''DELETE FROM
                                virtualInputEvents
                            WHERE
                                MODBUS_ADDR='{inputDevice['MODBUS_ADDR']}'
                                AND MODBUS_IO='{inputDevice['MODBUS_IO']}'
                                AND type='{inputDevice['type']}'
                                AND MQTT_TOPICS='{inputDevice['MQTT_TOPICS']}'
                            '''
                cur.execute( query )
                db.commit()

if __name__ == '__main__':
    global modules
    DELAY = 0.01

    cur,db = sqliteSetup()
    logger, virtualInputs, gpioConfigs, commandConfigs, client, modules = initialise(modbusaddresses=[1,], DELAY=DELAY)

    virtualEventsLastRun = time.time()
    scheduledEventsLastRun = time.time()
    eventsCleanupLastRun = time.time()
    while True:
        if time.time() >= eventsCleanupLastRun + 10:
            cur.execute(f'''DELETE FROM virtualInputEvents WHERE timestamp < '{eventsCleanupLastRun}';''')
            db.commit()
            eventsCleanupLastRun = time.time()

        if time.time() >= scheduledEventsLastRun + 0.05:
            loopScheduledEvents(cur=cur,db=db,logger=logger)
            scheduledEventsLastRun = time.time()

        if time.time() > virtualEventsLastRun + 0.05:
            loopVirtualEvents(cur=cur,db=db,logger=logger)
            virtualEventsLastRun = time.time()

        if mqtt_connected == False:
            mqtt_connect()
        modules.pollReadInputs()
        client.loop(DELAY)
