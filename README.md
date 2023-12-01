<p align="center">
  <img height="400px" src="mezubu.jpg" />
  <br>
  <br>
  <br>
   Mezebu Botnet - A botnet controlled by a hidden service and designed to attack surface and darknet websites.
  
</p>
<br>
<p align="center">
  Installation
</p>
  1- git clone https://github.com/Heiden-Ichmanov/mezubu-botnet.git <br>
  2- cd mezubu-botnet <br>
  3- openssl req -x509 -sha256 -nodes -newkey rsa:4096 -keyout cert.key -out cert.pem<br>
    &nbsp&nbsp3.1- copy the cert.key and cert.pem files to the /server directory<br>
    &nbsp&nbsp3.2- copy the cert.pem file to the /client directory<br>
  4- <br>
    &nbsp&nbsp5.1 Server - pip3 install pysocks tk stem pillow python-vlc<br>
    &nbsp&nbsp5.2 Client  - pip3 install pysocks aiohttp aiohttp-socks<br>
  5- <br>
    &nbsp&nbsp6.1 Server - apt install python3-tk python3-stem python3-pil python3-pil.imagetk vlc pulseaudio<br>
    &nbsp&nbsp6.2 Client  - nothing <br>
  6- chmod 777 tor<br>
  7- chmod 777 server/tor<br>
  8- chmod 777 client/tor<br>
  <br><br>
<p align="center">
  Configuration
</p>
  1- ./tor --hash-password PUTTHETORPASSWORDHERE<br>
    &nbsp&nbsp1.1- add the hashed password in torcc file on line 4<br>
    &nbsp&nbsp1.2- add the password in main.py on line 17<br>
  2- python3 sha256-password-generator.py PUTYOURMEZUBUPASSWORDHERE<br>
    &nbsp&nbsp2.1- add the hashed password in main.py on line 18<br>
    &nbsp&nbsp2.2- add the hashed password in client.py on line 10<br>
  3- After the first launch you need to copy the hostname and add in client.py on line 15 <br>
<br>
<p align="center">
  Demonstration
</p>





https://github.com/Heiden-Ichmanov/mezubu-botnet/assets/142114701/17ee85d6-9051-4148-aa2f-a0d30a8dd1be

