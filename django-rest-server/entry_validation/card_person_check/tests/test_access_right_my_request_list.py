# tests/tests_access_right_my_request_list.py
import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from django.db.models import Value, BooleanField

MY_REQUESTS_URL = "/api/access-right-requests/"  # adjust to your URL

today = date.today()
tomorrow = today + timedelta(days=1)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_data(db):
    from card_person_check.models import Employee, SecurityZone, Department

    zone = SecurityZone.objects.create(name="Zone A")
    dept = Department.objects.create(name="IT")
    supervisor = Employee.objects.create(
        firstname="Super", lastname="Visor",
        hr_id=10001, department=dept, current_zone=zone, is_supervisor=True,
        date_of_birth="1990-01-01",
    )
    employee = Employee.objects.create(
        firstname="John", lastname="Doe",
        hr_id=10002, department=dept, current_zone=zone, supervisor=supervisor,
        date_of_birth="1990-01-01",
    )
    other = Employee.objects.create(
        firstname="Other", lastname="User",
        hr_id=10003, department=dept, current_zone=zone,
        date_of_birth="1990-01-01",
    )
    return {"employee": employee, "supervisor": supervisor, "zone": zone, "other": other}


@pytest.fixture
def auth_client(api_client, setup_data):
    api_client.force_authenticate(user=setup_data["employee"])
    return api_client


def make_request(employee, supervisor, zone):
    from card_person_check.models import AccessRightRequest
    return AccessRightRequest.objects.create(
        employee=employee,
        supervisor=supervisor,
        security_zone=zone,
        start_date=tomorrow,
        end_date=tomorrow + timedelta(days=30),
    )


# ─── 1. Unauthenticated ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_returns_401(api_client):
    response = api_client.get(MY_REQUESTS_URL)
    assert response.status_code == 401


# ─── 2. Returns only own requests ─────────────────────────────────────────────

@pytest.mark.django_db
def test_returns_own_requests_only(auth_client, setup_data):
    """Must not return requests belonging to other employees."""
    own = make_request(setup_data["employee"], setup_data["supervisor"], setup_data["zone"])
    make_request(setup_data["other"], setup_data["supervisor"], setup_data["zone"])

    response = auth_client.get(MY_REQUESTS_URL)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == own.id


@pytest.mark.django_db
def test_returns_empty_list_when_no_requests(auth_client):
    response = auth_client.get(MY_REQUESTS_URL)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_results_ordered_newest_first(auth_client, setup_data):
    from card_person_check.models import AccessRightRequest
    import time
    r1 = make_request(setup_data["employee"], setup_data["supervisor"], setup_data["zone"])
    time.sleep(0.01)  # ensure distinct created_at timestamps
    r2 = make_request(setup_data["employee"], setup_data["supervisor"], setup_data["zone"])

    response = auth_client.get(MY_REQUESTS_URL)
    ids = [r["id"] for r in response.data]
    assert ids == [r2.id, r1.id]


# ─── 3. covered_as_deputy always False ────────────────────────────────────────

@pytest.mark.django_db
def test_covered_as_deputy_is_always_false(auth_client, setup_data):
    """Employee's own requests are never deputy-covered."""
    make_request(setup_data["employee"], setup_data["supervisor"], setup_data["zone"])
    response = auth_client.get(MY_REQUESTS_URL)
    assert all(r["covered_as_deputy"] is False for r in response.data)


# ─── 4. Query count ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_query_count_single_record(auth_client, setup_data, django_assert_num_queries):
    make_request(setup_data["employee"], setup_data["supervisor"], setup_data["zone"])

    with django_assert_num_queries(1):
        response = auth_client.get(MY_REQUESTS_URL)

    assert response.status_code == 200


@pytest.mark.django_db
def test_query_count_flat_with_many_records(auth_client, setup_data, django_assert_num_queries):
    """
    THE CRITICAL REGRESSION TEST — must stay at 1 query regardless of row count.
    If this fails with N+1, select_related was removed from the view.
    """
    from card_person_check.models import AccessRightRequest
    AccessRightRequest.objects.bulk_create([
        AccessRightRequest(
            employee=setup_data["employee"],
            supervisor=setup_data["supervisor"],
            security_zone=setup_data["zone"],
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=30),
        )
        for _ in range(100)
    ])

    with django_assert_num_queries(1):
        response = auth_client.get(MY_REQUESTS_URL)

    assert len(response.data) == 100