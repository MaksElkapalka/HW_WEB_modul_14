from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.services.auth import auth_service


class TestRouterContacts:
    current_date = datetime.now().strftime("%Y-%m-%d")
    test_contact = {
        "first_name": "test_contact_name",
        "last_name": "test_contact_last_name",
        "email": "test_contact@example.com",
        "phone_number": "12345678",
        "birthday": current_date,
    }

    @staticmethod
    def setup_monkeypatch(monkeypatch):
        redis_mock = Mock()
        redis_mock.get.return_value = None
        monkeypatch.setattr(auth_service, "cache", redis_mock)
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

    def test_get_contacts(
        self,
        client,
        get_token,
        monkeypatch,
    ):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1

    def test_get_contact(self, client, get_token, monkeypatch, contact_id=1):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"api/contacts/{contact_id}", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == contact_id

    def test_get_contact_not_found(
        self, client, get_token, monkeypatch, contact_id=100
    ):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        url = f"api/contacts/{contact_id}"
        response = client.get(url, headers=headers)
        assert response.status_code == 404, response.text

    def test_create_contact(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("api/contacts", headers=headers, json=self.test_contact)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["id"]
        assert data["first_name"] == self.test_contact["first_name"]
        assert data["last_name"] == self.test_contact["last_name"]
        assert data["email"] == self.test_contact["email"]
        assert data["phone_number"] == self.test_contact["phone_number"]
        assert data["birthday"] == self.test_contact["birthday"]

    def test_update_contact(self, client, get_token, monkeypatch, contact_id=1):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(
            f"api/contacts/{contact_id}", headers=headers, json=self.test_contact
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == self.test_contact["first_name"]
        assert data["last_name"] == self.test_contact["last_name"]
        assert data["email"] == self.test_contact["email"]
        assert data["phone_number"] == self.test_contact["phone_number"]
        assert data["birthday"] == self.test_contact["birthday"]

    def test_search_contacts(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        search_params = {
            "first_name": "test_contact_name",
            "last_name": "test_contact_last_name",
            "email": "test_contact@example.com",
        }
        response = client.get(
            "api/contacts/search/", headers=headers, params=search_params
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) > 0
        assert data[0]["first_name"] == search_params["first_name"]
        assert data[0]["last_name"] == search_params["last_name"]
        assert data[0]["email"] == search_params["email"]

    def test_get_birthdays(self, client, get_token, monkeypatch):
        self.setup_monkeypatch(monkeypatch)
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/birthdays/", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) > 0
        assert data[0]["birthday"] == self.test_contact["birthday"]
