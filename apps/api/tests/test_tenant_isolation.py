def test_reports_are_tenant_isolated(client_org1_admin, client_org2_analyst, seeded):
    create_response = client_org1_admin.post(
        "/api/v1/reports",
        json={
            "title": "Org1 Report",
            "query_text": "Analyze NVDA",
            "summary": "summary",
        },
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["id"]

    list_org2 = client_org2_analyst.get("/api/v1/reports")
    assert list_org2.status_code == 200
    assert list_org2.json() == []

    read_org2 = client_org2_analyst.get(f"/api/v1/reports/{report_id}")
    assert read_org2.status_code == 404


def test_org_invite_requires_admin(client_org2_analyst, seeded):
    invite_response = client_org2_analyst.post("/api/v1/orgs/invites")
    assert invite_response.status_code == 403
