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
Multiple Device NManager
'''


from eletech23iod import ModbusDIO
from serial import SerialException
import datetime
import time

class MultipleModuleManager():
    def __init__(self, port, desiredbaudrate=115200, modbusaddresses=[], inputchangecallback=None, intermoduledelay=20000, ):
        self.__intermoduledelay__ = intermoduledelay
        self.__modules__ = {}
        self.__lastmoduleused__ = None
        self.__lastmoduleusedat__ = None



        for modbusaddress in modbusaddresses:
            self.__modules__[modbusaddress] = ModbusDIO(port=port, desiredbaudrate=desiredbaudrate, modbusaddress=modbusaddress, inputchangecallback=inputchangecallback)
            self.__lastmoduleused__ = modbusaddress
            self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
            time.sleep(self.__intermoduledelay__ / 1000000 )

    def __delay__(self, currentmodule):
        if currentmodule == self.__lastmoduleused__:
            return None
        else:
            timediff = datetime.datetime.now(datetime.UTC) - self.__lastmoduleusedat__
            if timediff.days == 0 and timediff.seconds == 0 and timediff.microseconds <= self.__intermoduledelay__:
                time.sleep(self.__intermoduledelay__ / 1000000)
        

    def getModbusAddresses( self, ):
        return list(self.__modules__.keys())

    def getBaudRate(self,modbusaddress):
        if modbusaddress not in self.__modules__:
            return None
        return self.__modules__[modbusaddress].baudrate


    def getNumberInputOutputs(self,modbusaddress):
        if modbusaddress not in self.__modules__:
            return None
        return self.__modules__[modbusaddress].numberinputoutputs

    def pollReadInputs(self,modbusaddress=None):
        if modbusaddress is None:
            for module in self.__modules__:
                self.__delay__(module)
                self.__modules__[module].pollreadinputs()
                self.__lastmoduleused__ = module
                self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
                
            return None
        
        if modbusaddress not in self.__modules__:
            return None
        
        self.__delay__(modbusaddress)
        self.__modules__[modbusaddress].pollreadinputs()
        self.__lastmoduleused__ = modbusaddress
        self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)

    def updateOutput(self,modbusaddress,output,value):
        if modbusaddress is None:
            return None
        if modbusaddress not in self.__modules__:
            return None

        self.__delay__(modbusaddress)

        def retrySerialCall( modbusaddress, output, value, retry=0 ):
            try:
                self.__modules__[modbusaddress].updateOutput(output,value)
            except SerialException:
                self.__delay__(modbusaddress)
                if retry > 0:
                    retrySerialCall( modbusaddress, output, value, retry=retry-1 )
                else:
                    raise 

        retrySerialCall( modbusaddress, output, value, )

        self.__lastmoduleused__ = modbusaddress
        self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)


    def updateOutputs(self, modbusaddress, value):
        if modbusaddress not in self.__modules__:
            return None

        if modbusaddress is None:
            modbusaddress = self.__modules__
        else:
            modbusaddress = [ modbusaddress ]

        for modbusaddress in self.__modules__:
            self.__delay__(modbusaddress)
            self.__modules__[modbusaddress].updateOutputs(value)
            self.__lastmoduleused__ = modbusaddress
            self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)



    def updateOutputsByList(self, modbusaddress, valueList):
        if modbusaddress not in self.__modules__:
            return None

        if modbusaddress is None:
            modbusaddress = self.__modules__
        else:
            modbusaddress = [ modbusaddress ]

        for address in modbusaddress:
            self.__delay__(address)
            self.__modules__[address].updateOutputsByList(valueList)
            self.__lastmoduleused__ = address
            self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
        
    def updateOutputsByHexStr(self, modbusaddress, hexStr, outputValue=True, keepCurrent=False,):
        if modbusaddress not in self.__modules__:
            return None

        if modbusaddress is None:
            modbusaddress = self.__modules__
        else:
            modbusaddress = [ modbusaddress ]

        for address in self.__modules__:
            self.__delay__(address)
            self.__modules__[address].updateOutputsByHexStr(hexStr,outputValue=outputValue,keepCurrent=keepCurrent)

    def getInput(self, modbusaddress, inputnumber):
        if modbusaddress is None:
            return None
        if modbusaddress not in self.__modules__:
            return None

        self.__delay__(modbusaddress)
        input = self.__modules__[modbusaddress].getInput(inputnumber)
        self.__lastmoduleused__ = modbusaddress
        self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
        return input

    def getInputs(self, modbusaddress, inputnumbers=None):
        if modbusaddress is None:
            return None
        if modbusaddress not in self.__modules__:
            return None

        self.__delay__(modbusaddress)
        inputs = self.__modules__[modbusaddress].getInputs(inputnumbers)
        self.__lastmoduleused__ = modbusaddress
        self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
        return inputs

    def getOutputs(self, modbusaddress, outputnumbers=None):
        if modbusaddress is None:
            return None
        if modbusaddress not in self.__modules__:
            return None

        self.__delay__(modbusaddress)
        outputs = self.__modules__[modbusaddress].getOutputs(outputnumbers)
        self.__lastmoduleused__ = modbusaddress
        self.__lastmoduleusedat__ = datetime.datetime.now(datetime.UTC)
        return outputs
