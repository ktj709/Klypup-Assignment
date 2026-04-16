def test_watchlist_crud_and_tenant_isolation(client_org1_admin, client_org2_analyst, seeded):
    create_response = client_org1_admin.post(
        "/api/v1/watchlist",
        json={"ticker": "NVDA", "company_name": "NVIDIA"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    watchlist_id = created["id"]

    org1_list = client_org1_admin.get("/api/v1/watchlist")
    assert org1_list.status_code == 200
    assert len(org1_list.json()) == 1
    assert org1_list.json()[0]["ticker"] == "NVDA"

    org2_list = client_org2_analyst.get("/api/v1/watchlist")
    assert org2_list.status_code == 200
    assert org2_list.json() == []

    org2_delete_attempt = client_org2_analyst.delete(f"/api/v1/watchlist/{watchlist_id}")
    assert org2_delete_attempt.status_code == 404

    org1_delete = client_org1_admin.delete(f"/api/v1/watchlist/{watchlist_id}")
    assert org1_delete.status_code == 204

    org1_after_delete = client_org1_admin.get("/api/v1/watchlist")
    assert org1_after_delete.status_code == 200
    assert org1_after_delete.json() == []
