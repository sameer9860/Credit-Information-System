from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Loan
from .forms import LoanForm


@login_required
def loan_list(request):

    loans = Loan.objects.all().order_by("-loan_date")

    return render(
        request,
        "loans/loan_list.html",
        {"loans": loans}
    )


@login_required
def create_loan(request):

    if request.method == "POST":

        form = LoanForm(request.POST)

        if form.is_valid():

            loan = form.save(commit=False)
            loan.created_by = request.user
            loan.save()

            return redirect("loan_list")

    else:
        form = LoanForm()

    return render(
        request,
        "loans/loan_form.html",
        {"form": form}
    )


@login_required
def loan_detail(request, loan_id):

    loan = get_object_or_404(Loan, loan_id=loan_id)

    return render(
        request,
        "loans/loan_detail.html",
        {"loan": loan}
    )