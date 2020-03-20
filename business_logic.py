# -*- coding: utf-8 -*-

#импорт всех менеджеров для сбора информации
from means import MacManager, CPUManager, OSManager, IPManager, RouteTableManager, MacNearestGateways, DiskSerialNumberManager, MotherboardManager, GPUManager, RAMManager

import logging #импорт модуля для сбора логов


class MainManager:

	'''
		Класс главного менеджера, который в ответ на запрос собирает данные в словарь и отправляет клиенту
	'''

	def __init__(self, mac_manager, 
					   cpu_manager, 
					   os_manager,
					   ip_manager,
					   route_table_manager,
					   mac_nearest_gateways,
					   disk_serial_number,
					   motherboard_manager,
					   gpu_manager,
					   ram_manager
				
				): 
		self.mac_manager = mac_manager
		self.cpu_manager = cpu_manager
		self.os_manager = os_manager
		self.ip_manager = ip_manager
		self.route_table_manager = route_table_manager
		self.mac_nearest_gateways = mac_nearest_gateways
		self.disk_serial_number = disk_serial_number
		self.motherboard_manager = motherboard_manager
		self.gpu_manager = gpu_manager
		self.ram_manager = ram_manager

	def mac_info(self):

		'''
			Метод для сбора информации о mac адресах
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success', 
					'data':self.mac_manager.get_mac()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)

		return to_be_returned

	def default_mac_info(self):

		'''
			Метод для сбора mac адреса интерфейса, с которого происходит выход в Интернет на данный момент 
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.mac_manager.get_default_mac()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)

		return to_be_returned

	def CPU_info(self):

		'''
			Метод для сбора информации о CPU
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':{'CPU' : self.cpu_manager.get_CPU()}
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)

		return to_be_returned

	def os_info(self):

		'''
			Метод для сбора наименования и версии ОС
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':{'OS' : self.os_manager.get_os()}
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def ip_info(self):

		'''
			Метод для сбора IP адресов со всех сетевых интерфейсов
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.ip_manager.get_ip_addresses()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned

	def ip_default_info(self):

		'''
			Метод для сбора IP адреса шлюза по умолчанию
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.ip_manager.get_ip_address_default_gateway()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def route_table_info(self):

		'''
			Метод для сбора информации о таблице маршрутизации
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.route_table_manager.get_route_table()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def mac_nearest_gateways_info(self):

		'''
			Метод для сбора информации о mac адресах ближайших шлюзов
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.mac_nearest_gateways.get_mac_addresses_nearest_gateways()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def disk_serial_number_info(self):

		'''
			Метод для сбора информации о серийных номерах жестких дисков 
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.disk_serial_number.get_disk_serial_number()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def motherboard_info(self):

		'''
			Метод для сбора информации о модели материнской платы 
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.motherboard_manager.get_motherboard()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def gpu_info(self):

		'''
			Метод для сбора информации о видеокарте 
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.gpu_manager.get_GPU()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
	
	def ram_info(self):

		'''
			Метод для сбора информации об оперативной памяти 
			:return to_be_returned: dict of data neede
			:rtype to_be_returned: dict
		'''

		try:
			to_be_returned = {
					'status': 'success',
					'data':self.ram_manager.get_RAM()
			}
		except Exception as msg:
			to_be_returned = {
					'status': 'failed',
					'data': {'reason' : msg}
			}
			logging.debug(msg)
			

		return to_be_returned
