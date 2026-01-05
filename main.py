from __future__ import annotations
import os
import requests
import pathlib

from os import environ
from dotenv import load_dotenv
from hcloud import Client
from hcloud.zones import Zone, ZoneRRSet, ZoneRecord

IP_FILE = pathlib.Path("./current_public_ip.txt")  # adjust path as needed

def main():
    print("Starting Hetzner DynDNS Update")
    public_ip = get_public_ip()
    changed = store_ip_if_changed(public_ip)
    if changed:
        print("Public IP has changed, updating Hetzner DNS record to " + public_ip)
        update(public_ip)
    else:
        print("Skipping Hetzner update (IP unchanged).")

def get_public_ip() -> str:
    response = requests.get("https://api.ipify.org?format=text")
    public_ip = response.text
    print(f"Current Public IP: {public_ip}")
    return public_ip

def update(public_ip: str):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    domain = os.getenv('HETZNER_ZONE_DOMAIN')

    print(f"Accessing HETZNER API for {domain} to update IP")
    client = Client(token=api_key)
    zones = client.zones.get_all()
    for zone in zones:
        print(f"Zone: {zone.id} - {zone.name}")
        if zone.name == domain:
            for subdomain in os.getenv('HETZNER_ZONE_SUB_DOMAINS', '').split(','):
                if subdomain:
                    print(f"Updating subdomain: {subdomain}.{domain}")
                    update_subdomains(client, zone, public_ip, domain, subdomain)         


def update_subdomains(client: Client, zone: Zone, public_ip: str, domain: str, subdomain: str):
    rrset = client.zones.get_rrset(zone=Zone(name=domain), name=subdomain, type="A")
    print(f"ID {rrset.id}, Name {rrset.name}, Type {rrset.type}, TTL {rrset.ttl}, Records {rrset.records}")

    action = client.zones.set_rrset_records(

    rrset = ZoneRRSet(
        zone=Zone(name=domain),
        name=subdomain,
        type="A",
    ),
    records = [
        ZoneRecord(value=public_ip, comment="Updated by Hetzner DynDNS Script")
    ],
    )
    action.wait_until_finished()

def read_stored_ip() -> str | None:
    try:
        return IP_FILE.read_text(encoding="utf-8").strip() or None
    except FileNotFoundError:
        return None

def write_stored_ip(ip: str) -> None:
    IP_FILE.parent.mkdir(parents=True, exist_ok=True)
    IP_FILE.write_text(ip + "\n", encoding="utf-8")

def store_ip_if_changed(new_ip: str) -> bool:
    old_ip = read_stored_ip()
    if old_ip == new_ip:
        print("IP unchanged; no file update.")
        return False
    write_stored_ip(new_ip)
    print(f"Stored IP updated: {old_ip} -> {new_ip}")
    return True


if __name__ == "__main__":
    main()
