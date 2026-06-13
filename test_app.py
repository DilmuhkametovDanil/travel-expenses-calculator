import pytest
from app import app, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_add_expense(client):
    response = client.post('/add', data={
        'category': 'Еда',
        'amount': '150',
        'description': 'Тестовый обед'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE description = ?', ('Тестовый обед',)).fetchone()
    conn.close()
    assert expense is not None
    assert expense['amount'] == 150.0

def test_delete_expense(client):
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)',
                 ('Транспорт', 100.0, 'Тестовое удаление'))
    conn.commit()
    expense = conn.execute('SELECT id FROM expenses WHERE description = ?', ('Тестовое удаление',)).fetchone()
    expense_id = expense['id']
    conn.close()

    response = client.get(f'/delete/{expense_id}', follow_redirects=True)
    assert response.status_code == 200

    conn = get_db_connection()
    deleted_expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
    conn.close()
    assert deleted_expense is None