from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from members.models import Member
from cooperatives.models import Cooperative
from accounts.models import User
from .models import Loan, Guarantor
from .services import validate_loan_eligibility

class LoanEligibilityTests(TestCase):
    def setUp(self):
        self.cooperative = Cooperative.objects.create(
            name="Test Coop",
            code="COOP001",
            status="Active"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
            role="staff",
            cooperative=self.cooperative
        )
        self.member = Member.objects.create(
            full_name="John Doe",
            citizenship_number="12345",
            cooperative=self.cooperative
        )

    def test_eligible_member_can_take_loan(self):
        # John is clean, should be eligible
        self.assertTrue(validate_loan_eligibility(self.member))

    def test_blacklisted_member_cannot_take_loan(self):
        self.member.blacklist_status = True
        self.member.save()
        with self.assertRaises(ValidationError) as cm:
            validate_loan_eligibility(self.member)
        self.assertIn("blacklisted", str(cm.exception))

    def test_member_with_active_loan_cannot_take_another(self):
        # Create an active loan for John
        Loan.objects.create(
            member=self.member,
            cooperative=self.cooperative,
            loan_amount=1000,
            interest_rate=10,
            loan_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            status="Active",
            created_by=self.user
        )
        with self.assertRaises(ValidationError) as cm:
            validate_loan_eligibility(self.member)
        self.assertIn("already has an active or overdue loan", str(cm.exception))

    def test_member_with_overdue_loan_cannot_take_another(self):
        # Create an overdue loan for John
        Loan.objects.create(
            member=self.member,
            cooperative=self.cooperative,
            loan_amount=1000,
            interest_rate=10,
            loan_date=timezone.now().date() - timedelta(days=60),
            due_date=timezone.now().date() - timedelta(days=30),
            status="Overdue",
            created_by=self.user
        )
        with self.assertRaises(ValidationError) as cm:
            validate_loan_eligibility(self.member)
        self.assertIn("already has an active or overdue loan", str(cm.exception))

    def test_guarantor_of_active_loan_cannot_take_loan(self):
        # Another member takes a loan
        another_member = Member.objects.create(
            full_name="Jane Smith",
            citizenship_number="67890",
            cooperative=self.cooperative
        )
        loan = Loan.objects.create(
            member=another_member,
            cooperative=self.cooperative,
            loan_amount=2000,
            interest_rate=12,
            loan_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=60),
            status="Active",
            created_by=self.user
        )
        # John becomes a guarantor
        Guarantor.objects.create(
            name=self.member.full_name,
            citizenship_number=self.member.citizenship_number,
            loan=loan,
            member=self.member,
            contact_number="9876543210",
            status="Active"
        )
        
        with self.assertRaises(ValidationError) as cm:
            validate_loan_eligibility(self.member)
        self.assertIn("is a guarantor for an active or overdue loan", str(cm.exception))

    def test_member_can_take_loan_if_previous_loan_cleared(self):
        # John had a loan but it's cleared
        Loan.objects.create(
            member=self.member,
            cooperative=self.cooperative,
            loan_amount=1000,
            interest_rate=10,
            loan_date=timezone.now().date() - timedelta(days=60),
            due_date=timezone.now().date() - timedelta(days=30),
            status="Cleared",
            created_by=self.user
        )
        self.assertTrue(validate_loan_eligibility(self.member))

    def test_member_can_take_loan_if_guarantorship_released(self):
         # Another member takes a loan
        another_member = Member.objects.create(
            full_name="Jane Smith",
            citizenship_number="67890",
            cooperative=self.cooperative
        )
        loan = Loan.objects.create(
            member=another_member,
            cooperative=self.cooperative,
            loan_amount=2000,
            interest_rate=12,
            loan_date=timezone.now().date() - timedelta(days=60),
            due_date=timezone.now().date() - timedelta(days=30),
            status="Cleared",
            created_by=self.user
        )
        # John was a guarantor but status is Released now
        Guarantor.objects.create(
            name=self.member.full_name,
            citizenship_number=self.member.citizenship_number,
            loan=loan,
            member=self.member,
            contact_number="9876543210",
            status="Released"
        )
        self.assertTrue(validate_loan_eligibility(self.member))
