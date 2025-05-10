def test_patient_creation(client):
    response = client.post('/api/patients', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'email': 'john@example.com',
        'phone': '+1234567890'
    })
    assert response.status_code == 201
    assert 'patient_id' in response.json

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
