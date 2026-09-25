import pytest
from httpx import AsyncClient

from tests.conftest import authenticated_client, create_test_client


@pytest.mark.anyio
async def test_success_upload(authenticated_client: AsyncClient):
    client = await create_test_client(client=authenticated_client)
    print(client)
    document = await authenticated_client.post(f"/api/documents/upload?name=TestDoc?client_id={client.get('id')}?doc_type=report")
    print(document)



