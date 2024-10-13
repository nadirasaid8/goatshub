import os
import json
import random
import asyncio
from colorama import *
from urllib.parse import unquote
from aiohttp import ClientSession
from json.decoder import JSONDecodeError
from .agent import generate_random_user_agent
from .deeplchain import (log, read_config, countdown_timer,
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

        if not proxies:
            print("No proxies found in proxies.txt.")
            user_input = input("Do you want to continue without proxies? (y/n): ").strip().lower()
            if user_input == 'y':
                print(htm + "~" * 60)
                return []
            else:
                print(htm + "~" * 60)
                log(mrh + f"Exiting...")
                return True

        return proxies

    async def load_token(self, userid):
        if not os.path.exists("tokens.json"):
            with open("tokens.json", "w") as f:
                json.dump({}, f)
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        token = tokens.get(str(userid))
        if token:
            self.access_token = token
        return token

    async def save_token(self, userid, token):
        if not os.path.exists("tokens.json"):
            with open("tokens.json", "w") as f:
                json.dump({}, f)
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        tokens[str(userid)] = token
        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)

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
            await self.save_token(self.user_id, access_token)
            return True
        
    def get_auth_headers(self) -> dict:
        return {
            'Authorization': f"Bearer {self.access_token}",
            'origin': 'https://dev.goatsbot.xyz',
            'referer': 'https://dev.goatsbot.xyz/',
            'User-Agent': generate_random_user_agent()
        }
    
    async def user_data(self) -> dict:
        token_data = await self.load_token(self.user_id)
        if not token_data:
            if not await self.login():
                log("Login failed.")
                return {}
        try:
            async with self.http.get("https://api-me.goatsbot.xyz/users/me", headers=self.get_auth_headers()) as resp:
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

    async def fetch_and_complete_missions(self) -> bool:
        max_retries = 5
        retry_delay = 2 
        for attempt in range(max_retries):
            try:
                async with self.http.get(
                    "https://api-mission.goatsbot.xyz/missions/user",
                    headers=self.get_auth_headers()
                ) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  
                        continue 

                    if resp.status != 200:
                        log(f"Mission request failed with status code: {resp.status}")
                        return False
                    
                    resp_json = await resp.json()
                    if isinstance(resp_json, str) or resp_json.get("statusCode"):
                        log(f"Error getting missions: {resp_json.get('message', 'Unknown error')}")
                        return False

                    for category, missions in resp_json.items():
                        for mission in missions:
                            if not mission.get("status", True):
                                mission_data = {
                                    "id": mission.get("_id"),
                                    "name": mission.get("name"),
                                    "reward": mission.get("reward"),
                                }

                                async with self.http.post(
                                    f"https://dev-api.goatsbot.xyz/missions/action/{mission_data['id']}",
                                    headers=self.get_auth_headers()
                                ) as complete_resp:
                                    complete_resp_json = await complete_resp.json()
                                    if complete_resp_json.get("statusCode"):
                                        log(f"Error completing mission | {complete_resp_json['message']}")
                                        continue
                                    if complete_resp_json.get("status"):
                                        log(pth + f"{mission_data['name']} {hju}completed")
                                        log(hju + f"Success earned reward: {pth}{mission_data['reward']}")
                                        await countdown_timer(3)
                                    else:
                                        log(mrh + f"Mission {mission_data['name']} not finished")
                            else:
                                log(kng + f"No mission available to complete")
                    return True
            except Exception as e:
                log(f"Error fetching missions: {e}")
                return False

    async def watch(self, block_id: int, tg_id: int) -> bool:     
        watch_time = random.randint(16, 17)
        log(bru + f"Watching ads for {pth}{watch_time} {bru}seconds...")
        ad_url = f"https://api.adsgram.ai/adv?blockId={block_id}&tg_id={tg_id}&tg_platform=android&platform=Linux+aarch64&language=id"
        resp = await self.http.get(ad_url, headers=self.get_auth_headers())
        resp = self.decode_json(await resp.text())

        if resp.get("statusCode"):
            log(f"Error watching ad | {resp['message']}")
            return False

        await countdown_timer(watch_time)

        mission_id = "66db47e2ff88e4527783327e" 
        verify_url = f"https://dev-api.goatsbot.xyz/missions/action/{mission_id}"

        verify_resp = await self.http.post(verify_url, headers=self.get_auth_headers())
        verify_resp = self.decode_json(await verify_resp.text())

        if verify_resp.get("status") == "success":
            log(hju + f"Watching ads reward {pth}+200")
            return True
        else:
            log(mrh + "Ads verification failed.")
            return False

    async def checkin_user(self) -> dict:
        try:
            async with self.http.get(
                "https://api-checkin.goatsbot.xyz/checkin/user",
                headers=self.get_auth_headers()
            ) as resp:
                if resp.status != 200:
                    log(htm + f"Check-in request failed with status code: {resp.status}")
                    return False

                resp_json = self.decode_json(await resp.text())
                if "error" in resp_json:
                    log(f"Error decoding JSON: {resp_json['text']}")
                    return False
                if "result" not in resp_json:
                    log(f"Key 'result' not found in check-in response: {resp_json}")
                    return False
                for day in resp_json["result"]:
                    if not day.get("status"):
                        post_resp = await self.http.post(
                            f"https://api-checkin.goatsbot.xyz/checkin/action/{day['_id']}",
                            headers=self.get_auth_headers()
                        )
                        post_json = self.decode_json(await post_resp.text())
                        
                        if post_json.get("statusCode") == 400:
                            log(kng + "You have already checked in today")
                            return False
                        elif post_json.get("status"):
                            log(hju + f"Checked in for day {pth}{day['day']} {hju}| Reward: {pth}{day['reward']}")
                            return True
                        else:
                            log(mrh + "Failed to check in. Try again later.")
                            return False
        except Exception as e:
            log(f"Exception in checkin_user: {e}")
            return False

    async def spin(self, slot_machine_coin: int) -> bool:
        for _ in range(slot_machine_coin):
            try:
                async with self.http.post(
                    "https://api-slotmachine.goatsbot.xyz/slot-machine/spin",
                    headers=self.get_auth_headers()) as resp:
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