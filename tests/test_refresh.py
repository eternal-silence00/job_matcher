async def _register_and_login(client, email="refresh@test.com", password="test12345"):
    await client.post("/auth/register", json={"email": email, "password": password})
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()


async def test_refresh_happy_path(async_client):
    tokens = await _register_and_login(async_client)
    resp = await async_client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    new = resp.json()
    assert "access_token" in new
    assert "refresh_token" in new
    assert new["refresh_token"] != tokens["refresh_token"]


async def test_refresh_reuse_detected(async_client):
    tokens = await _register_and_login(async_client)
    old = tokens["refresh_token"]

    r1 = await async_client.post("/auth/refresh", json={"refresh_token": old})
    assert r1.status_code == 200

    r2 = await async_client.post("/auth/refresh", json={"refresh_token": old})
    assert r2.status_code == 401

    new = r1.json()["refresh_token"]
    r3 = await async_client.post("/auth/refresh", json={"refresh_token": new})
    assert r3.status_code == 401


async def test_logout_invalidates_token(async_client):
    tokens = await _register_and_login(async_client)
    r = await async_client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 204

    r2 = await async_client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 401


async def test_refresh_invalid_token(async_client):
    r = await async_client.post("/auth/refresh", json={"refresh_token": "garbage.not.jwt"})
    assert r.status_code == 401


async def test_logout_idempotent(async_client):
    tokens = await _register_and_login(async_client)
    await async_client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    r = await async_client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 204


async def test_logout_all_revokes_everything(async_client):
    tokens = await _register_and_login(async_client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = await async_client.post("/auth/logout-all", headers=headers)
    assert r.status_code == 204
    r2 = await async_client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 401