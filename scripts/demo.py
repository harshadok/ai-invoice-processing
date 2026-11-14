"""Run a synthetic-data walkthrough against a running local API."""
import argparse
import json
from pathlib import Path
import httpx

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8102')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
client = httpx.Client(base_url=args.url, timeout=300)

def call(method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()

invoice = call('POST', '/invoices', files={'file': ('invoice.txt', (root/'examples/invoice.txt').read_bytes())})
print('Extracted:', json.dumps(invoice, indent=2))
if invoice['issues'] or invoice['data'] is None:
    invoice = call('PATCH', '/invoices/'+invoice['id'], json={'version':invoice['version'],'data':json.loads((root/'examples/corrected.json').read_text())})
if invoice['status'] != 'reviewed':
    invoice = call('POST','/invoices/'+invoice['id']+'/review',json={'version':invoice['version']})
print('Reviewed export:', json.dumps(call('GET','/invoices/'+invoice['id']+'/export'),indent=2))
