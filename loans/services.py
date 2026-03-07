from django.core.exceptions import ValidationError
from .models import Loan, Guarantor

def validate_loan_eligibility(member):
    """
    Validates if a member is eligible to take a new loan.
    Rules:
    1. Member must not be blacklisted.
    2. Member must not have any active or overdue loans.
    3. Member must not be a guarantor for any active or overdue loan.
    """
    
    # 1. Blacklist Check
    if member.blacklist_status:
        raise ValidationError(f"Member {member.full_name} is blacklisted and cannot take a loan.")

    # 2. Active/Overdue Loan Check
    active_loans = Loan.objects.filter(member=member, status__in=['Active', 'Overdue'])
    if active_loans.exists():
        raise ValidationError(f"Member {member.full_name} already has an active or overdue loan.")

    # 3. Guarantor Check
    # We check by citizenship_number to catch cases where the guarantor might not be linked as a member object
    # but has the same citizenship number.
    guaranteed_active_loans = Guarantor.objects.filter(
        citizenship_number=member.citizenship_number,
        status='Active',
        loan__status__in=['Active', 'Overdue']
    )
    if guaranteed_active_loans.exists():
        raise ValidationError(f"Member {member.full_name} is a guarantor for an active or overdue loan.")

    return True
