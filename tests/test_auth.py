from tickethub.routers import auth as auth_router


async def test_login_returns_token_for_valid_user(client, monkeypatch):
    async def fake_login(username, password):
        return {"id": 1, "username": username}

    monkeypatch.setattr(auth_router.dummyjson, "login", fake_login)

    response = await client.post(
        "/auth/login", json={"username": "emilys", "password": "emilyspass"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    response = await client.post(
        "/tickets", json={"title": "Auth works", "priority": "low"}, headers=headers
    )
    assert response.status_code == 201


async def test_login_with_wrong_credentials_returns_401(client, monkeypatch):
    async def fake_login(username, password):
        return None

    monkeypatch.setattr(auth_router.dummyjson, "login", fake_login)

    response = await client.post("/auth/login", json={"username": "emilys", "password": "wrong"})
    assert response.status_code == 401


async def test_invalid_token_is_rejected(client):
    headers = {"Authorization": "Bearer not-a-real-token"}
    response = await client.post(
        "/tickets", json={"title": "x", "priority": "low"}, headers=headers
    )
    assert response.status_code == 401
