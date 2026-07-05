async def test_stats_aggregates_tickets(client, seeded_tickets):
    response = await client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["by_status"] == {"open": 2, "closed": 1}
    assert body["by_priority"] == {"low": 1, "medium": 1, "high": 1}


async def test_stats_cache_is_invalidated_on_write(client, seeded_tickets, auth_headers):
    response = await client.get("/stats")
    assert response.json()["total"] == 3

    await client.post(
        "/tickets", json={"title": "New", "priority": "low"}, headers=auth_headers
    )

    response = await client.get("/stats")
    assert response.json()["total"] == 4


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
