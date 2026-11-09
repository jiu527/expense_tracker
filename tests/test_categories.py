import pytest


@pytest.mark.category
def test_create_category(client, auth_headers):

    response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "测试分类", "type": "expense"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "测试分类"
    assert response.json()["type"] == "expense"


@pytest.mark.category
def test_list_categories(client, auth_headers):

    # 创建两个分类
    client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "分类1", "type": "expense"}
    )
    client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "分类2", "type": "income"}
    )

    # 列出分类
    response = client.get("/categories", headers=auth_headers)
    assert response.status_code == 200
    categories = response.json()
    assert [cat["name"] for cat in categories] == ["分类1", "分类2"]
    assert [cat["type"] for cat in categories] == ["expense", "income"]


@pytest.mark.category
def test_update_category(client, auth_headers):

    # 创建一个分类
    create_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "旧分类", "type": "expense"}
    )
    category_id = create_response.json()["id"]

    # 更新分类
    update_response = client.patch(
        f"/categories/{category_id}",
        headers=auth_headers,
        json={"name": "新分类"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "新分类"
    assert update_response.json()["type"] == "expense"  # 类型未变


@pytest.mark.category
def test_delete_category(client, auth_headers):

    # 创建一个分类
    create_response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "待删除分类", "type": "expense"}
    )
    category_id = create_response.json()["id"]

    # 删除分类
    delete_response = client.delete(f"/categories/{category_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # 确认分类已删除
    get_response = client.get("/categories", headers=auth_headers)
    categories = get_response.json()
    assert all(cat["id"] != category_id for cat in categories)


@pytest.mark.category
@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("patch", {"name": "越权修改"}),
        ("delete", None),
    ],
)
def test_category_forbidden_access_return_404(client, method, payload, login_headers):
    # 用户 A 创建分类
    userA_headers = login_headers("userA@test.com")

    create_response = client.post(
        "/categories",
        headers=userA_headers,
        json={"name": "用户A分类", "type": "expense"}
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    # 用户 B 尝试访问用户 A 的分类
    userB_headers = login_headers("userB@test.com")

    if method == "patch":
        response = client.patch(
            f"/categories/{category_id}",
            headers=userB_headers,
            json=payload,
        )
    elif method == "delete":
        response = client.delete(
            f"/categories/{category_id}",
            headers=userB_headers,
        )
    assert response.status_code == 404
    assert response.json()["detail"] == "分类不存在"

    # 验证分类仍然存在于用户 A 的列表中
    list_response = client.get("/categories", headers=userA_headers)
    assert list_response.status_code == 200
    categories = list_response.json()
    assert any(cat["id"] == category_id for cat in categories)
    assert all(cat["name"] != "越权修改" for cat in categories)  # 确认没有被修改