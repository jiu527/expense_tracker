import pytest


@pytest.mark.record
def test_create_record(client, auth_headers):
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
        "occurred_at": "2024-01-01"
    }
    response = client.post("/records", headers=auth_headers, json=record_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category_id"] == category_id
    assert data["amount"] == "100.00"
    assert data["note"] == "测试记录"
    assert data["type"] == "expense"


@pytest.mark.record
@pytest.mark.parametrize(
    "amount",
    [
        "-100.0",  # 负数金额
        "0.0",     # 零金额
        "10000000000.0",  # 超过最大值
    ]
)
def test_create_record_invalid_amount(client, auth_headers, amount):
    # 创建一个分类
    category_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    )
    category_id = category_response.json()["id"]

    record_payload = {
        "category_id": category_id,
        "amount": amount,
        "note": "测试记录",
        "type": "expense",
        "occurred_at": "2024-01-01"
    }
    response = client.post("/records", headers=auth_headers, json=record_payload)
    assert response.status_code == 422  # 应该返回验证错误


@pytest.mark.record
def test_create_record_rejects_more_than_two_decimal_places(client, auth_headers):
    # 创建一个分类
    category_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    )
    category_id = category_response.json()["id"]

    record_payload = {
        "category_id": category_id,
        "amount": 100.123,  # 超过两位小数
        "note": "测试记录",
        "type": "expense",
        "occurred_at": "2024-01-01"
    }
    response = client.post("/records", headers=auth_headers, json=record_payload)
    assert response.status_code == 422  # 应该返回验证错误


@pytest.mark.record
def test_delete_record(client, auth_headers):
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
        "occurred_at": "2024-01-01"
    }
    create_response = client.post("/records", headers=auth_headers, json=record_payload)
    record_id = create_response.json()["id"]

    # 删除记录
    delete_response = client.delete(f"/records/{record_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # 确认记录已删除
    get_response = client.get("/records", headers=auth_headers)
    records = get_response.json()["items"]
    assert all(record["id"] != record_id for record in records)


@pytest.mark.record
def test_update_record(client, auth_headers):
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
        "occurred_at": "2024-01-01"
    }
    create_response = client.post("/records", headers=auth_headers, json=record_payload)
    record_id = create_response.json()["id"]

    # 更新记录
    update_payload = {
        "amount": 150.0,
        "note": "更新后的记录"
    }
    update_response = client.patch(f"/records/{record_id}", headers=auth_headers, json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["amount"] == "150.00"
    assert updated_data["note"] == "更新后的记录"


@pytest.mark.record
def test_list_records_pagination(client, auth_headers):
    # 创建一个分类
    category_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    ).json()

    for day in range(1, 11):  # 创建10条记录
        record_response = client.post(
            "/records",
            headers=auth_headers,
            json={
                "category_id": category_response["id"],
                "amount": 10.0 * day,
                "note": f"记录{day}",
                "type": "expense",
                "occurred_at": f"2024-01-{day:02d}"
            }
        )
        assert record_response.status_code == 201

    # 列出第一页记录
    first_page_response = client.get(
        "/records",
        headers=auth_headers,
        params={"page": 1, "page_size": 5}
    )

    assert first_page_response.status_code == 200
    assert first_page_response.json()["total"] == 10
    assert first_page_response.json()["page"] == 1
    assert first_page_response.json()["page_size"] == 5
    assert len(first_page_response.json()["items"]) == 5

    # 列出第二页记录
    second_page_response = client.get(
        "/records",
        headers=auth_headers,
        params={"page": 2, "page_size": 5}
    )

    assert second_page_response.status_code == 200
    assert second_page_response.json()["total"] == 10
    assert second_page_response.json()["page"] == 2
    assert second_page_response.json()["page_size"] == 5
    assert len(second_page_response.json()["items"]) == 5

    assert first_page_response.json()["items"][0]["note"] == "记录10"  # 最新的记录在前
    assert second_page_response.json()["items"][0]["note"] == "记录5"  # 第二页的第一条记录


@pytest.mark.record
def test_list_records_invalid_date_range(client, auth_headers):
    response = client.get(
        "/records",
        headers=auth_headers,
        params={"start": "2024-01-10", "end": "2024-01-01"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "start不能晚于end"


@pytest.mark.record
def test_list_records_filters(client, auth_headers):
    income_category = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "收入分类", "type": "income"}
    ).json()

    expense_category = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "支出分类", "type": "expense"}
    ).json()

    # 创建一些记录用于测试过滤
    for i in range(1, 6):
        client.post(
            "/records",
            headers=auth_headers,
            json={
                "category_id": income_category["id"],
                "amount": 100.0 * i,
                "note": f"收入记录{i}",
                "type": "income",
                "occurred_at": f"2024-01-{i:02d}"
            }
        )

    for i in range(6, 11):
        client.post(
            "/records",
            headers=auth_headers,
            json={
                "category_id": expense_category["id"],
                "amount": 50.0 * i,
                "note": f"支出记录{i}",
                "type": "expense",
                "occurred_at": f"2024-01-{i:02d}"
            }
        )

    # 测试按类型过滤
    income_response = client.get(
        "/records",
        headers=auth_headers,
        params={
            "start": "2024-01-01",
            "end": "2024-01-31",
            "category_id": income_category["id"],
            "type": "income"
        }
    )
    assert income_response.status_code == 200
    data = income_response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert all(record["type"] == "income" for record in data["items"])

    expense_response = client.get(
        "/records",
        headers=auth_headers,
        params={
            "start": "2024-01-01",
            "end": "2024-01-31",
            "category_id": expense_category["id"],
            "type": "expense"
        }
    )
    assert expense_response.status_code == 200
    data = expense_response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert all(record["type"] == "expense" for record in data["items"])
