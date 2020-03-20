# AgentHardware - руководство пользователя

Агент выполняет функцию сбора информации с компьютера, которая позволит в дальнейшем привязать пользователя к этому компьютеру. 
Программа не имеет графического интерфейса, запускается автоматически после установки и работает в фоновом режиме, а также автоматически запускается после перезагрузки ОС.

## Установка

AgentHardware - кроссплатформенная программа, которая работает на Windows, Mac OS X и GNU / Linux.

```
Для корректной работы программы рекомендуется не менять директорию установки по умолчанию.
```

### Windows

Для установки под ОС Windows, скачайте последнюю версию AgentHardware в формате exe. Запустите файл agent-1.0-1.x86_64.exe и следуйте инструкциям по установке.


### Mac OS X

Для установки под Mac OS X, скачайте последнюю версию AgentHardware в формате pkg. Запустите файл agent-1.0-1.x86_64.pkg и следуйте инструкциям по установке.

### Ubuntu

Для установки под ОС Ubuntu, скачайте последнюю версию AgentHardware в формате deb. Запустить файл agent-1.0-1.x86_64.deb можно двумя способами:
* Дважды кликнуть по нему и следовать инструкциям по установке.
* Открыть терминал, перейти в директорию где лежит deb пакет и ввести следующую команду:
```
sudo dpkg -i agent-1.0-1.x86_64.deb
```
### CentOS

Для установки под ОС CentOS, скачайте последнюю версию AgentHardware. Откройте терминал, перейдите в директорию, где лежит файл agent-1.0-1.x86_64.pkg и введите следующую команду:
```
sudo yum install agent-1.0-1.x86_64.pkg
```
# AgentHardware - руководство для разработчиков
## Концепция агента
Агент предназначен для усиления аутентификации пользователя. Концепция агента основана на формировании отпечатка физического устройства, состоящего из признаков этого устройства в окружении операционной системы и позволяет усовершенствовать любой из современных подходов аутентификации. 
Агент, являясь частью более сложной системы информационной безопасности, должен выполнять функцию сбора информации с компьютера, которая позволит  привязать пользователя к этому компьютеру. В дальнейшем, опираясь на историю входов пользователей в систему, будет производится проверка: соответствует ли устройство, с которого на данный момент был осуществлен вход, устройствам зарегистрированных во время предыдущих входов. И на основании этого у системы будет возможность повысить уровень доверия к пользователю.

## Функционал агента
Функционал агента включает в себя:
* сбор информации об устройстве;
* ответы на запросы из браузера;
* защищённую коммуникацию между браузером и агентом;
* проверку добавлен ли он в автозапуск;
* работу в фоновом режиме;
* поддержку: Windows, Linux (Ubuntu/Cent OS), Mac OS;
* поддержку всех современных браузеров;
* сокрытие важной информации в исходном коде;
* защиту от декомпиляции исходного кода;

## Используемые технологии
Агент написан на языке Python 3.6.

