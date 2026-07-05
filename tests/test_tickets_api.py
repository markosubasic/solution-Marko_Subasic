async def test_list_tickets_paginated(client, seeded_tickets):
    response = await client.get("/tickets", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["items"][0]["id"] == 1


async def test_list_description_is_truncated_to_100_chars(client, seeded_tickets):
    response = await client.get("/tickets", params={"limit": 10})
    items = {item["id"]: item for item in response.json()["items"]}
    assert len(items[2]["description"]) <= 100
    assert items[2]["description"].endswith("...")


async def test_filter_by_status_and_priority(client, seeded_tickets):
    response = await client.get("/tickets", params={"status": "open"})
    assert response.json()["total"] == 2

    response = await client.get("/tickets", params={"priority": "high"})
    assert response.json()["total"] == 1

    response = await client.get("/tickets", params={"status": "open", "priority": "low"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == 3


async def test_filter_with_invalid_status_returns_422(client, seeded_tickets):
    response = await client.get("/tickets", params={"status": "banana"})
    assert response.status_code == 422


async def test_search_by_title(client, seeded_tickets):
    response = await client.get("/tickets/search", params={"q": "dark"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Add dark mode"


async def test_ticket_detail_includes_raw_source(client, seeded_tickets):
    response = await client.get("/tickets/1")
    assert response.status_code == 200
    body = response.json()
    assert body["assignee"] == "emilys"
    assert body["raw_source"]["todo"] == "Fix login bug"


async def test_ticket_detail_not_found(client, seeded_tickets):
    response = await client.get("/tickets/999")
    assert response.status_code == 404


async def test_create_ticket(client, auth_headers):
    payload = {"title": "New ticket", "priority": "high", "assignee": "marko"}
    response = await client.post("/tickets", json=payload, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["priority"] == "high"

    response = await client.get(f"/tickets/{body['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "New ticket"


async def test_create_ticket_requires_auth(client):
    response = await client.post("/tickets", json={"title": "x", "priority": "low"})
    assert response.status_code == 401


async def test_create_ticket_validates_input(client, auth_headers):
    response = await client.post("/tickets", json={"priority": "low"}, headers=auth_headers)
    assert response.status_code == 422

    response = await client.post(
        "/tickets", json={"title": "x", "priority": "urgent"}, headers=auth_headers
    )
    assert response.status_code == 422


async def test_update_ticket_persists(client, seeded_tickets, auth_headers):
    response = await client.patch(
        "/tickets/1", json={"status": "closed", "assignee": "marko"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "closed"

    response = await client.get("/tickets/1")
    body = response.json()
    assert body["status"] == "closed"
    assert body["assignee"] == "marko"
    assert body["title"] == "Fix login bug"


async def test_update_ticket_requires_auth(client, seeded_tickets):
    response = await client.patch("/tickets/1", json={"status": "closed"})
    assert response.status_code == 401


async def test_update_missing_ticket_returns_404(client, seeded_tickets, auth_headers):
    response = await client.patch("/tickets/999", json={"status": "closed"}, headers=auth_headers)
    assert response.status_code == 404
