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

Example code that shows how HEX strings can be sent to the module to update multiple IOs at the same time.
'''
import sys
import os
import time 

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from multipleModuleManager import MultipleModuleManager


'''
Example and test code
'''
if __name__ == '__main__': 
    modbusaddresses=[1,]
    modules = MultipleModuleManager(port='/dev/ttyUSB0', desiredbaudrate=115200, modbusaddresses=modbusaddresses,)

    numberIOs = modules.getNumberInputOutputs(modbusaddresses[0])

    modules.updateOutputsByHexStr(modbusaddresses[0],'ZFFFFFFF')

    stateList = [
        '00000000',
        '00000001',
        '00000002',
        '00000004',
        '00000008',
        '00000010',
        '00000020',
        '00000040',
        '00000080',
        '00000100',
        '00000200',
        '00000400',
        '00000800',
        '00001000',
        '00002000',
        '00004000',
        '00008000',
        '00010000',
        '00020000',
        '00040000',
        '00080000',
        '00100000',
        '00200000',
        '00400000',
        '00800000',
        '01000000',
        '02000000',
        '04000000',
        '08000000',
        '10000000',
        '20000000',
        '40000000',
        '80000000',
    ]

    INVstateList = []

    for item in stateList:
        val = hex(~(int(item,16)))
        INVstateList.append(val)

    stateList2 = [
        '00000000',
        '0000000F',
        '000000F0',
        '00000F00',
        '0000F000',
        '000F0000',
        '00F00000',
        '0F000000',
        'F0000000',
    ]

    INVstateList2 = []

    for item in stateList2:
        val = hex(~(int(item,16)))
        INVstateList2.append(val)
    while True:

        
        #single LED up and down
        for i in range(0,len(stateList)):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList[i])
        for i in range(len(stateList)-1,0,-1):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList[i])
        

        #single LED snaking up and down
        modules.updateOutputsByHexStr(modbusaddresses[0],'0',keepCurrent=False)
        for i in range(0,len(stateList)):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList[i],keepCurrent=True)
        modules.updateOutputsByHexStr(modbusaddresses[0],'0',keepCurrent=False)
        for i in range(len(stateList)-1,0,-1):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList[i],keepCurrent=True)


        #single unlit LED up and down
        for i in range(0,len(INVstateList)):
            modules.updateOutputsByHexStr(modbusaddresses[0],INVstateList[i])
        for i in range(len(stateList)-1,0,-1):
            modules.updateOutputsByHexStr(modbusaddresses[0],INVstateList[i])


        #four LEDs moving up and down
        for i in range(0,len(stateList2)):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList2[i])
            time.sleep(0.05)
        for i in range(len(stateList2)-1,0,-1):
            modules.updateOutputsByHexStr(modbusaddresses[0],stateList2[i])
            time.sleep(0.05)

        #four unlit LEDs moving up and down
        for i in range(0,len(INVstateList2)):
            modules.updateOutputsByHexStr(modbusaddresses[0],INVstateList2[i])
            time.sleep(0.05)
        for i in range(len(INVstateList2)-1,0,-1):
            modules.updateOutputsByHexStr(modbusaddresses[0],INVstateList2[i])
            time.sleep(0.05)

        #Two Leds On Two Leds off Two Leds On chasing up and down
        value = 51
        for i in range(0,numberIOs):
            modules.updateOutputsByHexStr(modbusaddresses[0],hex(value))
            value = value << 1

        for i in range(0,numberIOs):
            modules.updateOutputsByHexStr(modbusaddresses[0],hex(value))
            value = value >> 1