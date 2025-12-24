import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app import create_app, get_db
from app.models import ShortUrl

load_dotenv()


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_short_url():
    short_url = ShortUrl(
        id=1,
        short_id='abc12345',
        full_url='https://example.com/very/long/url/path',
        created_at=datetime.now(timezone.utc)
    )
    return short_url


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_shorten_url(client, mock_db_session):
    data = {
        'url': 'https://example.com/very/long/url/path'
    }

    short_id = 'abc12345'

    mock_short_url = ShortUrl(
        id=1,
        short_id=short_id,
        full_url='https://example.com/very/long/url/path',
        created_at=datetime.now(timezone.utc)
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None  # short_id не существует
    mock_db_session.query.return_value = mock_query

    port = os.getenv('URL_SERVICE_PORT', 8000)

    with patch('app.routes.ShortUrl') as mock_short_url_class:
        mock_short_url_class.return_value = mock_short_url
        with patch('app.routes.generate_short_id', return_value='abc12345'):
            client.app.dependency_overrides[get_db] = lambda: mock_db_session
            try:
                response = client.post('/shorten', json=data)
                assert response.status_code == 201
                assert response.json()['short_id'] == short_id
                assert response.json()['short_url'] == f'http://127.0.0.1:{port}/{short_id}'
                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()
            finally:
                client.app.dependency_overrides.clear()


def test_shorten_url_validation_error_invalid_url(client):
    data = {
        'url': 'not-a-valid-url'
    }
    response = client.post('/shorten', json=data)
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    assert 'detail' in response.json()


def test_shorten_url_validation_error_missing_url(client):
    data = {}
    response = client.post('/shorten', json=data)
    assert response.status_code == 422
    assert 'detail' in response.json()


def test_redirect_url(client, mock_short_url, mock_db_session):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_short_url
    mock_db_session.query.return_value = mock_query

    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/abc12345', follow_redirects=False)
        assert response.status_code == 301  # Temporary Redirect
        assert response.headers['location'] == 'https://example.com/very/long/url/path'
    finally:
        client.app.dependency_overrides.clear()


def test_redirect_url_not_found(client, mock_db_session):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query

    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/nonexistent', follow_redirects=False)
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_get_stats(client, mock_short_url, mock_db_session):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_short_url
    mock_db_session.query.return_value = mock_query

    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/stats/abc12345')
        assert response.status_code == 200
        assert response.json()['short_id'] == 'abc12345'
        assert response.json()['full_url'] == 'https://example.com/very/long/url/path'
        assert 'created_at' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_get_stats_not_found(client, mock_db_session):
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query

    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response = client.get('/stats/nonexistent')
        assert response.status_code == 404
        assert 'detail' in response.json()
    finally:
        client.app.dependency_overrides.clear()


def test_shorten_url_duplicate_short_id(client, mock_db_session):
    data = {
        'url': 'https://example.com/another/url'
    }

    existing_short_url = ShortUrl(
        id=1,
        short_id='abc12345',
        full_url='https://example.com/existing',
        created_at=datetime.now(timezone.utc)
    )

    short_id = 'xyz98765'

    new_short_url = ShortUrl(
        id=2,
        short_id=short_id,
        full_url='https://example.com/another/url',
        created_at=datetime.now(timezone.utc)
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.side_effect = [existing_short_url, None]
    mock_db_session.query.return_value = mock_query

    port = os.environ.get('URL_SERVICE_PORT', 8000)

    with patch('app.routes.ShortUrl') as mock_short_url_class:
        mock_short_url_class.return_value = new_short_url
        with patch('app.routes.generate_short_id', side_effect=['abc12345', 'xyz98765']):
            client.app.dependency_overrides[get_db] = lambda: mock_db_session
            try:
                response = client.post('/shorten', json=data)
                assert response.status_code == 201
                assert response.json()['short_id'] == short_id
                assert response.json()['short_url'] == f'http://127.0.0.1:{port}/{short_id}'
                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()
            finally:
                client.app.dependency_overrides.clear()


def test_redirect_url_different_short_ids(client, mock_db_session):
    short_url_1 = ShortUrl(
        id=1,
        short_id='id1',
        full_url='https://example.com/url1',
        created_at=datetime.now(timezone.utc)
    )

    short_url_2 = ShortUrl(
        id=2,
        short_id='id2',
        full_url='https://example.com/url2',
        created_at=datetime.now(timezone.utc)
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.side_effect = [short_url_1, short_url_2]
    mock_db_session.query.return_value = mock_query

    client.app.dependency_overrides[get_db] = lambda: mock_db_session
    try:
        response1 = client.get('/id1', follow_redirects=False)
        assert response1.status_code == 301
        assert response1.headers['location'] == 'https://example.com/url1'

        response2 = client.get('/id2', follow_redirects=False)
        assert response2.status_code == 301
        assert response2.headers['location'] == 'https://example.com/url2'
    finally:
        client.app.dependency_overrides.clear()
