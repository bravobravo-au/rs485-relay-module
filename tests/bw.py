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

Example code that is used to test
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

   DELAY_TIME = 0.05

   while True:
      modules.updateOutputsByHexStr(modbusaddresses[0],'0',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)

      modules.updateOutputsByHexStr(modbusaddresses[0],'1',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'100',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'200',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'400',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'800',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'1000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'100000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'200000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'400000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'800000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME) 
      modules.updateOutputsByHexStr(modbusaddresses[0],'1000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80000000',outputValue=True,keepCurrent=False)
      time.sleep(DELAY_TIME)       

      modules.updateOutputsByHexStr(modbusaddresses[0],'0',outputValue=True,keepCurrent=False)

      modules.updateOutputsByHexStr(modbusaddresses[0],'0',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'1',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'100',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'200',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'400',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'800',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'1000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'100000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'200000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'400000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'800000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME) 
      modules.updateOutputsByHexStr(modbusaddresses[0],'1000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'2000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'4000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'8000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'10000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'20000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'40000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)
      modules.updateOutputsByHexStr(modbusaddresses[0],'80000000',outputValue=True,keepCurrent=True)
      time.sleep(DELAY_TIME)

      for i in range(1,10):
         NEW_DELAY_TIME = DELAY_TIME * i
         modules.updateOutputsByHexStr(modbusaddresses[0],'FFFFFFFF',outputValue=True,keepCurrent=False)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'F0000000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'0F000000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'00F00000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'000F0000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'0000F000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'00000F00',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'000000F0',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'0000000F',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)
         modules.updateOutputsByHexStr(modbusaddresses[0],'00000000',outputValue=False,keepCurrent=True)
         time.sleep(NEW_DELAY_TIME)