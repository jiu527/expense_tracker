import pytest


def register_user(client, email, password):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def login_user(client, username, password):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )


@pytest.mark.register
def test_register_success(client):
    response = register_user(client, "test1@test.com", "testpassword")
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test1@test.com"
    assert "id" in data


@pytest.mark.register
def test_register_existing_user(client):
    # 首先注册一个用户
    register_user(client, "test2@test.com", "testpassword")
    # 尝试注册相同的邮箱
    response = register_user(client, "test2@test.com", "testpassword")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "邮箱已注册"


@pytest.mark.register
def test_register_short_password(client):
    response = register_user(client, "test3@test.com", "short")
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert data["detail"][0]["msg"] == "登录密码不能少于 8 个字符"


@pytest.mark.login
def test_login_success(client):
    # 首先注册一个用户
    register_user(client, "test4@test.com", "testpassword")
    # 然后尝试登录
    response = login_user(client, "test4@test.com", "testpassword")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.login
def test_login_wrong_password(client):
    # 首先注册一个用户
    register_user(client, "test5@test.com", "testpassword")
    # 然后尝试使用错误的密码登录
    response = login_user(client, "test5@test.com", "wrongpassword")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "邮箱或密码错误"


@pytest.mark.login
def test_login_notoken_access(client):
    # 尝试在不提供 token 的情况下访问受保护的接口
    response = client.get("/stats/by-category")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "未提供有效的访问令牌"