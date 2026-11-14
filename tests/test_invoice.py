import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app, InvoiceData, validate_invoice
from app.runtime import ProviderError

DATA = json.loads((Path(__file__).resolve().parents[1] / 'examples/corrected.json').read_text())


class FakeModel:
    def structured(self, *args):
        return copy.deepcopy(DATA)


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / 'invoice.sqlite3', FakeModel()))


def upload(client):
    response = client.post('/invoices', files={'file': ('invoice.txt', b'Invoice INV-1001\nTotal 1180 INR')})
    assert response.status_code == 200
    return response.json()


def test_review_export_and_reopen(client, tmp_path):
    invoice = upload(client)
    assert invoice['issues'] == []
    assert client.get(f"/invoices/{invoice['id']}/export").status_code == 409
    reviewed = client.post(f"/invoices/{invoice['id']}/review", json={'version': 1})
    assert reviewed.status_code == 200
    assert reviewed.json()['version'] == 2
    assert client.get(f"/invoices/{invoice['id']}/export").json()['total'] == '1180.00'
    assert 'Design consultation' in client.get(f"/invoices/{invoice['id']}/export?format=csv").text
    reopened = TestClient(create_app(tmp_path / 'invoice.sqlite3', FakeModel()))
    assert reopened.get('/invoices/' + invoice['id']).json()['status'] == 'reviewed'


def test_duplicate_and_stale_correction(client):
    invoice = upload(client)
    assert upload(client)['duplicate'] is True
    path = '/invoices/' + invoice['id']
    assert client.patch(path, json={'version': 1, 'data': DATA}).status_code == 200
    assert client.patch(path, json={'version': 1, 'data': DATA}).status_code == 409
    assert client.post(path + '/review', json={'version': 1}).status_code == 409


def test_arithmetic_missing_fields_and_nonfinite(client):
    invoice = upload(client)
    invalid = copy.deepcopy(DATA)
    invalid['total'] = '1181.00'
    result = client.patch('/invoices/' + invoice['id'], json={'version': 1, 'data': invalid})
    assert any(issue['rule'] == 'total' for issue in result.json()['issues'])
    assert client.post('/invoices/' + invoice['id'] + '/review', json={'version': 2}).status_code == 422
    assert validate_invoice(InvoiceData())
    invalid['total'] = 'NaN'
    assert client.patch('/invoices/' + invoice['id'], json={'version': 2, 'data': invalid}).status_code == 422


def test_failed_model_is_recoverable(tmp_path):
    class Broken:
        def structured(self, *args):
            raise ProviderError('offline')
    client = TestClient(create_app(tmp_path / 'db', Broken()))
    invoice = upload(client)
    assert invoice['status'] == 'extraction_failed'
    response = client.patch('/invoices/' + invoice['id'], json={'version': 1, 'data': DATA})
    assert response.json()['status'] == 'needs_review'
    assert client.post('/invoices/' + invoice['id'] + '/review', json={'version': 2}).status_code == 200


def test_csv_formula_escaped(client):
    invoice = upload(client)
    data = copy.deepcopy(DATA)
    data['vendor'] = '=MALICIOUS()'
    path = '/invoices/' + invoice['id']
    client.patch(path, json={'version': 1, 'data': data})
    client.post(path + '/review', json={'version': 2})
    assert "'=MALICIOUS()" in client.get(path + '/export?format=csv').text


def test_invalid_uploads(client):
    assert client.post('/invoices', files={'file': ('a.txt', b'')}).status_code == 422
    assert client.post('/invoices', files={'file': ('a.exe', b'hello')}).status_code == 422
    assert client.post('/invoices', files={'file': ('a.png', b'not an image')}).status_code == 422
    assert client.get('/invoices/missing').status_code == 404
