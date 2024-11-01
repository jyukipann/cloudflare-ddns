#!/bin/python3
import os
import requests

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4/zones"

# 必要な環境変数を読み込む
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
RECORD_ID = os.getenv("CLOUDFLARE_RECORD_ID")
RECORD_ID_W = os.getenv("CLOUDFLARE_RECORD_ID_W")
DNS_NAME = os.getenv("DNS_NAME")
INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))  # 更新間隔（秒）
E_MAIL = os.getenv("EMAIL")

def get_public_ip():
    """IPアドレス取得"""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json()["ip"]
    except requests.RequestException as e:
        print("Failed to get public IP:", e)
        return None

def update_dns_record(ip):
    """Cloudflare DNSレコードを更新"""
    url = f"{CLOUDFLARE_API_URL}/{ZONE_ID}/dns_records/{RECORD_ID}"
    headers = {
        'X-Auth-Email:': E_MAIL,
        "Content-Type": "application/json",
        'X-Auth-Key': API_TOKEN,
    }
    data = {
        "type": "A",
        "name": DNS_NAME,
        "content": ip,
        "ttl": 1,
    }
    try:
        response = requests.put(url, json=data, headers=headers)
        # response.raise_for_status()
        print(f"DNS record updated successfully {data['name']}:", response.json())
    except requests.RequestException as e:
        print("Failed to update DNS record:", e)
    
    data['name'] = '*.'+DNS_NAME
    url = f"{CLOUDFLARE_API_URL}/{ZONE_ID}/dns_records/{RECORD_ID_W}"
    try:
        response = requests.put(url, json=data, headers=headers)
        # response.raise_for_status()
        print(f"DNS record updated successfully {data['name']}:", response.json())
    except requests.RequestException as e:
        print("Failed to update DNS record:", e)

def main():
    """定期的にDDNSを更新"""
    ip = get_public_ip()
    if ip:
        print(f"Current IP: {ip}")
        update_dns_record(ip)
    else:
        print("Failed to retrieve IP address.")

if __name__ == "__main__":
    main()

