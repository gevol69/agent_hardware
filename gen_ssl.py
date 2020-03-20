import ssl #модуль для генерирования объекта ssl_context
from cryptography.fernet import Fernet #модуль для расшифрования сертификата и приватных ключей
import tempfile #модуль для создания временных файлов и папок
import os #модуль для создания/удаления папок и файлов и для перемещения по директориям


def generate_ssl(self):

		'''
			Функция для генерации объекта ssl_context для установки ssl соединения между сервером и клиентом
			:return ssl_context: объект ssl_context
            :rtype ssl_context: <class 'ssl.SSLContext'>
		'''

		cipher_key = b'....'
		encrypted_cert_str = b'...'
		encrypted_key_str = b'....'
		encrypted_password = b'....'
		cipher = Fernet(cipher_key)

		'''
			Создаётся временная папка, в которой создаются сертификат и ключ, после использования всё подчищается
		'''

		cur_dir = os.getcwd()
		try:
			temp_dir = tempfile.mkdtemp()
			os.chdir(os.path.abspath(temp_dir))
			cert = open('test.eu.cer', 'w')
			cert.write(cipher.decrypt(encrypted_cert_str).decode())
			cert.close()
			key = open('test.eu.key', 'w')
			key.write(cipher.decrypt(encrypted_key_str).decode())
			key.close()
			ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			ssl_context.load_cert_chain(os.path.abspath('test.eu.cer'), os.path.abspath('test.eu.key'), password=cipher.decrypt(encrypted_password).decode())
		finally:
			os.remove('test.eu.cer')
			os.remove('test.eu.key')
			os.chdir(cur_dir)
			os.rmdir(temp_dir)
		return ssl_context

