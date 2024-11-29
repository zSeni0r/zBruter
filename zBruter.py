import requests
import threading
from queue import Queue
import sys
import os
import time
from colorama import Fore, Style

# Function to clear the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to display loading animation
def loading_animation():
    logo = Fore.CYAN + r"""
 _                    _ _             
| |    ___   __ _  __| (_)_ __   __ _ 
| |   / _ \ / _` |/ _` | | '_ \ / _` |
| |__| (_) | (_| | (_| | | | | | (_| |
|_____\___/ \__,_|\__,_|_|_| |_|\__, |
                                |___/ 
""" + Style.RESET_ALL
    print(logo)

    print(Fore.WHITE + "[*] Loading, please wait..." + Style.RESET_ALL)
    
    for i in range(101):
        time.sleep(0.02)  # Simulate loading (2 seconds total)
        sys.stdout.write(f"\r{Fore.YELLOW}Loading... Please Wait{i}%")
        sys.stdout.flush()
    
    print()  # Move to the next line after loading completes

# Function to print the logo
def print_logo():
    logo = Fore.CYAN + r"""
      ____             _            
     |  _ \           | |           
  ___| |_) |_ __ _   _| |_ ___ _ __ 
 |_  /  _ <| '__| | | | __/ _ \ '__|
  / /| |_) | |  | |_| | ||  __/ |   
 /___|____/|_|   \__,_|\__\___|_|   
    BreachForums.st/User-zSenior
""" + Style.RESET_ALL
    print(logo)

# Function to read user agents from the file
def load_user_agents(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(Fore.YELLOW + "[*] User agents file not found, proceeding without." + Style.RESET_ALL)
        return []

# Function to read proxies from the file
def load_proxies(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(Fore.YELLOW + "[*] Proxies file not found, proceeding without." + Style.RESET_ALL)
        return []

# Function to perform the directory brute forcing
def brute_force_directory(base_url, wordlist, user_agent, proxy):
    found_urls = []
    for directory in wordlist:
        url = f"{base_url}/{directory}"
        headers = {'User-Agent': user_agent}
        try:
            if proxy:
                response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=3)
            else:
                response = requests.get(url, headers=headers, timeout=3)

            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Found: {url}" + Style.RESET_ALL)
                found_urls.append(url)
            elif response.status_code == 404:
                print(Fore.RED + f"[-] Not found: {url}" + Style.RESET_ALL)
        except requests.ConnectionError:
            print(Fore.RED + "[!] Connection error!" + Style.RESET_ALL)
            continue
        except Exception as e:
            print(Fore.RED + f"[!] An error occurred: {e}" + Style.RESET_ALL)

    return found_urls

# Thread worker function
def worker(queue, base_url, user_agent, proxy, found_urls):
    while not queue.empty():
        directory = queue.get()
        urls = brute_force_directory(base_url, [directory], user_agent, proxy)
        if urls:
            found_urls.extend(urls)
        queue.task_done()

# Main function
def main():
    clear_terminal()
    loading_animation()  # Show loading animation before proceeding

    print_logo()

    base_url = input(Fore.CYAN + "[*] Enter the Target URL (Include http/https): " + Style.RESET_ALL)

    # Add default wordlists
    default_wordlists = ['headshot.txt']
    wordlist_file = input(Fore.CYAN + "[*] Enter the path to the directory wordlist (press Enter to use default): " + Style.RESET_ALL)

    # Check for default wordlists if input is empty
    if not wordlist_file:
        for default in default_wordlists:
            if os.path.isfile(default):
                print(Fore.CYAN + f"[*] Using default wordlist: {default}" + Style.RESET_ALL)
                wordlist_file = default
                break
        else:
            print(Fore.RED + "[!] No valid wordlist found. Please provide a valid wordlist path." + Style.RESET_ALL)
            sys.exit(1)

    if not os.path.isfile(wordlist_file):
        print(Fore.RED + "[!] Wordlist file does not exist." + Style.RESET_ALL)
        sys.exit(1)

    wordlist = [line.strip() for line in open(wordlist_file).readlines()]
    num_threads = int(input(Fore.CYAN + "[*] Enter the number of threads: " + Style.RESET_ALL))
    ua_file = input(Fore.CYAN + "[*] Enter the path to the user agent file (optional, press Enter to skip): " + Style.RESET_ALL)
    proxy_file = input(Fore.CYAN + "[*] Enter the path to the proxy file (optional, press Enter to skip): " + Style.RESET_ALL)

    user_agents = load_user_agents(ua_file) if ua_file else [None]
    proxies = load_proxies(proxy_file) if proxy_file else [None]

    queue = Queue()
    for directory in wordlist:
        queue.put(directory)

    threads = []
    found_urls = []

    for i in range(num_threads):
        user_agent = user_agents[i % len(user_agents)]
        proxy = proxies[i % len(proxies)]
        thread = threading.Thread(target=worker, args=(queue, base_url, user_agent, proxy, found_urls))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Save successful URLs to file
    if found_urls:
        with open('success_200_output.txt', 'w') as output_file:
            for url in found_urls:
                output_file.write(url + '\n')
        print(Fore.CYAN + f"[*] Successfully found URLs with status code 200 saved to 'success_200_output.txt'." + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "[*] No URLs with status code 200 found." + Style.RESET_ALL)

    print(Fore.CYAN + "[*] Finished scanning!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()

