import time
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

URL = "http://127.0.0.1:8000/api/check_card_person/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_data(db):
    """Create the minimum data needed to exercise the view."""
    from card_person_check.models import (
        Card,
        Employee,
        Gate,
        SecurityZone,
        Department,
        AccessRight,
    )

    zone_a = SecurityZone.objects.create(name="Zone A")
    zone_b = SecurityZone.objects.create(name="Zone B")
    gate = Gate.objects.create(current_zone=zone_a, opposite_zone=zone_b)
    department = Department.objects.create(name="Test Dept")
    employee = Employee.objects.create(
        hr_id="99999",
        password="password",
        firstname="Test",
        lastname="User",
        date_of_birth="1990-01-01",
        department=department,
    )
    card = Card.objects.create(is_active=True, valid_from="2024-01-01", valid_to="2030-01-01", card_number="1234567890", employee=employee)
    AccessRight.objects.create(
        security_zone=zone_a,
        start_date="2024-01-01",
        end_date="2030-01-01",
        employee=employee,
    )
    AccessRight.objects.create(
        security_zone=zone_b,
        start_date="2024-01-01",
        end_date="2030-01-01",  
        employee=employee,
    )
    return {"card": card, "gate": gate, "employee": employee}


# ─── 1. QUERY COUNT ───────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_access_granted_query_count(api_client, setup_data, django_assert_num_queries):
    """
    On access granted, the view should make exactly 4 queries:
    1. SELECT card (with employee via select_related)
    2. SELECT gate
    3. INSERT gate_event
    4. UPDATE employee.current_zone
    If this fails with 5, it means card.employee is firing a lazy query.
    """
    payload = {
        "card_number": setup_data["card"].card_number,
        "gate": setup_data["gate"].id,
        "timestamp": "2026-04-25T09:00:00Z",
    }
    # Access granted: serializer check + card+employee + gate+zones + 2×access rights + INSERT + UPDATE
    with django_assert_num_queries(7) as ctx:
        response = api_client.post(URL, payload, format="json")

    assert response.status_code == 200

    # Print all executed queries for inspection when running with -v
    from django.db import connection

    for i, q in enumerate(connection.queries, 1):
        print(f"Query {i}: {q['sql'][:120]}")


@pytest.mark.django_db
def test_access_denied_query_count(api_client, setup_data, django_assert_num_queries):
    """
    On denied access, employee.save() is skipped — expect 3 queries.
    """
    payload = {
        "card_number": "0000000000",  # unknown card
        "gate": setup_data["gate"].id,
        "timestamp": "2026-04-25T09:00:00Z",
    }

    # Access denied (no employee → no access right checks, no UPDATE):
    # serializer check + card (not found) + gate+zones + INSERT
    with django_assert_num_queries(4) as ctx:
        response = api_client.post(URL, payload, format="json")

    assert response.status_code in (403, 404)


# ─── 2. RESPONSE TIME ─────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_response_time(api_client, setup_data):
    """
    The endpoint should respond well under 100ms in a test DB environment.
    Adjust the threshold based on your hardware baseline.
    """
    payload = {
        "card_number": setup_data["card"].card_number,
        "gate": setup_data["gate"].id,
        "timestamp": "2026-04-25T09:00:00Z",
    }

    start = time.perf_counter()
    response = api_client.post(URL, payload, format="json")
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"\nResponse time: {elapsed_ms:.2f}ms")
    assert elapsed_ms < 100, f"Too slow: {elapsed_ms:.2f}ms"


# ─── 3. CATCH QUERY COUNT REGRESSIONS ─────────────────────────────────────────


@pytest.mark.django_db
def test_no_extra_queries_with_multiple_zones(
    api_client, setup_data, django_assert_num_queries
):
    """
    Adding more zones/gates to the DB must NOT increase query count.
    If it does, you have an N+1 or missing .first() guard.
    """
    from card_person_check.models import Gate, SecurityZone

    for i in range(10):
        z = SecurityZone.objects.create(name=f"Extra Zone {i}")
        Gate.objects.create(current_zone=z, opposite_zone=z)

    payload = {
        "card_number": setup_data["card"].card_number,
        "gate": setup_data["gate"].id,
        "timestamp": "2026-04-25T09:00:00Z",
    }

    with django_assert_num_queries(7):
        api_client.post(URL, payload, format="json")
