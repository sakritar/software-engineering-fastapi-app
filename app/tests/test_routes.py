import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app import create_app
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
    post = MagicMock(spec=Post)
    post.id = 1
    post.title = 'Test Post'
    post.content = 'Test Content'
    post.created_at = datetime.now(timezone.utc)
    post.updated_at = datetime.now(timezone.utc)
    return post


def test_get_posts_empty(client):
    with patch('app.routes.db') as mock_db:
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_db.__enter__.return_value = mock_session
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert response.json() == []


def test_get_posts(client, mock_post):
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = [mock_post]
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.get('/api/posts')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 1
        assert response.json()[0]['title'] == 'Test Post'


def test_get_post(client, mock_post):
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = mock_post
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.get('/api/posts/1')
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['title'] == 'Test Post'
        assert response.json()['content'] == 'Test Content'


def test_get_post_not_found(client):
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.get('/api/posts/999')
        assert response.status_code == 404
        assert 'detail' in response.json()


def test_create_post(client):
    data = {
        'title': 'New Post',
        'content': 'Post content'
    }
    mock_post = MagicMock(spec=Post)
    mock_post.id = 1
    mock_post.title = 'New Post'
    mock_post.content = 'Post content'
    mock_post.created_at = datetime.now(timezone.utc)
    mock_post.updated_at = datetime.now(timezone.utc)
    
    with patch('app.routes.Post') as mock_post_class:
        mock_post_class.return_value = mock_post
        with patch('app.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value.__enter__.return_value = mock_db
            mock_get_db.return_value.__exit__.return_value = None
            response = client.post('/api/posts', json=data)
            assert response.status_code == 201
            assert response.json()['title'] == 'New Post'
            assert response.json()['content'] == 'Post content'
            assert 'id' in response.json()
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()


def test_create_post_validation_error(client):
    data = {
        'title': '',
        'content': 'Post content'
    }
    response = client.post('/api/posts', json=data)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    assert 'detail' in response.json()


def test_update_post(client, mock_post):
    data = {
        'title': 'Updated Post',
        'content': 'Updated Content'
    }
    updated_post = MagicMock(spec=Post)
    updated_post.id = 1
    updated_post.title = 'Updated Post'
    updated_post.content = 'Updated Content'
    updated_post.created_at = mock_post.created_at
    updated_post.updated_at = datetime.now(timezone.utc)
    
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = mock_post
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Post'
        assert response.json()['content'] == 'Updated Content'
        mock_db.commit.assert_called_once()


def test_update_post_partial(client, mock_post):
    data = {
        'title': 'Updated Title Only'
    }
    
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = mock_post
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Title Only'
        assert response.json()['content'] == 'Test Content'
        mock_db.commit.assert_called_once()


def test_update_post_not_found(client):
    data = {
        'title': 'Updated Post',
        'content': 'Updated Content'
    }
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.put('/api/posts/999', json=data)
        assert response.status_code == 404
        assert 'detail' in response.json()


def test_update_post_validation_error(client, mock_post):
    data = {
        'title': '',
        'content': 'Updated Content'
    }
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = mock_post
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.put('/api/posts/1', json=data)
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        assert 'detail' in response.json()


def test_delete_post(client, mock_post):
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = mock_post
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        response = client.delete('/api/posts/1')
        assert response.status_code == 200
        assert response.json()['message'] == 'Post deleted successfully'
        mock_db.delete.assert_called_once_with(mock_post)
        mock_db.commit.assert_called_once()


def test_delete_post_not_found(client):
    with patch('app.routes.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_db.get.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_db
        response = client.delete('/api/posts/999')
        assert response.status_code == 404
        assert 'detail' in response.json()
