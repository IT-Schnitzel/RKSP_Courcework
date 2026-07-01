import requests
import random
import string
import json
from datetime import datetime, timedelta
import pytest
import time

BASE_URL = "http://localhost:8000"


class Fuzzer:
    def __init__(self):
        self.session_id = None
        self.user_id = None
        self.test_results = []

    def generate_random_string(self, length=10, chars=None):
        if chars is None:
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_random_email(self):
        domains = ["test.com", "example.org", "mail.ru", "gmail.com", "yandex.ru"]
        return f"{self.generate_random_string(8).lower()}@{random.choice(domains)}"

    def generate_random_date(self, days_offset=30):
        date = datetime.now() + timedelta(days=random.randint(-days_offset, days_offset))
        return date.isoformat()

    def generate_random_number(self, min_val=-1000, max_val=1000):
        return random.randint(min_val, max_val)

    def generate_random_float(self, min_val=-1000.0, max_val=1000.0):
        return round(random.uniform(min_val, max_val), 2)

    def register_test_user(self):
        username = f"fuzz_{self.generate_random_string(8)}"
        email = self.generate_random_email()
        password = self.generate_random_string(12)

        data = {
            "username": username,
            "email": email,
            "password": password
        }

        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=data)
            return response, data
        except Exception as e:
            return None, data

    def login_test_user(self, username, password):
        data = {
            "username_or_email": username,
            "password": password
        }

        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=data)
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get("session_id")
                self.user_id = result.get("user_id")
            return response
        except Exception as e:
            return None

    def create_test_task(self, task_data):
        if not self.session_id:
            return None
        try:
            response = requests.post(
                f"{BASE_URL}/api/tasks",
                params={"session_id": self.session_id},
                json=task_data
            )
            return response
        except Exception as e:
            return None

    def get_tasks(self):
        if not self.session_id:
            return None
        try:
            response = requests.get(
                f"{BASE_URL}/api/tasks",
                params={"session_id": self.session_id}
            )
            return response
        except Exception as e:
            return None


# === ТЕСТЫ ===

def test_fuzz_register_empty_fields():
    """Тест 1: Регистрация с пустыми полями"""
    fuzzer = Fuzzer()
    test_data = [
        {"username": "", "email": "test@test.com", "password": "test123"},
        {"username": "testuser", "email": "", "password": "test123"},
        {"username": "testuser", "email": "test@test.com", "password": ""},
        {"username": "", "email": "", "password": ""}
    ]

    for i, data in enumerate(test_data):
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        status = response.status_code
        print(f"Тест 1.{i + 1}: Пустые поля → Статус: {status}")
        assert status in [422, 400, 200]


