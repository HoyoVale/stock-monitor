"""Tests for authentication service and API."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.auth import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_and_verify(self):
        password = "secure123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_hash_is_deterministic_within_verify(self):
        password = "test"
        h1 = hash_password(password)
        h2 = hash_password(password)
        # Each hash should be different (different salt)
        assert h1 != h2
        # Both should verify
        assert verify_password(password, h1)
        assert verify_password(password, h2)


class TestJWTToken:
    """Test JWT token creation and decoding."""

    def test_create_and_decode(self):
        token = create_access_token({"sub": "testuser"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        payload = decode_access_token("not.a.token")
        assert payload is None

    def test_decode_expired_token(self):
        from datetime import timedelta
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(seconds=-1),
        )
        payload = decode_access_token(token)
        assert payload is None


class TestAuthAPI:
    """Test auth API endpoints."""

    @pytest.fixture
    def test_user_data(self):
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "secure123",
        }

    @pytest.mark.asyncio
    async def test_register_and_login(self, db_session: AsyncSession):
        from app.database import get_db

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)

        try:
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Register
                resp = await client.post("/api/auth/register", json={
                    "username": "newuser",
                    "email": "new@test.com",
                    "password": "mypassword",
                })
                assert resp.status_code == 201
                data = resp.json()
                assert "access_token" in data
                assert data["username"] == "newuser"

                # Login
                resp = await client.post("/api/auth/login", json={
                    "username": "newuser",
                    "password": "mypassword",
                })
                assert resp.status_code == 200
                data = resp.json()
                assert "access_token" in data

                # Get /me with token
                token = data["access_token"]
                resp = await client.get("/api/auth/me", headers={
                    "Authorization": f"Bearer {token}",
                })
                assert resp.status_code == 200
                me = resp.json()
                assert me["username"] == "newuser"
                assert me["email"] == "new@test.com"

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, db_session: AsyncSession):
        from app.database import get_db

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)

        try:
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # First registration
                await client.post("/api/auth/register", json={
                    "username": "dupuser",
                    "email": "dup1@test.com",
                    "password": "password",
                })
                # Duplicate
                resp = await client.post("/api/auth/register", json={
                    "username": "dupuser",
                    "email": "dup2@test.com",
                    "password": "password",
                })
                assert resp.status_code == 400
                assert "已存在" in resp.json()["detail"]

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_bad_credentials(self, db_session: AsyncSession):
        from app.database import get_db

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)

        try:
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/auth/login", json={
                    "username": "nobody",
                    "password": "wrong",
                })
                assert resp.status_code == 401

        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_me_without_token(self, db_session: AsyncSession):
        from app.database import get_db

        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)

        try:
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/auth/me")
                assert resp.status_code == 401

        finally:
            app.dependency_overrides.clear()
