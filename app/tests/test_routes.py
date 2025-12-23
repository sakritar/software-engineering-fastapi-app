import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app import create_app, get_db
from app.models import Post


@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_post():
    """Создает реальный объект Post для тестов"""
    post = Post(
        id=1,
        title='Test Post',
        content='Test Content',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return post


@pytest.fixture
def mock_db_session():
    """Создает моковую сессию БД"""
    return MagicMock()


def test_get_posts_empty(client, mock_db_session):
    mock_db_session.query.return_value.all.return_value = []
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert response.json() == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_posts(client, mock_post, mock_db_session):
    mock_db_session.query.return_value.all.return_value = [mock_post]
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 1
        assert response.json()[0]['title'] == 'Test Post'
    finally:
        client.app.dependency_overrides.clear()


def test_get_post(client, mock_post, mock_db_session):
    mock_db_session.get.return_value = mock_post
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/posts/1')
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['title'] == 'Test Post'
        assert response.json()['content'] == 'Test Content'
    finally:
        client.app.dependency_overrides.clear()


def test_get_post_not_found(client, mock_db_session):
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/posts/999')
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_create_post(client, mock_db_session):
    data = {
        'title': 'New Post',
        'content': 'Post content'
    }
    mock_post = Post(
        id=1,
        title='New Post',
        content='Post content',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Мокируем создание Post объекта
    with patch('app.routes.Post') as mock_post_class:
        mock_post_class.return_value = mock_post
        client.app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            response = client.post('/api/posts', json=data)
            assert response.status_code == 201
            assert response.json()['title'] == 'New Post'
            assert response.json()['content'] == 'Post content'
            assert 'id' in response.json()
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
        finally:
            client.app.dependency_overrides.clear()


def test_create_post_validation_error(client):
    data = {
        'title': '',
        'content': 'Post content'
    }
    response = client.post('/api/posts', json=data)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    assert 'detail' in response.json()


def test_update_post(client, mock_post, mock_db_session):
    data = {
        'title': 'Updated Post',
        'content': 'Updated Content'
    }
    mock_db_session.get.return_value = mock_post
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Post'
        assert response.json()['content'] == 'Updated Content'
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_update_post_partial(client, mock_post, mock_db_session):
    data = {
        'title': 'Updated Title Only'
    }
    mock_db_session.get.return_value = mock_post
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Title Only'
        assert response.json()['content'] == 'Test Content'
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_update_post_not_found(client, mock_db_session):
    data = {
        'title': 'Updated Post',
        'content': 'Updated Content'
    }
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/posts/999', json=data)
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_update_post_validation_error(client, mock_post, mock_db_session):
    data = {
        'title': '',
        'content': 'Updated Content'
    }
    mock_db_session.get.return_value = mock_post
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_delete_post(client, mock_post, mock_db_session):
    mock_db_session.get.return_value = mock_post
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.delete('/api/posts/1')
        assert response.status_code == 200
        assert response.json()['message'] == 'Post deleted successfully'
        mock_db_session.delete.assert_called_once_with(mock_post)
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_delete_post_not_found(client, mock_db_session):
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.delete('/api/posts/999')
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()
