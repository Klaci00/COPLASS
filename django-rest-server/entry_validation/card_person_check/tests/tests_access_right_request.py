# card_person_check/tests_access_right_request.py
import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Employee, Department, SecurityZone, AccessRightRequest

URL = "/api/access_right_requests/"  # adjust to your actual URL

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, db):
    """Authenticated client — force_authenticate bypasses password hashing (faster)."""
    department = Department.objects.create(name="Test Dept")
    user = Employee.objects.create(
        hr_id="99999",
        password="password",
        firstname="Test",
        lastname="User",
        date_of_birth="1990-01-01",
        department=department,
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def setup_data(db):
    from card_person_check.models import Employee, SecurityZone, Department

    zone = SecurityZone.objects.create(name="Zone A")
    dept = Department.objects.create(name="IT")
    supervisor = Employee.objects.create(
        firstname="Super", lastname="Visor",
        hr_id=10001, department=dept,
        current_zone=zone, is_supervisor=True,
        date_of_birth="1990-01-01",

    )
    employee = Employee.objects.create(
        firstname="John", lastname="Doe",
        hr_id=10002, department=dept,
        current_zone=zone, supervisor=supervisor,
        date_of_birth="1990-01-01",
    )
    return {"employee": employee, "supervisor": supervisor, "zone": zone}


def valid_payload(data):
    """Build a valid payload, overriding any field for negative tests."""
    base = {
        "employee": data["employee"].id,
        "supervisor": data["supervisor"].id,
        "security_zone": data["zone"].id,
        "start_date": str(tomorrow),
        "end_date": str(tomorrow + timedelta(days=30)),
    }
    return base


# ─── 1. Authentication ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_unauthenticated_request_is_rejected(api_client, setup_data):
    """Unauthenticated requests must return 401, not 403 or 200."""
    response = api_client.post(URL, valid_payload(setup_data), format="json")
    assert response.status_code == 401


# ─── 2. Happy Path ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_valid_request_returns_201(auth_client, setup_data):
    response = auth_client.post(URL, valid_payload(setup_data), format="json")
    assert response.status_code == 201
    assert response.data["message"] == "Access right request created successfully."


@pytest.mark.django_db
def test_valid_request_creates_db_record(auth_client, setup_data):
    from card_person_check.models import AccessRightRequest
    assert AccessRightRequest.objects.count() == 0
    auth_client.post(URL, valid_payload(setup_data), format="json")
    assert AccessRightRequest.objects.count() == 1


@pytest.mark.django_db
def test_created_record_has_correct_fields(auth_client, setup_data):
    from card_person_check.models import AccessRightRequest
    auth_client.post(URL, valid_payload(setup_data), format="json")
    obj = AccessRightRequest.objects.first()
    assert obj.employee == setup_data["employee"]
    assert obj.security_zone == setup_data["zone"]
    assert obj.start_date == tomorrow


# ─── 3. Query Count ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_happy_path_query_count(auth_client, setup_data, django_assert_num_queries):
    """
    Expected queries (6 total):
    1. SELECT employee     — DRF FK validation (full object fetch)
    2. SELECT supervisor   — DRF FK validation (full object fetch)
    3. SELECT securityzone — DRF FK validation (full object fetch)
    4. SAVEPOINT           — Django test transaction savepoint
    5. INSERT              — accessrightrequest record
    6. RELEASE SAVEPOINT   — savepoint cleanup
    """
    with django_assert_num_queries(6):
        auth_client.post(URL, valid_payload(setup_data), format="json")


@pytest.mark.django_db
def test_query_count_stable_with_more_data(auth_client, setup_data, django_assert_num_queries):
    """Query count must not grow as more employees/zones are added."""
    from card_person_check.models import Employee, SecurityZone, Department
    dept = Department.objects.first()
    zone = SecurityZone.objects.first()
    for i in range(20):
        Employee.objects.create(
            firstname=f"Extra{i}", lastname="User",
            hr_id=20000 + i, department=dept, current_zone=zone,
            date_of_birth="1990-01-01",

        )

    with django_assert_num_queries(6):
        auth_client.post(URL, valid_payload(setup_data), format="json")


# ─── 4. Validation Errors ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_missing_employee_returns_400(auth_client, setup_data):
    payload = valid_payload(setup_data)
    del payload["employee"]
    response = auth_client.post(URL, payload, format="json")
    assert response.status_code == 400
    assert "employee" in response.data


@pytest.mark.django_db
def test_missing_zone_returns_400(auth_client, setup_data):
    payload = valid_payload(setup_data)
    del payload["security_zone"]
    response = auth_client.post(URL, payload, format="json")
    assert response.status_code == 400
    assert "security_zone" in response.data


@pytest.mark.django_db
def test_nonexistent_employee_returns_400(auth_client, setup_data):
    payload = valid_payload(setup_data)
    payload["employee"] = 99999  # does not exist
    response = auth_client.post(URL, payload, format="json")
    assert response.status_code == 400


# ─── 5. Date Validation ────────────────────────────────────────────────────────
# These tests currently EXPOSE BUGS — they will fail until the serializer
# validate() method is added as described in the review above.

@pytest.mark.django_db
def test_end_date_before_start_date_returns_400(auth_client, setup_data):
    """
    EXPOSES BUG: serializer has no cross-field date validation.
    This test will fail until validate() is added to the serializer.
    """
    payload = valid_payload(setup_data)
    payload["start_date"] = str(tomorrow + timedelta(days=10))
    payload["end_date"] = str(tomorrow)  # end before start
    response = auth_client.post(URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_start_date_in_past_returns_400(auth_client, setup_data):
    """
    EXPOSES BUG: no validation prevents backdated requests.
    """
    payload = valid_payload(setup_data)
    payload["start_date"] = str(yesterday)
    payload["end_date"] = str(tomorrow)
    response = auth_client.post(URL, payload, format="json")
    assert response.status_code == 400


# ─── 6. Security ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_cannot_self_approve_on_creation(auth_client, setup_data):
    """
    EXPOSES BUG: 'approved' is not read_only, so a user can POST approved=True.
    This test will fail until approved is marked read_only in the serializer.
    """
    payload = valid_payload(setup_data)
    payload["approved"] = True
    auth_client.post(URL, payload, format="json")

    from card_person_check.models import AccessRightRequest
    obj = AccessRightRequest.objects.first()
    assert obj.approved is False, "approved must always be False on creation"


# ─── 7. Response Time ──────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_response_time(auth_client, setup_data):
    import time
    payload = valid_payload(setup_data)
    start = time.perf_counter()
    auth_client.post(URL, payload, format="json")
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\nResponse time: {elapsed_ms:.2f}ms")
    assert elapsed_ms < 100, f"Too slow: {elapsed_ms:.2f}ms"