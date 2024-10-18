import sys
import time
import json
import argparse
from colorama import *
from .core import GoatsBot
from . import *


config = read_config()

def get_status(status):
    return hju + "ON" + reset if status else mrh + "OFF" + reset

def save_setup(setup_name, setup_data):
    with open(f'src/config/{setup_name}.json', 'w') as file:
        json.dump(setup_data, file, indent=4)
    awak()
    print(hju + f" Setup saved on {kng}setup{pth}/{setup_name}.json")
    with open(f'src/config/{setup_name}.json', 'r') as file:
        setup_content = json.load(file)
        print(f"\n{json.dumps(setup_content, indent=4)}\n")
    print(hju + f" Quick start : {pth}python main.py {htm}--setup {pth}{setup_name}")
    input(f" Press Enter to continue...")

def load_setup_from_file(setup_file):
    with open(setup_file, 'r') as file:
        setup = json.load(file)
    return setup

def show_menu(proxies_enabled, complete_task, auto_spin, watch_ads):
    clear()
    banner()
    menu = f"""
{kng} Choose Setup :{reset}
{kng}  1.{reset} Use Proxy                  : {get_status(proxies_enabled)}
{kng}  2.{reset} Auto Complete Tasks        : {get_status(complete_task)} 
{kng}  3.{reset} Auto Spin Ticket           : {get_status(auto_spin)}
{kng}  4.{reset} Auto Watch Ads             : {get_status(watch_ads)}
{kng}  5.{reset} Additional Configs         : {hju}config.json{reset}
{mrh}    {pth} --------------------------------{reset}
{kng}  8.{reset} {kng}Save Setup{reset}
{kng}  9.{reset} {mrh}Reset Setup{reset}
{kng}  0.{reset} {hju}Start Bot {kng}(default){reset}

    """
    print(menu)
    choice = input(" Enter your choice (1/2/3/4/5/8/9/0): ")
    log_line()
    return choice

def write_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def show_config():
    while True:
        clear()
        banner()
        config = read_config()
        
        menu = f"""
{hju} Active Menu {kng}'Change Configuration'{reset}
{htm} {'~' * 50}{reset}
{hju} Select the configuration to change:{reset}
{kng} 1. sleep before start         {hju}(current: {config['sleep_before_start']} seconds){reset}
{kng} 2. delay for each account     {hju}(current: {config['account_delay']} seconds){reset}
{kng} 3. countdown looping timer    {hju}(current: {config['countdown_loop']} seconds){reset}
{kng} 4. back to {bru}main menu{reset}

        """
        print(menu)
        
        choice = input(" Enter your choice (1/2/3/4): ")
        
        if choice in ['1', '2', '3']:
            key_map = {
                '1': 'sleep_before_start',
                '2': 'account_delay',
                '3': 'countdown_loop'
            }
            
            key = key_map[choice]
            
            if choice == '99': 
                config[key] = not config[key]
            else: 
                new_value = input(f" Enter new value for {key}: ")
                try:
                    config[key] = int(new_value)
                except ValueError:
                    print(" Invalid input. Please enter a valid number.")
                    continue 

            write_config(config)
            print(f" {key} updated to {config[key]}")
        
        elif choice == '4':
            break 
        else:
            print(" Invalid choice. Please try again.")

