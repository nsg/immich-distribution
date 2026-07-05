from __future__ import annotations

import httpx


class ImmichApi:
    def __init__(self, base_url: str, client: httpx.Client):
        self.base_url = base_url.rstrip("/")
        self.client = client

    def ping(self) -> bool:
        response = self.client.get(f"{self.base_url}/api/server/ping")
        if response.status_code != 200:
            return False

        return response.json().get("res") == "pong"

    def create_admin_user(self, *, email: str, password: str, name: str) -> None:
        response = self.client.post(
            f"{self.base_url}/api/auth/admin-sign-up",
            json={"email": email, "password": password, "name": name},
        )
        if response.status_code in (200, 201):
            return

        login_response = self.client.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password},
        )
        if login_response.status_code in (200, 201):
            return

        raise AssertionError(f"failed to create admin user: {response.status_code} {response.text}")

    def login(self, *, email: str, password: str) -> str:
        response = self.client.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code in (200, 201), response.text

        access_token = response.json().get("accessToken")
        assert access_token, f"login response did not include an access token: {response.text}"
        return access_token

    def create_api_key(
        self,
        *,
        access_token: str,
        name: str,
        permissions: list[str] | None = None,
    ) -> str:
        response = self.client.post(
            f"{self.base_url}/api/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": name, "permissions": permissions or ["all"]},
        )
        assert response.status_code in (200, 201), response.text

        secret = response.json().get("secret")
        assert secret and len(secret) > 20, f"API key response did not include a valid secret: {response.text}"
        return secret

    def complete_admin_onboarding(self, *, access_token: str) -> None:
        response = self.client.post(
            f"{self.base_url}/api/system-metadata/admin-onboarding",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"isOnboarded": True},
        )
        assert response.status_code in (200, 204), response.text

    def complete_user_onboarding(self, *, access_token: str) -> None:
        response = self.client.put(
            f"{self.base_url}/api/users/me/onboarding",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"isOnboarded": True},
        )
        assert response.status_code in (200, 204), response.text

    def disable_version_check(self, *, access_token: str) -> None:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = self.client.get(f"{self.base_url}/api/system-config", headers=headers)
        assert response.status_code == 200, response.text

        config = response.json()
        config["newVersionCheck"]["enabled"] = False

        response = self.client.put(f"{self.base_url}/api/system-config", headers=headers, json=config)
        assert response.status_code in (200, 204), response.text

    def current_user(self, *, api_key: str) -> dict:
        response = self.client.get(f"{self.base_url}/api/users/me", headers={"X-API-KEY": api_key})
        assert response.status_code == 200, response.text
        return response.json()
