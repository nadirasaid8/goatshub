# R3al G0ats Bot Telegram Automation Script

G0atsBot is an automation script for completing missions, checking in, and spinning the slot machine on the R3al G0ats Bot Telegram. This script handles multiple accounts, automates login, mission completion, and daily check-ins.

[TELEGRAM CHANNEL](https://t.me/Deeplchain) | [CONTACT](https://t.me/imspecials)


### This bot helpfull?  Please support me by buying me a coffee: 
```
0x705C71fc031B378586695c8f888231e9d24381b4 - EVM
TDTtTc4hSnK9ii1VDudZij8FVK2ZtwChja - TRON
UQBy7ICXV6qFGeFTRWSpnMtoH6agYF3PRa5nufcTr3GVOPri - TON
```

## Register

To use this bot, you need to register it with the Goats Telegram Bot. 

1. Open the bot [t.me/R34lgot_real](https://t.me/realgoats_bot/run?startapp=99effa5e-ac44-4be5-8f0d-64cf69f796e9)
2. Click on the "[Start App](https://t.me/realgoats_bot/run?startapp=99effa5e-ac44-4be5-8f0d-64cf69f796e9)" or "[Open App]([url](https://t.me/realgoats_bot/run?startapp=99effa5e-ac44-4be5-8f0d-64cf69f796e9))" button
3. Install This Real Goats Automations Bot
4. Have Fun 🦈

## Update 2024/10/19
  - Basic Optimations Scripts
  - Display Menu : run the bot and set `ON` / `OFF`
  - Instant Setup : save your setup and run easily 
  - Add Random User Agent 

## Features
- **Watching Ads**: automatically watching ads `ON` / `OFF`
- **Mission Completion**: Completes available missions `ON` / `OFF`
- **Daily Check-in**: Checks in daily and collects rewards. `Auto ON`
- **Slot Machine**: Spins the slot machine if coins are available. `ON` / `OFF`
- **Multi-account Support**: Automates For multiple accounts listed in `data.txt`.
- **Enable Proxies**: To use proxies enable **Use Proxy** `ON` in the menu

## Requirements

- `Python` 3.10+
- `aiohttp` for asynchronous HTTP requests
- `colorama` for colored output

## Setup and Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/nadirasaid8/goatshub.git
cd goatshub
```
**Create a virtual environment (optional but recommended)**

 ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
 ```
### Step 2: Install dependencies
You can install the required packages by running the following command:

```bash
pip install -r requirements.txt
```

### Step 3: Configure accounts
Create a `data.txt` file in the root directory.
Add Telegram authentication data for each account on a new line:

1. Use PC/Laptop or Use USB Debugging Phone
2. open the `r34l g04ts bot`
3. Inspect Element `(F12)` on the keyboard
4. at the top of the choose "`Application`" 
5. then select "`Session Storage`" 
6. Select the links "`dev.g04tsbot.xyz`" and "`"telegram-apps/launch-params`"
7. Take the value part of "`"tgWebAppPlatform=`"
8. Decode all the value with https://www.urldecoder.org/
9. take the part that looks like this: 

```txt 
query_id=xxxxxxxxx-1
```

10. add it to `data.txt` file or create it if you dont have one

### Step 4: Modify Configurations (Optional)
The `config.json` file allows you to modify script settings:
account_delay: Time (in seconds) between account operations.
looping: Time (in seconds) before starting a new loop of account runs.

### Configuration
You can adjust the bot's behavior via config.json:

  ```json
  {
      "sleep_before_start": 5,
      "account_delay": 5,
      "countdown_loop": 100
  } 
  ```
`sleep_before_start`: Delay before starting the first run

`account_delay`: Delay in seconds between switching accounts.

`countdown_loop`: Time in seconds to wait before running all accounts again.

### Format of proxies.txt
The proxies.txt file should contain one proxy per line in the following format:

```ruby
username:password@ip:port
username:password@ip:port
```

### Step 5: Run the script
To start the bot, run:

```bash
python main.py
```

### Instant Setup:
- **Loading setup via CLI argument:** If the `--setup` argument is provided, the script will load the corresponding `.json` file and run the bot directly without displaying the menu.
- **Menu display:** If no `--setup` argument is provided, the script will display the menu as usual.
- **Setup saving:** The option to save setups has been included in the menu as option `8`.

This will allow you to run the script directly with a predefined setup like this:

```bash
python main.py --setup mysetup
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions or support, please contact [ https://t.me/DeeplChain ]