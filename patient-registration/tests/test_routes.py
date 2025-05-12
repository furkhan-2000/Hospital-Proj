import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    })
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
azureuser@azure:~/Hospital-Proj/patient-registration/tests$ cat test_routes.py
def test_patient_creation(client):
    response = client.post('/api/patients', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'sex': 'Male',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'description': 'Test patient'
    })
    assert response.status_code == 201
    assert 'patient_id' in response.json

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
