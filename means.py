# -*- coding: utf-8 -*-
import netifaces #модуль для кроссплатформенного получения информации о сетевых интерфейсов
from cpuinfo import * #модуль для получения информации о CPU
import sys #модуль для получения информации об имени системы
import logging #импорт модуля для сбора логов
import subprocess #модуль для работы с командной строкой
import re #регулярные выражения для фильтрации вывода командной строки
import socket #для проверки валидности IP адреса
import struct #упаковка полученной информации из таблицы маршрутизации
import platform #для получения полного наименования и версии ОС

if sys.platform == 'win32':
	import winreg as wr #модуль для работы с реестром Windows
	import wmi #модуль для реализации wmi запросов в Windows
elif sys.platform == 'linux2' or sys.platform == 'linux':
	pass


class MacManager:

	'''
		Класс для получения информации о mac адресах
	'''

	def get_driver_name_from_guid(self, iface_guids):

		'''
			Метод netifaces.interfaces() возвращает guid сетевых интерфейсов
			Нужно получить понятные имена интерфейсов из реестра
			:param iface_guids: список guid интерфейсов
			:type iface_guids: list
			:return iface_names: список имён интерфейсов
			:rtype iface_names: list
		'''

		iface_names = ['(unknown)' for i in range(len(iface_guids))]
		reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
		reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}')
		for i in range(wr.QueryInfoKey(reg_key)[0]):
			subkey_name = wr.EnumKey(reg_key, i)
			try:
				reg_subkey = wr.OpenKey(reg_key, subkey_name)
				guid = wr.QueryValueEx(reg_subkey, 'NetCfgInstanceId')[0]
				try:
					idx = iface_guids.index(guid)
					iface_names[idx] = wr.QueryValueEx(reg_subkey, 'DriverDesc')[0]
				except ValueError as msg:
					logging.debug(msg)
			except Exception as msg:
				logging.debug(msg)
		return iface_names

	def get_mac(self): 
		
		'''
			Метод для получения mac адресов 
			В зависимости от ОС - разные способы получения
			:return names_and_macs: словарь в формате: "имя интерфейса : mac адрес"
			:rtype names_and_macs: dict		
		'''

		names_and_macs = {}
		if sys.platform == 'win32':
			guid_interfaces = netifaces.interfaces()
			names_interfaces = self.get_driver_name_from_guid(guid_interfaces)
			mac_addresess = []
			for guid_interface in guid_interfaces:
				addr = netifaces.ifaddresses(guid_interface)[netifaces.AF_LINK]
				mac_addresess.append(addr[0]['addr'])
			for i in range(len(names_interfaces)):
				if names_interfaces[i] == '(unknown)':
					break
				else:
					names_and_macs[names_interfaces[i].encode().decode()] = mac_addresess[i]
		elif sys.platform == 'linux2' or sys.platform == 'linux' or sys.platform == 'darwin':
			names_interfaces = netifaces.interfaces()
			names_and_macs = {}
			for index, name_interface in enumerate(names_interfaces):
				mac_addr = ''
				try:
					mac_addr = netifaces.ifaddresses(name_interface)[netifaces.AF_LINK]
				except Exception as msg:
					logging.debug(msg)
				if mac_addr:
					names_and_macs[names_interfaces[index]] = mac_addr[0]['addr']

		return names_and_macs


	def get_default_mac(self):

		'''
			Метод для получения mac адреса интерфейса, с которого происходит выход в Интернет на данный момент 
			:return dict_mac: словарь в формате: "имя интерфейса : mac адрес"
			:rtype dict_mac: dict	
		'''

		dict_mac = {}
		if sys.platform == 'win32':
			default_guid_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
			default_names_interfaces = self.get_driver_name_from_guid(default_guid_interface)
			default_name_interfaces = default_names_interfaces[0]
			default_addr = netifaces.ifaddresses(default_guid_interface)[netifaces.AF_LINK]
			default_mac = default_addr[0]['addr']
			dict_mac[default_name_interfaces] = default_mac

		elif sys.platform == 'linux2' or sys.platform == 'linux'  or sys.platform == 'darwin':
			default_name_interfaces = netifaces.gateways()['default'][netifaces.AF_INET][1]
			default_addr = netifaces.ifaddresses(default_name_interfaces)[netifaces.AF_LINK]
			default_mac = default_addr[0]['addr']
			dict_mac[default_name_interfaces] = default_mac

		return dict_mac

