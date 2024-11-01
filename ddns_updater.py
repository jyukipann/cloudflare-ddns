#!/bin/python3
import os
import requests
import pathlib
import subprocess

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4/zones"

env_path = pathlib.Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# 必要な環境変数を読み込む
GLOBAL_API_KEY = os.getenv("CLOUDFLARE_GLOBAL_API_KEY")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
RECORD_ID = os.getenv("CLOUDFLARE_RECORD_ID")
RECORD_ID_W = os.getenv("CLOUDFLARE_RECORD_ID_W")
DNS_NAME = os.getenv("DNS_NAME")
INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))  # 更新間隔（秒）
E_MAIL = os.getenv("E_MAIL")

def get_public_ip():
    """IPアドレス取得"""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json()["ip"]
    except requests.RequestException as e:
        print("Failed to get public IP:", e)
        return None

def get_zone_id(dns_name:str):
    """CloudflareゾーンID取得"""
    url = f"{CLOUDFLARE_API_URL}?name={dns_name}"
    headers = {
        'X-Auth-Email': E_MAIL,
        'X-Auth-Key': GLOBAL_API_KEY,
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(response.json())
        return response.json()["result"][0]["id"]
    except requests.RequestException as e:
        print("Failed to get zone ID:", e)
        print(response.json())
        return None

def get_dns_record_id(dns_name:str):
    """Cloudflare DNSレコードID取得"""
    url = f"{CLOUDFLARE_API_URL}/{ZONE_ID}/dns_records"
    headers = {
        'X-Auth-Email': E_MAIL,
        'X-Auth-Key': GLOBAL_API_KEY,
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return [record["id"] for record in response.json()["result"]]
    except requests.RequestException as e:
        print("Failed to get DNS record ID:", e)
        return None

def update_dns_record(ip):
    """Cloudflare DNSレコードを更新"""
    url = f"{CLOUDFLARE_API_URL}/{ZONE_ID}/dns_records/{RECORD_ID}"
    headers = {
        'X-Auth-Email': E_MAIL,
        # 'X-Auth-Key': API_TOKEN,
        'Authorization': f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "type": "A",
        "name": DNS_NAME,
        "content": ip,
        "ttl": 1,
    }
    
    # print(url)
    # print(headers)
    # print(data)
    # exit()
    
    results = []
    try:
        response = requests.put(url, json=data, headers=headers)
        # response.raise_for_status()
        # print(f"DNS record updated successfully {data['name']}:", response.json())
        results.append(response.json())
    except requests.RequestException as e:
        # print("Failed to update DNS record:", e)
        results.append(e)
    
    data['name'] = '*.'+DNS_NAME
    url = f"{CLOUDFLARE_API_URL}/{ZONE_ID}/dns_records/{RECORD_ID_W}"
    try:
        response = requests.put(url, json=data, headers=headers)
        # response.raise_for_status()
        # print(f"DNS record updated successfully {data['name']}:", response.json())
        results.append(response.json())
    except requests.RequestException as e:
        # print("Failed to update DNS record:", e)
        results.append(e)
    
    return results

def get_dns_record(dns_name:str):
    current_recorded_ip = (
        subprocess.run(
            [
                'dig',
                '@1.1.1.1',
                '+short',
                dns_name,
            ], 
            stdout=subprocess.PIPE)
        .stdout
        .decode()
        .strip()
    )
    return current_recorded_ip

def main():
    ip = get_public_ip()
    current_recorded_ip = get_dns_record(DNS_NAME)
    if ip is not None and ip != current_recorded_ip:
        # print("Updating DNS record...")
        result = update_dns_record(ip)
        result = [str(r) for r in result]
        result = '\n'.join(result)
        subprocess.run([
            'discord_notifier.py', 
            'Cloudflare DDNS', 
            f"detected mismatch between public IP and DNS record\n{ip} != {current_recorded_ip}\n{result}"
        ])
    else:
        # print("No update required")
        pass

if __name__ == "__main__":
    main()
    # print(get_zone_id(DNS_NAME))
    # print(get_dns_record_id(DNS_NAME))

