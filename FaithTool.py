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

init()

MAX_THREADS = 500
REQUEST_TIMEOUT = 10

class UltimatePlayFabTool:
    def __init__(self):
        self.accounts_created = 0
        self.running = True
        self.proxies = []
        self.lock = threading.Lock()
        self.target_accounts = 0
        self.COLOR_SUCCESS = Fore.LIGHTGREEN_EX
        self.COLOR_ERROR = Fore.LIGHTRED_EX
        self.COLOR_RESET = Style.RESET_ALL
        self.clear_console()
        self.print_banner()
        self.show_menu()

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        banner = """
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

    def show_menu(self):
        print(f"{Fore.LIGHTCYAN_EX}[1] PlayFab Account Spammer")
        print(f"[2] DLC Puller (No Proxies){self.COLOR_RESET}")
        choice = input(f"{Fore.LIGHTCYAN_EX}[?] Select: {self.COLOR_RESET}").strip()
        if choice == "1":
            self.get_spammer_parameters()
            self.load_proxies()
            self.start_spammer()
        elif choice == "2":
            self.get_dlc_puller_parameters()
            self.pull_dlc_no_proxy()
        else:
            self.__init__()

    def print_message(self, message, color=None):
        color = color or Fore.LIGHTCYAN_EX
        print(f"{color}{message}{self.COLOR_RESET}")

    def get_spammer_parameters(self):
        self.title_id = input(f"{Fore.LIGHTCYAN_EX}[?] Title ID: {self.COLOR_RESET}").strip()
        self.prefix = input(f"{Fore.LIGHTCYAN_EX}[?] Prefix (blank=random): {self.COLOR_RESET}").strip() or ""
        self.target_accounts = int(input(f"{Fore.LIGHTCYAN_EX}[?] Amount: {self.COLOR_RESET}").strip())
        self.executor = ThreadPoolExecutor(max_workers=MAX_THREADS)

    def get_dlc_puller_parameters(self):
        self.title_id = input(f"{Fore.LIGHTCYAN_EX}[?] Title ID: {self.COLOR_RESET}").strip()
        self.custom_id = input(f"{Fore.LIGHTCYAN_EX}[?] Custom ID (blank=random): {self.COLOR_RESET}").strip() or f"dlc_puller_{random.randint(0,999999999)}"

    def load_proxies(self):
        try:
            sources = [
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
            ]
            self.proxies = []
            for source in sources:
                try:
                    r = requests.get(source, timeout=5)
                    if r.status_code == 200:
                        self.proxies.extend(r.text.splitlines())
                except:
                    continue
            if not self.proxies:
                with open('proxies.json', 'r') as f:
                    self.proxies = json.load(f)
        except:
            self.proxies = []

    def get_random_proxy(self):
        if not self.proxies:
            self.load_proxies()
        return random.choice(self.proxies) if self.proxies else None

    def create_account(self):
        while self.running and self.accounts_created < self.target_accounts:
            try:
                custom_id = f"{self.prefix}{random.randint(0,999999999)}"
                payload = {
                    "TitleId": self.title_id,
                    "CreateAccount": True,
                    "CustomId": custom_id
                }
                proxy = self.get_random_proxy()
                proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
                r = requests.post(
                    f"https://{self.title_id}.playfabapi.com/Client/LoginWithCustomID",
                    json=payload,
                    proxies=proxies,
                    timeout=REQUEST_TIMEOUT
                )
                if r.status_code == 200:
                    with self.lock:
                        self.accounts_created += 1
                        print(f"{proxy or 'DIRECT'} | Successfully Spammed {self.accounts_created}/{self.target_accounts}")
                elif r.status_code == 429:
                    time.sleep(0.1)
            except:
                continue

    def start_spammer(self):
        for _ in range(MAX_THREADS):
            self.executor.submit(self.create_account)
        try:
            while self.accounts_created < self.target_accounts and self.running:
                time.sleep(0.1)
            self.executor.shutdown(wait=False)
            self.print_message(f"\nCompleted {self.target_accounts} accounts!", self.COLOR_SUCCESS)
            self.ask_for_restart()
        except KeyboardInterrupt:
            self.running = False
            self.executor.shutdown(wait=False)
            self.print_message(f"\nStopped. Created {self.accounts_created} accounts.", Fore.LIGHTYELLOW_EX)
            self.ask_for_restart()

    def pull_dlc_no_proxy(self):
        try:
            login_payload = {
                "TitleId": self.title_id,
                "CreateAccount": True,
                "CustomId": self.custom_id
            }
            r = requests.post(
                f"https://{self.title_id}.playfabapi.com/Client/LoginWithCustomID",
                json=login_payload,
                timeout=REQUEST_TIMEOUT
            )
            if r.status_code != 200:
                self.print_message(f"Login failed: {r.status_code}", self.COLOR_ERROR)
                return
            
            session_ticket = r.json().get('data', {}).get('SessionTicket')
            if not session_ticket:
                self.print_message("No session ticket", self.COLOR_ERROR)
                return
            
            headers = {
                "Content-Type": "application/json",
                "X-PlayFabSDK": "PlayFabSDK/2.94.210118",
                "X-Authorization": session_ticket
            }
            
            r = requests.post(
                f"https://{self.title_id}.playfabapi.com/Client/GetCatalogItems",
                json={},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if r.status_code == 200:
                catalog = r.json().get('data', {})
                filename = f"{self.title_id}-dlc.json"
                with open(filename, "w") as f:
                    json.dump(catalog, f, indent=2)
                self.print_message(f"Saved DLC catalog to {filename}", self.COLOR_SUCCESS)
            else:
                self.print_message(f"Catalog failed: {r.status_code}", self.COLOR_ERROR)
        except Exception as e:
            self.print_message(f"Error: {str(e)}", self.COLOR_ERROR)
        self.ask_for_restart()

    def ask_for_restart(self):
        if input(f"\n{Fore.LIGHTCYAN_EX}[?] Menu? (y/n): {self.COLOR_RESET}").lower() == 'y':
            self.__init__()
        else:
            sys.exit(0)

if __name__ == "__main__":
    tool = UltimatePlayFabTool()
