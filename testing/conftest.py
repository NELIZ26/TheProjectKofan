import importlib
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.core.security import hash_password


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def test_db(monkeypatch):
    """Crea una base de datos MongoDB en memoria para no tocar Atlas."""
    mock_client = AsyncMongoMockClient()
    db = mock_client["ecohotel_kofan_test_db"]

    modules_to_patch = [
        "backend.db.client",
        "backend.main",
        "backend.services.user_service",
        "backend.services.booking_service",
        "backend.services.room_service",
        "backend.services.config_service",
        "backend.services.dashboard_service",
        "backend.services.gallery_service",
        "backend.services.notifications_service",
        "backend.services.task_service",
        "backend.routers.rooms",
        "backend.routers.invoices",
    ]

    for module_name in modules_to_patch:
        module = importlib.import_module(module_name)
        if hasattr(module, "db"):
            monkeypatch.setattr(module, "db", db, raising=False)

    room_service = importlib.import_module("backend.services.room_service")
    monkeypatch.setattr(room_service, "collection", db.rooms, raising=False)
    monkeypatch.setattr(room_service, "logs_collection", db.room_logs, raising=False)

    yield db

    await mock_client.drop_database("ecohotel_kofan_test_db")


@pytest_asyncio.fixture
async def api_client(test_db):
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def admin_user(test_db):
    admin_doc = {
        "tipo_persona": "natural",
        "full_name": "Administrador Kofan",
        "type_document": "CC",
        "number_document": "10000001",
        "email": "admin@kofan.test",
        "country": "Colombia",
        "city": "Puerto Asís",
        "phone": "3200000001",
        "role": "admin",
        "is_active": True,
        "password": hash_password("Admin123*"),
    }
    result = await test_db.users.insert_one(admin_doc)
    admin_doc["_id"] = result.inserted_id
    return admin_doc


@pytest_asyncio.fixture
async def client_user(test_db):
    client_doc = {
        "tipo_persona": "natural",
        "full_name": "Cliente Kofan",
        "type_document": "CC",
        "number_document": "10000002",
        "email": "cliente@kofan.test",
        "country": "Colombia",
        "city": "Mocoa",
        "phone": "3200000002",
        "role": "client",
        "is_active": True,
        "password": hash_password("Cliente123*"),
    }
    result = await test_db.users.insert_one(client_doc)
    client_doc["_id"] = result.inserted_id
    return client_doc


@pytest_asyncio.fixture
async def admin_headers(api_client, admin_user):
    response = await api_client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "Admin123*"},
    )
    data = response.json()
    return {"Authorization": f"{data['token_type']} {data['access_token']}"}


@pytest_asyncio.fixture
async def sample_room(test_db):
    room_doc = {
        "room_number": "101",
        "name": "Cabaña Río",
        "description": "Vista a la selva",
        "price": 180000,
        "capacity": 2,
        "stock": 1,
        "images": [],
        "main_image": None,
        "active": True,
        "is_available": True,
        "type": "cabins",
        "num_cuartos": 1,
        "tipo_camas": "1 cama doble",
        "amenities": ["Wifi", "Baño Privado"],
        "created_by": "admin@kofan.test",
        "updated_by": "admin@kofan.test",
    }
    result = await test_db.rooms.insert_one(room_doc)
    room_doc["_id"] = result.inserted_id
    return room_doc
