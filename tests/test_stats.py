import pytest


@pytest.mark.stats
def test_stats_by_month(client, auth_headers):
    # 创建一个分类
    category_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    )
    category_id = category_response.json()["id"]

    # 创建一条记录
    record_payload = {
        "category_id": category_id,
        "amount": 100.0,
        "note": "测试记录",
        "type": "expense",
        "occurred_at": "2024-01-15"
    }
    client.post("/records", headers=auth_headers, json=record_payload)

    # 获取统计数据
    response = client.get("/stats/monthly?year=2024&month=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2024
    assert data["month"] == 1
    assert data["income"] == 0.0
    assert data["expense"] == 100.0
    assert data["balance"] == -100.0


@pytest.mark.stats
def test_stats_by_category(client, auth_headers):
    # 创建一个分类
    category_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    )
    category_id = category_response.json()["id"]

    # 创建一条记录
    record_payload = {
        "category_id": category_id,
        "amount": 100.0,
        "note": "测试记录",
        "type": "expense",
        "occurred_at": "2024-01-15"
    }
    client.post("/records", headers=auth_headers, json=record_payload)

    # 获取按分类统计数据
    response = client.get(
        "/stats/by-category?start=2024-01-01&end=2024-01-31", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category_id"] == category_id
    assert data[0]["category_name"] == "测试分类"
    assert data[0]["category_type"] == "expense"
    assert data[0]["amount"] == 100.0


@pytest.mark.stats
def test_stats_monthly_user_data_is_isolated(client, login_headers):
    # 使用两个独立用户
    userA_headers = login_headers("stats_A@test.com")
    userB_headers = login_headers("stats_B@test.com")

    # 用户 A 创建收入、支出两个分类
    income_category_response = client.post(
        "/categories",
        headers=userA_headers,
        json={"name": "A收入分类", "type": "income"}
    ).json()

    expense_category_response = client.post(
        "/categories",
        headers=userA_headers,
        json={"name": "A支出分类", "type": "expense"}
    ).json()

    # 用户 B 创建一个分类
    userB_category_response = client.post(
        "/categories",
        headers=userB_headers,
        json={"name": "B支出分类", "type": "expense"}
    ).json()

    # 用户 A 创建收入和支出记录
    client.post(
        "/records",
        headers=userA_headers,
        json={
            "category_id": income_category_response["id"],
            "amount": 200.0,
            "note": "A收入记录",
            "type": "income",
            "occurred_at": "2026-01-10"
        }
    )
    client.post(
        "/records",
        headers=userA_headers,
        json={
            "category_id": expense_category_response["id"],
            "amount": 100.0,
            "note": "A支出记录",
            "type": "expense",
            "occurred_at": "2026-01-15"
        }
    )

    # 用户 B 创建支出记录
    client.post(
        "/records",
        headers=userB_headers,
        json={
            "category_id": userB_category_response["id"],
            "amount": 150.0,
            "note": "B支出记录",
            "type": "expense",
            "occurred_at": "2026-01-20"
        }
    )

    response_A = client.get(
        "/stats/monthly",
        headers=userA_headers,
        params={"year": 2026, "month": 1}
    )
    response_B = client.get(
        "/stats/monthly",
        headers=userB_headers,
        params={"year": 2026, "month": 1}
    )

    assert response_A.status_code == 200
    assert response_B.status_code == 200

    # 验证两个用户的统计数据隔离
    assert response_A.json()["income"] == 200.0
    assert response_A.json()["expense"] == 100.0
    assert response_A.json()["balance"] == 100.0

    assert response_B.json()["income"] == 0.0
    assert response_B.json()["expense"] == 150.0
    assert response_B.json()["balance"] == -150.0


@pytest.mark.stats
def test_stats_by_category_isolated(client, login_headers):
    # 使用两个独立用户
    userA_headers = login_headers("category_A@test.com")
    userB_headers = login_headers("category_B@test.com")

    # 两个用户都创建同名分类，避免分类名影响测试准确性
    category_A_response = client.post(
        "/categories",
        headers=userA_headers,
        json={"name": "分类", "type": "expense"}
    )
    category_B_response = client.post(
        "/categories",
        headers=userB_headers,
        json={"name": "分类", "type": "expense"}
    )

    assert category_A_response.status_code == 201
    assert category_B_response.status_code == 201

    category_A_id = category_A_response.json()["id"]
    category_B_id = category_B_response.json()["id"]
    assert category_A_id != category_B_id  # 确保两个用户的分类ID不同

    # 分类名、日期、金额都相同
    userA_record = client.post(
        "/records",
        headers=userA_headers,
        json={
            "category_id": category_A_id,
            "amount": 100.0,
            "note": "记录",
            "type": "expense",
            "occurred_at": "2026-01-20"
        }
    )
    userB_record = client.post(
        "/records",
        headers=userB_headers,
        json={
            "category_id": category_B_id,
            "amount": 150.0,
            "note": "记录",
            "type": "expense",
            "occurred_at": "2026-01-20"
        }
    )

    assert userA_record.status_code == 201
    assert userB_record.status_code == 201

    params = {
        "start": "2026-01-01",
        "end": "2026-01-31"
    }

    # 验证两个用户的统计数据隔离
    response_A = client.get(
        "/stats/by-category",
        headers=userA_headers,
        params=params
    )
    response_B = client.get(
        "/stats/by-category",
        headers=userB_headers,
        params=params
    )

    assert response_A.status_code == 200
    assert response_B.status_code == 200

    data_A = response_A.json()
    data_B = response_B.json()

    assert len(data_A) == 1
    assert len(data_B) == 1

    assert data_A[0]["category_id"] == category_A_id
    assert data_A[0]["amount"] == 100.0
    assert data_A[0]["category_name"] == "分类"
    assert data_A[0]["percentage"] == 100.0

    assert data_B[0]["category_id"] == category_B_id
    assert data_B[0]["amount"] == 150.0
    assert data_B[0]["category_name"] == "分类"
    assert data_B[0]["percentage"] == 100.0
