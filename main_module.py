from web_component import Server
from business_logic import MainManager
from means import MacManager, CPUManager, OSManager, IPManager, RouteTableManager, MacNearestGateways, DiskSerialNumberManager, MotherboardManager, GPUManager, RAMManager

import sys 

import logging #logging module
from pathlib import *
import os


if sys.platform == 'win32':
	import winreg as wr
	system = 'win'
	logging.basicConfig(
	filename="agent_debug.log", 
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s"
	)

if sys.platform == 'linux2' or sys.platform == 'linux':
	system = 'linux'
	logging.basicConfig(
	filename='hw_agent.log.log',  
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s"
	)

if sys.platform == 'darwin':
	system = 'darwin'
	logging.basicConfig(
	filename='hw_agent.log.log',  
	level=logging.DEBUG,
	format="%(asctime)s:%(levelname)s:%(message)s"
	)

def add_to_startup_win():
	path_exe = os.path.abspath(sys.argv[0]) 
	key_my = wr.OpenKey(wr.HKEY_CURRENT_USER, 
	                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 
	                 0, wr.KEY_ALL_ACCESS)
	wr.SetValueEx(key_my, 'agent', 0, wr.REG_SZ, path_exe)
	wr.CloseKey(key_my)


def start():
	server = Server(MainManager(mac_manager=MacManager(), 
								cpu_manager=CPUManager(), 
								os_manager=OSManager(),
								ip_manager=IPManager(),
								route_table_manager = RouteTableManager(),
								mac_nearest_gateways = MacNearestGateways(),
								disk_serial_number = DiskSerialNumberManager(),
								motherboard_manager = MotherboardManager(),
								gpu_manager = GPUManager(),
								ram_manager = RAMManager()
			
								)
					)
	# if sys.platform == 'linux2' or sys.platform == 'linux':
	#  	server.run_server()
	#  	add_to_startup_linux()
	# elif sys.platform == 'win32':
	if system == 'linux' or system == 'darwin':
		try:
			print('Server running...')
			print('Press ctrl+C for stop server')
			server.run_server_linux()
		except KeyboardInterrupt:
			print('Server stop')
	elif system == 'win':
		'''
		Check value in registry for autostart
		'''
		key_my = wr.OpenKey(wr.HKEY_CURRENT_USER, 
	                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 
	                 0, wr.KEY_ALL_ACCESS)
		name_list_key = []
		try:
			i = 0
			while True:
				name_list_key.append(wr.EnumValue(key_my, i)[0])
				i += 1
		except WindowsError:
			pass
		if 'agent' in name_list_key:
			pass
		else:
			add_to_startup_win()
		print('Server running...')
		print('Press ctrl+C for stop server')
		server.run_server_win()


	


