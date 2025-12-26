import os
from dotenv import load_dotenv

def main():
    print("Hello from hetzner-dyndns!")
    load_dotenv()
    api_key = os.getenv('API_KEY')
    hetzner_api = os.getenv('HETZNER_API')
    hetzner_zone_id = os.getenv('HETZNER_ZONE_ID')
    domain = os.getenv('DOMAIN')

    print(f"Accessing HETZNER API {hetzner_api} for ZONE ID {hetzner_zone_id} to update DOMAIN {domain}")

if __name__ == "__main__":
    main()
