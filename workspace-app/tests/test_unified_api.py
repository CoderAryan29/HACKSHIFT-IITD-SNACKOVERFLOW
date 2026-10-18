from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "workspace-app"))

import core_api.main as unified_api


def test_saving_profile_persists_verified_firebase_email_and_name(monkeypatch) -> None:
    from agent_service.auth import get_current_user
    from core_api.db.session import get_db

    class FakeResult:
        def mappings(self):
            return self

        def one(self):
            return {
                "uid": "firebase-user",
                "role": "farmer",
                "display_name": "Kisan Farmer",
                "phone": None,
                "state": None,
                "district_name": None,
                "farm_size_acres": None,
                "land_ownership": None,
                "crops": [],
                "buyer_interests": [],
                "lat": None,
                "lng": None,
                "onboarding_completed": False,
                "questionnaire_completed": False,
            }

    class FakeDatabase:
        statement = ""
        parameters = {}
        committed = False

        def execute(self, statement, parameters):
            self.statement = str(statement)
            self.parameters = parameters
            return FakeResult()

        def commit(self):
            self.committed = True

    database = FakeDatabase()
    monkeypatch.setitem(
        unified_api.app.dependency_overrides,
        get_current_user,
        lambda: {
            "uid": "firebase-user",
            "email": "farmer@example.com",
            "name": "Kisan Farmer",
        },
    )
    monkeypatch.setitem(
        unified_api.app.dependency_overrides,
        get_db,
        lambda: database,
    )

    with TestClient(unified_api.app) as client:
        response = client.put("/auth/profile", json={"role": "farmer"})

    assert response.status_code == 200
    assert response.json()["uid"] == "firebase-user"
    assert response.json()["role"] == "farmer"
    assert response.json()["questionnaire_completed"] is False
    assert "email, display_name, role, onboarding_completed" in database.statement
    assert database.parameters == {
        "uid": "firebase-user",
        "email": "farmer@example.com",
        "display_name": "Kisan Farmer",
        "role": "farmer",
    }
    assert database.committed


def test_questionnaire_saves_optional_location_and_details(monkeypatch) -> None:
    from agent_service.auth import get_current_user
    from core_api.db.session import get_db

    class FakeResult:
        def mappings(self):
            return self

        def first(self):
            return {"role": "farmer"}

        def one(self):
            return {
                "uid": "firebase-user",
                "role": "farmer",
                "display_name": "Asha",
                "phone": "9999999999",
                "state": "Haryana",
                "district_name": "Sonipat",
                "farm_size_acres": 3.5,
                "land_ownership": "Owner",
                "crops": ["Wheat"],
                "buyer_interests": [],
                "lat": 28.9931,
                "lng": 77.0151,
                "onboarding_completed": True,
                "questionnaire_completed": True,
            }

    class FakeDatabase:
        statements = []
        parameters = []
        committed = False

        def execute(self, statement, parameters):
            self.statements.append(str(statement))
            self.parameters.append(parameters)
            return FakeResult()

        def commit(self):
            self.committed = True

    database = FakeDatabase()
    monkeypatch.setitem(
        unified_api.app.dependency_overrides,
        get_current_user,
        lambda: {
            "uid": "firebase-user",
            "email": "farmer@example.com",
            "name": "Asha",
        },
    )
    monkeypatch.setitem(unified_api.app.dependency_overrides, get_db, lambda: database)

    with TestClient(unified_api.app) as client:
        response = client.put(
            "/auth/questionnaire",
            json={
                "display_name": "Asha",
                "phone": "9999999999",
                "state": "Haryana",
                "district_name": "Sonipat",
                "farm_size_acres": 3.5,
                "land_ownership": "Owner",
                "crops": ["Wheat"],
                "lat": 28.9931,
                "lng": 77.0151,
            },
        )

    assert response.status_code == 200
    assert response.json()["questionnaire_completed"] is True
    assert database.parameters[1]["lat"] == 28.9931
    assert database.parameters[1]["lng"] == 77.0151
    assert database.parameters[1]["crops"] == ["Wheat"]
    assert database.committed


