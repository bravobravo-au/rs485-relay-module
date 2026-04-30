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

23IOD48 48CH PNP NPN Multifunction RS485 Remote IO Module PLC DI-DO Expansion Board DIN Rail Box Standard MODBUS RTU Protocol
23IOD32 32CH PNP NPN Multifunction RS485 Remote IO Module PLC DI-DO Expansion Board DIN Rail Box Standard MODBUS RTU Protocol
23IOD24 24CH PNP NPN Multifunction RS485 Remote IO Module PLC DI-DO Expansion Board DIN Rail Box Standard MODBUS RTU Protocol
23IOD16 16CH PNP NPN Multifunction RS485 Remote IO Module PLC DI-DO Expansion Board DIN Rail Box Standard MODBUS RTU Protocol
23IOD08 8CH  PNP NPN Multifunction RS485 Remote IO Module PLC DI-DO Expansion Board DIN Rail Box Standard MODBUS RTU Protocol

Notes:
    This code works with Modbus RTU Command 2 that is M0 jumper shorted out. By default these modules ship with M0 not shorted.
    If you are wiring up multiple modules on the same RS485 bus / pair remember that each needs a unique modbus address set using the DIP switches. 
    The test code shows
        1. single LED moving up and back from 0 to N where N is number inputs and outputs showing off single output control
        2. each LED turning on from 0 to N and then each LED turning off fron N to 0 showing off single output control
        3. each LED turning on from 0 to N and then each LED turning off fron 0 to N showing off single output control
        4. each LED blinking 5 times showing multiple LED control
        5. each 4 LEDs turning on in order 5 times showing multiple LED control

