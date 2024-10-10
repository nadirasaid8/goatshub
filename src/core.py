import os
import json
import random
import asyncio
from colorama import *
from urllib.parse import unquote
from json.decoder import JSONDecodeError
from aiohttp import ClientSession
from src.deeplchain import (log, read_config, countdown_timer,
                        hju, mrh, htm, kng, bru, pth)

init(autoreset=True)
config = read_config()

class GoatsBot:
    def __init__(self, tg_auth_data: str, proxy: dict = None) -> None:
        self.proxy = proxy
        self.http = self.create_session()
        self.auth_data = tg_auth_data
        self.access_token = None 
        self.access_token_expiry = 0
        userdata = self.extract_user_data(tg_auth_data)
        self.user_id = userdata.get("id")

    def create_session(self) -> ClientSession:
        return ClientSession()

    def get_proxy_url(self) -> str:
        """Returns the proxy URL in the format http://username:password@host:port"""
        if self.proxy:
            return f"http://{self.proxy['username']}:{self.proxy['password']}@{self.proxy['host']}:{self.proxy['port']}"
        return None

    @staticmethod
    def extract_user_data(auth_data: str) -> dict:
        try:
            return json.loads(unquote(auth_data).split("user=")[1].split("&auth")[0])
        except (IndexError, JSONDecodeError):
            return {}

    @staticmethod
    def decode_json(text: str) -> dict:
        try:
            return json.loads(text)
        except JSONDecodeError:
            return {"error": "Error decoding to JSON", "text": text}

    @staticmethod
    def get_proxies() -> list:
        proxies = []
        try:
            with open("proxies.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        username, password_host = line.strip().split(':', 1)
                        password, host_port = password_host.split('@')
                        host, port = host_port.split(':')
                        proxies.append({
                            "username": username,
                            "password": password,
                            "host": host,
                            "port": port
                        })
        except FileNotFoundError:
            print("Proxies file not found!")
        return proxies

    async def login(self) -> bool:
        proxy_url = self.get_proxy_url()
        headers = {
            "Rawdata": self.auth_data,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        async with self.http.post(
            "https://dev-api.goatsbot.xyz/auth/login",
            data={},
            headers=headers,
            proxy=proxy_url
        ) as resp:
            resp_text = await resp.text()
            try:
                resp_json = self.decode_json(resp_text)
            except Exception as e:
                log(f"Error decoding login response: {e}")
                return False

            if resp_json.get("statusCode"):
                log(f"Error while logging in | {resp_json['message']}")
                return False

            access_token = resp_json["tokens"]["access"]["token"]
            self.access_token = access_token
            self.http.headers["Authorization"] = f"Bearer {access_token}"
            await self.save_local_token(self.user_id, access_token)
            return True

    async def user_data(self) -> dict:
        token_data = await self.get_local_token(self.user_id)
        if not token_data:
            if not await self.login():
                log("Login failed.")
                return {}

        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            async with self.http.get("https://api-me.goatsbot.xyz/users/me", headers=headers) as resp:
                content_type = resp.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    resp_text = await resp.text()
                    log(f"Unexpected content type: {content_type}, Response text: {resp_text}")
                    return {}

                resp_json = await resp.json()
                if resp_json.get("statusCode"):
                    log(f"Error getting profile data | {resp_json['message']}")
                    return {}

                return resp_json

        except Exception as e:
            log(f"Exception while getting user data: {e}")
            return {}

    async def get_local_token(self, userid):
        if not os.path.exists("tokens.json"):
            with open("tokens.json", "w") as f:
                json.dump({}, f)
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        token = tokens.get(str(userid))
        if token:
            self.access_token = token
        return token

    async def save_local_token(self, userid, token):
        if not os.path.exists("tokens.json"):
            with open("tokens.json", "w") as f:
                json.dump({}, f)
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        tokens[str(userid)] = token
        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)

    async def get_missions(self) -> list:
        try:
            headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with self.http.get(
                "https://api-mission.goatsbot.xyz/missions/user",
                headers=headers
            ) as resp:
                if resp.status == 403:
                    log("Mission request failed with status code: 403")
                    return False
                resp_json = self.decode_json(await resp.text())
                if resp_json.get("statusCode"):
                    log(f"Error getting missions {resp_json['message']}")
                    return False

                result = []
                for category in resp_json:
                    for mission in resp_json[category]:
                        if not mission.get("status", True):
                            result.append({
                                "id": mission.get("_id"),
                                "name": mission.get("name"),
                                "reward": mission.get("reward"),
                            })
                return result
        except Exception as e:
            log(f"Error fetching missions: {e}")
            return False

    async def watch(self, block_id: int, tg_id: int) -> bool:
        headers = {
        'Authorization': f"Bearer {self.access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }        
        watch_time = random.randint(16, 17)
        log(bru + f"Watching ads for {pth}{watch_time} {bru}seconds...")
        ad_url = f"https://api.adsgram.ai/adv?blockId={block_id}&tg_id={tg_id}&tg_platform=android&platform=Linux+aarch64&language=id"
        resp = await self.http.get(ad_url, headers=headers)
        resp = self.decode_json(await resp.text())

        if resp.get("statusCode"):
            log(f"Error watching ad | {resp['message']}")
            return False

        await countdown_timer(watch_time)

        mission_id = "66db47e2ff88e4527783327e" 
        verify_url = f"https://dev-api.goatsbot.xyz/missions/action/{mission_id}"

        verify_resp = await self.http.post(verify_url, headers=headers)
        verify_resp = self.decode_json(await verify_resp.text())

        if verify_resp.get("status") == "success":
            log(hju + f"Watching ads reward {pth}+500")
            return True
        else:
            log(mrh + "Ads verification failed.")
            return False

    async def complete_mission(self, mission_data: dict) -> bool:
        headers = {
        'Authorization': f"Bearer {self.access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = await self.http.post(
            f"https://dev-api.goatsbot.xyz/missions/action/{mission_data['id']}", headers=headers
        )
        resp = self.decode_json(await resp.text())
        if resp.get("statusCode"):
            log(f"Error completing mission | {resp['message']}")
            return False
        else:
            if resp.get("status"):
                log(pth + f"{mission_data['name']} {hju}completed")
                log(hju + f"Success earned reward: {pth}{mission_data['reward']}")
                return True
            else:
                log(mrh + f"Mission {mission_data['name']} not fininshed")
                return False

    async def get_checkin(self) -> dict:
        headers = {
        'Authorization': f"Bearer {self.access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }        
        try:
            async with self.http.get(f"https://api-checkin.goatsbot.xyz/checkin/user", headers=headers) as resp:
                if resp.status != 200:
                    log(htm + f"Check-in request failed with status code: {resp.status}")
                    return False
                
                resp_text = await resp.text()
                resp_json = self.decode_json(resp_text)
                if "error" in resp_json:
                    log(f"Error decoding JSON: {resp_json['text']}")
                    return False
                if "result" not in resp_json:
                    log(f"Key 'result' not found in check-in response: {resp_json}")
                    return False
                for day in resp_json["result"]:
                    if not day.get("status"):
                        return day
        except Exception as e:
            log(f"Exception in get_checkin: {e}")
            return False

    async def checkin(self, checkin_data: dict) -> dict:
        headers = {
        'Authorization': f"Bearer {self.access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = await self.http.post(f"https://api-checkin.goatsbot.xyz/checkin/action/{checkin_data['_id']}", headers=headers)
        resp = self.decode_json(await resp.text())
        if resp.get("statusCode") == 400:
            log(kng + f"You have already checkin today")
            return False
        elif resp.get("status"):
            log(hju + f"Checked in for day {pth}{checkin_data['day']} {hju}| Reward: {pth}{checkin_data['reward']}")
            return True
        else:
            log(mrh + f"Failed to checkin. Try again later.")
            return False

    async def spin(self, slot_machine_coin: int) -> bool:
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for _ in range(slot_machine_coin):
            try:
                async with self.http.post(
                    "https://api-slotmachine.goatsbot.xyz/slot-machine/spin",headers=headers) as resp:
                    if resp.status != 201:
                        log(f"Spin request failed with status code: {resp.status}")
                        return False

                    resp_json = self.decode_json(await resp.text())
                    if resp_json.get("statusCode"):
                        log(f"Error during spin | {resp_json['message']}")
                        return False

                    result_list = resp_json['result']['result']
                    reward = resp_json['result']['reward']
                    unit = resp_json['result']['unit']
                    log(hju + f"Spin: {pth}{result_list} {hju}| Reward: {pth}{reward} {hju}{unit}")
                    await asyncio.sleep(0.5)
            
            except Exception as e:
                log(f"Exception during spin: {e}")
                return False
        return True

    async def run(self):

        account_delay = config.get('account_delay', 5)
        user_data = await self.user_data()
        if user_data:
            log(hju + f"Username: {pth}{user_data.get('user_name')}")
            log(hju + f"Balance: {pth}{user_data.get('balance'):,.0f} ")
            log(hju + f"Telegram Age: {pth}{user_data.get('age')} years")

        checkin_data = await self.get_checkin()
        if checkin_data:
            await self.checkin(checkin_data)
            
        missions_to_complete = await self.get_missions()
        if missions_to_complete:
            for mission_data in missions_to_complete:
                await self.complete_mission(mission_data)
                await asyncio.sleep(1.5)
                continue
        else:
            log(kng + "No missions available to complete")
            
        slot_machine_coin = user_data.get('slot_machine_coin', 0)
        if slot_machine_coin > 0:
            log(pth + f"{slot_machine_coin} {hju}slot machine Coins available")
            await self.spin(slot_machine_coin)
        else:
            log(kng + f"No slot machine coins available.")

        block_id = 2373
        await self.watch(block_id, self.user_id)
        await self.http.close()

        print(pth + f"~" * 60)
        await countdown_timer(account_delay)

async def main():
    loop = config.get('looping', 3800)
    proxies_enabled = config.get('use_proxies', False)
    proxies = GoatsBot.get_proxies() if proxies_enabled else []
    
    if proxies_enabled and proxies:
        proxy = proxies[0] 
        if proxy:
            if isinstance(proxy, dict): 
                host = proxy.get('host', 'unknown_host')
                port = proxy.get('port', 'unknown_port')
                host_port = f"{host}:{port}"
            else:
                proxy_url = proxy
                if '@' in proxy_url:
                    host_port = proxy_url.split('@')[-1]
                else:
                    host_port = proxy_url
        else:
            host_port = 'No proxy'
    else:
        host_port = 'No proxy'

    while True:
        with open("data.txt", "r", encoding="utf-8") as file:
            accounts = [line.strip() for line in file if line.strip()]
        for i, auth_data in enumerate(accounts, start=1):
            log(bru + f"Processing Account: {pth}{i}/{len(accounts)}")
            log(hju + f"Using proxy: {pth}{host_port}")
            log(pth + f"~" * 38)

            proxy = proxies[i % len(proxies)] if proxies_enabled and proxies else None

            bot = GoatsBot(auth_data.strip(), proxy=proxy)
            await bot.run()

        await countdown_timer(loop)

