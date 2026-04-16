def test_report_tagging_and_search(client_org1_admin, seeded):
    create_response = client_org1_admin.post(
        "/api/v1/reports",
        json={
            "title": "NVIDIA Earnings Deep Dive",
            "query_text": "Analyze NVDA earnings",
            "summary": "Initial summary",
        },
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["id"]

    add_tag = client_org1_admin.post(f"/api/v1/reports/{report_id}/tags?name=q3-earnings")
    assert add_tag.status_code == 200
    assert any(tag["name"] == "q3-earnings" for tag in add_tag.json()["tags"])

    filtered_by_tag = client_org1_admin.get("/api/v1/reports?tag=q3-earnings")
    assert filtered_by_tag.status_code == 200
    assert len(filtered_by_tag.json()) == 1
    assert filtered_by_tag.json()[0]["id"] == report_id

    filtered_by_search = client_org1_admin.get("/api/v1/reports?search=NVIDIA")
    assert filtered_by_search.status_code == 200
    assert len(filtered_by_search.json()) == 1
    assert filtered_by_search.json()[0]["id"] == report_id

    remove_tag = client_org1_admin.delete(f"/api/v1/reports/{report_id}/tags/q3-earnings")
    assert remove_tag.status_code == 200
    assert remove_tag.json()["tags"] == []