'''

import serial
from serial import SerialException
import time
import datetime
import sys
from fastcrc import crc16


BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
MODELS = [2308, 2316, 2324, 2332, 2348]
FUNCTIONCODES = {
    'READ_DO': 0x01,
    'READ_DI': 0x02,
    'READ_SPECIAL_FUNCTION': 0x03,
    'WRITE_DO': 0x05,
    'WRITE_SPECIAL_FUNCTION': 0x06,
    'WRITE_MULTIPLE_DO': 0x0F,
    'WRITE_MULTIPLE_SPECIAL_FUNCTION': 0x10,
}
DATETIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ%z'

class ChecksumMismatchException(Exception):
    """Computed checksum does not match the checksum provided"""


class ModbusDIO():
    def __init__(self, port, desiredbaudrate=115200, modbusaddress=1, inputchangecallback=None):
        self.__port__ = port
        self.__modbusaddress__ = modbusaddress
        self.__serial__ = None
        self.__model__ = None
        self.__baudrate__ = None
        self.__inputvalues__ = 0
        self.__inputs__ = []
        self.__outputs__ = []
        self.__inputchangecallback__ = inputchangecallback

        self.__serialconnect__(desiredbaudrate)
        if self.__baudrate__ != desiredbaudrate:
            self.__setdefaultbaudrate__(desiredbaudrate)

        self.__numberinputoutputs__ = int(str(self.__model__)[-2:])

        
        for i in range(0,self.__numberinputoutputs__):
            initialvalue = { 
                            'number': i, 
                            'lastchange': datetime.datetime.now(datetime.UTC),
                            'lastOn': datetime.datetime.now(datetime.UTC),
                            'lastOff': datetime.datetime.now(datetime.UTC),
                            'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                            'value': False, 
                            }
            self.__inputs__.append( initialvalue )
            self.__outputs__.append( initialvalue )

    def __str__(self):
        outstring = ''
        for i in range(0,self.__numberinputoutputs__):
            outstring += f'''Input: {i} State: {self.__inputs__[i]['value']} LastChanged: {self.__inputs__[i]['lastchange']} Output: {i} State: {self.__outputs__[i]['value']} LastChanged: {self.__outputs__[i]['lastchange']}\n'''

        return outstring
    
    def __appendModbusChecksum__(self, data):
        checksum = crc16.modbus(data).to_bytes(2,'little')
        return data + checksum

    def __validateModbusChecksum__(self,data):
        if data is None:
            return False
        message = data[:-2]
        checksum = data[-2:]
        calculatedchecksum = crc16.modbus(message).to_bytes(2,'little')

        if calculatedchecksum == checksum:
            return True
        
        raise(ChecksumMismatchException(f'''CHECKSUM DOES NOT MATCH got: {checksum} expected {calculatedchecksum}'''))
        return False
        

    def __setdefaultbaudrate__(self, newbaudrate,):
        if self.__serial__.isOpen() and newbaudrate in BAUDRATES:
            value = BAUDRATES.index(newbaudrate)
            data = self.__generatemodbusmessage__( 'WRITE_SPECIAL_FUNCTION', 0x00fe, value )
            self.__serial__.write( data )

    def __serialconnect__(self,baudrate):

        ser = serial.Serial(
            port=self.__port__,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout = 0.35,
        )

        
        if ser.isOpen():
            self.__serial__ = ser
            data = self.__generatemodbusmessage__( 'READ_SPECIAL_FUNCTION', 0x00f7, 0x0001 )
            self.__serial__.write( data )
            modelresponse = self.__serial__.read(8)

            try:
                self.__validateModbusChecksum__(modelresponse)
                self.__serial__.reset_input_buffer()

                modelbytes = modelresponse[3:5]
                modelint = int.from_bytes(modelbytes, signed=False,byteorder='big')
            except ChecksumMismatchException:
                modelint = 0

            
            if modelint in MODELS:
                self.__model__ = modelint
                self.__baudrate__ = baudrate
            else:
                currentindex = BAUDRATES.index(baudrate)
                if currentindex > 0:
                    self.__serialconnect__( BAUDRATES[currentindex - 1] )
                
    def __generatemodbusmessage__(self,functioncode,address,value=None):
        message = ''
        if functioncode in FUNCTIONCODES:
            message = self.__modbusaddress__.to_bytes(1,'little') 
            message += FUNCTIONCODES[functioncode].to_bytes(1,'little')

            message += address.to_bytes(2,'big')[0].to_bytes(1)
            message += address.to_bytes(2,'big')[1].to_bytes(1)

            if value is not None:
                message += value.to_bytes(2,'big')[0].to_bytes(1)
                message += value.to_bytes(2,'big')[1].to_bytes(1)

            message = self.__appendModbusChecksum__(message)
        return message


    def __updateinput__(self,number,newvalue):
        fieldName = 'lastOff'
        oppFieldName = 'lastOn'
        if newvalue == True:
            fieldName = 'lastOn'
            oppFieldName = 'lastOff'

        self.__inputs__[number] = { 
                                   'number': number, 
                                   'lastchange': datetime.datetime.now(datetime.UTC), 
                                   'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                                   'value': newvalue, 
                                   fieldName : datetime.datetime.now(datetime.UTC),
                                   oppFieldName : self.__inputs__[number][oppFieldName],
                                   }


    @property
    def numberinputoutputs(self):
        return self.__numberinputoutputs__

    @property
    def model(self):
        return self.__model__

    @property
    def baudrate(self):
        return self.__baudrate__

    @property
    def modbusaddress(self):
        return self.__modbusaddress__


    def updateOutput(self,output,value):

        if isinstance(value,str):
            if value.upper() == 'TOGGLE':
                value = not self.__outputs__[output]['value']

        fieldName = 'lastOff'
        oppFieldName = 'lastOn'
        if value == True:
            fieldName = 'lastOn'
            oppFieldName = 'lastOff'

        self.__outputs__[output] = { 
                                    'number': output, 
                                    'lastchange': datetime.datetime.now(datetime.UTC), 
                                    'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                                    'value': value,
                                    fieldName : datetime.datetime.now(datetime.UTC),
                                    oppFieldName : self.__outputs__[output][oppFieldName],
                                    }


        if value == True:
            value = 0xFF00
        else:
            value = 0x0000
        data = self.__generatemodbusmessage__( 'WRITE_DO', output, value )
        self.__serial__.write(data)
        x = self.__serial__.read(8)
        self.__validateModbusChecksum__(x)
        self.__serial__.reset_input_buffer()

    def updateOutputs(self,value):
        def performupdate(addr):
            data = self.__generatemodbusmessage__( 'WRITE_SPECIAL_FUNCTION', addr, value, )
            self.__serial__.write(data)
            x = self.__serial__.read(8)
            self.__validateModbusChecksum__(x)
            self.__serial__.reset_input_buffer()


        for i in range(0,self.__numberinputoutputs__):
            fieldName = 'lastOff'
            oppFieldName = 'lastOn'
            if value == True:
                fieldName = 'lastOn'
                oppFieldName = 'lastOff'

            self.__outputs__[i] = { 
                                   'number': i, 
                                   'lastchange': datetime.datetime.now(datetime.UTC), 
                                   'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                                   'value': value,
                                   fieldName : datetime.datetime.now(datetime.UTC),
                                   oppFieldName : self.__outputs__[i][oppFieldName],
                                   }
        
        if value == True:
            value = 0xFFFF
        else:
            value = 0x0000

        performupdate(0x0080)
        if self.__model__ in [2324, 2332, 2348]:
            performupdate(0x0081)

        if self.__model__ in [2348]:
            performupdate(0x0082)

    def updateOutputsByList(self,outputlist):
        '''
        Update all outputs using a list of Bools
        '''

        for i in range(0,self.__numberinputoutputs__):
            if self.__outputs__[i]['value'] != outputlist[i]:
        
                fieldName = 'lastOff'
                oppFieldName = 'lastOn'
                if outputlist[i] == True:
                    fieldName = 'lastOn'
                    oppFieldName = 'lastOff'

                self.__outputs__[i] = { 
                                        'number': i, 
                                       'lastchange': datetime.datetime.now(datetime.UTC), 
                                       'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                                       'value': outputlist[i], 
                                       fieldName : datetime.datetime.now(datetime.UTC),
                                       oppFieldName : self.__outputs__[i][oppFieldName],
                                       }

        def performupdate(addr, value):
            data = self.__generatemodbusmessage__( 'WRITE_SPECIAL_FUNCTION', addr, value, )
            self.__serial__.write(data)
            x = self.__serial__.read(8)
            self.__validateModbusChecksum__(x)
            self.__serial__.reset_input_buffer()

        '''
        Handle these extra 16 bits for 2348 model as int is 32 bits 
        '''
        if self.__model__ in [2348]:
            highlist = outputlist[32:47]
            outputlist = outputlist[0:31]


        '''
        Convert list of bools to single int
        '''
        bits = 0
        for count,item in enumerate(outputlist):
            if item is False:
                continue
            bits = bits | (item << count)

        lower16bits = bits & 0x0000FFFF
        performupdate(0x0080, lower16bits)


        if self.__model__ in [2324, 2332, 2348]:
            upper16bits = (bits >> 16) & 0x0000FFFF 
            performupdate(0x0081, upper16bits)

        
        if self.__model__ in [2348]:
            highbits = 0
            for count,item in enumerate(highlist):
                if item is False:
                    continue
                highbits = highbits | (item << count)
            
            highbits = highbits & 0x0000FFFF
            performupdate(0x0082, highbits)

    def updateOutputsByHexStr(self,hexStr, outputValue=True, keepCurrent=False, ):
        '''
        Update all outputs using a list of Bytes
        '''
        bitwiseORMask = 0x0000000
        outputMask = 0x0000000

        if outputValue == True:
            outputMask = 0xFFFFFFFF

        def performupdate(addr, value):
            data = self.__generatemodbusmessage__( 'WRITE_SPECIAL_FUNCTION', addr, value, )
            self.__serial__.write(data)
            x = self.__serial__.read(8)
            self.__validateModbusChecksum__(x)
            self.__serial__.reset_input_buffer()

        try:
            value = int(hexStr, 16)
            if value > 4294967295:
                return None
        except ValueError:
            return None

        if keepCurrent == True:
            for i,output in enumerate(self.__outputs__):
                currBit = pow(2,i)
                if output['value'] == True:
                    bitwiseORMask = bitwiseORMask | currBit
            bitwiseORMask = ((value & bitwiseORMask) ^ ((1 << 32) -1)) & bitwiseORMask
      
        value = (value & outputMask)| bitwiseORMask

        for i,output in enumerate(self.__outputs__):
            newValue = False
            if value & pow(2,i) > 0:
                newValue = True

            if newValue != output['value']:
                fieldName = 'lastOff'
                oppFieldName = 'lastOn'
                if newValue == True:
                    fieldName = 'lastOn'
                    oppFieldName = 'lastOff'

                self.__outputs__[i] = { 
                                            'number': i, 
                                            'lastchange': datetime.datetime.now(datetime.UTC), 
                                            'lastchangestr': datetime.datetime.now(datetime.UTC).strftime(DATETIME_STRING_FORMAT), 
                                            'value': newValue,
                                            fieldName : datetime.datetime.now(datetime.UTC),
                                            oppFieldName : self.__outputs__[i][oppFieldName],
                                            }

        lower16bits = (value & 0x0000FFFF) | (bitwiseORMask & 0x0000FFFF)
        performupdate(0x0080, lower16bits)

        if self.__model__ in [2324, 2332, 2348]:
            upper16bits = ((value >> 16) & 0x0000FFFF) | (bitwiseORMask >> 16 & 0x0000FFFF)
            performupdate(0x0081, upper16bits)

        if self.__model__ in [2348]:
            upper16bits = ((value >> 32) & 0x0000FFFF) | (bitwiseORMask >> 32 & 0x0000FFFF)
            performupdate(0x0081, upper16bits)

    def getInput(self, inputnumber):
        if inputnumber <= self.__numberinputoutputs__ and inputnumber >= 0:
            return self.__inputs__[inputnumber]

    def getInputs(self, inputnumbers=None):
        if inputnumbers is None:
            return self.__inputs__
        if isinstance(inputnumbers,list):
            ret = []
            for inputnumber in inputnumbers:
                ret.append(self.getInput(inputnumber))
            return ret
        if isinstance(inputnumbers, int):
            return self.getInput(inputnumbers)


    def getOutputs(self, outputnumbers=None):
        if outputnumbers is None:
            return self.__outputs__
        if isinstance(outputnumbers,list):
            ret = []
            for outputnumber in outputnumbers:
                ret.append(self.__outputs__[outputnumber])
            return ret
        if isinstance(outputnumbers, int):
            return self.__outputs__[outputnumbers]

    def pollreadoutputs(self):
        pass

    def pollreadinputs(self):
        def getInput(address, value):
            data = self.__generatemodbusmessage__( 'READ_SPECIAL_FUNCTION', address, value )
            self.__serial__.write(data)
            x = self.__serial__.read(7)
            self.__validateModbusChecksum__(x)
            self.__serial__.reset_input_buffer()
            return x[3:5]


        def updatechangedbits(bits,state):
            '''
            We pass in which bits have changed (bits) computed using bitwise manipulation and the changed state (True/False). This allows the function to bail out early if we have updated all changed inputs.

            This means that if the last input has changed we have gone through this loop the maximum number of times and saved nothing.
            '''
            subtotal = 0
            for i in range(0,self.__numberinputoutputs__):
                powerof2val = pow(2,i)
                if bits & powerof2val == powerof2val:
                    subtotal += powerof2val
                    self.__updateinput__(i,state)
                    if self.__inputchangecallback__ is not None:
                        self.__inputchangecallback__( self.__modbusaddress__, i, state )
                    if bits == subtotal:
                        '''
                        All changes have been found.
                        '''
                        break
        try:
            inputs1 = getInput(0x0090, 0x0001)
        except SerialException:
            return None

        inputs = inputs1

        if self.__model__ in [2324, 2332, 2348]:
            try:
                inputs2 = getInput(0x0091, 0x0001)
            except SerialException:
                return None
            inputs = inputs2 + inputs1

        if self.__model__ in [2348]:
            try:
                inputs3 = getInput(0x0092, 0x0001)
            except SerialException:
                return None
            inputs = inputs3 + inputs2 + inputs1

        inputs = int.from_bytes(inputs,signed=False,byteorder='big')

        if self.__inputvalues__ != inputs:
            bitsgonehigh = ~self.__inputvalues__ & inputs
            bitsgonelow = self.__inputvalues__ & ~inputs

            if bitsgonehigh > 0:
                updatechangedbits(bitsgonehigh, True)
            if bitsgonelow > 0:
                updatechangedbits(bitsgonelow, False)

            self.__inputvalues__ = inputs

