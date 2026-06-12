from unittest.mock import patch 


async def test_create_jobs_as_admin(admin_client_with_token):
     with patch("app.jobs.service.EmbeddingService") as mock:
        mock.return_value.get_embedding.return_value = [0.1] * 384
        response = await admin_client_with_token.post("/jobs", json = {
            "title": "test",
            "description": "test test",
            "company": "test_company",
            "url": "https://test.com",
            "location": "testland",
            "published_at": "2026-06-12T10:00:00+00:00"
        })
        assert response.status_code == 201
        
async def test_job_as_user_forbidden(client_with_token):
    with patch("app.jobs.service.EmbeddingService") as mock:
        mock.return_value.get_embedding.return_value = [0.1] * 384
        response = await client_with_token.post("/jobs", json = {
            "title": "test",
            "description": "test test",
            "company": "test_company",
            "url": "https://test.com",
            "location": "testland",
            "published_at": "2026-06-12T10:00:00+00:00"
        })
        assert response.status_code == 403
        
async def test_get_all_jobs(async_client):
    response = await async_client.get("/jobs")
    assert response.status_code == 200
    
async def test_get_job_by_id_not_found(async_client):
    response = await async_client.get("/jobs/999")
    assert response.status_code == 404