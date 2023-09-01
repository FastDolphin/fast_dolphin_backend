import pytest
import sys
from pyhere import here

sys.path.append(str(here().resolve()))
from model import CustomerRequest


def test_valid_customer_request():
    # Arrange
    valid_request = CustomerRequest(
        Email="test@example.com",
        Name="John",
        Surname="Doe",
        KidsName="Jane",
        KidsSurname="Doe",
        BirthYear=2022,
        PhoneNumber="1234567890",
        numberOfLessonsWeekly=2,
        typeOfLessons="swimming",
        SwimmingLevel="beginner",
        canSwim=True,
        hasTakenCourses=False,
    )

    # Act
    assert valid_request.has_valid_email()


def test_invalid_customer_request():
    # Arrange
    invalid_request = CustomerRequest(
        Email="invalid_email",
        Name="John",
        Surname="Doe",
        KidsName="Jane",
        KidsSurname="Doe",
        BirthYear=2022,
        PhoneNumber="1234567890",
        numberOfLessonsWeekly=2,
        typeOfLessons="swimming",
        SwimmingLevel="beginner",
        canSwim=True,
        hasTakenCourses=False,
    )

    assert not invalid_request.has_valid_email()
