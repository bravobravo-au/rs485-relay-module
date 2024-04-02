# rs485-relay-module python code
23IO Modbus RTU Python Library for eletechsup PNP and NPN relay modules. 
Specification for RS485 comms can be found here https://485io.com/eletechsup/23IOA08_23IOB16_23IOC24_23IOD32_23IOE48.rar with M0 shorted / command 2 mode.

This package provides the following Objects ModbusDIO and MultipleModuleManager in eletech23iod.py. All inputs and outputs work.

ModbusDIO is useful for controlling a single module on the RS485 bus. MultipleModuleManager is useful when you need to control multiple modules on the same bus using a unqiue slave address for each module. When multiple modules are controlled on the same bus there is a requirement to have some delays to stop two devices writing on the bus at the same time and corrupting the data. To wire multiple modules on the same bus, connect all A- together and all A+ together. Note the need for unique addresses. 

You may need to either
provide your user write access something like (sudo chmod a+rw /dev/ttyUSB0)
add your user to a group that can write to the serial device that you are using (add user to group dialout or similar on your system)

I have only tested this with three 23IOD32 modules but I have tried to handled the cases for the bigger and smaller variants. If you get this working with other variants then please let me know.
