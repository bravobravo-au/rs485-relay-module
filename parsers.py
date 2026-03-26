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
'''
import json
from json.decoder import JSONDecodeError
import datetime
from dateutil import parser

"""
Parser of MQTT messages in JSON taking an Integer and returning a BOOL

ARG1 is used to specify the name to use to trigger off

0 is logic Low and anything else is logic High
"""
def PARSER_JSONINT(message, config):
    jsonDecode = json.loads( str(message.payload.decode("utf-8")) )

    #logger.debug("JSONINT Topic: %s Payload: %s" % (message.topic,jsonDecode))

    value = int(jsonDecode[config['MQTT_PARSER_ARG1']])
    if value == 0:
        value = False
    else:
        value = True

    return value


"""
Parser of MQTT messages in JSON taking a String and returning a BOOL

ARG1 is used to specify the name to use to trigger off

OFF is logic Low and ON is logic High
"""
def PARSER_STRONOFF(message, config):
    jsonDecode = json.loads( str(message.payload.decode("utf-8")) )
    messagePayload = jsonDecode[config['MQTT_PARSER_ARG1']].upper()
    #logger.debug("STRONOFF Topic: %s Payload: %s" % (message.topic,messagePayload))

    value = None

    if messagePayload == 'OFF':
        value = False
    if messagePayload == 'ON':
        value = True
    if messagePayload == 'TOGGLE':
        value = 'toggle'
    return value

def BOOL_ONOFFSTRING( booleanVal ):
    if booleanVal == False:
        return 'OFF'
    return 'ON'

def ONOFFSTRING_BOOL( stringVal ):
    if stringVal.upper() == 'ON':
        return True
    if stringVal.uppser() == 'OFF':
        return False
    return False

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def numberShortPressEventsToString( numberShortPressEvents, state ):
    if numberShortPressEvents == 2:
        return 'SINGLE'
    if numberShortPressEvents == 4:
        return 'DOUBLE'
    if numberShortPressEvents == 6:
        return 'TRIPLE'
    if numberShortPressEvents == 8:
        return 'QUAD'
    if numberShortPressEvents == 10:
        return 'QUIN'


'''
Convert a value to a future dated UTC unix timestamp

Pass in a Unix Timestamp as INT or FLOAT
Pass in a String that can be converted to a date using date-util
Pass in a dict of timedelta intervals  {"seconds":15,"minutes":1} 

Returns 0.0 when things are wrong
'''
def convertValueToTimestamp( value ):
    if value is None:
        return  0.0
    if isinstance(value,str):
        '''
        Try a dict of params for a timedelta
        '''
        try:
            jsonData = json.loads( value )
            if isinstance(jsonData,dict):
                dictArgs = {}
                for interval in ['days','seconds','microseconds','milliseconds','minutes','hours','weeks']:
                    if interval in jsonData:
                        dictArgs[interval] = jsonData[interval]
                if len(dictArgs) > 0:
                    delta = datetime.timedelta( **dictArgs )
                    return (datetime.datetime.now( datetime.timezone.utc ) + delta).timestamp()
        except json.JSONDecodeError:
            pass

        '''
        Try a timestamp string formatted string
        '''
        try:
            dt = parser.parse(value)
            now_utc = datetime.datetime.now( datetime.timezone.utc ).timestamp()
            if dt.timestamp() > now_utc:
                return dt.timestamp()
        except parser.ParserError:
            return 0.0
        return  0.0


    if isinstance(value,int) or isinstance(value,float):
        now_utc = datetime.datetime.now( datetime.timezone.utc ).timestamp()
        if value > now_utc:
            return value
        else:
            return 0.0
