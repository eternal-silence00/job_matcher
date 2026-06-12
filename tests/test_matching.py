from unittest.mock import patch 

async def test_matching_jobs(client_with_token):
    with patch("app.resumes.service.PdfService") as pdf_mock, \
         patch("app.resumes.service.StorageService") as storage_mock, \
         patch("app.resumes.service.EmbeddingService") as embedding_mock:
        
        pdf_mock.return_value.extract_text.return_value = "fake resume text"
        storage_mock.return_value.upload_file.return_value = "test.pdf"
        storage_mock.return_value.get_file_url.return_value = "http://fake-url"
        embedding_mock.return_value.get_embedding.return_value = [0.1] * 384
        
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        await client_with_token.post("/resumes", files=files)
        
        response = await client_with_token.get("/matching/jobs")
        assert response.status_code == 200
        
async def test_matching_jobs_without_resume(client_with_token):
    response = await client_with_token.get("/matching/jobs")
    assert response.status_code == 404