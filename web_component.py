# -*- coding: utf-8 -*-
import asyncio #для реализации асинхронной работы сервера 
import json #для работы с json объектами
import logging #импорт модуля для сбора логов
import websockets #модуль для создания websocket сервера
import signal #для остановки сервера в Linux через терминал
#импорт главного менеджера из бизнес-логики
from business_logic import MainManager
#импорт модуля для генерации объекта ssl_context для установления ssl соединения
from gen_ssl import generate_ssl

class Server:

	'''
		Класс для создания и запуска сервера
	'''

	def __init__(self, manager=None):
		self.main_manager = manager
		self.loop = asyncio.get_event_loop()
	


	async def send_hardware(self, websocket, path):

		'''
			Асинхронный метод для отправки информации об оборудовании клиенту
			:param websocket: сам вебсокет 
			:type websocket: <class 'websockets.server.WebSocketServerProtocol'>
			:param path: путь URL запроса
			:type path: str
		'''

		try:
			async for message in websocket:
				data = json.loads(message)
				if data['type'] == 'get' and data['action'] == 'mac_all':
					message = json.dumps(self.main_manager.mac_info())
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'default_mac':
					message = json.dumps(self.main_manager.default_mac_info())
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'cpu':
					message = json.dumps(self.main_manager.CPU_info())
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'os':
					message = json.dumps(self.main_manager.os_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'ip':
					message = json.dumps(self.main_manager.ip_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'ip_default':
					message = json.dumps(self.main_manager.ip_default_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'route_table':
					message = json.dumps(self.main_manager.route_table_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'mac_nearest_gateways':
					message = json.dumps(self.main_manager.mac_nearest_gateways_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'disk_serial':
					message = json.dumps(self.main_manager.disk_serial_number_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'motherboard':
					message = json.dumps(self.main_manager.motherboard_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'gpu':
					message = json.dumps(self.main_manager.gpu_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'get' and data['action'] == 'ram':
					message = json.dumps(self.main_manager.ram_info(), ensure_ascii=False)
					await websocket.send(message)
				elif data['type'] == 'post':
					message = json.dumps({'status': 'success'})
					await websocket.send(message)
		except Exception as msg:
			logging.debug(msg)
	
	async def serve(self, stop):

		'''
			Метод для запуска сервера
			:param stop: условие остановки
			:type stop: <class '_asyncio.Future'>
		'''

		async with websockets.serve(self.send_hardware, 'srv158026.hoster-test.ru', 8080, ssl=generate_ssl(self)):
			await stop
		

	def run_server_win(self):

		'''
			Метод для запуска сервера на Windows
			Необходим раздельный запуск для разных ОС из-за специфичности терминала и командной строки
			В данном случае остановка сервера возможна при запуске из консоли
		'''

		async def ticker(delay):
			while True:
				await asyncio.sleep(delay)

		stop = asyncio.Future()
		ticker_task = asyncio.ensure_future(ticker(1))  # Проверять Ctrl+C каждые 3 секунды
		try:
			self.loop.run_until_complete(asyncio.wait([
				self.serve(stop),
				ticker_task
			]))
		except KeyboardInterrupt:
			stop.set_result(None)
			ticker_task.cancel()
			self.loop.run_until_complete(asyncio.sleep(1))  # 5 секунд ждать завершения работы
		finally:
			self.loop.close()
			print('Server stop')

	
	def run_server_linux(self):

		'''
			Метод для запуска сервера на Linux/Darwin
			Необходим раздельный запуск для разных ОС из-за специфичности терминала и командной строки
			В данном случае остановка сервера возможна при запуске из консоли
		'''

		stop = asyncio.Future()
		self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
		self.loop.run_until_complete(self.serve(stop))


