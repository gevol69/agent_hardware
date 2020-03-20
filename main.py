from web_component import Server
from business_logic import MainManager
from means import MacManager, CPUManager, OSManager, IPManager, RouteTableManager, MacNearestGateways, DiskSerialNumberManager, MotherboardManager, GPUManager, RAMManager
import netifaces #модуль для кроссплатформенного получения информации о сетевых интерфейсов
from cpuinfo import * #модуль для получения информации о CPU
import sys #модуль для получения информации об имени системы
import logging #импорт модуля для сбора логов
import subprocess #модуль для работы с командной строкой
import re #регулярные выражения для фильтрации вывода командной строки
import socket #для проверки валидности IP адреса
import struct #упаковка полученной информации из таблицы маршрутизации
import platform #для получения полного наименования и версии ОС
import ssl #модуль для генерирования объекта ssl_context
from cryptography.fernet import Fernet #модуль для расшифрования сертификата и приватных ключей
import tempfile #модуль для создания временных файлов и папок
import os 
from pathlib import *
from main_module import start

if sys.platform == 'win32':
	import winreg
	import wmi

if __name__ == '__main__':
	start()