class IPManager:

	'''
		Класс для получения IP адресов со всех сетевых интерфейсов и IP адреса шлюза по умолчанию
	'''

	def get_ip_addresses(self):

		'''
			Метод для получения IP адресов со всех интерфейсов
			:return names_and_ip: словарь в формате: "имя интерфейса : IP адрес"
			:rtype names_and_ip: dict
		'''

		names_and_ip = {}
		if sys.platform == 'win32':
			guid_interfaces = netifaces.interfaces()
			names_interfaces = MacManager().get_driver_name_from_guid(guid_interfaces)
			for index, guid_interface in enumerate(guid_interfaces):
				addr = ''
				try:
					addr = netifaces.ifaddresses(guid_interface)[netifaces.AF_INET]
				except Exception as msg:
					logging.debug(msg)
				if addr:
					if names_interfaces[index] == '(unknown)':
						break
					else:
						names_and_ip[names_interfaces[index]] = addr[0]['addr']
		elif sys.platform == 'linux2' or sys.platform == 'linux' or sys.platform == 'darwin':
			names_interfaces = netifaces.interfaces()
			for name_interface in names_interfaces:
				addr = ''
				try:
					addr = netifaces.ifaddresses(name_interface)[netifaces.AF_INET]
					names_and_ip[name_interface] = addr[0]['addr']
				except Exception as msg:
					logging.debug(msg)
					continue
				
		
		return names_and_ip
	
	def get_ip_address_default_gateway(self):

		'''
			Метод для получения IP адреса шлюза по умолчанию
			:return dict_ip: словарь в формате: "ip address default gateway : IP адрес"
			:rtype dict_ip: dict		
		'''

		default_ip_address_gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
		dict_ip = {}
		dict_ip['ip address default gateway'] = default_ip_address_gateway
		return dict_ip

