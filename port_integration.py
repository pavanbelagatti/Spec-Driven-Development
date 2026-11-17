"""Optional Port integration: update existing service entity properties.

Prerequisite: add string properties `sddStatus` and `sddSummary` to your
service blueprint, and set the entity identifier in .env.
"""
import os
import requests

BASE = 'https://api.getport.io/v1'

def report_to_port(status: str, summary: str) -> None:
    client_id = os.getenv('PORT_CLIENT_ID')
    client_secret = os.getenv('PORT_CLIENT_SECRET')
    entity = os.getenv('PORT_ENTITY_IDENTIFIER')
    blueprint = os.getenv('PORT_ENTITY_BLUEPRINT', 'service')
    if not all([client_id, client_secret, entity]):
        print('Port not configured; skipping optional status update.')
        return
    token_response = requests.post(f'{BASE}/auth/access_token', json={
        'clientId': client_id, 'clientSecret': client_secret
    }, timeout=20)
    token_response.raise_for_status()
    token = token_response.json()['accessToken']
    # PATCH only supplied properties of an existing entity.
    response = requests.patch(
        f'{BASE}/blueprints/{blueprint}/entities/{entity}',
        headers={'Authorization': f'Bearer {token}'},
        json={'properties': {'sddStatus': status, 'sddSummary': summary[:500]}},
        timeout=20,
    )
    response.raise_for_status()
    print('Port service status updated.')
