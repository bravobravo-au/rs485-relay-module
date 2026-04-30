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

Output LED chase effect from High numbered outputs to low numbered outputs
'''
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from multipleModuleManager import MultipleModuleManager


'''
Example and test code
'''
if __name__ == '__main__': 
    DELAY = 0.01
    modbusaddresses=[1,]
    modules = MultipleModuleManager(port='/dev/ttyUSB0', desiredbaudrate=115200, modbusaddresses=modbusaddresses)

    while True:
        if True:
            for module in modbusaddresses:
                for i in range(modules.getNumberInputOutputs(module)-1,-1,-1):
                    modules.updateOutput(module,i,True)
            for module in reversed(modbusaddresses):
                for i in range(modules.getNumberInputOutputs(module)-1,-1,-1):
                    modules.updateOutput(module,i,False)