async def run_bot(proxies_enabled, complete_task, auto_spin, watch_ads):
    clear()
    banner()
    loop = config.get('countdown_loop', 3800)
    account_delay = config.get('account_delay', 5)
    proxies = GoatsBot.get_proxies() if proxies_enabled else []

    while True:
        try:
            with open("data.txt", "r", encoding="utf-8") as file:
                accounts = [line.strip() for line in file if line.strip()]

            current_proxy_index = 0 

            for auth_data in accounts:
                log(bru + f"Processing Account: {pth}{accounts.index(auth_data) + 1}/{len(accounts)}")

                if proxies_enabled and proxies:
                    proxy = proxies[current_proxy_index]
                    host_port = (f"{proxy.get('host', 'unknown_host')}:{proxy.get('port', 'unknown_port')}" 
                                  if isinstance(proxy, dict) 
                                  else proxy.split('@')[-1] if '@' in proxy else proxy)
                    log(hju + f"Using proxy: {pth}{host_port}")
                    current_proxy_index = (current_proxy_index + 1) % len(proxies)
                else:
                    log(hju + f"Using proxy: {pth}No proxy")

                log(pth + f"~" * 38)

                bot = GoatsBot(auth_data.strip(), proxy=proxy)
                user_data = await bot.user_data()
                
                if user_data:
                    log(hju + f"Username: {pth}{user_data.get('user_name')}")
                    log(hju + f"Balance: {pth}{user_data.get('balance'):,.0f} ")
                    log(hju + f"Telegram Age: {pth}{user_data.get('age')} years")
                    await bot.checkin_user()

                    if complete_task:
                        await bot.fetch_and_complete_missions()
                    else:
                        log(kng + f"Auto complete task is not activated.")

                    if auto_spin:
                        slot_machine_coin = user_data.get('slot_machine_coin', 0)
                        if slot_machine_coin > 0:
                            log(pth + f"{slot_machine_coin} {hju}slot machine Coins available")
                            await bot.spin(slot_machine_coin)
                        else:
                            log(kng + f"No slot machine coins available.")
                    else:
                        log(kng + f"Auto Spin slot is not activated.")

                    if watch_ads:
                        block_id = 2373
                        await bot.watch(block_id, bot.user_id)
                    else:
                        log(kng + f"Auto watching ads is not activated.")

                await bot.http.close()
                print(pth + f"~" * 60)
                await countdown_timer(account_delay)
            await countdown_timer(loop)
 
        except HTTPError as e:
            log(mrh + f"HTTP error occurred check last.log for detail")
            log_error(f"{str(e)}")
        except (IndexError, JSONDecodeError) as e:
            log(mrh + f"Data extraction error: {kng}last.log for detail.")
            log_error(f"{str(e)}")
        except ConnectionError:
            log(mrh + f"Connection lost: {kng}Unable to reach the server.")
        except Timeout:
            log(mrh + f"Request timed out: {kng}The server is taking too long to respond.")
        except ProxyError:
            log(mrh + f"Proxy error: {kng}Failed to connect through the specified proxy.")
            if "407" in str(e):
                log(bru + f"Proxy authentication failed. Trying another.")
                if proxy:
                    proxy = random.choice(proxy)
                    log(bru + f"Switching proxy: {pth}{proxy}")
                else:
                    log(mrh + f"No more proxies available.")
                    break
            else:
                log(htm + f"An error occurred: {htm}{e}")
                break
        except RequestException as e:
            log(mrh + f"General request error: {kng}last.log for detail.")
            log_error(f"{str(e)}")
        except Exception as e:
            log(mrh + f"An unexpected error occurred: {kng}last.log for detail.")
            log_error(f"{str(e)}")
            return

async def main():
    parser = argparse.ArgumentParser(description="Run the bot with a specified setup.")
    parser.add_argument('--setup', type=str, help='Specify the setup file to load')
    args = parser.parse_args()
    sleep_before_start = config.get('sleep_before_start', 5)
    
    if args.setup:
        setup_file = f'src/config/{args.setup}.json'
        setup_data = load_setup_from_file(setup_file)
        proxies_enabled = setup_data.get('proxies_enabled', False)
        complete_task = setup_data.get('complete_task', False)
        auto_spin = setup_data.get('auto_spin', False)
        watch_ads = setup_data.get('watch_ads', False)
        await countdown_timer(sleep_before_start)
        await run_bot(proxies_enabled, complete_task, auto_spin, watch_ads)
    else:
        proxies_enabled = False
        complete_task = False
        auto_spin = False
        watch_ads = False

        while True:
            try:
                choice = show_menu(proxies_enabled, complete_task, auto_spin, watch_ads)
                if choice == '1':
                    proxies_enabled = not proxies_enabled
                elif choice == '2':
                    complete_task = not complete_task
                elif choice == '3':
                    auto_spin = not auto_spin
                elif choice == '4':
                    watch_ads = not watch_ads
                elif choice == '5':
                    show_config()
                elif choice == '8':
                    setup_name = input(" Enter setup name (without space): ")
                    setup_data = {
                        'use_proxy': proxies_enabled,
                        'complete_task': complete_task,
                        'auto_spin': auto_spin,
                        'watch_ads': watch_ads,
                    }
                    save_setup(setup_name, setup_data)
                elif choice == '0':
                    await countdown_timer(sleep_before_start)
                    await run_bot(proxies_enabled, complete_task, auto_spin, watch_ads)
                elif choice == '9':
                    proxies_enabled = False
                    complete_task = False
                    auto_spin = False
                    watch_ads = False
                else:
                    log(mrh + "Invalid choice. Please try again.")
                time.sleep(1)
            except KeyboardInterrupt as e:
                sys.exit()