Сторонние используемые библиотеки: 
| Бибилотека       | Версия             | 
| ------------- |:------------------:| 
| [cryptography](https://pypi.org/project/cryptography/) | 2.6.1    | 
| [Cython](https://cython.org/)   | 0.29.6 |   
| [netifaces](https://pypi.org/project/netifaces/)    | 0.10.9         |
| [PyInstaller](https://www.pyinstaller.org/)    | 3.4        |
| [pywin32](https://pypi.org/project/pywin32/)   | 224       |
| [websockets](https://pypi.org/project/pywin32/)   | 7.0       |
| [WMI](https://pypi.org/project/WMI/) | 1.4.9        |


## Поддерживаемые платформы
Агент поддерживает работу таких ОС как: Windows, Linux (Ubuntu/Cent OS), Mac OS

## Структура приложения
Для того чтобы поддерживать исходный код и вносить измененя было проще, было принято решение организовать следующую структуру приложения, состоящую из 3х главных компонентов:

* Веб-компонент (web_component) - сервер, который принимает запросы от скрипта в браузере и перенаправляет его на нужную функцию.
* Бизнес-логика (business_logic) - самый независимый компонент в этой структуре. Исходный код этого компонента не должен меняться и предназначен он исключительно для решения поставленных задач.
* Средства (means) - содержит инструменты для получения информации о системе. 

Подробнее о каждом компоненте.
### Web_component
Для создания сервера используется библиотека [websockets](https://pypi.org/project/pywin32/) 

Для отправки информации об оборудовании скрипту в браузере используется следующий метод:

```
	async def send_hardware(self, websocket, path):

		'''
			Асинхронный метод для отправки информации об оборудовании клиенту
			:param websocket: сам вебсокет 
			:param path: путь URL запроса
		'''
		try:
			async for message in websocket:
				data = json.loads(message)
				if data['type'] == 'get' and data['action'] == 'mac_all':
					message = json.dumps(self.main_manager.mac_info())
					await websocket.send(message)
		except Exception as msg:
			logging.debug(msg)
	
```
Для непосредственного запуска сервера используется метод serve:
```
async def serve(self, stop):

		'''
			Метод для запуска сервера
			:param stop: условие остановки
		'''

		async with websockets.serve(self.send_hardware, 'srv158026.hoster-test.ru', 8080, ssl=generate_ssl(self)):
			await stop
```
SSL соединение между сервером и клиентом осуществляется с помощью передачи ssl_context в качестве параметра методу websockets.serve(). Более подробно о коммуникации браузера и агента ниже.
### Business_logic
Этот компонент включает в себя класс MainManager,  который в ответ на запрос браузера, собирает данные в словарь и отправляет клиенту.

Например, формирование ответа клиенту в виде словаря, содержащий mac адреса, выглядит следующим образом:
```
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
```
### Means
Компонент включает в себя средства для получения информации об устройстве. 

Для сбора различной информации о сетевых интерфейсах используется кроссплатформенная библеотека [netifaces](https://pypi.org/project/netifaces/)
Например, сбор информации о mac адресах в Linux происходит следующим образом:
```
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
```
Для реализации корректного кроссплатформенного решения, которое позволит получить модель процессора используется сторонняя библиотека cpuinfo.
```
def get_CPU(self):
		if sys.platform == 'win32':
			CPU = cpu.info[0]['ProcessorNameString']
		elif sys.platform == 'linux2' or sys.platform == 'linux':
			CPU = cpu.info[0]['model name']
		return CPU
```
Для получения информации о компонентах устройства, используется библиотека [WMI](https://pypi.org/project/WMI/) (Windows) и манипуляции с командной строкой в Linux и Mac OS с помощью встроенного модуля subprocess. Например:
```
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
```
## Защищенное соединение между браузером и агентом
SSL нужен только для того, чтобы сделать запрос из браузера, если сайт был загружен с использованием ssl-соединения. В противном случае, браузер нам просто не даст этого сделать. Никакой необходимости защищать трафик нет, т.к. он не выходит за пределы локального хоста.

Для тестирования используется домен srv158026.hoster-test.ru и порт 8080.
На тестовый домен был выпущен Let's Encrypt сертификат. Этот сертификат и ключ используются для установки SSL-соединения.
Перед запуском сервера необходимо добавить в файл hosts следующую строку:
```
127.0.0.1       srv158026.hoster-test.ru
```

Для установки SSL-соединения между клиентом и сервером, существует модуль gen_ssl, который создаёт объект ssl_context, использующийся в дальнейшем для создания вебсокета в модуле web_component.
```
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(os.path.abspath('test.eu.cer'),                                           os.path.abspath('test.eu.key'),                                           password=cipher.decrypt(encrypted_password).decode())
```
Так как объект ssl_context может принимать сертификат и приватный ключ в виде файла, а в исходном коде, они лежат в виде строки, был реализовано следующее решение:
```
'''
    Создаётся временная папка, в которой создаются сертификат и ключ (расшифровывается содержимое переменных и записывается в файлы), после создания ssl_context, всё подчищается.
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
```


## Сокрытие важной информации в исходном коде
Сертификаты и приватные ключи, которые необходимы, чтобы установить SSL-соединение, скрыты в исходном коде в модуле gen_ssl путем шифрования. После получения сертификата и ключа на тестовый домен через Let's Encrypt, они были зашифрованы, используя симметричное шифрование Fernet из сторонней библиотеки [cryptography](https://pypi.org/project/cryptography/) 
```
from cryptography.fernet import Fernet
 
cipher_key = Fernet.generate_key()
print(cipher_key)

cipher = Fernet(cipher_key)

cert_str = str.encode(open('cert.txt').read())
key_str = str.encode(open('enkey.txt').read())
password = str.encode('localhost')

encrypted_cert_str = cipher.encrypt(cert_str)
encrypted_key_str = cipher.encrypt(key_str)
encrypted_password = cipher.encrypt(password)
```
В модуле gen_ssl подобная важная информация хранится в следующем виде:
```
cipher_key = b'Vvucy9QN5UR...'
encrypted_cert_str = b'gAAAAABcnRX-AdKNv4Mzy...'
encrypted_key_str = b'gAAAAABcnRX-9Au1hB6xoo7a9VADOyV...'
encrypted_password = b'gAAAAABcnRX-x_tGA9uUmILAO...'
```
## Техники автозапуска

### Windows

Во время каждого запуска программы, скрипт проверяет добавлено ли значение в соответствующую ветку реестра (SOFTWARE\Microsoft\Windows\CurrentVersion\Run). 
Для манипуляции с реестром используется стандартная библиотека [winreg](https://docs.python.org/3/library/winreg.html).
```
import winreg as wr
'''
Проверка лежащего в реестрt значения
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
```
Добавление в реестр нового значения производится с помощью функции add_to_startup_win()
```
#добавление в реестр windows
def add_to_startup_win():
	path_exe = os.path.abspath(sys.argv[0]) 
	key_my = wr.OpenKey(wr.HKEY_CURRENT_USER, 
	                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 
	                 0, wr.KEY_ALL_ACCESS)
	wr.SetValueEx(key_my, 'agent', 0, wr.REG_SZ, path_exe)
	wr.CloseKey(key_my)
```
### Ubuntu/Cent OS

В ОС Ubuntu/Cent OS автозапуск агента осуществлён в виде сервиса. После установки программы в директорию \lib\systemd\system\ копируется файл agent.service, который имеет следующее содержимое:
```
[Unit]
Description=Agent for IC Fraud
After=multi-user.target

[Service]
Type=forking
PIDFile=/run/agent.pid
ExecStart=/usr/bin/agent
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID

[Install]
WantedBy=multi-user.target
```
Старт сервиса производится выполнением команд после установки:
```
sudo systemctl daemon-reload
sudo systemctl enable agent.service
sudo systemctl start  agent.service &
```
### Mac OS X

В Mac OS X автозапуск оформлен в виде сервиса. После установки агента выполняется скрипт postinst, который в директории /Library/LaunchDaemons/ создаёт файл с расширением .plist. Этот файл включает в себя:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>Label</key>
        <string>'$IDENTIFIER'</string>
        <key>ProgramArguments</key>
        <array>
	    <string>'/Applications/agent.app/Contents/MacOS/main'</string>
       </array>
       <key>RunAtLoad</key>
	<true/>
</dict>
</plist>
```
Старт сервиса производится выполнением команды после установки:
```
sudo launchctl load "$LAUNCH_DAEMON_PLIST"
```

## Работа в фоновом режиме
Работа в фоновом режиме на всех платформах осуществляется за счет того, что в web_component запускается асинхронный вебсокет сервер в бесконечном цикле. Например:
```
def run_server_linux(self):
    stop = asyncio.Future()
    self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    self.loop.run_until_complete(self.serve(stop))
```

## Компиляция исходного кода в один исполняемый файл
Для компиляции используется библиотека [PyInstaller](https://www.pyinstaller.org/). После установки PyInstaller, необходимо перейти в директорию с исходным кодом в командной строке и ввести следующую команду:
```
pyinstaller main.py --onefile --noconsole
```
Флаг --noconsole говорит о том, что консоль при запуске не будет отображаться.
Таким образом, Pyinstaller автоматически собирает весь исходный код и все зависимости, необходимые для запуска программы в один исполняемый файл.

## Защита от декомпиляции исходного кода
Так как в исходном коде сокрыта важная информация (сертификаты и приватные ключи) и обычный исполняемый файл, скомпилированный в pyinstaller, можно распаковать, декомпилировать и получить исходный код в открытом виде, была реализована компиляция исходного кода в библиотеки под разные платформы с помощью [Cython](https://cython.org/)
### Windows
После установки Cython, необходимо создать файл compile.py со следующим содержимым:
```
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("business_logic", ["business_logic.py"]),
    Extension("cpuinfo", ["cpuinfo.py"]),
    Extension("main_module", ["main_module.py"]),
    Extension("means", ["means.py"]),
    Extension("web_component", ["web_component.py"])
    ]

setup(
    name = 'Agent',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    language_level = 3
)
```
Далее нужно открыть командую строку и выполнить команду:

```
python compile.py build_ext --inplace
```
Рядом с каждым .py файлом будут созданы .pyd библиотеки, который в дальнейшем, можно использовать для компиляции с помощью pyinstaller.
Аналогично и с другими ОС (Ubuntu/CentOS/Mac OS) только вместо .pyd файлов будут созданы .so файлы соответственно.

## Создание инсталляторов для каждой платформы

### Windows
Для создание инсталлятора под Windows была использована программа  [Inno Setup](http://www.jrsoftware.org/isinfo.php)
После компиляции этого скрипта в Inno Setup, создаётся инсталлятор в виде exe файла.
```
;------------------------------------------------------------------------------
;
;       Agent for IC Fraud
;       (c) maisvendoo, 15.04.2015
;
;------------------------------------------------------------------------------

;------------------------------------------------------------------------------
;   Определяем некоторые константы
;------------------------------------------------------------------------------

; Имя приложения
#define   Name       "Agent"
; Версия приложения
#define   Version    "0.0.1"
; Фирма-разработчик
#define   Publisher  "Gevol"
; Сафт фирмы разработчика
#define   URL        "http://www.frodex.ru"
; Имя исполняемого модуля
#define   ExeName    "agent.exe"

;------------------------------------------------------------------------------
;   Параметры установки
;------------------------------------------------------------------------------
[Setup]

; Уникальный идентификатор приложения, 
;сгенерированный через Tools -> Generate GUID
AppId={{993BF1EA-8291-4A22-A9D1-93AAC98E7548}

; Прочая информация, отображаемая при установке
AppName={#Name}
AppVersion={#Version}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}

; Путь установки по-умолчанию
DefaultDirName={pf}\{#Name}
; Имя группы в меню "Пуск"
DefaultGroupName={#Name}

; Каталог, куда будет записан собранный setup и имя исполняемого файла
OutputDir=C:\Users\Влад\Desktop\agent
OutputBaseFileName=agent

; Файл иконки
; SetupIconFile=E:\work\Mirami\Mirami\icon.ico

; Параметры сжатия
Compression=lzma
SolidCompression=yes

;------------------------------------------------------------------------------
;   Устанавливаем языки для процесса установки
;------------------------------------------------------------------------------
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; 
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl";

;------------------------------------------------------------------------------
;   Файлы, которые надо включить в пакет установщика
;------------------------------------------------------------------------------
[Files]

; Исполняемый файл
Source: "C:\Users\Влад\Desktop\frodex\current_version\agent\dist\agent.exe"; DestDir: "{app}"; Flags: ignoreversion

;------------------------------------------------------------------------------
;   Секция кода включенная из отдельного файла
;------------------------------------------------------------------------------
[Code]

[Tasks]
Name: StartAfterInstall; Description: Запустить агент после установки

[Run]
;------------------------------------------------------------------------------
;   Секция запуска после инсталляции
;------------------------------------------------------------------------------
Filename: "{app}\{#ExeName}"; Flags: nowait postinstall skipifsilent; Tasks: StartAfterInstall 
```
### Ubuntu 
В Ubuntu инсталлятор оформляется в виде .deb пакета.
Сначала в директории agent необходимо создать следующую структуру папок:
```
~/agent
|-- DEBIAN
|-- lib/systemd/system
|-- usr/bin
```

В директорию agent/DEBIAN помещаются 4 файла:
```
changelog
control
postinst
prerm
```
Содержимое changelog (история изменений):
```
agent (1.0-1) stable; urgency=medium

* Testing.

-- <frodex.ru> Sun, 01 Apr 2019 00:11:46 +0300

```
Содержимое control (центральный файл пакета, описывающего все основные свойства.):
```
Package:      agent
Version:      1.0-2019.04.02
Maintainer:   Maintainer <frodex.ru>
Architecture: all
Section:      web
Description:  Agent for IC Fraud
Depends:      python3
```
Содержимое postinst (скрипт, который выполняется сразу после установки пакета):
```
#!/bin/bash
sudo touch /var/log/hw_agent.log
sudo chmod 777  /var/log/hw_agent.log
sudo systemctl daemon-reload
sudo systemctl enable agent.service
sudo systemctl start  agent.service &
exit 0 
```
Содержимое prerm (скрипт, который выполняется непосредственно перед удалением пакета):
```
#!/bin/bash
sudo systemctl stop  agent.service
sudo systemctl disable  agent.service
sudo systemctl daemon-reload
sudo rm /var/log/hw_agent.log
exit 0 
```
В директории agent/usr/bin должен лежать исполняемый файл программы, скомпилированный в Pyinstaller.
В директорию agent/lib/systemd/system помещается .service файл, предназначенный для запуска агента в виде сервиса.

После проделанных манипуляций необходимо выйти в папку, из которой будет видно корневую папку проекта и выполнить команду:
```
dpkg-deb --build agent
```
Будет создан пакет с расширением .deb
### Cent OS
В CentOS инсталлятор оформляется в виде .rpm пакета.
Сначала в директории rpmbuild необходимо создать следующую структуру папок:
```
~/rpmbuild
|-- BUILD
|-- BUILDROOT
|-- RPMS
|-- SOURCES
|-- SPECS
`-- SRPMS
```
В директории rpmbuild/SOURCES должен лежать исполняемый файл программы, скомпилированный в Pyinstaller и .service файл, предназначенный для запуска агента в виде сервиса

В директорию rpmbuild/SPECS помещается .spec файл - самый главный файл rpm-пакета, со следующим содержимым:
```
Name: agent
Version: 1.0
Release: 1
Summary: Agent for IC Fraud
Group: Applications/Productivity
License: GPL
Source0: agent
Source1: agent.service
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
Agent for IC Fraud.

%build

%install
install -D  %{SOURCE0} $RPM_BUILD_ROOT/usr/bin/agent
install -D %{SOURCE1} $RPM_BUILD_ROOT/lib/systemd/system/agent.service

%files
%defattr(-,root,root)
/usr/bin/agent
/lib/systemd/system/agent.service


%post
sudo touch /var/log/hw_agent.log
sudo chmod 777  /var/log/hw_agent.log
sudo systemctl daemon-reload
sudo systemctl enable agent.service
sudo systemctl start  agent.service &

%preun
sudo systemctl stop  agent.service
sudo systemctl disable  agent.service
sudo systemctl daemon-reload
sudo rm /var/log/hw_agent.log

%clean
rm -rf $RPM_BUILD_ROOT
```

После проделанных манипуляций необходимо перейти в директорию rpmbuild/SPECS и выполнить команду:
```
rpmbuild -bb agent.spec
```
Будет создан пакет с расширением .rpm в директории rpmbuild/RPMS/x86_64
### Mac OS X
Для создания установочных пакетов в Mac OS существует программа [Packages](http://s.sudre.free.fr/Software/Packages/about.html)
В этой программе с понятным интерфейсом нужно положить скомпилированный в pyinstaller файл в Applications. Также необходимо указать путь до скрипта postinst, который имеет следующее содержимое:
```
#!/bin/bash

# Script identifier (same as package identifier).
IDENTIFIER=com.frodex.agent


LAUNCH_DAEMON_PLIST="/Library/LaunchDaemons/$IDENTIFIER.plist"

# Write LaunchDaemon plist file.
sudo echo '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>Label</key>
        <string>'$IDENTIFIER'</string>
        <key>ProgramArguments</key>
        <array>
	    <string>'/Applications/agent.app/Contents/MacOS/main'</string>
       </array>
       <key>RunAtLoad</key>
	<true/>
</dict>
</plist>' > "$LAUNCH_DAEMON_PLIST"


sudo touch /var/log/hw_agent.log
sudo chmod 777  /var/log/hw_agent.log
sudo chown root:wheel /Library/LaunchDaemons/$IDENTIFIER.plist
sudo chmod 755 /Library/LaunchDaemons/$IDENTIFIER.plist

# Load the new LaunchDaemon.
sudo launchctl load "$LAUNCH_DAEMON_PLIST"

exit 0
``` 
Сборка проекта осуществляется командой Build.
Будет создан пакет с расширением .pkg

