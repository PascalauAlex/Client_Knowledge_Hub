import pytest
from httpx import AsyncClient
from pathlib import Path
from tests.conftest import authenticated_client, create_test_client


@pytest.mark.anyio
async def test_success_upload(authenticated_client: AsyncClient):
    client = await create_test_client(client=authenticated_client)
    client_id = client.get("id")
    docs_dir = Path(__file__).parent / "demo_docs"
    file_path = docs_dir / "quarterly_report.pdf"

    with open(file_path,"rb+") as file:
        content = file.read()

    response = await authenticated_client.post("/api/documents/upload",
                                               params={
                                                   "name":"quarterly_report.pdf",
                                                   "client_id":client_id,
                                                   "doc_type":"report"
                                               },
                                               # UploadFile expects a file , it's name, bytes content and MIME type
                                                files={"file":("quarterly_report.pdf",content,"application/pdf")}
                                               )
    assert response.status_code == 201, response.text
    document = response.json()
    assert document.get("name") == "quarterly_report.pdf"
    assert document.get("client_id") == client_id
    assert document.get("type") == "report"
    assert document.get("extension_type") == ".pdf"
    print(document.get("file"))






