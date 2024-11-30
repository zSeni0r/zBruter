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
        sys.stdout.write(f"\r{Fore.YELLOW}Loading... Please Wait {i}%")
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

# Function to fetch subdomains from VirusTotal
def fetch_subdomains_from_virustotal(url, api_key):
    headers = {
        "x-apikey": api_key
    }
    response = requests.get(f"https://www.virustotal.com/api/v3/domains/{url}", headers=headers)
    
    if response.status_code == 200:
        subdomains = response.json().get('data', [])
        return [subdomain['id'].replace('http://', '').replace('https://', '') for subdomain in subdomains]
    else:
        print(Fore.RED + f"[!] Error fetching subdomains: {response.text}" + Style.RESET_ALL)
        return []

# Function for brute forcing directories
def brute_force(url, wordlist, num_threads):
    url_queue = Queue()
    for word in wordlist:
        url_queue.put(word)
    
    found_urls = []  # List to collect found URLs
    lock = threading.Lock()  # Create a lock for thread-safe file writing

    def worker():
        while not url_queue.empty():
            word = url_queue.get()
            target_url = f"{url}/{word}"
            try:
                response = requests.get(target_url, timeout=5)
                if response.status_code == 200:
                    found_urls.append(target_url)
                    print(Fore.GREEN + f"[+] Found: {target_url}" + Style.RESET_ALL)
                    # Write the found URL with status code 200 to the file
                    with lock:
                        with open('success_200_output.txt', 'a') as success_file:
                            success_file.write(target_url + '\n')
                elif response.status_code == 404:
                    pass  # Don't print for 404
                else:
                    print(Fore.YELLOW + f"[!] Status {response.status_code} for: {target_url}" + Style.RESET_ALL)
            except requests.ConnectionError:
                print(Fore.RED + "[!] Connection Error!" + Style.RESET_ALL)
            finally:
                url_queue.task_done()
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    url_queue.join()
    
    for thread in threads:
        thread.join()

    return found_urls  # Return the list of found URLs

# Main function
def main():
    clear_terminal()
    loading_animation()

    print_logo()

    base_url = input(Fore.CYAN + "[*] Enter the Target URL (Include http/https): " + Style.RESET_ALL)
    api_key = input(Fore.CYAN + "[*] Enter your VirusTotal API key (leave empty to skip): " + Style.RESET_ALL)
    
    subdomain_file_name = base_url.split("://")[-1].replace("/", "_") + "_subdomains.txt"
    
    if api_key.strip() == "":
        print(Fore.RED + "[!] No API key provided. Skipping subdomain gathering." + Style.RESET_ALL)
        start_brute_force(base_url)
    else:
        gather_subdomains = input(Fore.CYAN + "[*] Do you want to gather subdomains from VirusTotal? (y/n): " + Style.RESET_ALL)
        if gather_subdomains.lower() == 'y':
            print(Fore.YELLOW + "[*] Gathering subdomains from VirusTotal, please wait..." + Style.RESET_ALL)
            subdomains = fetch_subdomains_from_virustotal(base_url, api_key)
            subdomain_count = len(subdomains)

            # Write to file
            with open(subdomain_file_name, 'w') as file:
                for subdomain in subdomains:
                    file.write(subdomain + '\n')

            print(Fore.CYAN + f"[*] Found {subdomain_count} subdomains. Saved to {subdomain_file_name}" + Style.RESET_ALL)
        
        # Start brute force if subdomain gathering is complete or skipped
        found_urls = start_brute_force(base_url)

        # Display all found URLs
        if found_urls:
            print(Fore.CYAN + "[*] All found URLs:" + Style.RESET_ALL)
            for url in found_urls:
                print(Fore.GREEN + f"Found: {url}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "[*] No URLs found." + Style.RESET_ALL)

def start_brute_force(base_url):
    wordlist_path = input(Fore.CYAN + "[*] Enter the path to your wordlist file (press Enter to use default 'headshot.txt'): " + Style.RESET_ALL)
    
    # Set default wordlist path if input is empty
    if not wordlist_path.strip():
        wordlist_path = 'headshot.txt'
    
    num_threads = int(input(Fore.CYAN + "[*] Enter the number of threads (recommended: 10): " + Style.RESET_ALL) or 10)

    try:
        with open(wordlist_path, 'r') as f:
            wordlist = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(Fore.RED + "[!] Wordlist file not found." + Style.RESET_ALL)
        return []

    print(Fore.YELLOW + "[*] Starting brute force attack..." + Style.RESET_ALL)

    return brute_force(base_url, wordlist, num_threads)

if __name__ == "__main__":
    main()
