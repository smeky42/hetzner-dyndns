from __future__ import annotations
import os
import requests

from os import environ
from dotenv import load_dotenv
from hcloud import Client
from hcloud.zones import Zone, ZoneRRSet, ZoneRecord


def main():
    print("Starting Hetzner DynDNS Update")
    public_ip = get_public_ip()
    update(public_ip)


def get_public_ip() -> str:
    response = requests.get("https://api.ipify.org?format=text")
    public_ip = response.text
    print(f"Current Public IP: {public_ip}")
    return public_ip

def update(public_ip: str):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    domain = os.getenv('DOMAIN')

    print(f"Accessing HETZNER API for {domain} to update IP")
    client = Client(token=api_key)
    zones = client.zones.get_all()
    for zone in zones:
        print(f"Zone: {zone.id} - {zone.name}")
        if zone.name == domain:
            rrset = client.zones.get_rrset(zone=Zone(name=domain), name="@", type="A")
            print(f"ID {rrset.id}, Name {rrset.name}, Type {rrset.type}, TTL {rrset.ttl}, Records {rrset.records}")

            action = client.zones.set_rrset_records(

            rrset = ZoneRRSet(
                zone=Zone(name=domain),
                name="@",
                type="A",

            ),
            records = [
                ZoneRecord(value=public_ip, comment="Updated by Hetzner DynDNS Script")
            ],
            )
            action.wait_until_finished()


if __name__ == "__main__":
    main()