def test_fuzz_register_invalid_email():
    """Тест 2: Регистрация с некорректными email"""
    fuzzer = Fuzzer()
    test_emails = [
        "invalid-email",
        "test@",
        "@test.com",
        "test@@test.com",
        "test@test",
        "test test@test.com",
        "test@test..com",
        "test@test.c",
        "test@test.toolongtld",
        "test@-test.com",
        "test@test-.com",
        "test@.test.com"
    ]

    for i, email in enumerate(test_emails):
        data = {
            "username": f"testuser_{i}",
            "email": email,
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        status = response.status_code
        print(f"Тест 2.{i + 1}: Email: '{email}' → Статус: {status}")
        assert status in [422, 400]


def test_fuzz_register_short_password():
    """Тест 3: Регистрация с короткими паролями"""
    fuzzer = Fuzzer()
    passwords = ["", "1", "12", "123", "1234", "12345"]

    for i, password in enumerate(passwords):
        data = {
            "username": f"testuser_{i}",
            "email": f"test{i}@test.com",
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        status = response.status_code
        print(f"Тест 3.{i + 1}: Пароль: '{password}' → Статус: {status}")
        assert status in [422, 400]


def test_fuzz_register_special_characters():
    """Тест 4: Регистрация с специальными символами"""
    fuzzer = Fuzzer()
    special_names = [
        "test<script>alert(1)</script>",
        "test' OR '1'='1",
        "test; DROP TABLE users;",
        "test\u0000user",
        "test\nuser",
        "test\tuser",
        "test\\user",
        "test/user",
        "test.user",
        "test_user",
        "test-user",
        "test@user",
        "test#user",
        "test$user",
        "test%user"
    ]

    for i, username in enumerate(special_names):
        data = {
            "username": username,
            "email": f"test{i}@test.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        status = response.status_code
        print(f"Тест 4.{i + 1}: Username: '{username[:20]}...' → Статус: {status}")
        assert status in [200, 400, 422]


def test_fuzz_login_invalid_credentials():
    """Тест 5: Вход с неверными данными"""
    fuzzer = Fuzzer()
    invalid_data = [
        {"username_or_email": "nonexistent", "password": "wrongpass"},
        {"username_or_email": "", "password": "test123"},
        {"username_or_email": "test@test.com", "password": ""},
        {"username_or_email": "", "password": ""},
        {"username_or_email": "test@test", "password": "test"},
        {"username_or_email": "test" * 100, "password": "test" * 100}
    ]

    for i, data in enumerate(invalid_data):
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        status = response.status_code
        print(f"Тест 5.{i + 1}: Неверные данные → Статус: {status}")
        assert status in [401, 422, 400]


def test_fuzz_create_task_empty_fields():
    """Тест 6: Создание задачи с пустыми полями"""
    fuzzer = Fuzzer()
    # Сначала создаём и логиним пользователя
    reg_data = {"username": "fuzz_user", "email": "fuzz@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"username_or_email": "fuzz_user", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    test_tasks = [
        {"title": "", "assigned_to_id": 1, "status": "pending", "priority": "medium"},
        {"title": "Test", "assigned_to_id": "", "status": "pending", "priority": "medium"},
        {"title": "Test", "assigned_to_id": 1, "status": "", "priority": "medium"},
        {"title": "Test", "assigned_to_id": 1, "status": "pending", "priority": ""},
        {"title": "", "assigned_to_id": "", "status": "", "priority": ""}
    ]

    for i, task in enumerate(test_tasks):
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status = response.status_code
        print(f"Тест 6.{i + 1}: Пустые поля задачи → Статус: {status}")
        assert status in [201, 422, 400]


def test_fuzz_create_task_invalid_priority():
    """Тест 7: Создание задачи с неверным приоритетом"""
    fuzzer = Fuzzer()
    # Создаём пользователя
    reg_data = {"username": "fuzz_user2", "email": "fuzz2@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user2", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    invalid_priorities = [
        "invalid", "high_priority", "very_low", "critical_urgent",
        "1", "0", "true", "null", "undefined", "HIGH", "LOW"
    ]

    for i, priority in enumerate(invalid_priorities):
        task = {
            "title": f"Test task {i}",
            "assigned_to_id": 1,
            "status": "pending",
            "priority": priority
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status = response.status_code
        print(f"Тест 7.{i + 1}: Приоритет: '{priority}' → Статус: {status}")
        assert status in [422, 400]


def test_fuzz_create_task_invalid_status():
    """Тест 8: Создание задачи с неверным статусом"""
    fuzzer = Fuzzer()
    # Создаём пользователя
    reg_data = {"username": "fuzz_user3", "email": "fuzz3@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user3", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    invalid_statuses = [
        "invalid", "in_progres", "complete", "cancelledd", "archivedd",
        "pendingg", "in progress", "COMPLETED", "PENDING", "1", "0", "true"
    ]

    for i, status in enumerate(invalid_statuses):
        task = {
            "title": f"Test task {i}",
            "assigned_to_id": 1,
            "status": status,
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 8.{i + 1}: Статус: '{status}' → Статус: {status_code}")
        assert status_code in [422, 400]


def test_fuzz_create_task_negative_hours():
    """Тест 9: Создание задачи с отрицательными часами"""
    fuzzer = Fuzzer()
    # Создаём пользователя
    reg_data = {"username": "fuzz_user4", "email": "fuzz4@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user4", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    negative_hours = [-1, -0.5, -10, -100, -999, -1000.5]

    for i, hours in enumerate(negative_hours):
        task = {
            "title": f"Test task {i}",
            "assigned_to_id": 1,
            "status": "pending",
            "priority": "medium",
            "planned_hours": hours
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 9.{i + 1}: Часы: '{hours}' → Статус: {status_code}")
        assert status_code in [422, 400]


def test_fuzz_create_task_large_values():
    """Тест 10: Создание задачи с большими значениями"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user5", "email": "fuzz5@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user5", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    large_values = [
        999999, 9999999, 10 ** 9, 10 ** 12, 2 ** 31, 2 ** 63, 10 ** 100
    ]

    for i, val in enumerate(large_values):
        task = {
            "title": "A" * 100000,
            "assigned_to_id": val,
            "status": "pending",
            "priority": "medium",
            "planned_hours": val
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 10.{i + 1}: Большое значение: '{str(val)[:10]}...' → Статус: {status_code}")
        assert status_code in [422, 413, 400]


def test_fuzz_create_task_sql_injection():
    """Тест 11: SQL-инъекции в полях задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user6", "email": "fuzz6@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user6", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    sql_injections = [
        "'; DROP TABLE tasks; --",
        "'; DELETE FROM tasks WHERE '1'='1",
        "'; UPDATE tasks SET status='completed' WHERE '1'='1",
        "'; SELECT * FROM users; --",
        "'; INSERT INTO tasks VALUES (1, 'hack', 1, 'completed'); --",
        "' OR '1'='1",
        "' UNION SELECT * FROM users; --",
        "1'; DROP TABLE projects; --"
    ]

    for i, injection in enumerate(sql_injections):
        task = {
            "title": injection,
            "description": injection,
            "assigned_to_id": 1,
            "status": "pending",
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 11.{i + 1}: SQL-инъекция: '{injection[:30]}...' → Статус: {status_code}")
        assert status_code in [200, 201, 422, 400]


def test_fuzz_create_task_xss():
    """Тест 12: XSS в полях задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user7", "email": "fuzz7@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user7", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "onerror=alert(1)",
        "onclick=alert(1)",
        "<body onload=alert(1)>",
        "<iframe src='javascript:alert(1)'>",
        "<a href='javascript:alert(1)'>click</a>",
        "&#60;script&#62;alert(1)&#60;/script&#62;"
    ]

    for i, payload in enumerate(xss_payloads):
        task = {
            "title": payload,
            "description": payload,
            "assigned_to_id": 1,
            "status": "pending",
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 12.{i + 1}: XSS: '{payload[:30]}...' → Статус: {status_code}")
        assert status_code in [200, 201, 422, 400]


def test_fuzz_get_nonexistent_task():
    """Тест 13: Запрос несуществующей задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user8", "email": "fuzz8@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user8", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    nonexistent_ids = [0, -1, 999999, 9999999, 10 ** 9, 2 ** 31]

    for i, task_id in enumerate(nonexistent_ids):
        response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}",
            params={"session_id": session_id}
        )
        status_code = response.status_code
        print(f"Тест 13.{i + 1}: ID: {task_id} → Статус: {status_code}")
        assert status_code in [404, 422]


def test_fuzz_update_nonexistent_task():
    """Тест 14: Обновление несуществующей задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user9", "email": "fuzz9@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user9", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    update_data = {"title": "Updated", "status": "completed"}

    for i, task_id in enumerate([0, -1, 999999, 9999999]):
        response = requests.put(
            f"{BASE_URL}/api/tasks/{task_id}",
            params={"session_id": session_id},
            json=update_data
        )
        status_code = response.status_code
        print(f"Тест 14.{i + 1}: ID: {task_id} → Статус: {status_code}")
        assert status_code in [404, 422]


def test_fuzz_delete_nonexistent_task():
    """Тест 15: Удаление несуществующей задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user10", "email": "fuzz10@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user10", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    for i, task_id in enumerate([0, -1, 999999, 9999999]):
        response = requests.delete(
            f"{BASE_URL}/api/tasks/{task_id}",
            params={"session_id": session_id}
        )
        status_code = response.status_code
        print(f"Тест 15.{i + 1}: ID: {task_id} → Статус: {status_code}")
        assert status_code in [404, 422]


def test_fuzz_create_task_without_session():
    """Тест 16: Создание задачи без сессии"""
    fuzzer = Fuzzer()
    task = {
        "title": "Test task",
        "assigned_to_id": 1,
        "status": "pending",
        "priority": "medium"
    }
    response = requests.post(f"{BASE_URL}/api/tasks", json=task)
    status_code = response.status_code
    print(f"Тест 16: Без сессии → Статус: {status_code}")
    assert status_code in [401, 422]


def test_fuzz_random_task_data():
    """Тест 17: Случайные данные для задачи"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user11", "email": "fuzz11@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user11", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    for i in range(20):
        task = {
            "title": fuzzer.generate_random_string(random.randint(0, 1000)),
            "description": fuzzer.generate_random_string(random.randint(0, 5000)),
            "assigned_to_id": fuzzer.generate_random_number(-100, 1000),
            "status": random.choice(
                ["pending", "in_progress", "completed", "cancelled", "archived", "invalid", "", None]),
            "priority": random.choice(["low", "medium", "high", "urgent", "critical", "invalid", "", None]),
            "planned_hours": fuzzer.generate_random_float(-1000, 1000),
            "deadline": fuzzer.generate_random_date(365)
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        status_code = response.status_code
        print(f"Тест 17.{i + 1}: Случайные данные → Статус: {status_code}")
        assert status_code in [200, 201, 400, 422]


def test_fuzz_concurrent_requests():
    """Тест 18: Конкурентные запросы"""
    import concurrent.futures

    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user12", "email": "fuzz12@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user12", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    def make_request(i):
        task = {
            "title": f"Concurrent task {i}",
            "assigned_to_id": 1,
            "status": "pending",
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            json=task
        )
        return response.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = [f.result() for f in futures]

    print(f"Тест 18: Конкурентные запросы → Результаты: {results}")
    assert all(r in [200, 201, 400, 422, 429] for r in results)


def test_fuzz_invalid_content_type():
    """Тест 19: Неверный Content-Type"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user13", "email": "fuzz13@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user13", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    invalid_content = [
        "text/plain",
        "application/xml",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ]

    for content_type in invalid_content:
        headers = {"Content-Type": content_type}
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            headers=headers,
            data="invalid data"
        )
        status_code = response.status_code
        print(f"Тест 19: Content-Type: {content_type} → Статус: {status_code}")
        assert status_code in [400, 415, 422]


def test_fuzz_malformed_json():
    """Тест 20: Неверный JSON"""
    fuzzer = Fuzzer()
    reg_data = {"username": "fuzz_user14", "email": "fuzz14@test.com", "password": "test123"}
    requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username_or_email": "fuzz_user14", "password": "test123"})
    session_id = login_resp.json().get("session_id")

    malformed_json = [
        '{"title": "test", "assigned_to_id": 1,}',
        '{"title": "test" "assigned_to_id": 1}',
        "{title: test, assigned_to_id: 1}",
        '{"title": "test", assigned_to_id: 1}',
        '{"title": "test", "assigned_to_id": 1, "status": "pending"',
        '{"title": "test" "assigned_to_id": 1 "status": "pending"}'
    ]

    for i, malformed in enumerate(malformed_json):
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            params={"session_id": session_id},
            data=malformed,
            headers={"Content-Type": "application/json"}
        )
        status_code = response.status_code
        print(f"Тест 20.{i + 1}: Неверный JSON → Статус: {status_code}")
        assert status_code in [400, 422]


# Запуск всех тестов
def run_all_fuzzing_tests():
    print("\n" + "=" * 60)
    print("НАЧАЛО ФАЗЗИНГ-ТЕСТИРОВАНИЯ API")
    print("=" * 60 + "\n")

    tests = [
        test_fuzz_register_empty_fields,
        test_fuzz_register_invalid_email,
        test_fuzz_register_short_password,
        test_fuzz_register_special_characters,
        test_fuzz_login_invalid_credentials,
        test_fuzz_create_task_empty_fields,
        test_fuzz_create_task_invalid_priority,
        test_fuzz_create_task_invalid_status,
        test_fuzz_create_task_negative_hours,
        test_fuzz_create_task_large_values,
        test_fuzz_create_task_sql_injection,
        test_fuzz_create_task_xss,
        test_fuzz_get_nonexistent_task,
        test_fuzz_update_nonexistent_task,
        test_fuzz_delete_nonexistent_task,
        test_fuzz_create_task_without_session,
        test_fuzz_random_task_data,
        test_fuzz_concurrent_requests,
        test_fuzz_invalid_content_type,
        test_fuzz_malformed_json
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ ТЕСТ ПРОВАЛЕН: {test.__name__} - {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ОШИБКА: {test.__name__} - {e}")
        print("-" * 40)

    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📊 Всего: {passed + failed}")
    print(f"📈 Успешность: {passed / (passed + failed) * 100:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    run_all_fuzzing_tests()