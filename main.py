from __future__ import annotations
import os
import requests
import logging

from os import environ
from pathlib import Path 
from dotenv import load_dotenv
from hcloud import Client
from hcloud.zones import Zone, ZoneRRSet, ZoneRecord


SCRIPT_DIR = Path(__file__).resolve().parent

IP_FILE = SCRIPT_DIR / "current_public_ip.txt"
LOG_FILE = SCRIPT_DIR / "hetzner_dyndns.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Hetzner DynDNS Update")
    public_ip = get_public_ip()
    changed = store_ip_if_changed(public_ip)
    if changed:
        logger.info("Public IP has changed, updating Hetzner DNS record to " + public_ip)
        update(public_ip)
    else:
        logger.info("Skipping Hetzner update (IP unchanged).")

def get_public_ip() -> str:
    response = requests.get("https://api.ipify.org?format=text")
    public_ip = response.text
    logger.info(f"Current Public IP: {public_ip}")
    return public_ip

def update(public_ip: str):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    domain = os.getenv('HETZNER_ZONE_DOMAIN')

    logger.info(f"Accessing HETZNER API for {domain} to update IP")
    client = Client(token=api_key)
    zones = client.zones.get_all()
    for zone in zones:
        logger.info(f"Zone: {zone.id} - {zone.name}")
        if zone.name == domain:
            for subdomain in os.getenv('HETZNER_ZONE_SUB_DOMAINS', '').split(','):
                if subdomain:
                    logger.info(f"Updating subdomain: {subdomain}.{domain}")
                    update_subdomains(client, zone, public_ip, domain, subdomain)         


def update_subdomains(client: Client, zone: Zone, public_ip: str, domain: str, subdomain: str):
    rrset = client.zones.get_rrset(zone=Zone(name=domain), name=subdomain, type="A")
    logger.info(f"ID {rrset.id}, Name {rrset.name}, Type {rrset.type}, TTL {rrset.ttl}, Records {rrset.records}")

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
        logger.info("IP unchanged; no file update.")
        return False
    write_stored_ip(new_ip)
    logger.info(f"Stored IP updated: {old_ip} -> {new_ip}")
    return True


if __name__ == "__main__":
    main()
