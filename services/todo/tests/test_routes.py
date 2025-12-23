import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app import create_app, get_db
from app.models import TodoItem


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_todo_item():
    """Создает реальный объект TodoItem для тестов"""
    item = TodoItem(
        id=1,
        title='Test Task',
        description='Test Description',
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return item


@pytest.fixture
def mock_db_session():
    """Создает моковую сессию БД"""
    return MagicMock()


def test_get_items_empty(client, mock_db_session):
    mock_db_session.query.return_value.all.return_value = []
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/todo')
        assert response.status_code == 200
        assert response.json() == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_items(client, mock_todo_item, mock_db_session):
    mock_db_session.query.return_value.all.return_value = [mock_todo_item]
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/todo')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 1
        assert response.json()[0]['title'] == 'Test Task'
        assert response.json()[0]['description'] == 'Test Description'
        assert response.json()[0]['completed'] is False
    finally:
        client.app.dependency_overrides.clear()


def test_get_item(client, mock_todo_item, mock_db_session):
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/todo/1')
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['title'] == 'Test Task'
        assert response.json()['description'] == 'Test Description'
        assert response.json()['completed'] is False
    finally:
        client.app.dependency_overrides.clear()


def test_get_item_not_found(client, mock_db_session):
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/api/todo/999')
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_create_item(client, mock_db_session):
    data = {
        'title': 'New Task',
        'description': 'New Description',
        'completed': False
    }
    mock_item = TodoItem(
        id=1,
        title='New Task',
        description='New Description',
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Мокируем создание TodoItem объекта
    with patch('app.routes.TodoItem') as mock_item_class:
        mock_item_class.return_value = mock_item
        client.app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            response = client.post('/api/todo', json=data)
            assert response.status_code == 201
            assert response.json()['title'] == 'New Task'
            assert response.json()['description'] == 'New Description'
            assert response.json()['completed'] is False
            assert 'id' in response.json()
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
        finally:
            client.app.dependency_overrides.clear()


def test_create_item_minimal(client, mock_db_session):
    """Тест создания задачи только с title"""
    data = {
        'title': 'Minimal Task'
    }
    mock_item = TodoItem(
        id=1,
        title='Minimal Task',
        description=None,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    with patch('app.routes.TodoItem') as mock_item_class:
        mock_item_class.return_value = mock_item
        client.app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            response = client.post('/api/todo', json=data)
            assert response.status_code == 201
            assert response.json()['title'] == 'Minimal Task'
            assert response.json()['description'] is None
            assert response.json()['completed'] is False
        finally:
            client.app.dependency_overrides.clear()


def test_create_item_validation_error_empty_title(client):
    data = {
        'title': '',
        'description': 'Description'
    }
    response = client.post('/api/todo', json=data)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    assert 'detail' in response.json()


def test_create_item_validation_error_missing_title(client):
    data = {
        'description': 'Description without title'
    }
    response = client.post('/api/todo', json=data)
    assert response.status_code == 422
    assert 'detail' in response.json()


def test_update_item(client, mock_todo_item, mock_db_session):
    data = {
        'title': 'Updated Task',
        'description': 'Updated Description',
        'completed': True
    }
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/todo/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Task'
        assert response.json()['description'] == 'Updated Description'
        assert response.json()['completed'] is True
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_update_item_partial_title(client, mock_todo_item, mock_db_session):
    """Тест частичного обновления - только title"""
    data = {
        'title': 'Updated Title Only'
    }
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/todo/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Updated Title Only'
        assert response.json()['description'] == 'Test Description'  # Остается прежним
        assert response.json()['completed'] is False  # Остается прежним
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_update_item_partial_completed(client, mock_todo_item, mock_db_session):
    """Тест частичного обновления - только completed"""
    data = {
        'completed': True
    }
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/todo/1', json=data)
        assert response.status_code == 200
        assert response.json()['title'] == 'Test Task'  # Остается прежним
        assert response.json()['completed'] is True
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_update_item_not_found(client, mock_db_session):
    data = {
        'title': 'Updated Task',
        'completed': True
    }
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/todo/999', json=data)
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_update_item_validation_error(client, mock_todo_item, mock_db_session):
    data = {
        'title': '',  # Пустой title недопустим
        'completed': True
    }
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.put('/api/todo/1', json=data)
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_delete_item(client, mock_todo_item, mock_db_session):
    mock_db_session.get.return_value = mock_todo_item
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.delete('/api/todo/1')
        assert response.status_code == 200
        assert response.json()['message'] == 'Item deleted successfully'
        mock_db_session.delete.assert_called_once_with(mock_todo_item)
        mock_db_session.commit.assert_called_once()
    finally:
        client.app.dependency_overrides.clear()


def test_delete_item_not_found(client, mock_db_session):
    mock_db_session.get.return_value = None
    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.delete('/api/todo/999')
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()

