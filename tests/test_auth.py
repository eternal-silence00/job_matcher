

async def test_register(async_client):
    response = await async_client.post("/auth/register", json={"email": "test@mail.com", "password": "test"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@mail.com"
    
async def test_register_duplicate(async_client):
    response1 = await async_client.post("/auth/register", json={"email": "test@mail.com", "password": "test"})
    response2 = await async_client.post("/auth/register", json={"email": "test@mail.com", "password": "test"})
    assert response2.status_code == 400
    
async def test_login(async_client):
    await async_client.post("/auth/register", json={"email": "test@mail.com", "password": "test"})
    response = await async_client.post("/auth/login", json={"email": "test@mail.com", "password": "test"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    
async def test_login_wrong_password(async_client):
    await async_client.post("/auth/register", json={"email": "test@mail.com", "password": "test"})
    response = await async_client.post("/auth/login", json={"email": "test@mail.com", "password": "wrong"})
    assert response.status_code == 400
    
async def test_get_me(client_with_token):
    response = await client_with_token.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@mail.com"
    
    