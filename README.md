# rs485-relay-module
23IO Modbus RTU Python Library for eletechsup PNP and NPN relay modules. 
Specification for RS485 comms can be found here https://485io.com/eletechsup/23IOA08_23IOB16_23IOC24_23IOD32_23IOE48.rar with M0 shorted / command 2 mode.

This package provides the following Objects ModbusDIO and MultipleModuleManager in eletech23iod.py.

ModbusDIO is useful for controlling a single module on the RS485 bus. MultipleModuleManager is useful when you need to control multiple modules on the same bus using a unqiue slave address for each module. When multiple modules are controlled on the same bus there is a requirement to have some delays to stop two devices writing on the bus at the same time and corrupting the data.