def test_questionnaire_rejects_partial_coordinates(monkeypatch) -> None:
    from agent_service.auth import get_current_user

    monkeypatch.setitem(
        unified_api.app.dependency_overrides,
        get_current_user,
        lambda: {"uid": "firebase-user", "email": "farmer@example.com", "name": "Asha"},
    )

    with TestClient(unified_api.app) as client:
        response = client.put("/auth/questionnaire", json={"lat": 28.9})

    assert response.status_code == 422
    assert response.json()["detail"] == "Latitude and longitude must be submitted together."


def test_unified_app_mounts_existing_service_routes() -> None:
    paths = set(unified_api.app.openapi()["paths"])

    assert {
        "/health",
        "/health/db",
        "/health/ml",
        "/predict",
        "/prices/",
        "/mandis",
        "/agent/v1/health",
        "/agent/v1/chat",
        "/auth/profile",
        "/auth/questionnaire",
    }.issubset(paths)


def test_price_record_filter_accepts_plural_commodity_names() -> None:
    from sqlalchemy.dialects import postgresql

    from core_api.api.market import get_price_records

    class FakeQuery:
        def __init__(self) -> None:
            self.filters = []

        def join(self, *_args):
            return self

        def filter(self, *expressions):
            self.filters.extend(expressions)
            return self

        def order_by(self, *_expressions):
            return self

        def limit(self, _count):
            return self

        def all(self):
            return []

    class FakeDatabase:
        query_instance = FakeQuery()

        def query(self, *_entities):
            return self.query_instance

    database = FakeDatabase()
    result = get_price_records(commodity="Tomatoes", days=90, db=database)
    commodity_filter = database.query_instance.filters[-1]
    compiled = commodity_filter.compile(dialect=postgresql.dialect())

    assert result["count"] == 0
    assert "regexp_replace" in str(compiled)
    assert any(
        isinstance(value, str) and value.casefold() == "tomatoes"
        for value in compiled.params.values()
    )


def test_missing_model_degrades_health_without_blocking_other_routes(monkeypatch) -> None:
    def model_unavailable(state) -> None:
        state.interpreter = None
        state.labels = None
        state.inference_lock = None
        state.model_error = "TFLite model cache is unavailable."

    monkeypatch.setattr(unified_api, "initialize_model_state", model_unavailable)

    with TestClient(unified_api.app) as client:
        health = client.get("/health")
        model_health = client.get("/health/ml")
        root = client.get("/")

    assert health.status_code == 200
    assert health.json()["status"] == "degraded"
    assert health.json()["services"]["disease_model"]["ready"] is False
    assert model_health.status_code == 503
    assert root.status_code == 200


def test_chat_requires_verified_firebase_identity(monkeypatch) -> None:
    def model_unavailable(state) -> None:
        state.interpreter = None
        state.labels = None
        state.inference_lock = None
        state.model_error = "not loaded in this test"

    monkeypatch.setattr(unified_api, "initialize_model_state", model_unavailable)

    with TestClient(unified_api.app) as client:
        response = client.post(
            "/agent/v1/chat",
            json={"message": "Hello", "thread_id": "test-thread", "user_uid": "forged"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "A Firebase ID token is required."


def test_alternate_vite_port_is_allowed_by_cors(monkeypatch) -> None:
    def model_unavailable(state) -> None:
        state.interpreter = None
        state.labels = None
        state.inference_lock = None
        state.model_error = "not loaded in this test"

    monkeypatch.setattr(unified_api, "initialize_model_state", model_unavailable)

    with TestClient(unified_api.app) as client:
        response = client.options(
            "/agent/v1/chat",
            headers={
                "Origin": "http://127.0.0.1:5174",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"