class RouteTableManager:

	'''
		Класс для получения информации о таблице маршрутизации
	'''

	def is_valid_ipv4_address(self, address):

		'''
			Метод для проверки IP адреса на валидность
			(используется во время отсеивания не актуальной информации из вывода командной строки)
			:param address: исходная строка для проверки является ли она IP адресом
			:type address: str
			:return: True or False
			:rtype: bool
		'''

		try:
			socket.inet_pton(socket.AF_INET, address)
		except AttributeError:  # no inet_pton here, sorry
			try:
				socket.inet_aton(address)
			except socket.error:
				return False
			return address.count('.') == 3
		except socket.error:  # not a valid address
			return False

		return True

	def command_output(self, args):

		'''
			Метод для передачи команды в командную строку и получения вывода
			:param args: список из аргументов для ввода в командную строку (например: ['route', 'print'])
			:type args: list
			:return data: строка, содержащая вывод
			:rtype data: str
		'''

		if sys.platform == 'win32':
			CREATE_NO_WINDOW = 0x08000000 #в Windows необходимо, чтобы при вызове команд не мелькало окно командной строки
			data = subprocess.check_output(args, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
		else:
			data = subprocess.check_output(args, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE)
		return data

	def get_route_table(self):

		'''
			Метод для получения информации о таблице маршрутизации
			В Windows используется вывод команды: route print
			В Linux используется информация из /proc/net/route
			В Mac OS используется вывод команды: netstat -nr
			:return route_table_list: список словарей в следующем формате:
					[
						{
							'address': '192.168.1.100',
							'gateway': '192.168.1.1',
							'metric': '111',
							....
						}, {
							'address': '192.168.1.101',
							'gateway': '192.168.1.1',
							'metric': '111',
							....
						}
						....
					]
			:rtype route_table_list: list
		'''

		route_table_list = []
		if sys.platform == 'win32':
			args = ['route', 'print']
			output_rtr_table = self.command_output(args).decode('utf-8', 'ignore')
			if output_rtr_table:
				rtr_table = [elem.strip().split() for elem in output_rtr_table.split("\n") if re.match("^[0-9]", elem.strip()) and self.is_valid_ipv4_address(elem.strip().split()[0]) and len(elem.strip().split()[0]) > 4]
			for list_elem in rtr_table:
				tags = ['Network address', 'Netmask', 'Gateway address', 'Interface', 'Metrics']
				route_table_list.append(dict(zip(tags, list_elem)))
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			rt = open('/proc/net/route', 'r')
			if rt:
				rtr_table = [elem.strip().split() for elem in rt.read().split("\n")]
			tags = rtr_table[0]
			for list_elem in rtr_table[1:]:
				route_table_list.append(dict(zip(tags, list_elem)))
			for dict_elem in route_table_list:
				if dict_elem:
					dict_elem['Destination'] = socket.inet_ntoa(struct.pack("<L", int(dict_elem['Destination'], 16)))
					dict_elem['Gateway'] = socket.inet_ntoa(struct.pack("<L", int(dict_elem['Gateway'], 16)))
					dict_elem['Mask'] = socket.inet_ntoa(struct.pack("<L", int(dict_elem['Mask'], 16)))
		elif sys.platform == 'darwin':
			args = ['netstat', '-nr']
			output_rtr = self.command_output(args).decode()
			if output_rtr:
				rtr_table = [elem.strip().split() for elem in output_rtr.split("\n")]
			tags = rtr_table[3:][0]
			rtr_table = rtr_table[4:]
			for elem in rtr_table:
				if elem == []:
					del_index = rtr_table.index(elem)
			rtr_table = rtr_table[4:del_index]
			for list_elem in rtr_table:
				route_table_list.append(dict(zip(tags, list_elem)))
		return route_table_list

class MacNearestGateways:
	'''
		Класс для получения информации о mac адресах ближайших шлюзов
	'''
	def get_mac_addresses_nearest_gateways(self):

		'''
			Метод для получения mac адресов ближайших шлюзов
			В Windows используется вывод команды: arp - a
			В Linux используется информация из /proc/net/arp
			В Mac OS используется вывод команды: arp -all
			:return mac_addresses_nearest_gateways: список вложенных словарей в следующем формате:
					[
						{
							'192.168.1.1': [{
							'ip address': '192.168.1.1',
							'mac address': 38-2c-4a-bf-d4-f8',
							}, {
							'ip address': '192.168.1.255',
							'mac address': 'ff-ff-ff-ff-ff-ff',
							}]
						},{
							'192.168.56.1': [{
							'ip address': '192.168.1.1',
							'mac address': 38-2c-4a-bf-d4-f8',
							}, {
							'ip address': '192.168.1.255',
							'mac address': 'ff-ff-ff-ff-ff-ff',
							}]
						}
						....
					]
			:rtype mac_addresses_nearest_gateways: list
		'''
		mac_addresses_nearest_gateways = []
		if sys.platform == 'win32':
			args = ['arp', '-a']
			output_arp_table = RouteTableManager().command_output(args).decode('cp866','ignore')
			tags = ['ip address', 'mac address']
			dict_elem = {}
			if output_arp_table:
				for elem in output_arp_table.split("\n"):
					if '---' in elem:
						key = 'Interface: ' + elem.strip().split(' ')[1]
						list_elem = []
					else:
						if re.match("^[0-9]", elem.strip()):
							list_elem.append(dict(zip(tags, elem.strip().split())))
							dict_elem.update({key : list_elem})
				mac_addresses_nearest_gateways.append(dict_elem)		
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			arp = open('/proc/net/arp', 'r')
			if arp:
				arp_table = [elem.strip().split() for elem in arp.read().split("\n")]
			tags = ['IP address', 'HW type', 'Flags', 'HW address', 'Mask', 'Device']
			for list_elem in arp_table [1:]:
				mac_addresses_nearest_gateways.append(dict(zip(tags, list_elem)))
		elif sys.platform == 'darwin':
			args = ['arp', '-all']
			output_arp_table = RouteTableManager().command_output(args).decode()
			if output_arp_table:
				arp_table = [elem.strip().split() for elem in output_arp_table.split("\n")]
			tags = ['Neighbor', 'Linklayer Address', 'Expire(O)', 'Expire(I)', 'Netif', 'Refs', 'Prbs']
			for list_elem in arp_table[1:]:
				mac_addresses_nearest_gateways.append(dict(zip(tags, list_elem)))
		
		return mac_addresses_nearest_gateways

class DiskSerialNumberManager():

	'''
		Метод для получения серийных номеров жестких дисков 
		В Windows используется метод computer.Win32_DiskDrive()
		В Linux используется информация из /dev/disk/by-id
		В Mac OS используется вывод команды: system_profiler SPHardwareDataType
		:return list_disk: список словарей в формате: "Model" : "Serial"
		:rtype list_disk: list
	'''

	def get_disk_serial_number(self):
		list_disk = []
		if sys.platform == 'win32':
			computer = wmi.WMI()
			for disk in computer.Win32_DiskDrive():
				list_disk.append({'Model' : disk.Model, 'Serial' : disk.SerialNumber.strip()})
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			args = 'ls /dev/disk/by-id'.split()
			output = RouteTableManager().command_output(args).decode().split()
			disks = []
			for elem in output:
				if 'ata' in elem or 'usb' in elem:
					disks.append(elem[4:])
			disks = list(filter(lambda x : 'part' not in x, disks))
			list_disk = []
			for elem in disks:
				index = elem.rfind('_')
				dict_disks = {
					'Model' : elem[:index],
					'Serial' : elem[index+1:]
				}
				list_disk.append(dict_disks)
		elif sys.platform == 'darwin':
			args = ['system_profiler', 'SPHardwareDataType']
			data = RouteTableManager().command_output(args).decode().split('\n')
			for elem in data:
				if 'Hardware' in elem:
					UUID = elem[elem.index(':')+1:]
			dict_disks = {
				'Hardware UUID' : UUID
			}
			list_disk.append(dict_disks)
		return list_disk


class OSManager:

	'''
		Класс для получения имени и версии ОС
	'''

	def get_os(self):

		'''
			Метод для получения имения и версии ОС
			Используется стандартная библиотека platform
			:return os_name: строка, содержащая имя и версию ОС
			:rtype os_name: str
			
		'''

		os_name = platform.platform() + ' ' + platform.architecture()[0]
		return os_name


class CPUManager:

	'''
		Класс для получения имени CPU
	'''

	def get_CPU(self):

		'''
			Метод для получения имени CPU
			Windows и Linux: используется сторонняя библиотека cpuinfo
			Mac OS: используется вывод команды sysctl -n machdep.cpu.brand_string
			:return CPU: строка, содержащая имя CPU
			:rtype CPU: str
		'''

		if sys.platform == 'win32':
			CPU = cpu.info[0]['ProcessorNameString']
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			CPU = cpu.info[0]['model name']
		elif sys.platform == 'darwin':
			args = ['sysctl', '-n', 'machdep.cpu.brand_string']
			CPU =  RouteTableManager().command_output(args).decode().strip()
		return CPU

class MotherboardManager:

	'''
		Класс для получения модели материнской платы
	'''

	def get_motherboard(self):

		'''
			Метод для получения модели материнской платы
			Windows: используется метод computer.Win32_BaseBoard()
			Linux: используется информация из /sys/devices/virtual/dmi/id/board
			Mac OS: используется вывод команды system_profiler SPHardwareDataType
			:return motherboard_info: словарь в формате: "vendor" : "name"
			:rtype motherboard_info: dict
		'''

		motherboard_info = {}
		if sys.platform == 'win32':
			computer = wmi.WMI()
			motherboard_info['vendor'] = computer.Win32_BaseBoard()[0].Manufacturer
			motherboard_info['name'] = computer.Win32_BaseBoard()[0].Product
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			args = 'cat /sys/devices/virtual/dmi/id/board_vendor'.split()
			vendor = RouteTableManager().command_output(args).decode().split('\n')[0]
			args = 'cat /sys/devices/virtual/dmi/id/board_name'.split()
			name = RouteTableManager().command_output(args).decode().split('\n')[0]
			args = 'cat /sys/devices/virtual/dmi/id/board_version'.split()
			version = RouteTableManager().command_output(args).decode().split('\n')[0]
			motherboard_info['vendor'] = vendor 
			motherboard_info['name'] = name
			motherboard_info['version'] = version
		elif sys.platform == 'darwin':
			args = ['system_profiler', 'SPHardwareDataType']
			data = RouteTableManager().command_output(args).decode().split('\n')
			for elem in data:
				if 'Model Name' in elem:
					model = elem[elem.index(':')+1:]
				if 'Serial' in elem:
					serial = elem[elem.index(':')+1:]
			motherboard_info['model'] = model
			motherboard_info['serial'] = serial


		return motherboard_info

class GPUManager:

	'''
		Класс для получения модели GPU
	'''

	def get_GPU(self):

		'''
			Метод для получения модели GPU
			Windows: используется метод computer.Win32_VideoController()
			Linux: используется информация из lspci
			Mac OS: используется вывод команды system_profiler SPDisplaysDataType
			:return gpu_info: словарь с моделями GPU
			:rtype gpu_info: dict
		'''

		gpu_info = []
		if sys.platform == 'win32':
			computer = wmi.WMI()
			video_info = computer.Win32_VideoController()
			for i in range(len(video_info)):
				gpu_info.append(video_info[i].Caption)
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			args = 'lspci'.split()
			data = RouteTableManager().command_output(args).decode().split('\n')
			for elem in data:
				if 'VGA' in elem:
					GPU = elem[elem.index(' ')+1:].split(':')[1]
			gpu_info.append(GPU)
		elif sys.platform == 'darwin':
			args = ['system_profiler', 'SPDisplaysDataType']
			data = RouteTableManager().command_output(args).decode().split('\n')
			for elem in data:
				if 'Type' in elem:
					Type = elem[elem.index(':')+1:]
				if 'VRAM' in elem:
					vram = elem[elem.index(':')+1:]
				if 'Device' in elem:
					device_id = elem[elem.index(':')+1:]
				if 'Vendor' in elem:
					vendor_id = elem[elem.index(':')+1:]
			dict_gpu = {
				'type' : Type,
				'VRAM' : vram,
				'Device id' : device_id,
				'Vendor id' : vendor_id
			}
			gpu_info.append(dict_gpu)
		
		return gpu_info

class RAMManager:

	'''
		Класс для получения информации об оперативной памяти
	'''

	def get_RAM(self):

		'''
			Метод для получения информации об оперативной памяти
			Windows: используется метод computer.Win32_PhysicalMemory()
			Linux: используется информация из /proc/meminfo
			Mac OS: используется вывод команды system_profiler SPHardwareDataType
			:return list_RAM: подробный список в Windows и кол-во ОЗУ в Linux и Mac OS
			:rtype list_RAM: list
		'''

		list_RAM = []
		if sys.platform == 'win32':
			computer = wmi.WMI()
			for item_RAM in computer.Win32_PhysicalMemory():
				amount_RAM = str(int(item_RAM.Capacity) / 1048576)
				tag_RAM = item_RAM.Tag
				name_RAM = item_RAM.PartNumber.strip()
				serial_number_RAM = item_RAM.SerialNumber
				list_RAM.append({
					'Tag RAM' : tag_RAM,
					'Name RAM' : name_RAM,
					'Amount RAM' : amount_RAM,
					'Serial Number RAM' : serial_number_RAM
				})
			
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			args = 'cat /proc/meminfo'.split()
			mem = RouteTableManager().command_output(args).decode().split('\n')[0]
			list_RAM.append({
					'Mem Total' : mem[mem.index(':')+1:],
				})
		elif sys.platform == 'darwin':
			args = ['system_profiler', 'SPHardwareDataType']
			data = RouteTableManager().command_output(args).decode().split('\n')
			for elem in data:
				if 'Memory' in elem:
					memory = elem[elem.index(':')+1:]
			list_RAM.append(
				{
					'Memory' : memory
				}
			)
		return list_RAM



