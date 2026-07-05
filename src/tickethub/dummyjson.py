from typing import Any

import httpx

from tickethub.config import settings


async def fetch_todos() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(base_url=settings.dummyjson_url, timeout=30) as client:
        response = await client.get("/todos", params={"limit": 0})
        response.raise_for_status()
        return response.json()["todos"]


async def fetch_users() -> dict[int, str]:
    async with httpx.AsyncClient(base_url=settings.dummyjson_url, timeout=30) as client:
        response = await client.get("/users", params={"limit": 0, "select": "id,username"})
        response.raise_for_status()
        return {user["id"]: user["username"] for user in response.json()["users"]}


async def login(username: str, password: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(base_url=settings.dummyjson_url, timeout=30) as client:
        response = await client.post(
            "/auth/login", json={"username": username, "password": password}
        )
        if response.status_code != 200:
            return None
        return response.json()
