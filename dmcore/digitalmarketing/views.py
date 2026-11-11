#DMCORE with buffer


import hmac
import logging
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render,redirect
from django.contrib import messages
from digitalmarketing.models import *
from django.contrib import messages
from datetime import date
from django.http import JsonResponse
from django.http import JsonResponse
from .models import ClientRegister
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from itertools import chain
import re
from datetime import datetime
from django.db.models import Count
from django.utils.timezone import localdate
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
import traceback
from digitalmarketing.models import (
    LogRegister_Details, 
    EmployeeRegister_Details, 
    EmployeeLeave,
    Feedback,
    Complaint,
    ActionTaken
)
from django.utils import timezone
from .models import ActionTaken, LogRegister_Details, EmployeeRegister_Details, BusinessRegister_Details
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.serializers import serialize
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import Http404
from datetime import datetime, date
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timesince import timesince
from .models import (
    EmployeeRegister_Details,
    EmployeeSchedule,
    EmployeeLeave,
    LogRegister_Details,
    Complaint,
    AllocationDetails,
    Feedback,
    ActionTaken
)
from django.http import HttpResponseForbidden
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from datetime import date                    
from digitalmarketing.models import *
from django.conf import settings
import os
from .models import EmployeeLeave, EmployeeRegister_Details
from django.db.models import Q  # Add this import at top of file
from collections import defaultdict                              
from django.utils import timezone
from openpyxl import Workbook  
from .models import Leads, DataBank, LeadDetails
from django.db.models import Sum
from .models import TaskAssign, TaskDetails, LogRegister_Details, EmployeeRegister_Details
from django.utils.text import slugify
from .models import Leads, LeadCategory_Register, LeadField_Register, EmployeeRegister_Details, LogRegister_Details
from .interview_questions import INTERVIEW_QUESTIONS, QUESTION_BY_ID
from django.db.models.functions import Lower
import openpyxl # type: ignore
from .models import Leads, LeadCategory_Register, EmployeeRegister_Details
from django.db.models import Max
from django.db.models import Exists, OuterRef 
from django.db.models import OuterRef, Subquery, Count, Value, IntegerField, Q, F
from django.db.models.functions import Coalesce
from django.utils.html import escape
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
import os


def home(request):
    check_telecaller_followups()
    return render(request,'landingpage/home.html')

def compsignup(request):
    return render(request,'landingpage/compsignup.html')

def registerbusiness(request):
    if request.method == 'POST':
        # Fetch all form data
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        company_id = request.POST.get('company_id') or 'COMID001'  # fallback
        contact_no = request.POST.get('contact_no')
        email = request.POST.get('email')
        location = request.POST.get('location')
        website = request.POST.get('website')
        username = request.POST.get('username')
        password = request.POST.get('password')

        login_obj = LogRegister_Details.objects.create(
    log_username=username,
    log_password=password,
    position='Admin',
    is_staff=True
)


        # Save business details
        business = BusinessRegister_Details.objects.create(
            login=login_obj,
            owner_fname=fname,
            owner_lname=lname,
            company_name=company_name,
            contact_number=contact_no,
            email=email,
            website=website,
            location=location,
            company_code=company_id,
        )

        messages.success(request, 'Business registered successfully!')
        return redirect('registerbusiness')  # or another page

    return render(request, 'landingpage/compsignup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try: user = LogRegister_Details.objects.get(log_username=username) 
        except LogRegister_Details.DoesNotExist: 
            messages.error(request, "Invalid username or password.") 
            return redirect('login') 
        except LogRegister_Details.MultipleObjectsReturned: 
            messages.error(request, "Duplicate username detected. Please contact the administrator.") 
            return redirect('login')

        if user.log_password != password:
            messages.error(request, "Incorrect password")
            return redirect(login)

        if not user.is_staff:
            messages.error(request, "Your account is not yet approved.")
            return redirect(login)
	
        if not user.status:
            messages.error(request, "Your account is Blocked.")
            return redirect(login)

        # Set session based on role
        if user.position == 'Admin':
            request.session['aid'] = user.log_username
            return redirect(admin_dashboard)

        elif user.position == 'Digital_Marketing_Head':
            request.session['hid'] = user.log_username
            print("Set session hid:", request.session['hid'])

            return redirect(dmhead)  # Replace with actual URL name

        elif user.position == 'Team_Lead':
            request.session['tid'] = user.log_username
            return redirect(teamlead)  # Replace with actual URL name

        elif user.position == 'Executive':

            employee = EmployeeRegister_Details.objects.filter(
                login=user
            ).first()

            if employee:
                today = timezone.localdate()

                attendance, created = EmployeeAttendance.objects.get_or_create(
                    employee=employee,
                    date=today
                )

                if not attendance.first_login_time:
                    attendance.first_login_time = timezone.now()
                    attendance.save()

                session = EmployeeSession.objects.create(
                    employee=employee,
                    attendance=attendance,
                    login_time=timezone.now()
                )

                request.session['session_id'] = session.id

            request.session['eid'] = user.log_username

            return redirect(executive)

        elif user.position == 'Data_Manager':
            request.session['did'] = user.log_username
            return redirect(manager)  # Replace with actual URL name

        elif user.position == 'Telecaller':

            employee = EmployeeRegister_Details.objects.filter(
                login=user
            ).first()

            if employee:
                today = timezone.localdate()

                attendance, created = EmployeeAttendance.objects.get_or_create(
                    employee=employee,
                    date=today
                )

                if not attendance.first_login_time:
                    attendance.first_login_time = timezone.now()
                    attendance.save()

                session = EmployeeSession.objects.create(
                    employee=employee,
                    attendance=attendance,
                    login_time=timezone.now()
                )

                request.session['session_id'] = session.id

            request.session['tcid'] = user.log_username

            return redirect(telecaller)
	 
        elif user.position == 'HR':
            request.session['hrid'] = user.log_username
            return redirect(hr)
        
        elif user.position == 'Graphics Designer':
            request.session['gdid'] = user.log_username
            return redirect(graphics_designer)

        else:
            messages.error(request, "Unauthorized position.")
            return redirect('login')
    return render(request,'landingpage/login.html')

from django.http import JsonResponse


def check_email(request):
    email = request.GET.get("email", None)
    exists = BusinessRegister_Details.objects.filter(email=email).exists()
    return JsonResponse({"exists": exists})

def check_company_id(request):
    company_id = request.GET.get("company_id", None)
    exists = BusinessRegister_Details.objects.filter(company_code=company_id).exists()
    return JsonResponse({"exists": exists})

def admin_dashboard(request):
    aid = request.session.get('aid')
    print(f"--- Debug: Dashboard ---")
    print(f"Session AID: {aid}")

    if not aid:
        print("Redirecting to login: No aid found in session.")
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        print(f"User found: {user.log_username}")

        company = BusinessRegister_Details.objects.filter(login=user).first()
        if company:
            print(f"Company associated: {company.company_name} (ID: {company.id})")
        else:
            print("No company found for this user.")
        
        clients = ClientRegister.objects.filter(company=company).order_by('-client_reg_date')
        print(f"Clients count: {clients.count()}")

    except LogRegister_Details.DoesNotExist:
        print(f"Error: LogRegister_Details with aid '{aid}' does not exist.")
        user = None
        company = None
        clients = []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        user = None
        company = None
        clients = []

    print(f"-------------------------------")
    
    return render(request, 'admin/admindash.html', {
        'user': user,
        'company': company,
        'clients': clients,
    })

def dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
        print(company)
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
    print("hello")
    
    # check if Lead task exist in DB else create
    if not Work_Task.objects.filter(task_name__iexact='Lead Collection', company__isnull=True).exists():
        Work_Task.objects.create(
            task_name='Lead Collection',
            task_description='Efficient lead collection is the cornerstone of successful business growth',
        )
    
    meetings = LeadMeet.objects.filter(created_by__company=company)

    notifications = []

    for m in meetings:
       
        if not m.is_seen_dm:
            notifications.append({
                "message": f"{m.lead.name} meeting scheduled by {m.created_by}",
                "time": m.created_at
            })

      
        if m.is_update_notification:
            notifications.append({
                "message": f"{m.lead.name} meeting is updated",
                "time": m.updated_at
            })

    # Followup Notifications (NEW)
    followups = FollowupDetails.objects.filter(company=company)

    for f in followups:
        if f.response_date and f.next_followup_date:
            if not f.is_notified_dm and f.next_followup_date > f.response_date + timedelta(days=10):

                notifications.append({
                    "message": f"{f.telecaller.name} updated follow-up for {f.lead.name} "
                            f"(Delayed - Next follow-up on {f.next_followup_date.strftime('%d %b %Y')})",
                    "time": f.response_date
                })

                f.is_notified_dm = True
                f.save()

    # sort latest first
    notifications = sorted(notifications, key=lambda x: x["time"], reverse=True)

    return render(request, 'dmhead/headdash.html', {
        'user': user,
        'company': company,
        'name':name,
        "notifications": notifications,
        "notify_count": len(notifications)
    })
    
def teamlead(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
    print("hello")
    return render(request, 'teamlead/teamleaddash.html', {
        'user': user,
        'company': company,
        'name':name
    })

from django.utils.timezone import now
def executive(request): 
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    today = now().date()
    current_month = today.strftime("%B")
    current_year = today.year   


    target = TargetAssign.objects.filter(
        executive=name,
        month=current_month,
        year=current_year
    )

    monthly_achieved = (
        Leads.objects.filter(
            collected_by=name,
            added_date__month=today.month,
            added_date__year=today.year
        ).count()
    )

   
    today_leads = (
        Leads.objects.filter(
            collected_by=name,
            added_date=today
        ).count()
    )

    for t in target:
        t.achieved = monthly_achieved
        t.today_leads = today_leads

        if t.target_count > 0:
            t.progress = (t.achieved / t.target_count) * 100
        else:
            t.progress = 0

    return render(request, 'executive/executivedash.html', {
        'user': user,
        'company': company,
        'name': name,
        'target': target,
        'today_leads': today_leads
    })

def manager(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
    print("hello")
    return render(request, 'datamanager/managerdash.html', {
        'user': user,
        'company': company,
        'name':name
    })
    
def telecaller(request):
    username = request.session.get('tcid')
    user = LogRegister_Details.objects.get(log_username=username)
    employee = EmployeeRegister_Details.objects.get(login=user)

    leads_qs = LeadAssignedToTC.objects.filter(
        telecaller=employee,
        status=0
    ).select_related('lead')

    status_filter = request.GET.get('status')
    start = request.GET.get('start')
    end = request.GET.get('end')
    query = request.GET.get('q')

    if status_filter:
        if status_filter.lower() == 'allocated':
            leads_qs = leads_qs.filter(status=1)
        elif status_filter.lower() == 'opened':
            leads_qs = leads_qs.filter(status=2)
        elif status_filter.lower() == 'closed':
            leads_qs = leads_qs.filter(status=3)

    if start:
        start_date = parse_date(start)
        leads_qs = leads_qs.filter(assign_date__gte=start_date)
    if end:
        end_date = parse_date(end)
        leads_qs = leads_qs.filter(assign_date__lte=end_date)

    if query:
        leads_qs = leads_qs.filter(
            Q(lead__name__icontains=query) |
            Q(lead__email__icontains=query) |
            Q(lead__contact__icontains=query)
        )

    context = {
        'user': user,
        'name': employee,
        'new_leads': leads_qs,
        'lead_count': leads_qs.count(),
    }

    return render(request, 'telecaller/hr_dashboard.html', context)
    
def departments(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    # Save new department (if POST)
    if request.method == 'POST':
        name = request.POST.get('dept_name')
        content = request.POST.get('dept_content')
        if name and content and company:
            DepartmentRegister_Details.objects.create(
                business=company,
                name=name,
                description=content
            )
            return redirect('departments')  # Redirect to refresh page after POST

    departments = DepartmentRegister_Details.objects.filter(business=company)
    return render(request, 'admin/departments.html', {
        'departments': departments,
        'company': company
    })

from django.shortcuts import get_object_or_404

def edit_department(request, dept_id):
    dept = get_object_or_404(DepartmentRegister_Details, id=dept_id)

    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, BusinessRegister_Details.DoesNotExist):
        return redirect('departments')

    # Ensure department belongs to the current company
    if dept.business != company:
        return redirect('departments')

    if request.method == 'POST':
        name = request.POST.get('dept_name')
        content = request.POST.get('dept_content')
        if name and content:
            dept.name = name
            dept.description = content
            dept.save()
        return redirect('departments')
        
def delete_department(request, dept_id):
    dept = get_object_or_404(DepartmentRegister_Details, id=dept_id)

    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, BusinessRegister_Details.DoesNotExist):
        return redirect('departments')

    if dept.business == company:
        dept.delete()

    return redirect('departments')

def view_designations(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    departments = DepartmentRegister_Details.objects.filter(business=company)
    designations = DesignationRegister_Details.objects.filter(business=company)
    
    # For dropdown from LogRegister_Details positions
    all_positions = LogRegister_Details.ROLE_CHOICES

    pos=DesignationRegister_Details.ROLE_CHOICES

    if request.method == 'POST':
        department_id = request.POST.get('department')
        dashboard_id = request.POST.get('dashboard_id')
        designation_name = request.POST.get('designation_name')
        description = request.POST.get('description')

        if department_id and designation_name:
            dept = DepartmentRegister_Details.objects.get(id=department_id)
            DesignationRegister_Details.objects.create(
                business=company,
                department=dept,
                dashboard_id=dashboard_id,
                name=designation_name,
                description=description
            )
            return redirect('view_designations')

    return render(request, 'admin/designations.html', {
        'designations': designations,
        'departments': departments,
        'all_positions': all_positions,
        'pos':pos,
        'company':company
    })


def edit_designation(request, designation_id):
    designation = get_object_or_404(DesignationRegister_Details, id=designation_id)

    if request.method == 'POST':
        department_id = request.POST.get('department')
        designation_name = request.POST.get('designation_name')
        description = request.POST.get('description')

        department = get_object_or_404(DepartmentRegister_Details, id=department_id)

        designation.department = department
        designation.name = designation_name
        designation.description = description
        designation.save()

        return redirect('view_designations')  # Replace with your actual view name

def delete_designation(request, designation_id):
    designation = get_object_or_404(DesignationRegister_Details, id=designation_id)
    designation.delete()
    return redirect('view_designations')

def empsignup(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        department_id = request.POST.get('department')
        designation_id = request.POST.get('designation')

        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')

        company_instance = BusinessRegister_Details.objects.get(company_code=company_id)

        department_instance = get_object_or_404(DepartmentRegister_Details, id=department_id)
        designation_instance = get_object_or_404(DesignationRegister_Details, id=designation_id)

        # Create Login Entry
        login_entry = LogRegister_Details.objects.create(
            log_username=username,
            log_password=password,  
              position=designation_instance.name,
            is_staff='False'  
        )

        last_employee = EmployeeRegister_Details.objects.order_by('-id').first()

        if last_employee and last_employee.employee_code:
            try:
                last_number = int(last_employee.employee_code.replace('EMP', ''))
                new_employee_code = f"EMP{last_number + 1:03d}"
            except ValueError:
                new_employee_code = "EMP001"
        else:
            new_employee_code = "EMP001"

        # Create Employee Entry
        EmployeeRegister_Details.objects.create(
            login=login_entry,
            company=company_instance,
            department=department_instance,
            designation=designation_instance,
            employee_code=new_employee_code,
            name=name,
            contact_number=contact_number,
            email=email,
            address_line1=address,
            active_status="Approved"
        )

        messages.success(request, 'Employee registered successfully.')
        return redirect('login')  # Or wherever you want

    # For GET request: load departments for dropdown
    departments = DepartmentRegister_Details.objects.all()
    return render(request, 'landingpage/empsignup.html', {'departments': departments})

def ajax_load_departments(request):
    company_id = request.GET.get('company_id')
    departments = DepartmentRegister_Details.objects.filter(business__company_code=company_id)
    return JsonResponse(list(departments.values('id', 'name')), safe=False)

def ajax_load_designations(request):
    department_id = request.GET.get('department_id')
    designations = DesignationRegister_Details.objects.filter(department__id=department_id)
    return JsonResponse(list(designations.values('id', 'name')), safe=False)

def validate_email(request):
    email = request.GET.get('email', None)
    is_taken = EmployeeRegister_Details.objects.filter(email__iexact=email).exists()
    return JsonResponse({'is_taken': is_taken})

def login_requests(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        admin_user = LogRegister_Details.objects.filter(log_username=aid).first()
        if not admin_user:
            return redirect('login')   # or whatever your login URL name is
        company = BusinessRegister_Details.objects.get(login=admin_user)
    except (LogRegister_Details.DoesNotExist, BusinessRegister_Details.DoesNotExist):
        messages.error(request, "Invalid admin session.")
        return redirect('login')

    # Get users under this company with is_staff=False
    employee_list = EmployeeRegister_Details.objects.filter(
        company=company,
        login__is_staff=False
    )

    return render(request, 'admin/requests.html', {
        'employee_list': employee_list,
        'company':company
    })

from django.views.decorators.http import require_POST

@require_POST
def accept_user(request, login_id):
    login_entry = get_object_or_404(LogRegister_Details, id=login_id)
    login_entry.is_staff = True
    login_entry.save()
    
    return redirect('login_requests')


@require_POST
def decline_user(request, login_id):
    login_entry = get_object_or_404(LogRegister_Details, id=login_id)
    # Also delete associated employee
    EmployeeRegister_Details.objects.filter(login=login_entry).delete()
    login_entry.delete()
    
    return redirect('login_requests')
    
def employees(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()
    return render(request,'dmhead/employees.html',{'name':name})

def view_employees(request):
    hid = request.session.get('hid')
    if not hid:
        messages.error(request, "Session expired or invalid.")
        return redirect('login')

    try:
        # Fetch the head's login entry
        head_user = LogRegister_Details.objects.get(log_username=hid)

        # Fetch the EmployeeRegister_Details entry for the head user to get the company
        head_employee = EmployeeRegister_Details.objects.get(login=head_user)
        name=EmployeeRegister_Details.objects.filter(login=head_user).first()
        company_code = head_employee.company.company_code  # Get the company code from this
        department = head_employee.department
        company = head_employee.company

        # Now get all employees with the same company code
        employee_list = EmployeeRegister_Details.objects.filter(company__company_code=company_code,department=department)
        designations = DesignationRegister_Details.objects.filter(business=company)
        print(designations)


        return render(request, 'dmhead/view_employees.html', {
            'employee_list': employee_list,
            'company_name': head_employee.company.company_name,
            'designations':designations,
            'name':name
        })

    except LogRegister_Details.DoesNotExist:
        messages.error(request, "Head user not found.")
    except EmployeeRegister_Details.DoesNotExist:
        messages.error(request, "Head's employee record not found.")
    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}")

    return redirect('login')
    
def update_designation(request, emp_id):
    if request.method == 'POST':
        new_designation_id = request.POST.get('designation_id')
        employee = get_object_or_404(EmployeeRegister_Details, id=emp_id)
        new_designation = get_object_or_404(DesignationRegister_Details, id=new_designation_id)

        # Check if the employee is currently a Team Lead
        is_currently_team_lead = AllocationDetails.objects.filter(team_lead=employee).exists()
        # Check if the employee is currently an allocated Executive
        is_currently_allocated_exec = AllocationDetails.objects.filter(employee=employee, allocate_status=1).exists()

        # Update employee's designation
        employee.designation = new_designation
        employee.save()

        # Update the login position
        if employee.login:
            employee.login.position = new_designation.name
            employee.login.save()

        # If the person was a Team Lead but is no longer, remove all their allocations
        if is_currently_team_lead and new_designation.name.lower() != 'team lead':
            AllocationDetails.objects.filter(team_lead=employee).delete()

        # If the person was an Executive but is no longer, remove their allocation
        if is_currently_allocated_exec and new_designation.name.lower() != 'executive':
            AllocationDetails.objects.filter(employee=employee).delete()

        return redirect('view_employees')

def assign_team_lead(request):
    if request.method == 'POST':
        team_lead_id = request.POST.get('team_lead_id')
        executive_ids = request.POST.getlist('executive_ids')

        team_lead = get_object_or_404(EmployeeRegister_Details, id=team_lead_id)

        for eid in executive_ids:
            executive = get_object_or_404(EmployeeRegister_Details, id=eid)

            # Directly create allocation assuming executives shown are not allocated
            AllocationDetails.objects.create(
                employee=executive,
                team_lead=team_lead,
                allocate_status=1
            )

        messages.success(request, "Team Lead allocated to selected Executives.")
        return redirect('assign_team_lead')

    # GET: show only unallocated executives and all team leads
    head_username = request.session.get('hid')  # Head user session
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = EmployeeRegister_Details.objects.get(login=head_login)
    name = EmployeeRegister_Details.objects.filter(login=head_login).first()
    company_code = head_employee.company.company_code 

    # Only show executives not already allocated (no active allocation)
    allocated_exec_ids = AllocationDetails.objects.filter(
        allocate_status=1
    ).values_list('employee_id', flat=True)

    executives = EmployeeRegister_Details.objects.filter(
        company__company_code=company_code,
        designation__name='Executive'
    ).exclude(id__in=allocated_exec_ids)

    team_leads = EmployeeRegister_Details.objects.filter(
        company__company_code=company_code,
        designation__name='Team_Lead'
    )

    return render(request, 'dmhead/assign_teamlead.html', {
        'executives': executives,
        'team_leads': team_leads,
        'name': name
    })


def show_reallocation_page(request):
    head_user = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_user)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    company_code = head_employee.company.company_code
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    # Get all executives under this head
    executives = EmployeeRegister_Details.objects.filter(
        company__company_code=company_code, designation__name='Executive'
    )

    team_leads = EmployeeRegister_Details.objects.filter(
        company__company_code=company_code, designation__name='Team_Lead'
    )
    print("teamleads",team_leads)

    return render(request, 'dmhead/reallocate.html', {
        'executives': executives,
        'team_leads': team_leads,
        'name':name
    })

def reallocate_executives(request):
    if request.method == 'POST':
        selected_executives = request.POST.getlist('executive_ids')
        new_team_lead_id = request.POST.get('team_lead_id')

        new_team_lead = get_object_or_404(EmployeeRegister_Details, id=new_team_lead_id)

        for exec_id in selected_executives:
            executive = get_object_or_404(EmployeeRegister_Details, id=exec_id)

            # Update existing allocation or create new one
            allocation, created = AllocationDetails.objects.get_or_create(employee=executive)
            allocation.team_lead = new_team_lead
            allocation.allocate_status = 1
            allocation.save()

        return redirect('show_reallocation_page')  # Update this to your actual view name

    return redirect('show_reallocation_page')

def Leave(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    department = head_employee.department

    # All employees in the same department
    department_employees = EmployeeRegister_Details.objects.filter(department=department)

    leave = EmployeeLeave.objects.filter(employee__department=department)

    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if employee_id:
        leave = leave.filter(employee__id=employee_id)

    if from_date:
        leave = leave.filter(start_date__gte=from_date)

    if to_date:
        leave = leave.filter(end_date__lte=to_date)

    return render(request, 'dmhead/leaves.html', {
        'leave': leave,
        'department_employees': department_employees,
        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })

def schedules(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    department = head_employee.department

    # All employees in the same department
    department_employees = EmployeeRegister_Details.objects.filter(department=department)

    schedules = EmployeeSchedule.objects.filter(employee__department=department)

    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if employee_id:
        schedules = schedules.filter(employee__id=employee_id)

    if from_date:
        schedules = schedules.filter(schedule_date__gte=from_date)

    if to_date:
        schedules = schedules.filter(schedule_date__lte=to_date)

    return render(request, 'dmhead/schedules.html', {
        'schedules': schedules,
        'department_employees': department_employees,
        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })

def actiontaken(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    department = head_employee.department

    # All employees in the same department
    department_employees = EmployeeRegister_Details.objects.filter(department=department)

    leave = ActionTaken.objects.filter(employee__department=department)

    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if employee_id:
        leave = leave.filter(employee__id=employee_id)

    if from_date:
        leave = leave.filter(action_date__gte=from_date)

    if to_date:
        leave = leave.filter(action_date__lte=to_date)

    return render(request, 'dmhead/actiontaken.html', {
        'leave': leave,
        'department_employees': department_employees,
        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })


def complaint(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    department = head_employee.department

    # All employees in the same department
    department_employees = EmployeeRegister_Details.objects.filter(department=department)

    leave = Complaint.objects.filter(employee__department=department)

    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if employee_id:
        leave = leave.filter(employee__id=employee_id)

    if from_date:
        leave = leave.filter(complaint_date__gte=from_date)

    if to_date:
        leave = leave.filter(complaint_date__lte=to_date)

    return render(request, 'dmhead/complaint.html', {
        'leave': leave,
        'department_employees': department_employees,
        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })

def dm_works(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = (
        EmployeeRegister_Details.objects
        .select_related('company', 'department', 'designation')
        .filter(login=user)
        .first()
    )

    company = employee.company if employee else None
    department = employee.department if employee else None

    company_id = company.id if company else None

    designation_ids = []
    if company_id:
        designation_qs = DesignationRegister_Details.objects.filter(
            business_id=company_id,
            dashboard_id__in=[
                'Digital_Marketing_Head',
                'Team_Lead',
                'Executive',
            ]
        )
        designation_ids = list(designation_qs.values_list('id', flat=True))

    search_users = EmployeeRegister_Details.objects.none()
    if company_id and department and designation_ids:
        search_users = (
            EmployeeRegister_Details.objects
            .select_related('company', 'department', 'designation', 'login')
            .filter(
                company_id=company_id,
                department=department,
                designation_id__in=designation_ids,
            )
            .order_by('name')
        )

    print(f'employee : {employee} \ncompany: {company} \nsearch_users count: {search_users.count()}')

    return render(request, 'dmhead/works.html', {
        'user': user,
        'company': company,
        'employee': employee,
        'search_users': search_users,
    })

def resigned_employees_list(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = (
        EmployeeRegister_Details.objects
        .select_related('company', 'department', 'designation')
        .filter(login=user)
        .first()
    )

    company = employee.company if employee else None
    department = employee.department if employee else None

    company_id = company.id if company else None
    resigned_list = EmployeeRegister_Details.objects.none()
    if company_id and department:
        resigned_list = (
            EmployeeRegister_Details.objects
            .select_related('company', 'department', 'designation', 'login')
            .filter(
                company_id=company_id,
                department=department
            )
            .exclude(active_status__in=['approved', 'pending'])  # // if its changed in future to boolean change here
            .order_by('name')
        )

    print(f'employee : {employee} \ncompany: {company} \resigned_list count: {resigned_list.count()}')

    context = {
        'name':employee,
        'resigned_list': resigned_list,
        'company_name': company.company_name if company else '',
    }

    return render(request, 'dmhead/resigned_employees_list.html', context)
    
def feedbacks(request):
    head_username = request.session.get('hid')
    head_login = get_object_or_404(LogRegister_Details, log_username=head_username)
    head_employee = get_object_or_404(EmployeeRegister_Details, login=head_login)
    name=EmployeeRegister_Details.objects.filter(login=head_login).first()

    department = head_employee.department
    department_employees = EmployeeRegister_Details.objects.filter(department=department)

    employee_id = request.GET.get('employee_id')
    feedback_type = request.GET.get('feedback_type', 'all')  # default to 'all'

    feedbacks = Feedback.objects.filter(employee__department=department)

    if employee_id:
        feedbacks = feedbacks.filter(employee__id=employee_id)

    if feedback_type == 'given':
        # Feedbacks given by head
        feedbacks = feedbacks.filter(from_id=head_employee.id)
    elif feedback_type == 'received':
        # Feedbacks received by head
        feedbacks = feedbacks.filter(employee=head_employee)

    return render(request, 'dmhead/feedbacks.html', {
        'leave': feedbacks,
        'department_employees': department_employees,
        'selected_employee': employee_id,
        'feedback_type': feedback_type,
        'name':name
    })
    
###executive###
def schedule(request):
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    today = date.today()
    today_schedules = EmployeeSchedule.objects.filter(employee=employee, schedule_date=today)

    return render(request, 'executive/schedule.html', {
        'today_schedules': today_schedules,
        'today': today,  
        'user': user,
        'company': company,
        'name': name,
    })

def add_employee_schedule(request):
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        schedule_head = request.POST.get('schedule_head')
        todo_content = request.POST.get('todo_content')
        EmployeeSchedule.objects.create(
            employee=employee,
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            schedule_head=schedule_head,
            todo_content=todo_content
        )
        messages.success(request, 'Schedule added successfully!')
        return redirect('schedule')

    return render(request, 'executive/add_schedule.html',{

        'user': user,
        'company': company,
        'name':name
    })

def edit_employee_schedule(request, schedule_id):
    schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()

    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        schedule_head = request.POST.get('schedule_head')
        todo_content = request.POST.get('todo_content')

        schedule.schedule_date = schedule_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.schedule_head = schedule_head
        schedule.todo_content = todo_content
        schedule.save()

        messages.success(request, 'Schedule updated successfully!')
        return redirect('schedule_list')

    return render(request, 'executive/edit_schedule.html',{
        'schedule': schedule,
        'user': user,
        'company': company,
        'name':name})

def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        schedule_head = request.POST.get('schedule_head')
        todo_content = request.POST.get('todo_content')
        schedule.schedule_date = schedule_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.schedule_head = schedule_head
        schedule.todo_content = todo_content
        schedule.save()
        return redirect('schedule')
    return render(request, 'executive/edit_schedule.html',{
        'schedule': schedule,
        'user': user,
        'company': company,
        'name':name})
        
def schedule_list(request):
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status_filter = request.GET.get('status_filter', 'All')
    schedules = EmployeeSchedule.objects.filter(employee=employee)
    if from_date:
        schedules = schedules.filter(schedule_date__gte=from_date)
    if to_date:
        schedules = schedules.filter(schedule_date__lte=to_date)
    if status_filter == 'Upcoming':
      schedules = schedules.filter(schedule_date__gte=date.today()).exclude(schedule_status='completed')
    elif status_filter == 'Completed':
      schedules = schedules.filter(schedule_status='completed')
    elif status_filter == 'All':
       pass  
    context = {
        'schedules': schedules.order_by('-schedule_date'),
        'from_date': from_date,
        'to_date': to_date,
        'status_filter': status_filter,
        'user': user,
        'company': company,
        'name': name
    }
    return render(request, 'executive/schedule_list.html', context)

def update_schedule_status(request):
    if request.method == "POST":
        schedule_id = request.POST.get("id")
        is_completed = request.POST.get("completed") == "true"

        try:
            sched = EmployeeSchedule.objects.get(id=schedule_id)
            sched.schedule_status = "Completed" if is_completed else "Upcoming"
            sched.save()
            return JsonResponse({"success": True})
        except EmployeeSchedule.DoesNotExist:
            return JsonResponse({"success": False, "error": "Schedule not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

def leave_apply(request):
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        reason = request.POST.get('reason')
        request_file = request.FILES.get('request_file')

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            number_of_days = (end - start).days + 1
        except Exception as e:
            messages.error(request, "Invalid date input.")
            return redirect('leave_apply')

        EmployeeLeave.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason,
            number_of_days=number_of_days,
            request_file=request_file,
        )
        messages.success(request, "Leave request submitted successfully.")
        return redirect('leave_apply')


    leaves = EmployeeLeave.objects.filter(employee=employee).order_by('-start_date')

    return render(request, 'executive/leave_apply.html', {
        'user': user,
        'company': company,
        'name': name,
        'leaves': leaves,
        'today': datetime.today().date().isoformat()
    })

def delete_employee_schedule(request, pk):
    schedule = get_object_or_404(EmployeeSchedule, pk=pk)
    schedule.delete()
    messages.success(request, "Schedule deleted successfully.")
    return redirect('schedule_list')
    
# ======================================================== DM head ================================================================

def dm_work(request):
    user_id = request.session.get('hid')
    
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()

    logged_in_user = LogRegister_Details.objects.get(log_username=user_id)
    user_company = BusinessRegister_Details.objects.filter(login=logged_in_user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()


    return render(request, 'dmhead/dm_work.html',{
        'logged_in_user': logged_in_user,
        'user_company': user_company,
        'employee_profile': employee_profile,
        'user': user,
        'company': company,
        'name':name
    })

def task_list(request):

    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()

    logged_in_user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    dm_head_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()
    company = BusinessRegister_Details.objects.get(id=dm_head_profile.company_id)
    user_company = BusinessRegister_Details.objects.filter(login=logged_in_user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()


    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')

        if task_id:
            task = Work_Task.objects.get(id=task_id)
            task.task_name = task_name
            task.task_description = task_description
            task.save()
        else:
            if task_name and task_name.strip().lower() != 'lead collection':
                Work_Task.objects.create(
                    task_name=task_name,
                    task_description=task_description,
                    company=company
                )

        return redirect('task_list')

    tasks = Work_Task.objects.filter(models.Q(company=company) | models.Q(company__isnull=True)).order_by('id')
    context = {
        'tasks': tasks,
        'logged_in_user': logged_in_user,
        'user_company': user_company,
        'employee_profile': employee_profile,
        'user': user,
        'company': company,
        'name':name
    }
    return render(request, 'dmhead/task_list.html', context)

def delete_task_main(request, task_id):
    task = Work_Task.objects.get(id=task_id)
    task.delete()
    return redirect('task_list')


email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')
phone_regex = re.compile(r'^\d{10}$')
website_regex = re.compile(r'^https?:\/\/.+\..+')

def register_client(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    name=EmployeeRegister_Details.objects.filter(login=user).first()
    logged_in_user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    dm_head_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()

    user_company = BusinessRegister_Details.objects.filter(login=logged_in_user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()


    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        data = request.POST

        client_name = data.get('client_name', '').strip()
        client_email_primary = data.get('client_email_primary', '').strip()
        client_email_alter = data.get('client_email_alter', '').strip()
        client_phone = data.get('client_phone', '').strip()
        client_phone_alter = data.get('client_phone_alter', '').strip()
        client_business_name = data.get('client_business_name', '').strip()
        client_business_email_primary = data.get('client_business_email_primary', '').strip()
        client_business_email_alter = data.get('client_business_email_alter', '').strip()
        client_business_website = data.get('client_business_website', '').strip()
        client_business_phone = data.get('client_business_phone', '').strip()
        client_business_phone_alter = data.get('client_business_phone_alter', '').strip()

        # === Validations ===
        errors = []
        if not email_regex.match(client_email_primary):
            errors.append('Personal email must be valid.')
        if client_email_primary == client_email_alter:
            errors.append('Personal alternate email must differ from primary.')
        if not phone_regex.match(client_phone):
            errors.append('Personal phone must be 10 digits.')
        if client_phone == client_phone_alter:
            errors.append('Personal alternate phone must differ from primary.')
        if not email_regex.match(client_business_email_primary):
            errors.append('Business email must be valid.')
        if client_business_email_primary == client_business_email_alter:
            errors.append('Business alternate email must differ from primary.')
        if not phone_regex.match(client_business_phone):
            errors.append('Business phone must be 10 digits.')
        if client_business_phone == client_business_phone_alter:
            errors.append('Business alternate phone must differ from primary.')
        if not website_regex.match(client_business_website):
            errors.append('Website must start with http:// or https://')

        # ====== Check uniqueness ======
        check_qs = ClientRegister.objects.all()
        if client_id:
            check_qs = check_qs.exclude(id=client_id)

        if check_qs.filter(client_email_primary=client_email_primary).exists():
            errors.append('Personal email already exists.')
        if check_qs.filter(client_phone=client_phone).exists():
            errors.append('Personal phone already exists.')
        if check_qs.filter(client_business_email_primary=client_business_email_primary).exists():
            errors.append('Business email already exists.')
        if check_qs.filter(client_business_phone=client_business_phone).exists():
            errors.append('Business phone already exists.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect('register_client')

        # === Save or update ===
        if client_id:
            client = ClientRegister.objects.get(id=client_id)
        else:
            client = ClientRegister()
        
        client.company = company
        client.company_id = dm_head_profile.company.id
        client.client_name = client_name
        client.client_email_primary = client_email_primary
        client.client_email_alter = client_email_alter
        client.client_phone = client_phone
        client.client_phone_alter = client_phone_alter
        client.client_business_name = client_business_name
        client.client_business_email_primary = client_business_email_primary
        client.client_business_email_alter = client_business_email_alter
        client.client_business_website = client_business_website
        client.client_business_phone = client_business_phone
        client.client_business_phone_alter = client_business_phone_alter

        client.client_address1 = data.get('client_address1', '').strip()
        client.client_address2 = data.get('client_address2', '').strip()
        client.client_address3 = data.get('client_address3', '').strip()
        client.client_place = data.get('client_place', '').strip()
        client.client_district = data.get('client_district', '').strip()
        client.client_state = data.get('client_state', '').strip()

        if request.FILES.get('client_profile'):
            client.client_profile = request.FILES.get('client_profile')

        client.client_business_address1 = data.get('client_business_address1', '').strip()
        client.client_business_address2 = data.get('client_business_address2', '').strip()
        client.client_business_address3 = data.get('client_business_address3', '').strip()
        client.client_business_place = data.get('i_client_business_place', '').strip()
        client.client_business_district = data.get('i_client_business_district', '').strip()
        client.client_business_state = data.get('i_client_business_state', '').strip()

        if request.FILES.get('business_logo'):
            client.business_logo = request.FILES.get('business_logo')
        if request.FILES.get('client_business_file'):
            client.client_business_file = request.FILES.get('client_business_file')

        client.more_description = data.get('more_description', '').strip()

        client.save()

        messages.success(request, 'Client saved successfully.')
        return redirect('register_client')

    clients = ClientRegister.objects.filter(company=company)
    return render(request, 'dmhead/register_client.html', {
        'clients': clients,
        'logged_in_user': logged_in_user,
        'user_company': user_company,
        'employee_profile': employee_profile,
        'user': user,
        'company': company,
        'name':name
    })

def delete_client(request, client_id):
    client = ClientRegister.objects.get(id=client_id)
    client.delete()
    messages.success(request, 'Client deleted successfully.')
    return redirect('register_client')

def register_work(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    name=EmployeeRegister_Details.objects.filter(login=user).first()
    works = WorkRegister.objects.filter(company=company)
    user_id = request.session.get('hid')
    logged_in_user = LogRegister_Details.objects.get(log_username=user_id)
    user_company = BusinessRegister_Details.objects.filter(login=logged_in_user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()


    work_data = []
    for work in works:
        has_lead_collection = work.clienttask_register_set.filter(task_name__icontains='Lead Collection').exists()
        work_data.append({
            'work': work,
            'has_lead_collection': has_lead_collection,
        })

    context = {
        'work_data': work_data,
        'logged_in_user': logged_in_user,
        'user_company': user_company,
        'employee_profile': employee_profile,
        'user': user,
        'company': company,
        'name':name
    }
    return render(request, 'dmhead/register_work.html', context)

def check_unique_field(request):
    field = request.GET.get('field')
    value = request.GET.get('value')
    exclude_id = request.GET.get('exclude_id')

    response = {'is_unique': True}

    if field and value:
        qs = ClientRegister.objects.all()
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        field_map = {
            'client_email_primary': 'client_email_primary',
            'client_email_alter': 'client_email_alter',
            'client_phone': 'client_phone',
            'client_phone_alter': 'client_phone_alter',
            'client_business_email_primary': 'client_business_email_primary',
            'client_business_email_alter': 'client_business_email_alter',
            'client_business_phone': 'client_business_phone',
            'client_business_phone_alter': 'client_business_phone_alter',
        }

        model_field = field_map.get(field)
        if model_field:
            filter_kwargs = {model_field: value}
            if qs.filter(**filter_kwargs).exists():
                response['is_unique'] = False

    return JsonResponse(response)

@csrf_exempt
def create_work(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        company_id = request.POST.get('company_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('work_description')
        task_ids = request.POST.getlist('task_ids[]')
        new_task_name = request.POST.get('new_task')
        work_file = request.FILES.get('work_file')

        if not client_id or not company_id:
            return JsonResponse({'success': False, 'message': 'Client or company ID missing'})

        client = ClientRegister.objects.get(id=client_id)
        company = BusinessRegister_Details.objects.get(id=company_id)

        if new_task_name:
            ClientTask_Register.objects.create(
                company=company,
                client=client,
                work=None,
                task_name=new_task_name,
                task_description='(Custom Task)'
            )

        work = WorkRegister.objects.create(
            client=client,
            company=company,
            work_description=description,
            work_create_date=start_date,
            work_end_date=end_date
        )

        if work_file:
            work.work_file = work_file
            work.save()

        for task_id in task_ids:
            try:
                task = Work_Task.objects.get(id=task_id)
                ClientTask_Register.objects.create(
                    company=company,
                    client=client,
                    work=work,
                    task_name=task.task_name,
                    task_description=task.task_description
                )
            except Work_Task.DoesNotExist:
                continue

        ClientTask_Register.objects.filter(client=client, work__isnull=True).update(work=work)

        client.work_reg_status = 1
        client.save()

        return JsonResponse({'success': True, 'message': 'Work created successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

# edit work
@csrf_exempt
@require_POST
def edit_work(request):
    try:
        work_id = request.POST.get('work_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        file = request.FILES.get('work_file')

        work = WorkRegister.objects.get(id=work_id)
        work.work_create_date = start_date
        work.work_end_date = end_date
        work.work_description = description

        if file:
            if work.work_file:
                if default_storage.exists(work.work_file.name):
                    default_storage.delete(work.work_file.name)
            work.work_file = file

        work.save()
        return JsonResponse({'success': True, 'message': 'Work updated successfully'})

    except WorkRegister.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Work not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# delete work
@csrf_exempt
@require_POST
def delete_work(request, work_id):
    try:
        work = WorkRegister.objects.get(id=work_id)
        work.delete()
        return JsonResponse({'success': True, 'message': 'Work deleted successfully'})
    except WorkRegister.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Work not found'})

# edit task
@csrf_exempt
@require_POST
def edit_task(request):
    try:
        task_id = request.POST.get('task_id')
        task_name = request.POST.get('task_name')
        description = request.POST.get('task_description')
        file = request.FILES.get('task_file')

        task = ClientTask_Register.objects.get(id=task_id)
        is_common = Work_Task.objects.filter(task_name=task.task_name, company__isnull=True).exists()

        if not is_common:
            task.task_name = task_name

        task.task_description = description

        if file:
            if task.task_file and default_storage.exists(task.task_file.name):
                default_storage.delete(task.task_file.name)
            task.task_file = file

        task.save()
        return JsonResponse({'success': True, 'message': 'Task updated successfully'})
    except ClientTask_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# delete task
@csrf_exempt
@require_POST
def delete_task(request, task_id):
    try:
        task = ClientTask_Register.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True, 'message': 'Task deleted successfully'})
    except ClientTask_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Task not found'})

# add task
@csrf_exempt
@require_POST
def add_more_task(request):
    try:
        work_id = request.POST.get('work_id')
        task_type = request.POST.get('task_type')
        description = request.POST.get('task_description')
        file = request.FILES.get('task_file')

        work = WorkRegister.objects.get(id=work_id)
        client = work.client
        company = work.company

        if task_type == 'client':
            task_name = request.POST.get('task_name_client').strip()

            if ClientTask_Register.objects.filter(work=work, task_name__iexact=task_name).exists():
                return JsonResponse({'success': False, 'message': 'Client task with this name already exists.'})

        else:
            task_id = request.POST.get('task_name_company')
            task = Work_Task.objects.get(id=task_id)
            task_name = task.task_name
            description = description or task.task_description

        ClientTask_Register.objects.create(
            company=company,
            client=client,
            work=work,
            task_name=task_name,
            task_description=description,
            task_file=file if file else None
        )

        return JsonResponse({'success': True, 'message': 'Task added successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# add lead category btn
@csrf_exempt
@require_POST
def add_lead_category(request):
    try:
        task_id = request.POST.get('task_id')
        collection_for = request.POST.get('collection_for', '').strip()
        description = request.POST.get('description', '').strip()
        target = request.POST.get('target') or 0
        file = request.FILES.get('file')

        if not collection_for:
            return JsonResponse({'success': False, 'message': 'Collection Head is required.'})

        task = ClientTask_Register.objects.get(id=task_id)

        LeadCategory_Register.objects.create(
            client_task=task,
            collection_for=collection_for,
            description=description,
            target=target,
            file=file if file else None,
        )

        return JsonResponse({'success': True, 'message': 'Lead category added successfully'})

    except ClientTask_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# edit lead category
@csrf_exempt
@require_POST
def edit_category(request):
    try:
        category_id = request.POST.get('category_id')
        collection_for = request.POST.get('collection_for', '').strip()
        description = request.POST.get('description', '').strip()
        target = request.POST.get('target') or 0
        file = request.FILES.get('file')

        category = LeadCategory_Register.objects.get(id=category_id)
        category.collection_for = collection_for
        category.description = description
        category.target = target

        if file:
            if category.file and default_storage.exists(category.file.name):
                default_storage.delete(category.file.name)
            category.file = file

        category.save()
        return JsonResponse({'success': True, 'message': 'Category updated successfully'})
    except LeadCategory_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Category not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# delete lead category
@csrf_exempt
@require_POST
def delete_category(request, category_id):
    try:
        category = LeadCategory_Register.objects.get(id=category_id)
        category.delete()
        return JsonResponse({'success': True, 'message': 'Category deleted successfully'})
    except LeadCategory_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Category not found'})


# edit fields
def field_page(request, work_id):
    user_id = request.session.get('hid')
    logged_in_user = LogRegister_Details.objects.get(log_username=user_id)
    user_company = BusinessRegister_Details.objects.filter(login=logged_in_user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()

    try:
        work = WorkRegister.objects.get(id=work_id)
        client = work.client

        lead_task = ClientTask_Register.objects.filter(
            work=work, task_name__iexact="Lead Collection"
        ).first()

        if not lead_task:
            return HttpResponse("No 'Lead Collection' task found.", status=404)

        categories = list(
            LeadCategory_Register.objects.filter(client_task=lead_task).prefetch_related('leadfield_register_set')
        )
        all_fields = [field for cat in categories for field in cat.leadfield_register_set.all()]
        mapped_field_count = sum(1 for field in all_fields if field.question_id is not None)
        unmapped_field_names = [field.name or f'Field #{field.id}' for field in all_fields if field.question_id is None]

        context = {
            'work': work,
            'client': client,
            'lead_task': lead_task,
            'categories': categories,
            'mapped_field_count': mapped_field_count,
            'unmapped_field_names': unmapped_field_names,
            'logged_in_user': logged_in_user,
            'user_company': user_company,
            'employee_profile': employee_profile,
            'interview_questions': INTERVIEW_QUESTIONS,
        }
        return render(request, 'dmhead/field_page.html', context)
    except WorkRegister.DoesNotExist:
        return HttpResponse("Work not found", status=404)

# add field
@csrf_exempt
@require_POST
def add_field(request):
    from django.core.exceptions import ValidationError
    from django.db import IntegrityError, transaction

    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('field_name', '').strip()
        description = request.POST.get('description', '').strip()
        question_id_value = request.POST.get('question_id', '').strip()

        if question_id_value:
            try:
                question_id = int(question_id_value)
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'message': 'Choose a valid interview question.'}, status=400)
            if question_id not in QUESTION_BY_ID:
                return JsonResponse({'success': False, 'message': 'Choose a valid interview question.'}, status=400)
        else:
            question_id = None
        if not name:
            return JsonResponse({'success': False, 'message': 'Field name is required.'}, status=400)

        # Get these new values from the POST request
        client_id = request.POST.get('client_id')
        work_id = request.POST.get('work_id')
        print(f'to test category_id {category_id}\nclient {client_id}\nwork_id : {work_id}')

        category = LeadCategory_Register.objects.get(id=category_id)

        if LeadField_Register.objects.filter(lead_category=category, name__iexact=name).exists():
            return JsonResponse({'success': False, 'message': 'Field already exists for this category.'})

        cat_task = category.client_task
        client = ClientRegister.objects.get(id=client_id) if client_id else (cat_task.client if cat_task else None)
        work = WorkRegister.objects.get(id=work_id) if work_id else (cat_task.work if cat_task else None)

        field = LeadField_Register(
            lead_category=category,
            name=name,
            description=description,
            client=client,
            work=work,
            question_id=question_id,
        )
        field.full_clean()
        with transaction.atomic():
            field.save()

        return JsonResponse({'success': True, 'message': 'Field added successfully'})
    
    except LeadCategory_Register.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid category'})
    except ClientRegister.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid client'})
    except WorkRegister.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid work'})
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': ' '.join(e.messages)}, status=400)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'This interview question is already assigned to another field in this work.',
        }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@require_POST
def edit_field(request):
    from django.core.exceptions import ValidationError
    from django.db import IntegrityError, transaction

    try:
        field = LeadField_Register.objects.get(pk=request.POST.get('field_id'))
    except (LeadField_Register.DoesNotExist, TypeError, ValueError):
        return JsonResponse({'success': False, 'message': 'Field not found.'}, status=404)

    question_id_value = request.POST.get('question_id', '').strip()
    if question_id_value:
        try:
            question_id = int(question_id_value)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Choose a valid interview question.'}, status=400)
        if question_id not in QUESTION_BY_ID:
            return JsonResponse({'success': False, 'message': 'Choose a valid interview question.'}, status=400)
    else:
        question_id = None

    name = request.POST.get('field_name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'message': 'Field name is required.'}, status=400)

    field.name = name
    field.description = request.POST.get('description', '').strip()
    field.question_id = question_id
    if (not field.work_id or not field.client_id) and field.lead_category_id:
        cat_task = field.lead_category.client_task
        if cat_task:
            if not field.work_id and cat_task.work_id:
                field.work_id = cat_task.work_id
            if not field.client_id and cat_task.client_id:
                field.client_id = cat_task.client_id
    try:
        field.full_clean()
        with transaction.atomic():
            field.save(update_fields=['name', 'description', 'question_id', 'work', 'client'])
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': ' '.join(e.messages)}, status=400)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'This interview question is already assigned to another field in this work.',
        }, status=400)

    return JsonResponse({'success': True, 'message': 'Field updated successfully.'})

# Js get calls

def get_client(request, client_id):
    print(f'==================what the f is this : {client_id}================================')
    try:
        client = ClientRegister.objects.get(id=client_id)
        data = {
            'client_name': client.client_name,
            'client_email_primary': client.client_email_primary,
            'client_email_alter': client.client_email_alter,
            'client_phone': client.client_phone,
            'client_phone_alter': client.client_phone_alter,
            'client_address1': client.client_address1,
            'client_address2': client.client_address2,
            'client_address3': client.client_address3,
            'client_place': client.client_place,
            'client_district': client.client_district,
            'client_state': client.client_state,
            'client_business_name': client.client_business_name,
            'client_business_email_primary': client.client_business_email_primary,
            'client_business_email_alter': client.client_business_email_alter,
            'client_business_website': client.client_business_website,
            'client_business_phone': client.client_business_phone,
            'client_business_phone_alter': client.client_business_phone_alter,
            'client_business_address1': client.client_business_address1,
            'client_business_address2': client.client_business_address2,
            'client_business_address3': client.client_business_address3,
            'i_client_business_place': client.client_business_place,
            'i_client_business_district': client.client_business_district,
            'i_client_business_state': client.client_business_state,
            'more_description': client.more_description,
            'company_id': client.company.id if client.company else 'None',

        }
        return JsonResponse(data)
    except ClientRegister.DoesNotExist:
        raise Http404("Client not found")

def get_work(request, work_id):
    try:
        work = WorkRegister.objects.get(id=work_id)
        data = {
            'id': work.id,
            'start_date': work.work_create_date.isoformat() if work.work_create_date else '',
            'end_date': work.work_end_date.isoformat() if work.work_end_date else '',
            'description': work.work_description or '',
            'work_file_url': work.work_file.url if work.work_file else '',
        }
        return JsonResponse(data)
    except WorkRegister.DoesNotExist:
        raise Http404("Work not found")

def get_task(request, task_id):
    try:
        task = ClientTask_Register.objects.get(id=task_id)
        # determine if it's a company (common) task
        is_common = Work_Task.objects.filter(task_name=task.task_name, company__isnull=True).exists()

        data = {
            'client_name': task.client.client_name if task.client else '',
            'task_name': task.task_name,
            'task_description': task.task_description,
            'task_file_url': task.task_file.url if task.task_file else '',
            'is_common': is_common,
        }   
        return JsonResponse(data)
    except ClientTask_Register.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

def get_available_tasks(request):
    logged_in_user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    dm_head_profile = EmployeeRegister_Details.objects.filter(login=logged_in_user).first()
    company = dm_head_profile.company

    work_id = request.GET.get('work_id')
    all_tasks = Work_Task.objects.filter(company=company)

    if work_id:
        existing_task_names = ClientTask_Register.objects.filter(work_id=work_id).values_list('task_name', flat=True)
        all_tasks = all_tasks.exclude(task_name__in=existing_task_names)

        if not any(task.strip().lower() == "lead collection" for task in existing_task_names):
            lead_collection = Work_Task.objects.filter(company__isnull=True, task_name="Lead Collection")
            all_tasks = list(lead_collection) + list(all_tasks)
    else:
        lead_collection = Work_Task.objects.filter(company__isnull=True, task_name="Lead Collection")
        all_tasks = list(lead_collection) + list(all_tasks)

    task_list = [{'id': t.id, 'name': t.task_name, 'description': t.task_description} for t in all_tasks]
    return JsonResponse({'tasks': task_list})

def get_field(request, field_id):
    try:
        field = LeadField_Register.objects.select_related(
            'lead_category__client_task__client', 'client'
        ).get(id=field_id)
        category = field.lead_category
        task = category.client_task if category else None
        client_obj = (task.client if task and task.client else None) or field.client

        return JsonResponse({
            'name': field.name,
            'description': field.description or '',
            'question_id': field.question_id,
            'collection_for': category.collection_for if category else '',
            'client_name': client_obj.client_name if client_obj else '',
        })
    except LeadField_Register.DoesNotExist:
        return JsonResponse({'error': 'Field not found'}, status=404)

def get_category(request, category_id):
    try:
        category = LeadCategory_Register.objects.get(id=category_id)
        task = category.client_task
        client = task.client
        work = task.work

        data = {
            'collection_for': category.collection_for,
            'description': category.description or '',
            'target': category.target,
            'file_url': category.file.url if category.file else '',
            'client_name': client.client_name if client else 'Unknown',
            'client_business': client.client_business_name if client else '',
            'category_id': category.id,
            'task_id': task.id,
            'client_id': client.id if client else '',
            'work_id': work.id if work else '',
        }
        return JsonResponse(data)
    except LeadCategory_Register.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

# allocate work
def allocate_work_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    team_leads = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id='Team_Lead'
    )

    works = WorkRegister.objects.filter(company=company).select_related('client').prefetch_related('workassign_set__team_lead')

    for work in works:
        unique_tls = {}
        for wa in work.workassign_set.all():
            if wa.team_lead.id not in unique_tls:
                unique_tls[wa.team_lead.id] = wa
        work.unique_assignments = list(unique_tls.values())

    return render(request, 'dmhead/allocate_work.html', {
        'works': works,
        'team_leads': team_leads,
        'user': user,
        'company': company,
        'name':name
    })


# team lead tasks
def teamlead_tasks(request, tl_id):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()

    team_lead = EmployeeRegister_Details.objects.get(id=tl_id)

    client_id = request.GET.get('client_id')

    assigned_work = WorkAssign.objects.filter(team_lead=team_lead)

    if client_id:
        assigned_work = assigned_work.filter(work_register__client_id=client_id)

    return render(request, 'dmhead/teamlead_tasks.html', {
        'team_lead': team_lead,
        'assigned_works': assigned_work,
        'user': user,
        'company': company,
        'name':name,
        'client_id': client_id
    })


# add task to executive
def assign_to_exec_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    structured_assignments = []

    work_assigns = WorkAssign.objects.filter(
        company=company,
        assign_type=1
    ).select_related('client', 'team_lead').prefetch_related('client_task')

    for assign in work_assigns:
        for task in assign.client_task.all():
            if task.task_name.strip().lower() == "lead collection":
                # Split each category into its own row
                categories = LeadCateogry_TeamAllocate.objects.filter(
                    work_assign=assign,
                    lead_category__client_task=task
                ).select_related('lead_category')

                for cat in categories:
                    structured_assignments.append({
                        "client_name": assign.client.client_name,
                        "client_profile": assign.client.client_profile.url if assign.client.client_profile else '',
                        "start_date": assign.from_date,
                        "due_date": assign.due_date,
                        "team_lead": assign.team_lead.name,
                        "team_lead_id": assign.team_lead.id,
                        "assign_id": assign.id,
                        "task_name": task.task_name,
                        "is_category": True,
                        "category_id": cat.lead_category.id,
                        "category_name": cat.lead_category.collection_for,
                    })
            else:
                structured_assignments.append({
                    "client_name": assign.client.client_name,
                    "client_profile": assign.client.client_profile.url if assign.client.client_profile else '',
                    "start_date": assign.from_date,
                    "due_date": assign.due_date,
                    "team_lead": assign.team_lead.name,
                    "team_lead_id": assign.team_lead.id,
                    "assign_id": assign.id,
                    "task_name": task.task_name,
                    "task_id": task.id,
                    "is_category": False,
                })

    return render(request, 'dmhead/assign_to_exec.html', {
        'structured_assignments': structured_assignments,
        'user': user,
        'company': company,
        'name': employee
    })

# assign work
@csrf_exempt
def submit_work_allocation(request):
    if request.method == 'POST':
        try:
            work_id = request.POST.get('work_id')
            task_id = request.POST.get('task_id')
            team_lead_id = request.POST.get('team_lead')
            work_type = request.POST.get('work_type')
            from_date = request.POST.get('start_date')
            due_date = request.POST.get('due_date')
            target = request.POST.get('target')
            description = request.POST.get('description', '')
            file = request.FILES.get('file')
            criteria = request.POST.get('criteria', '').strip()

            is_instagram = bool(request.POST.get('is_instagram'))
            is_facebook = bool(request.POST.get('is_facebook'))
            is_x = bool(request.POST.get('is_x'))

            instagram_target = request.POST.get('instagram_target') or 0
            facebook_target = request.POST.get('facebook_target') or 0
            x_target = request.POST.get('x_target') or 0

            category_ids = request.POST.getlist('category')

            work = WorkRegister.objects.get(id=work_id)
            task = ClientTask_Register.objects.get(id=task_id)
            team_lead = EmployeeRegister_Details.objects.get(id=team_lead_id)
            company = work.company
            client = work.client
            assign_type = 1 if work_type == 'group' else 0

            # check existing lead collection logic (same work, same task, same type, same TL)
            if task.task_name.strip().lower() == "lead collection":
                existing = WorkAssign.objects.filter(
                    work_register_id=work_id,
                    client_task=task,
                    assign_type=assign_type,
                    team_lead=team_lead
                )
                if assign_type == 0 and existing.exists():
                    return JsonResponse({'success': False, 'message': 'Single Lead Collection already assigned to this TL.'})
                if assign_type == 1 and existing.exists():
                    return JsonResponse({'success': False, 'message': 'Group Lead Collection already assigned to this TL.'})

            work_assign = WorkAssign.objects.create(
                company=company,
                client=client,
                work_register=work,
                team_lead=team_lead,
                from_date=from_date,
                due_date=due_date,
                target=target,
                description=description,
                file=file,
                assign_type=assign_type,
                status=1,
                criteria=criteria,
                is_instagram=is_instagram,
                is_facebook=is_facebook,
                is_x=is_x,
                instagram_target=instagram_target,
                facebook_target=facebook_target,
                x_target=x_target
            )
            work_assign.client_task.add(task)

            work.work_allocate_status = 1
            work.save()

            if task.task_name.strip().lower() == "lead collection":
                for cid in category_ids:
                    category = LeadCategory_Register.objects.get(id=cid)
                    LeadCateogry_TeamAllocate.objects.create(
                        team_lead=team_lead,
                        lead_category=category,
                        work_assign=work_assign,
                        from_date=from_date,
                        due_date=due_date,
                        target=target,
                        description=description,
                        file=file,
                        status=1
                    )

            return JsonResponse({'success': True, 'message': 'Work assigned to TL'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

# add new categoried to existing work in TL view
@csrf_exempt
def add_lead_category_to_existing_assignment(request):
    if request.method == 'POST':
        try:
            assign_id = request.POST.get('assign_id')
            from_date = request.POST.get('start_date')
            due_date = request.POST.get('end_date')
            target = request.POST.get('target')
            description = request.POST.get('description', '')
            file = request.FILES.get('file')
            criteria = request.POST.get('criteria', '')
            is_instagram = bool(request.POST.get('is_instagram'))
            is_facebook = bool(request.POST.get('is_facebook'))
            is_x = bool(request.POST.get('is_x'))
            instagram_target = request.POST.get('instagram_target') or 0
            facebook_target = request.POST.get('facebook_target') or 0
            x_target = request.POST.get('x_target') or 0
            category_ids = request.POST.getlist('category')

            work_assign = WorkAssign.objects.get(id=assign_id)
            team_lead = work_assign.team_lead

            for cid in category_ids:
                category = LeadCategory_Register.objects.get(id=cid)
                LeadCateogry_TeamAllocate.objects.create(
                    team_lead=team_lead,
                    lead_category=category,
                    work_assign=work_assign,
                    from_date=from_date,
                    due_date=due_date,
                    target=target,
                    description=description,
                    file=file,
                    status=1
                )

            # Update WorkAssign shared fields
            work_assign.from_date = from_date
            work_assign.due_date = due_date
            work_assign.target = target
            work_assign.description = description
            work_assign.criteria = criteria
            work_assign.is_instagram = is_instagram
            work_assign.is_facebook = is_facebook
            work_assign.is_x = is_x
            work_assign.instagram_target = instagram_target
            work_assign.facebook_target = facebook_target
            work_assign.x_target = x_target
            if file:
                work_assign.file = file
            work_assign.save()

            return JsonResponse({'success': True, 'message': 'Category(ies) added successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

# delete category from work TL view
@csrf_exempt
def delete_lead_category(request, category_id):
    try:
        record = LeadCateogry_TeamAllocate.objects.get(id=category_id)
        record.delete()
        return JsonResponse({'success': True, 'message': 'Lead category assignment deleted.'})
    except LeadCateogry_TeamAllocate.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Record not found.'})

# delete assigned task to TL
@csrf_exempt
@require_POST
def delete_all_tasks_for_tl(request, work_id, tl_id):
    try:
        assigns = WorkAssign.objects.filter(work_register_id=work_id, team_lead_id=tl_id)
        count = assigns.count()
        assigns.delete()
        return JsonResponse({'success': True, 'message': f'{count} task(s) deleted for this Team Lead.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# update lead task in team lead view
@csrf_exempt
@require_POST
def update_lead_category(request):
    try:
        lead_alloc = LeadCateogry_TeamAllocate.objects.get(id=request.POST.get('edit_id'))
        work_assign = lead_alloc.work_assign

        # Shared values
        target = request.POST.get('target')
        from_date = request.POST.get('start_date')
        due_date = request.POST.get('end_date')
        description = request.POST.get('description')
        file = request.FILES.get('file')

        criteria = request.POST.get('criteria', '')
        is_instagram = bool(request.POST.get('is_instagram'))
        is_facebook = bool(request.POST.get('is_facebook'))
        is_x = bool(request.POST.get('is_x'))

        instagram_target = request.POST.get('instagram_target') or 0
        facebook_target = request.POST.get('facebook_target') or 0
        x_target = request.POST.get('x_target') or 0

        # Update LeadCateogry_TeamAllocate
        lead_alloc.target = target
        lead_alloc.from_date = from_date
        lead_alloc.due_date = due_date
        lead_alloc.description = description
        if file:
            lead_alloc.file = file
        lead_alloc.save()

        # Update WorkAssign
        work_assign.target = target
        work_assign.from_date = from_date
        work_assign.due_date = due_date
        work_assign.description = description
        work_assign.criteria = criteria
        work_assign.is_instagram = is_instagram
        work_assign.is_facebook = is_facebook
        work_assign.is_x = is_x
        work_assign.instagram_target = instagram_target
        work_assign.facebook_target = facebook_target
        work_assign.x_target = x_target
        if file:
            work_assign.file = file
        work_assign.save()

        return JsonResponse({'success': True, 'message': 'Lead category & work updated.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# delete assigned work (team lead view)
@csrf_exempt
@require_POST
def remove_task_from_assignment(request):
    try:
        import json
        data = json.loads(request.body)
        assign_id = data.get("assign_id")
        task_id = data.get("task_id")
        task_name = data.get("task_name")

        assign = WorkAssign.objects.get(id=assign_id)
        task = ClientTask_Register.objects.get(id=task_id)

        # Remove task from M2M
        assign.client_task.remove(task)

        # Delete related category assignments if "Lead Collection"
        if task_name == "lead collection":
            LeadCateogry_TeamAllocate.objects.filter(
                work_assign=assign,
                team_lead=assign.team_lead,
                lead_category__client_task=task
            ).delete()

        if assign.client_task.count() == 0:
            assign.delete()
            return JsonResponse({'success': True, 'message': 'Task and assignment fully removed.'})

        return JsonResponse({'success': True, 'message': f'Task "{task.task_name}" removed.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# save the allocations
@csrf_exempt
@csrf_exempt
def assign_to_executives(request):
    if request.method == 'POST':
        try:
            task_id = request.POST.get('task_id')
            team_assign_id = request.POST.get('team_allocation_id')
            executive_id = request.POST.get('executive')
            from_date = request.POST.get('start_date')
            due_date = request.POST.get('due_date')
            target = request.POST.get('target')
            description = request.POST.get('description', '')
            file = request.FILES.get('file')
            lead_category_id = request.POST.get('lead_category')


            if not executive_id or not team_assign_id:
                return JsonResponse({'success': False, 'message': 'Missing required fields.'})

            executive = EmployeeRegister_Details.objects.get(id=executive_id)
            team_assign = WorkAssign.objects.get(id=team_assign_id)
            task = None

            if task_id:
                task = ClientTask_Register.objects.get(id=task_id)

            elif lead_category_id:
                category = LeadCategory_Register.objects.get(id=lead_category_id)
                task = category.client_task  # infer from category

            if not task:
                return JsonResponse({'success': False, 'message': 'Unable to resolve task.'})

            # === Create TaskAssign ===
            task_assign = TaskAssign.objects.create(
                work_assign=team_assign,
                executive=executive,
                client_task=task,
                description=description,
                file=file,
                allocate_date=from_date,
                start_date=from_date,
                due_date=due_date,
                target=target,
                status=1
            )

            # === If Lead Category: Create LeadCategory_Assign too ===
            if lead_category_id:
                team_category = LeadCateogry_TeamAllocate.objects.filter(
                    work_assign=team_assign,
                    lead_category_id=lead_category_id
                ).first()

                if not team_category:
                    return JsonResponse({'success': False, 'message': 'Category assignment to TL not found.'})

                LeadCategory_Assign.objects.create(
                    executive=executive,
                    team_allocation=team_category,
                    task_assign=task_assign,
                    description=description,
                    from_date=from_date,
                    due_date=due_date,
                    target=target,
                    file=file,
                    status=1
                )

            return JsonResponse({'success': True, 'message': 'Task assigned to executive successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        
# getting task for allocation
def get_tasks_for_work(request, work_id):
    try:
        print(f'======================called {work_id}')
        tasks = ClientTask_Register.objects.filter(work_id=work_id)
        task_list = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'name': task.task_name,
                'description': task.task_description or '',
                'is_lead_collection': task.task_name.lower() == 'lead collection'
            }
            if task_data['is_lead_collection']:
                categories = LeadCategory_Register.objects.filter(client_task=task)
                task_data['categories'] = [{'id': cat.id, 'name': cat.collection_for} for cat in categories]
            task_list.append(task_data)
        return JsonResponse({'success': True, 'tasks': task_list})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# lead categoried in team leader page
def get_lead_categories_for_task(request, assign_id):
    print(f'==============================called {assign_id}')
    try:
        # Get the current assignment and work ID
        assign = WorkAssign.objects.get(id=assign_id)
        work_id = assign.work_register.id

        # Get the ClientTask with the name 'Lead Collection' for this work
        client_task = ClientTask_Register.objects.filter(
            work_id=work_id,
            task_name__iexact="lead collection"
        ).first()

        if not client_task:
            return JsonResponse({'success': False, 'categories': [], 'message': 'No Lead Collection task found for this work.'})

        # All categories for the matched task
        all_categories = LeadCategory_Register.objects.filter(client_task=client_task)

        # Categories already assigned to any TL in this work
        assigned_ids = LeadCateogry_TeamAllocate.objects.filter(
            work_assign_id=assign_id
        ).values_list('lead_category_id', flat=True)

        # Filter out already assigned categories
        available = all_categories.exclude(id__in=assigned_ids)

        data = [{'id': cat.id, 'name': cat.collection_for} for cat in available]
        return JsonResponse({'success': True, 'categories': data})

    except Exception as e:
        return JsonResponse({'success': False, 'categories': [], 'message': str(e)})

# TL name
def get_teamlead_name(request, tl_id):
    try:
        tl = EmployeeRegister_Details.objects.get(id=tl_id)
        return JsonResponse({'success': True, 'name': tl.name})
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({'success': False, 'name': 'Team Lead'})

# to get TL's executives
def get_employees_for_tl(request, tl_id):
    employees = AllocationDetails.objects.filter(team_lead_id=tl_id).select_related('employee')
    data = [
        {'id': emp.employee.id, 'name': emp.employee.name}
        for emp in employees if emp.employee.designation and emp.employee.designation.dashboard_id == 'Executive'
    ]
    return JsonResponse(data, safe=False)

def get_lead_categories_for_tl_task(request, assign_id):
    try:
        categories = LeadCateogry_TeamAllocate.objects.filter(
            work_assign_id=assign_id
        ).select_related('lead_category')

        data = [{'id': c.lead_category.id, 'name': c.lead_category.collection_for} for c in categories]
        return JsonResponse({'success': True, 'categories': data})
    except:
        return JsonResponse({'success': False, 'categories': []})

def get_lead_team_alloc_desc(request, category_id, assign_id):
    try:
        record = LeadCateogry_TeamAllocate.objects.get(
            lead_category_id=category_id,
            work_assign_id=assign_id
        )
        return JsonResponse({
            'description': record.description or '',
            'file_url': record.file.url if record.file else ''
        })
    except LeadCateogry_TeamAllocate.DoesNotExist:
        return JsonResponse({'description': '', 'file_url': ''})
    except Exception as e:
        return JsonResponse({'description': '', 'file_url': ''})

def get_workassign_desc(request, assign_id):
    try:
        assign = WorkAssign.objects.get(id=assign_id)
        return JsonResponse({
            'description': assign.description or '',
            'file_url': assign.file.url if assign.file else ''
        })
    except WorkAssign.DoesNotExist:
        return JsonResponse({'description': '', 'file_url': ''})
    except Exception as e:
        return JsonResponse({'description': '', 'file_url': ''})

@csrf_exempt
def get_full_workassign(request, assign_id):
    try:
        assign = WorkAssign.objects.get(id=assign_id)
        return JsonResponse({
            'description': assign.description or '',
            'criteria': assign.criteria or '',
            'file_url': assign.file.url if assign.file else '',
            'is_instagram': assign.is_instagram,
            'instagram_target': assign.instagram_target,
            'is_facebook': assign.is_facebook,
            'facebook_target': assign.facebook_target,
            'is_x': assign.is_x,
            'x_target': assign.x_target,
        })
    except WorkAssign.DoesNotExist:
        return JsonResponse({'error': 'WorkAssign not found'}, status=404)        
        
def dm_complaint(request):
    hid = request.session.get('hid')
    if not hid:
        messages.error(request, "You must be logged in.")
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
    except LogRegister_Details.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    if user.position != 'Digital_Marketing_Head':
        messages.error(request, "Access denied.")
        return redirect('login')

    # Common objects like in dm_work
    company = BusinessRegister_Details.objects.filter(login=user).first()
    employee_profile = EmployeeRegister_Details.objects.filter(login=user).first()

    if not employee_profile or not employee_profile.company:
        messages.error(request, "Company not linked to your profile.")
        return redirect('login')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        action_taken = request.POST.get('action_taken', '').strip()

        if not complaint_id:
            messages.error(request, "Please select a complaint.")
            return redirect('dm_complaint')

        if not action_taken:
            messages.error(request, "Action taken cannot be empty.")
            return redirect('dm_complaint')

        try:
            complaint = Complaint.objects.get(id=complaint_id, employee__company=employee_profile.company)
            complaint.action = action_taken
            complaint.action_date = timezone.now().date()
            complaint.status = 'resolved'
            complaint.save()
            messages.success(request, "Complaint resolved.")
        except Complaint.DoesNotExist:
            messages.error(request, "Complaint not found or unauthorized.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('dm_complaint')

    # Filter and order complaints: pending first
    complaints = Complaint.objects.filter(employee__company=employee_profile.company).annotate(
        status_order=Case(
            When(status='pending', then=Value(0)),
            When(status='resolved', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-complaint_date')

    context = {
        'complaints': complaints,
        'logged_in_user': user,
        'user_company': company,
        'employee_profile': employee_profile,
        'user': user,
        'company': company,
        'name': employee_profile,  # 'name' is same as employee_profile
    }

    return render(request, 'dmhead/complaints.html', context)

import logging
def leave_list(request):
    print(f"Session at the start: {request.session.items()}")  

    user_id = request.session.get('hid')  
    if not user_id:
        messages.warning(request, "You are not logged in.")
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.get(login=user)
        leaves = EmployeeLeave.objects.filter(employee=employee).order_by('-applied_date')

        user_company = BusinessRegister_Details.objects.filter(login=user).first()
        name = employee  
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "Employee profile not found")
        return redirect('login')  

    context = {
        'leaves': leaves,
        'employee_profile': employee,
        'user_company': user_company,
        'name': name,
    }

    return render(request, 'dmhead/myleave.html', context)

def apply_leave(request):
    """
    View to handle the submission of leave application form.
    Requires user session with 'hid' (email).
    """
    # Check if user is logged in
    if 'hid' not in request.session:
        return redirect('login')

  
    if request.method != 'POST':
        return redirect('myleave')

    try:
        employee_email = request.session['hid']
        employee = EmployeeRegister_Details.objects.get(email=employee_email)
    except EmployeeRegister_Details.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('myleave')

   
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    leave_type = request.POST.get('leave_type')
    reason = request.POST.get('reason')

    
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        number_of_days = (end_date_obj - start_date_obj).days + 1  # Inclusive

        if number_of_days <= 0:
            messages.error(request, "End date must be after start date.")
            return redirect('myleave')
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('myleave')

 
    request_file = request.FILES.get('request_file')

    leave = EmployeeLeave(
        employee=employee,
        start_date=start_date_obj,
        end_date=end_date_obj,
        leave_type=leave_type,
        reason=reason,
        number_of_days=number_of_days,
        status='pending',
        request_file=request_file 
    )
    leave.save()

    messages.success(request, "Leave application submitted successfully.")
    return redirect('myleave')

def filter_leaves(request):
    user_email = request.session.get('hid')
    if not user_email:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        log_user = LogRegister_Details.objects.get(log_username=user_email)
        employee = EmployeeRegister_Details.objects.get(login=log_user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'error': 'Employee not found'}, status=404)


    search_query = request.GET.get('search', '')
    from_date_str = request.GET.get('from_date', '')
    to_date_str = request.GET.get('to_date', '')

    leaves = EmployeeLeave.objects.filter(employee=employee)

    if search_query:
        leaves = leaves.filter(
            Q(reason__icontains=search_query) |
            Q(leave_type__icontains=search_query)
        )

    try:
        if from_date_str:
            from_date = parse_date('-'.join(reversed(from_date_str.split('-'))))
            leaves = leaves.filter(start_date__gte=from_date)
        if to_date_str:
            to_date = parse_date('-'.join(reversed(to_date_str.split('-'))))
            leaves = leaves.filter(end_date__lte=to_date)
    except:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    leaves_data = [{
        'id': leave.id,
        'start_date': leave.start_date.strftime('%d-%m-%Y'),
        'end_date': leave.end_date.strftime('%d-%m-%Y'),
        'leave_type': leave.leave_type,
        'reason': leave.reason,
        'status': leave.status,
        'status_changed_date': leave.status_changed_date.strftime('%d-%m-%Y') if leave.status_changed_date else None,
        'request_file_url': leave.request_file.url if leave.request_file else '',
    } for leave in leaves]

    return JsonResponse({'leaves': leaves_data})

def search_leaves(request):
    """
    View to handle AJAX requests for searching leave applications
    """
    if 'hid' not in request.session:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    try:
        employee = EmployeeRegister_Details.objects.get(email=request.session['hid'])
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({'error': 'Employee profile not found'}, status=400)

    search_query = request.GET.get('query', '').strip()
    page_number = request.GET.get('page', 1)

    if not search_query:
        leaves_queryset = EmployeeLeave.objects.filter(employee=employee).order_by('-applied_date')
    else:
        leaves_queryset = EmployeeLeave.objects.filter(
            employee=employee
        ).filter(
            Q(leave_type__icontains=search_query) |
            Q(reason__icontains=search_query) |
            Q(status__icontains=search_query)
        ).order_by('-applied_date')

    paginator = Paginator(leaves_queryset, 10)
    page = paginator.get_page(page_number)

    leaves_data = []
    for leave in page:
        leaves_data.append({
            'id': leave.id,
            'status': leave.get_status_display(),
            'start_date': leave.start_date.strftime('%B %d, %Y'),
            'end_date': leave.end_date.strftime('%B %d, %Y'),
            'leave_type': leave.leave_type,
            'reason': leave.reason,
            'status_changed_date': leave.status_changed_date.strftime('%B %d, %Y') if leave.status_changed_date else 'Data not available',
            'request_file_url': leave.request_file.url if leave.request_file else '',
        })

    return JsonResponse({
        'leaves': leaves_data,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'total_pages': paginator.num_pages
    })

def leave_req(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect("login")

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        dm_profile = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "User or employee not found.")
        return redirect("login")

    if user.position != 'Digital_Marketing_Head':
        return HttpResponseForbidden("Access denied: You are not a DM Head.")

    if not dm_profile.company:
        return HttpResponseForbidden("No company assigned to DM Head")

    company = dm_profile.company

    employees = EmployeeRegister_Details.objects.filter(company=company).exclude(id=dm_profile.id)

    leaves = EmployeeLeave.objects.filter(employee__in=employees)

    filter_status = request.GET.get('status', 'all')
    if filter_status == 'approved':
        leaves = leaves.filter(status='approved')
    elif filter_status == 'rejected':
        leaves = leaves.filter(status='rejected')
    elif filter_status == 'requested':
        leaves = leaves.filter(status='pending')
    elif filter_status == 'all':
        pass  
    else:
        leaves = leaves.filter(status='pending')

    search_query = request.GET.get('search', '')
    if search_query:
        leaves = leaves.filter(employee__name__icontains=search_query)

    leaves = leaves.annotate(
        status_order=Case(
            When(status='pending', then=Value(0)),
            When(status='approved', then=Value(1)),
            When(status='rejected', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-applied_date')

    user_company = BusinessRegister_Details.objects.filter(login=user).first()
    name = dm_profile

    context = {
        'leaves': leaves,
        'filter_status': filter_status,
        'search_query': search_query,
        'employee_profile': dm_profile,
        'user_company': user_company,
        'name': name,
    }
    return render(request, 'dmhead/request_leave.html', context)

def approve_leave(request, leave_id):  
    leave = get_object_or_404(EmployeeLeave, id=leave_id)
    leave.status = 'approved'
    leave.status_changed_date = timezone.now()
    leave.save()
    messages.success(request, "Leave request approved.")
    return redirect('leave_req')

def reject_leave(request, leave_id): 
    leave = get_object_or_404(EmployeeLeave, id=leave_id)
    leave.status = 'rejected'
    leave.status_changed_date = timezone.now()
    leave.save()
    messages.error(request, "Leave request rejected.")
    return redirect('leave_req')

def action_take(request):
    hid = request.session.get('hid')
    if not hid:
        return redirect("login")

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        dm_profile = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "User or employee not found.")
        return redirect("login")

    if user.position != 'Digital_Marketing_Head':
        return HttpResponseForbidden("Access denied: You are not a DM Head.")

    if not dm_profile.company:
        return HttpResponseForbidden("No company assigned to DM Head")

    company = dm_profile.company
    employees = EmployeeRegister_Details.objects.filter(company=company).exclude(id=dm_profile.id)
    actions = ActionTaken.objects.filter(employee__in=employees).order_by('-action_date')

   
    for action in actions:
        action.from_name = dm_profile.name  

    user_company = BusinessRegister_Details.objects.filter(login=user).first()
    name = dm_profile

    context = {
        'employees': employees,
        'actions': actions,
        'formname': dm_profile.name,
        'employee_profile': dm_profile,
        'user_company': user_company,
        'name': name,
    }

    return render(request, 'dmhead/action.html', context)

def submit_action_taken(request):
    if request.method == 'POST':
        hid = request.session.get('hid')
        if not hid:
            messages.error(request, "You must be logged in.")
            return redirect('login')

        try:
            user = LogRegister_Details.objects.get(log_username=hid)
            current_employee = EmployeeRegister_Details.objects.get(login=user)
        except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
            messages.error(request, "User not found.")
            return redirect('action_take')

        if user.position != 'Digital_Marketing_Head':
            return HttpResponseForbidden("Access denied.")

        employee_id = request.POST.get('employee')
        act_head = request.POST.get('act_head')
        act_reason = request.POST.get('act_reason')
        act_content = request.POST.get('act_content')
        action_date_str = request.POST.get('action_date')

        try:
            employee = EmployeeRegister_Details.objects.get(id=employee_id)
        except EmployeeRegister_Details.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
            return redirect('action_take')

        if employee.company != current_employee.company:
            messages.error(request, 'You cannot submit actions for employees outside your company.')
            return redirect('action_take')

        try:
            action_date = datetime.strptime(action_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid action date format.')
            return redirect('action_take')

        try:
            ActionTaken.objects.create(
                employee=employee,
                from_id=user.id,
                from_name=current_employee.name,  # Use employee's real name here
                act_head=act_head,
                act_reason=act_reason,
                act_content=act_content,
                action_date=action_date,
            )
            messages.success(request, 'Action submitted successfully.')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('action_take')

    return redirect('action_take')

def edit_action(request, action_id):
    hid = request.session.get('hid')
    if not hid:
        messages.error(request, "You must be logged in to edit actions.")
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        current_employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "User not found.")
        return redirect('login')

    action_taken = get_object_or_404(ActionTaken, id=action_id)

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        action_date = request.POST.get('date')
        reason = request.POST.get('reason')
        reason_action = request.POST.get('reason_action')
        action_taken_description = request.POST.get('action_taken')

        try:
            action_date = datetime.strptime(action_date, '%d-%m-%Y').date()
        except ValueError:
            employees = EmployeeRegister_Details.objects.filter(
                company=current_employee.company
            ).exclude(login__position='Digital_Marketing_Head')

            return render(request, 'dmhead/edit_action.html', {
                'action_taken': action_taken,
                'employees': employees,
                'current_user': current_employee,
                'employee_profile': current_employee,
                'user_company': BusinessRegister_Details.objects.filter(login=user).first(),
                'name': current_employee,
                'error_message': 'Invalid date format. Please use DD-MM-YYYY.'
            })

        
        action_taken.employee_id = employee_id
        action_taken.action_date = action_date
        action_taken.act_reason = reason
        action_taken.act_head = reason_action
        action_taken.act_content = action_taken_description
        action_taken.save()

        messages.success(request, "Action updated successfully.")
        return redirect('action_take')

    
    employees = EmployeeRegister_Details.objects.filter(
        company=current_employee.company
    ).exclude(login__position='Digital_Marketing_Head')

    context = {
        'action_taken': action_taken,
        'employees': employees,
        'current_user': current_employee,
        'employee_profile': current_employee,
        'user_company': BusinessRegister_Details.objects.filter(login=user).first(),
        'name': current_employee
    }
    return render(request, 'dmhead/edit_action.html', context)

def feedback(request):
    hid = request.session.get('hid')
    if not hid:
        messages.error(request, "You must be logged in.")
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        current_employee = EmployeeRegister_Details.objects.get(
            login=user, login__position='Digital_Marketing_Head'
        )
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "User not found or you do not have access.")
        return redirect('login')

    filter_type = request.GET.get('type', 'All')

    employees_under_dmhead = EmployeeRegister_Details.objects.filter(
        company=current_employee.company
    ).exclude(login__position='Digital_Marketing_Head')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        feedback_content = request.POST.get('feedback_content', '').strip()

        if not employee_id or not feedback_content:
            return redirect('feedback')

        try:
            receiver = EmployeeRegister_Details.objects.get(id=employee_id)
        except EmployeeRegister_Details.DoesNotExist:
            messages.error(request, "Selected employee not found.")
            return redirect('feedback')

        if receiver.company != current_employee.company:
            return redirect('feedback')

        
        Feedback.objects.create(
            employee=receiver,
            from_id=current_employee.id,
            from_name=current_employee.name,
            feedback_content=feedback_content,
            feedback_date=now(), 
        )
        return redirect('feedback')

  
    if filter_type == "Given":
        feedbacks = Feedback.objects.filter(from_id=current_employee.id).order_by('-feedback_date')
    elif filter_type == "Received":
        feedbacks = Feedback.objects.filter(employee=current_employee).order_by('-feedback_date')
    else:
        feedbacks = Feedback.objects.filter(
            models.Q(from_id=current_employee.id) | models.Q(employee=current_employee)
        ).order_by('-feedback_date')

   
    from_ids = set(fb.from_id for fb in feedbacks if fb.from_id != 0)
    senders = EmployeeRegister_Details.objects.filter(id__in=from_ids)
    sender_dict = {sender.id: sender.name for sender in senders}

   
    user_company = BusinessRegister_Details.objects.filter(login=user).first()
    name = current_employee

    context = {
        'employees': employees_under_dmhead,
        'feedbacks': feedbacks,
        'selected_type': filter_type,
        'sender_dict': sender_dict,
        'current_employee': current_employee,
        'employee_profile': current_employee,
        'user_company': user_company,
        'name': name,
    }

    return render(request, 'dmhead/feedback.html', context)
    
from django.core.mail import EmailMessage  
@csrf_exempt
def send_lead_pdf_mail(request):
    if request.method == "POST":
        try:
            email_list = request.POST.get("emails", "")
            message_body = request.POST.get("message", "")
            pdf_file = request.FILES.get("pdf")

            if not email_list or not pdf_file:
                return JsonResponse({"success": False, "message": "Missing email or PDF."})

            recipients = [email.strip() for email in email_list.split(",") if email.strip()]
            if not recipients:
                return JsonResponse({"success": False, "message": "No valid recipients."})

            email = EmailMessage(
                subject="Shared Lead Report",
                body=message_body,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients
            )
            email.attach("lead_report.pdf", pdf_file.read(), "application/pdf")
            email.send()
            return JsonResponse({"success": True, "message": "Email sent successfully."})

        except Exception as e:
            print("Email sending failed:", e)
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def upload_temp_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        unique_filename = f"{uuid.uuid4().hex}.pdf"

        folder_path = os.path.join(settings.BASE_DIR, "static", "img", "shared_reports")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, unique_filename)
        with open(file_path, "wb") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        def delete_file_later(path):
            import time
            time.sleep(30)
            try:
                os.remove(path)
            except Exception as e:
                print("Error deleting file:", e)

        threading.Thread(target=delete_file_later, args=(file_path,)).start()

        public_url = f"/static/img/shared_reports/{unique_filename}"
        return JsonResponse({"success": True, "url": public_url})

    return JsonResponse({"success": False, "message": "Invalid request"})

def leads_tracker_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    leads_qs = Leads.objects.filter(collected_by__company=company, transfer_status=1).select_related(
        'collected_by', 'lead_category__client_task__client'
    )

    lead_data = []
    for lead in leads_qs:
        obj = {
            'id': lead.id,
            'name': lead.name,
            'email': lead.email or '',
            'contact': lead.contact or '',
            'transfer_date': lead.transfer_date.strftime('%Y-%m-%d') if lead.transfer_date else '',
            'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else '',
            'assign_date': '',  # Will fill below if found
            'collected_by': lead.collected_by.name if lead.collected_by else '',
            'collected_by_id': lead.collected_by.id if lead.collected_by else '',
            'client_name': '',
            'client_id': '',
            'category_name': '',
            'category_id': '',
            'telecaller': '',
            'final_response': '',
            'allocated': 0,
            'opened': 0,
            'joined': 0,
            'recalled': 0,
            'closed': 0,
            'waste': 0,
            'lead_status': 'Not Allocated',
            'followup_status_tag': 'No Updation',
            'additional_fields': [],
        }

        if lead.lead_category and lead.lead_category.client_task:
            client = lead.lead_category.client_task.client
            obj['client_name'] = client.client_name
            obj['client_id'] = client.id
            obj['category_name'] = lead.lead_category.collection_for
            obj['category_id'] = lead.lead_category.id

        assigned = LeadAssignedToTC.objects.filter(lead=lead).first()
        if assigned:
            obj['allocated'] = 1
            obj['assign_date'] = assigned.assign_date.strftime('%Y-%m-%d') if assigned.assign_date else ''
            obj['final_response'] = assigned.response or ''
            obj['telecaller'] = assigned.telecaller.name if assigned.telecaller else ''

            if assigned.response == 'Recalled':
                obj['lead_status'] = 'Recalled'
                obj['recalled'] = 1
            elif assigned.response == 'Lead Joined':
                obj['lead_status'] = 'Joined'
                obj['joined'] = 1
            elif assigned.response == 'Lead Closed':
                obj['lead_status'] = 'Closed'
                obj['closed'] = 1
            elif assigned.response == 'Waste Lead':
                obj['lead_status'] = 'Waste'
                obj['waste'] = 1
            elif assigned.status == 1:
                obj['lead_status'] = 'Opened'
                obj['opened'] = 1
            else:
                obj['lead_status'] = 'Allocated'

        followups = FollowupDetails.objects.filter(
            lead=lead
        ).order_by('id')

        status_sequence = []

        for f in followups:
            if f.response_status:
                status_sequence.append({
                    'id': f.id,
                    'status': f.response_status
                })

        obj['followup_sequence'] = status_sequence

        extra_fields = LeadDetails.objects.filter(lead=lead)
        obj['additional_fields'] = [
            {'field': d.field_name, 'value': d.field_data} for d in extra_fields
        ]

        lead_data.append(obj)

    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.select_related('client_task__client').all()
    employees = EmployeeRegister_Details.objects.filter(
        id__in=leads_qs.values_list('collected_by_id', flat=True).distinct()
    )
    telecaller_ids = LeadAssignedToTC.objects.values_list('telecaller_id', flat=True).distinct()
    telecallers = EmployeeRegister_Details.objects.filter(id__in=telecaller_ids, company=company)
    followup_statuses = FollowupStatus.objects.all()

    context = {
        'name':employee,
        'leads_json': json.dumps(lead_data),
        'total_lead_count': len(lead_data),
        'clients': clients,
        'categories': categories,
        'employees': employees,
        'telecallers': telecallers,
        'followup_statuses': followup_statuses,
    }

    return render(request, 'dmhead/leads_tracker.html', context)

def waste_leads(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None
    company_id = company.id


    wasteleads = WasteLead.objects.filter(status=2,lead__collected_by__company=company).select_related(
        'lead', 'lead__collected_by', 'lead__lead_category', 'lead__work__client', 
    )

    leads_data = []
    for w in wasteleads:
        lead = w.lead
        obj = {
            "id": w.id,
            "lead_id": lead.id,
            "name": lead.name or "---",
            "email": lead.email or "---",
            "contact": lead.contact or "---",
            "added_date": str(lead.added_date),
            "added_time": str(lead.added_time)[:5],
            "collected_by": lead.collected_by.name if lead.collected_by else "---",
            "collected_by_id": lead.collected_by.id if lead.collected_by else '',
            "status": "Waste" if w.status == 1 else "Not Marked as Waste",
            "client_name": lead.lead_category.client_task.client.client_name if lead.lead_category.client_task and lead.lead_category.client_task.client else '',
            "client_id": lead.lead_category.client_task.client.id if lead.lead_category.client_task and lead.lead_category.client_task.client else '',
            "category_name": lead.lead_category.collection_for if lead.lead_category else '',
            "category_id": lead.lead_category.id if lead.lead_category else '',
            "assign_date": '',
            "telecaller": '',

            "verified_status": "Verified" if lead.status == 1 else "Unverified",
            "verified_class": "text-success" if lead.status == 1 else "text-danger",

            "waste_status": "Waste" if lead.waste_data == 1 else "Not Marked as Waste",
            "waste_class": "text-danger" if lead.waste_data == 1 else "text-secondary",

            "incomplete_status": "Marked as Incomplete" if lead.incomplete_status == 1 else "Not Marked as Incomplete",
            "incomplete_class": "text-warning" if lead.incomplete_status == 1 else "text-success",
        }

        extra_fields = LeadDetails.objects.filter(lead_id=lead.id)
        obj["additional_fields"] = [
            {"field": f.field_name, "value": f.field_data} for f in extra_fields
            ]
        
        followup = FollowupDetails.objects.filter(lead_id=lead.id).order_by('-id').first()
        obj["followup_details"] = {
            "date": str(followup.response_date) if followup else '',
            "response": followup.response if followup else '',
            "next_date": str(followup.next_followup_date) if followup else '',
            "status": followup.response_status if followup else '',
        }
        
        history_qs = FollowupHistory.objects.filter(lead_id=lead.id).order_by('-id')
        obj["followup_history"] = [{
            "date": str(h.allocated_date),
            "telecaller": h.telecaller.name if h.telecaller else '',
            "note": h.note,
            "status": h.final_status
        } for h in history_qs]

        assigned = LeadAssignedToTC.objects.filter(lead=lead).first()
        if assigned:
            obj["assign_date"] = str(assigned.assign_date) if assigned.assign_date else ''
            obj["telecaller"] = assigned.telecaller.name if assigned.telecaller else ''

        leads_data.append(obj)

    clients = ClientRegister.objects.filter(company_id=company_id) if company_id else ClientRegister.objects.none()
    categories = LeadCategory_Register.objects.filter(client_task__client__company_id=company_id) if company_id else LeadCategory_Register.objects.none()
    employees = EmployeeRegister_Details.objects.filter(id__in=[l['collected_by_id'] for l in leads_data if l['collected_by_id']])
    telecaller_ids = LeadAssignedToTC.objects.values_list('telecaller_id', flat=True).distinct()
    telecallers = EmployeeRegister_Details.objects.filter(id__in=telecaller_ids,company=company)

    pending_waste_count = WasteLead.objects.filter(
            lead__collected_by__company=company,
            confirmation=0
        ).count()

    return render(request, 'dmhead/waste_leads.html', {
        "name":employee,
        "leads_json": json.dumps(leads_data),
        "waste_count": len(leads_data),
        "pending_waste_count": pending_waste_count,
        "clients": clients,
        "categories": categories,
        "employees": employees,
        "telecallers": telecallers,
    })


def repeated_leads_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None

    leads_qs = Leads.objects.filter(repeated_status__in=[1, 2],collected_by__company=company).select_related(
        'collected_by', 'lead_category__client_task__client'
    )

    employees = EmployeeRegister_Details.objects.filter(
        id__in=leads_qs.values_list('collected_by_id', flat=True).distinct()
    )
    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.select_related('client_task__client')
    telecaller_ids = LeadAssignedToTC.objects.filter(
        lead__in=leads_qs
    ).values_list('telecaller_id', flat=True).distinct()
    telecallers = EmployeeRegister_Details.objects.filter(id__in=telecaller_ids)

    lead_data = []
    for lead in leads_qs:
        obj = {
            'id': lead.id,
            'name': lead.name,
            'email': lead.email or '',
            'contact': lead.contact or '',
            'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else '',
            'repeated_status': lead.repeated_status,
            'collected_by': lead.collected_by.name if lead.collected_by else '',
            'collected_by_id': lead.collected_by.id if lead.collected_by else '',
            'client_name': lead.lead_category.client_task.client.client_name if lead.lead_category and lead.lead_category.client_task else '',
            'client_id': lead.lead_category.client_task.client.id if lead.lead_category and lead.lead_category.client_task else '',
            'category_name': lead.lead_category.collection_for if lead.lead_category else '',
            'category_id': lead.lead_category.id if lead.lead_category else '',
            'telecaller': '',
            'assign_date': '',
        }

        assigned = LeadAssignedToTC.objects.filter(lead_id=lead.id).first()
        if assigned:
            obj['telecaller'] = assigned.telecaller.name if assigned.telecaller else ''
            obj['assign_date'] = assigned.assign_date.strftime('%Y-%m-%d') if assigned.assign_date else ''

        lead_data.append(obj)

    return render(request, 'dmhead/repeated_leads.html', {
        'name':employee,
        'leads_json': json.dumps(lead_data),
        'clients': clients,
        'categories': categories,
        'employees': employees,
        'telecallers': telecallers,
    })

def lead_reports_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None
    today = date.today()

    all_leads = Leads.objects.filter(collected_by__company=company)

    full_report = {
        "total": all_leads.count(),
        "transferred": all_leads.filter(transfer_status=1).count(),
        "pending": all_leads.filter(status=0).count(),
        "waste": all_leads.filter(waste_data=1).count(),
    }

    month_leads = all_leads.filter(added_date__year=today.year, added_date__month=today.month)
    month_report = {
        "total": month_leads.count(),
        "transferred": month_leads.filter(transfer_status=1).count(),
        "pending": month_leads.filter(status=0).count(),
        "waste": month_leads.filter(waste_data=1).count(),
    }

    sources = Leads.objects.filter(work__company=company).values_list('source', flat=True).distinct()
    distinct_sources = list(filter(None, sources))  # Remove null/empty values

    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.filter(client_task__client__company=company)
    executive_ids = Leads.objects.filter(collected_by__company=company).values_list('collected_by_id', flat=True).distinct()
    employees = EmployeeRegister_Details.objects.filter(id__in=executive_ids)

    leads_list = []
    for lead in all_leads:
        leads_list.append({
            "id": lead.id,
            "added_date": lead.added_date.strftime("%Y-%m-%d") if lead.added_date else "",
            "name": lead.name or "",
            "email": lead.email or "",
            "contact": lead.contact or "",
            "status": lead.status,
            "transfer_status": lead.transfer_status,
            "waste_data": lead.waste_data,
            "incomplete_status": lead.incomplete_status,
            "repeated_status": lead.repeated_status,
            "source": lead.source or "",
            "client_name": lead.lead_category.client_task.client.client_name if lead.lead_category.client_task and lead.lead_category.client_task.client else "",
            "category_name": lead.lead_category.collection_for if lead.lead_category else "",
            "collected_by": lead.collected_by.name if lead.collected_by else "",
        })

    context = {
        "name":employee,
        "clients": clients,
        "categories": categories,
        "employees": employees,
        "distinct_sources": distinct_sources,
        "leads_json": json.dumps(leads_list, cls=DjangoJSONEncoder),
        "report_summary": {
            "full": full_report,
            "month": month_report
        }
    }

    return render(request, 'dmhead/lead_reports.html', context)

def get_lead_tracking_details(request, lead_id):
    try:
        lead = Leads.objects.select_related('work__client', 'lead_category', 'collected_by').get(id=lead_id)
        extra_fields = LeadDetails.objects.filter(lead=lead)
        followup = FollowupDetails.objects.filter(lead=lead).first()
        history = FollowupHistory.objects.filter(lead=lead).order_by('-id')

        lead_data = {
            'name': lead.name,
            'email': lead.email or '---',
            'contact': lead.contact or '---',
            'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else '---',
            'collected_by': lead.collected_by.name if lead.collected_by else '---'
        }

        client = lead.work.client if lead.work and lead.work.client else None
        client_data = {
            'name': client.client_name if client else '---',
            'business': client.client_business_name if client else '---',
            'category': lead.lead_category.collection_for if lead.lead_category else '---'
        }

        extra = {f.field_name: f.field_data for f in extra_fields}
        followup_data = {
            'response': followup.response_status if followup else 'No update',
            'reason': followup.response if followup else '---',
            'next': followup.next_followup.strftime('%Y-%m-%d') if followup and followup.next_followup else '---',
        }

        history_data = [{
            'response': h.final_status,
            'reason': h.note,
            'date': h.allocated_date.strftime('%Y-%m-%d') if h.allocated_date else '---'
        } for h in history]

        return JsonResponse({
            'success': True,
            'lead': lead_data,
            'client': client_data,
            'details': extra,
            'followup': followup_data,
            'history': history_data
        })

    except Leads.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lead not found'})

@csrf_exempt
def delete_repeated_leads(request):
    if request.method == "POST":

        try:
            body = json.loads(request.body)
            ids = body.get('ids', [])

            if not ids:
                return JsonResponse({'success': False, 'message': 'No IDs provided'}, status=400)

            Leads.objects.filter(id__in=ids).delete()           
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

#! ============ new helper functions ==============
@require_POST
def dm_works_search(request):
    employee_id = request.POST.get('employee_id')

    if not employee_id:
        return JsonResponse({"success": False, "error": "missing_employee_id"}, status=400)

    try:
        employee = EmployeeRegister_Details.objects.get(id=employee_id)
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({"success": False, "error": "employee_not_found"}, status=404)

    work_ids = set()
    work_sources = {}

    def add_work(work_id, table_name, source_type, source_id):
        if not work_id:
            return
        work_ids.add(work_id)
        work_sources.setdefault(work_id, []).append({
            "table": table_name,
            "type": source_type,
            "id": source_id,
        })

    for wa in WorkAssign.objects.filter(team_lead_id=employee_id):
        add_work(wa.id, "workassign", "team_lead_direct", wa.id)

    for lcta in LeadCateogry_TeamAllocate.objects.filter(team_lead_id=employee_id):
        add_work(getattr(lcta, "work_assign_id", None),
                 "leadcategory_teamallocate",
                 "team_lead_category",
                 lcta.id)

    for ta in TaskAssign.objects.filter(executive_id=employee_id):
        add_work(getattr(ta, "work_assign_id", None),
                 "taskassign",
                 "executive_task",
                 ta.id)

    for lca in LeadCategory_Assign.objects.filter(executive_id=employee_id):
        wa_id = None
        if lca.team_allocation_id:
            wa_id = lca.team_allocation.work_assign_id
        add_work(wa_id,
                 "leadcategory_assign",
                 "executive_category",
                 lca.id)

    works_qs = (
        WorkAssign.objects
        .filter(id__in=work_ids)
        .select_related("client")
    )

    in_progress_data = []
    completed_data = []

    for work in works_qs:
        client = getattr(work, "client", None)
        client_name = getattr(client, "client_name", None) or getattr(client, "name", "") or ""

        is_completed = False

        if (work.status or 0) == 2:
            is_completed = True

        if not is_completed and TaskAssign.objects.filter(
            work_assign=work,
            executive_id=employee_id,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCategory_Assign.objects.filter(
            team_allocation__work_assign=work,
            executive_id=employee_id,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCateogry_TeamAllocate.objects.filter(
            work_assign=work,
            team_lead_id=employee_id,
            status=2
        ).exists():
            is_completed = True

        status = "completed" if is_completed else "in_progress"

        item = {
            "work_id": work.id,
            "client_name": client_name,
            "description": getattr(work, "description", "") or "",
            "status": status,
            "sources": work_sources.get(work.id, []),
        }

        if status == "completed":
            completed_data.append(item)
        else:
            in_progress_data.append(item)

    return JsonResponse({
        "success": True,
        "in_progress": in_progress_data,
        "completed": completed_data,
    })

def dm_work_details(request, work_id):
    work = get_object_or_404(
        WorkAssign.objects.select_related("client", "company", "team_lead"),
        id=work_id,
    )

    task_qs = (
        TaskAssign.objects
        .select_related("executive", "client_task")
        .filter(work_assign=work)
        .order_by("id")
    )

    client_task_ids = {t.client_task_id for t in task_qs if t.client_task_id}
    categories_map = {}
    if client_task_ids:
        for cat in LeadCategory_Register.objects.filter(client_task_id__in=client_task_ids):
            categories_map.setdefault(cat.client_task_id, []).append(cat.collection_for)

    task_rows = []
    for t in task_qs:
        client_task = t.client_task
        categories = categories_map.get(t.client_task_id, []) if t.client_task_id else []

        task_rows.append({
            "id": t.id,
            "source": "taskassign",
            "task_name": client_task.task_name if client_task else "",
            "categories": categories,
            "start_date": t.start_date,
            "due_date": t.due_date,
            "allocated_date": t.allocate_date,
            "done_by": t.executive.name if t.executive else "",
            "target": t.target,
            "achieved": t.target_achieved,
            "progress": t.progress or 0,
        })

    return render(request, "dmhead/work_task_list.html", {
        "work": work,
        "task_rows": task_rows,
    })

@require_POST
def dm_task_details(request):
    work_id = request.POST.get("work_id")
    task_assign_id = request.POST.get("task_assign_id")

    if not work_id:
        return JsonResponse({"success": False, "error": "missing_work_id"}, status=400)

    qs = TaskDetails.objects.filter(work_assign_id=work_id)

    if task_assign_id:
        qs = qs.filter(task_assign_id=task_assign_id)

    qs = qs.order_by("-collect_date")

    rows = []
    for idx, td in enumerate(qs, start=1):
        file_url = td.file.url if td.file else ""
        file_name = os.path.basename(td.file.name) if td.file else ""

        rows.append({
            "no": idx,
            "collect_date": td.collect_date.strftime("%b %d, %Y") if td.collect_date else "",
            "title": td.title or "",
            "description": td.description or "",
            "target": td.target,
            "file_url": file_url,
            "file_name": file_name,
        })

    return JsonResponse({
        "success": True,
        "rows": rows,
    })

@require_POST
def dm_works_search_multi(request):

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "invalid_json"}, status=400)

    raw_ids = body.get("employee_ids") or []
    employee_ids = []
    for v in raw_ids:
        try:
            employee_ids.append(int(v))
        except (TypeError, ValueError):
            continue

    if not employee_ids:
        return JsonResponse({"success": True, "in_progress": [], "completed": []})

    work_ids = set()
    work_sources = {}

    def add_work(work_id, table_name, source_type, source_id):
        if not work_id:
            return
        work_ids.add(work_id)
        work_sources.setdefault(work_id, []).append({
            "table": table_name,
            "type": source_type,
            "id": source_id,
        })

    for wa in WorkAssign.objects.filter(team_lead_id__in=employee_ids):
        add_work(wa.id, "workassign", "team_lead_direct", wa.id)

    for lcta in LeadCateogry_TeamAllocate.objects.filter(team_lead_id__in=employee_ids):
        add_work(getattr(lcta, "work_assign_id", None),
                 "leadcategory_teamallocate",
                 "team_lead_category",
                 lcta.id)

    for ta in TaskAssign.objects.filter(executive_id__in=employee_ids):
        add_work(getattr(ta, "work_assign_id", None),
                 "taskassign",
                 "executive_task",
                 ta.id)

    for lca in LeadCategory_Assign.objects.filter(executive_id__in=employee_ids):
        wa_id = None
        if lca.team_allocation_id:
            wa_id = lca.team_allocation.work_assign_id
        add_work(wa_id,
                 "leadcategory_assign",
                 "executive_category",
                 lca.id)

    works_qs = (
        WorkAssign.objects
        .filter(id__in=work_ids)
        .select_related("client")
    )

    in_progress_data = []
    completed_data = []

    for work in works_qs:
        client = getattr(work, "client", None)
        client_name = getattr(client, "client_name", None) or getattr(client, "name", "") or ""

        is_completed = False

        if (work.status or 0) == 2:
            is_completed = True

        if not is_completed and TaskAssign.objects.filter(
            work_assign=work,
            executive_id__in=employee_ids,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCategory_Assign.objects.filter(
            team_allocation__work_assign=work,
            executive_id__in=employee_ids,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCateogry_TeamAllocate.objects.filter(
            work_assign=work,
            team_lead_id__in=employee_ids,
            status=2
        ).exists():
            is_completed = True

        status = "completed" if is_completed else "in_progress"

        item = {
            "work_id": work.id,
            "client_name": client_name,
            "description": getattr(work, "description", "") or "",
            "status": status,
            "sources": work_sources.get(work.id, []),
        }

        if status == "completed":
            completed_data.append(item)
        else:
            in_progress_data.append(item)

    return JsonResponse({
        "success": True,
        "in_progress": in_progress_data,
        "completed": completed_data,
    })

# ======================================================== DM head ================================================================

def tl_employees_section(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        return render(request, 'teamlead/tl_employees_section.html', {
            'user': user,
            'name':name,
            'company': company
        })


def tl_employees_view(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        return render(request, 'teamlead/tl_employees_view.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation
        })

def tl_employees_leaves(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        allocated_employee = AllocationDetails.objects.filter(team_lead=name).values_list('employee', flat=True)
        leave = EmployeeLeave.objects.filter(employee__in=allocated_employee).order_by('-id')
        employee_id = request.GET.get('employee_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if employee_id:
            leave = leave.filter(employee__id=employee_id)
        if from_date:
            leave = leave.filter(start_date__gte=from_date)
        if to_date:
            leave = leave.filter(end_date__lte=to_date)
        return render(request, 'teamlead/tl_employees_leaves.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation,
            'leave':leave
        })
    
def tl_employees_schedules(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        allocated_employee = AllocationDetails.objects.filter(team_lead=name).values_list('employee', flat=True)
        schedule = EmployeeSchedule.objects.filter(employee__in=allocated_employee).order_by('-id')
        employee_id = request.GET.get('employee_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if employee_id:
            schedule = schedule.filter(employee__id=employee_id)
        if from_date:
            schedule = schedule.filter(schedule_date__gte=from_date)
        if to_date:
            schedule = schedule.filter(schedule_date__lte=to_date)
        return render(request, 'teamlead/tl_employees_schedules.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation,
            'schedule':schedule
        })
    
def tl_employees_action_taken(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        allocated_employee = AllocationDetails.objects.filter(team_lead=name).values_list('employee', flat=True)
        action = ActionTaken.objects.filter(employee__in=allocated_employee).order_by('-id')
        employee_id = request.GET.get('employee_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if employee_id:
            action = action.filter(employee__id=employee_id)
        if from_date:
            action = action.filter(action_date__gte=from_date)
        if to_date:
            action = action.filter(action_date__lte=to_date)
        return render(request, 'teamlead/tl_employees_action_taken.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation,
            'action':action
        })
    
def tl_employees_feedback(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        allocated_employee = AllocationDetails.objects.filter(team_lead=name).values_list('employee', flat=True)
        feedback = Feedback.objects.filter(employee__in=allocated_employee).order_by('-id')
        employee_id = request.GET.get('employee_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if employee_id:
            feedback = feedback.filter(employee__id=employee_id)
        if from_date:
            feedback = feedback.filter(feedback_date__gte=from_date)
        if to_date:
            feedback = feedback.filter(feedback_date__lte=to_date)
        return render(request, 'teamlead/tl_employees_feedback.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation,
            'feedback':feedback
        })
    
def tl_employees_complaints(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
        allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
        allocated_employee = AllocationDetails.objects.filter(team_lead=name).values_list('employee', flat=True)
        complaint = Complaint.objects.filter(employee__in=allocated_employee).order_by('-id')
        employee_id = request.GET.get('employee_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if employee_id:
            complaint = complaint.filter(employee__id=employee_id)
        if from_date:
            complaint = complaint.filter(complaint_date__gte=from_date)
        if to_date:
            complaint = complaint.filter(complaint_date__lte=to_date)
        return render(request, 'teamlead/tl_employees_complaints.html', {
            'user': user,
            'name':name,
            'company': company,
            'allocation':allocation,
            'complaint':complaint
        })

def teamlead_works(request):
    tid = request.session.get('tid')
    if not tid:
        return redirect('/')

    user = LogRegister_Details.objects.get(log_username=tid)
    tl = EmployeeRegister_Details.objects.filter(login=user).first()

    if not tl:
        return redirect('/')

    company = tl.company

    clients_map = {}

    wa_qs = WorkAssign.objects.filter(team_lead=tl).select_related('client')
    if company:
        wa_qs = wa_qs.filter(company=company)
    for wa in wa_qs:
        if wa.client:
            clients_map[wa.client_id] = wa.client.client_name

    ta_qs = TaskAssign.objects.filter(
        work_assign__team_lead=tl
    ).select_related('work_assign__client')
    if company:
        ta_qs = ta_qs.filter(work_assign__company=company)
    for ta in ta_qs:
        wa = ta.work_assign
        if wa and wa.client:
            clients_map[wa.client_id] = wa.client.client_name

    lcta_qs = LeadCateogry_TeamAllocate.objects.filter(
        team_lead=tl
    ).select_related('work_assign__client')
    if company:
        lcta_qs = lcta_qs.filter(work_assign__company=company)
    for lcta in lcta_qs:
        wa = lcta.work_assign
        if wa and wa.client:
            clients_map[wa.client_id] = wa.client.client_name

    lca_qs = LeadCategory_Assign.objects.filter(
        team_allocation__team_lead=tl
    ).select_related('team_allocation__work_assign__client')
    if company:
        lca_qs = lca_qs.filter(team_allocation__work_assign__company=company)
    for lca in lca_qs:
        team_alloc = lca.team_allocation
        wa = team_alloc.work_assign if team_alloc else None
        if wa and wa.client:
            clients_map[wa.client_id] = wa.client.client_name

    latc_qs = LeadAssignedToTC.objects.filter(
        telecaller=tl
    ).select_related('client')
    if company:
        latc_qs = latc_qs.filter(client__company=company)
    for la in latc_qs:
        if la.client:
            clients_map[la.client_id] = la.client.client_name

    clients = [
        {"id": cid, "name": name}
        for cid, name in sorted(clients_map.items(), key=lambda x: x[1].lower())
    ]

    context = {
        "user": user,
        "name": tl,
        "company": company,
        "clients": clients,
    }
    print("context:", context)
    return render(request, "teamlead/tl_employees_works.html", context)

#! ============ helper functions ==============

def _collect_tl_works_for_clients(tl, client_ids=None):

    if client_ids is None:
        client_ids = []

    work_map = {}
    work_ids = set()

    def ensure_work(wa, typ, title=None, category=None):
        if not wa:
            return

        work_ids.add(wa.id)

        client = wa.client
        client_name = ""
        if client:
            client_name = getattr(client, "client_name", None) or getattr(client, "name", "") or ""

        entry = work_map.setdefault(wa.id, {
            "work_id": wa.id,
            "client_name": client_name,
            "title": "",
            "type": typ, 
            "categories": set(),
            "status": "in_progress",
        })

        if title and not entry["title"]:
            entry["title"] = title

        if typ == "lead_collection":
            entry["type"] = "lead_collection"

        if category:
            entry["categories"].add(category)

    wa_qs = WorkAssign.objects.filter(team_lead=tl)
    if client_ids:
        wa_qs = wa_qs.filter(client_id__in=client_ids)

    for wa in wa_qs.select_related("client"):
        ensure_work(wa, "task", wa.description or "")

    ta_qs = TaskAssign.objects.filter(work_assign__team_lead=tl)
    if client_ids:
        ta_qs = ta_qs.filter(work_assign__client_id__in=client_ids)

    for ta in ta_qs.select_related("work_assign__client"):
        wa = ta.work_assign
        task_title = ta.description or "Task"
        ensure_work(wa, "task", task_title)

    lcta_qs = LeadCateogry_TeamAllocate.objects.filter(team_lead=tl)
    if client_ids:
        lcta_qs = lcta_qs.filter(work_assign__client_id__in=client_ids)

    for lcta in lcta_qs.select_related("work_assign__client", "lead_category"):
        wa = lcta.work_assign
        ensure_work(wa, "lead_collection", "Lead Collection")

    lca_qs = LeadCategory_Assign.objects.filter(team_allocation__team_lead=tl)
    if client_ids:
        lca_qs = lca_qs.filter(
            team_allocation__work_assign__client_id__in=client_ids
        )

    for lca in lca_qs.select_related(
        "team_allocation__work_assign__client",
        "team_allocation__lead_category"
    ):
        team_alloc = lca.team_allocation
        wa = team_alloc.work_assign if team_alloc else None

        category_label = None
        if team_alloc and team_alloc.lead_category:
            category_label = (
                team_alloc.lead_category.collection_for
                or str(team_alloc.lead_category)
            )

        ensure_work(wa, "lead_collection", "Lead Collection", category_label)

    if not work_ids:
        return [], []

    wa_all = WorkAssign.objects.filter(id__in=work_ids).select_related("client")

    for wa in wa_all:
        is_completed = False

        if (wa.status or 0) == 2:
            is_completed = True

        if not is_completed and TaskAssign.objects.filter(
            work_assign=wa,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCategory_Assign.objects.filter(
            team_allocation__work_assign=wa,
            status=1
        ).exists():
            is_completed = True

        if not is_completed and LeadCateogry_TeamAllocate.objects.filter(
            work_assign=wa,
            team_lead=tl,
            status=2
        ).exists():
            is_completed = True

        entry = work_map.get(wa.id)
        if not entry:
            continue

        entry["status"] = "completed" if is_completed else "in_progress"

    in_progress = []
    completed = []

    for work_id, entry in work_map.items():
        entry["categories"] = list(entry["categories"])
        if entry["status"] == "completed":
            completed.append(entry)
        else:
            in_progress.append(entry)

    return in_progress, completed

@require_GET
@csrf_exempt
def tl_works_search(request):
    tl_id = request.GET.get("tl_id")
    client_id = request.GET.get("client_id")

    if not tl_id:
        return JsonResponse({"success": False, "error": "missing_tl_id"}, status=400)

    try:
        tl = EmployeeRegister_Details.objects.get(id=tl_id)
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({"success": False, "error": "tl_not_found"}, status=404)

    client_ids = []

    if client_id:
        try:
            client_ids = [int(client_id)]
        except ValueError:
            return JsonResponse({"success": False, "error": "invalid_client_id"}, status=400)

    if not client_ids:
        return JsonResponse({
            "success": True,
            "in_progress": [],
            "completed": [],
        })

    in_progress, completed = _collect_tl_works_for_clients(tl, client_ids)

    return JsonResponse({
        "success": True,
        "in_progress": in_progress,
        "completed": completed,
    })

@require_POST
@csrf_exempt
def tl_works_search_multi(request):

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "invalid_json"}, status=400)

    tl_id = payload.get("tl_id")
    raw_client_ids = payload.get("client_ids") or []

    if not tl_id:
        return JsonResponse({"success": False, "error": "missing_tl_id"}, status=400)

    try:
        tl = EmployeeRegister_Details.objects.get(id=tl_id)
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({"success": False, "error": "tl_not_found"}, status=404)

    client_ids = []
    for v in raw_client_ids:
        try:
            client_ids.append(int(v))
        except (TypeError, ValueError):
            continue

    if not client_ids:
        return JsonResponse({
            "success": True,
            "in_progress": [],
            "completed": [],
        })

    in_progress, completed = _collect_tl_works_for_clients(tl, client_ids)

    return JsonResponse({
        "success": True,
        "in_progress": in_progress,
        "completed": completed,
    })
    
##admin_employee##

def admin_employee(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    return render(request,'admin/admin_employee.html',{
         'user': user,
        'company': company,
        'name': name,
    })

def view_emp(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    employees = EmployeeRegister_Details.objects.select_related(
        'login', 'company', 'department', 'designation'
    ).filter(company=company)

    if request.method == 'POST':
        search_query = request.POST.get('search', '').strip()
        if search_query:
            employees = employees.filter(name__icontains=search_query)
            return render(request, 'admin/view_emp.html', {
                'user': user,
                'company': company,
                'name': name,
                'employees': employees,
            })
        return redirect('view_emp')  
    context = {
        'user': user,
        'company': company,
        'name': name,
        'employees': employees,
    }
    return render(request, 'admin/view_emp.html', context)

def inactivate_employee(request, emp_id):
    employee = get_object_or_404(EmployeeRegister_Details, id=emp_id)
    if request.method == 'POST':
        employee.address_line1 = request.POST.get('address1', employee.address_line1)
        employee.address_line2 = request.POST.get('address2', employee.address_line2)
        employee.address_line3 = request.POST.get('address3', employee.address_line3)
        employee.pin = request.POST.get('pincode', employee.pin)
        employee.location = request.POST.get('location', employee.location)
        employee.district = request.POST.get('district', employee.district)
        employee.state = request.POST.get('state', employee.state)
        if employee.active_status == 'Active':
            employee.active_status = 'Inactive'
        employee.save()
        messages.success(request, f"{employee.name} has been deactivated and updated.")
        return redirect('view_emp')
    return redirect('view_emp')

def verify_employee(request, emp_id):
    employee = get_object_or_404(EmployeeRegister_Details, id=emp_id)
    if request.method == 'POST':
        employee.address_line1 = request.POST.get('address1', employee.address_line1)
        employee.address_line2 = request.POST.get('address2', employee.address_line2)
        employee.address_line3 = request.POST.get('address3', employee.address_line3)
        employee.pin = request.POST.get('pincode', employee.pin)
        employee.location = request.POST.get('location', employee.location)
        employee.district = request.POST.get('district', employee.district)
        employee.state = request.POST.get('state', employee.state)
        employee.verification_status = True
        employee.save()
        messages.success(request, f"{employee.name} has been verified and details updated.")
    return redirect('view_emp')

def allocation_view(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()

    # Team leads who have allocated employees, annotate count
    team_leads = EmployeeRegister_Details.objects.filter(
        allocated_employees__isnull=False ,company=company
    ).annotate(
        member_count=Count('allocated_employees')
    ).distinct()

    selected_team_lead_id = request.GET.get('team_lead')
    selected_team_lead = None
    allocated_employees = []

    if selected_team_lead_id:
        selected_team_lead = get_object_or_404(EmployeeRegister_Details, id=selected_team_lead_id)

        allocated_employees = AllocationDetails.objects.filter(
            team_lead=selected_team_lead
        ).select_related('employee', 'employee__department', 'employee__designation')

    context = {
        'user':user,
        'company':company,

        'team_leads': team_leads,
        'selected_team_lead': selected_team_lead,
        'allocated_employees': allocated_employees,
    }
    return render(request, 'admin/allocation_list.html', context)

def employee_leaves(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    employees = EmployeeRegister_Details.objects.select_related(
        'login', 'company', 'department', 'designation'
    ).filter(company=company)

    emp_id = request.GET.get('employee')
    from_str = request.GET.get('from', '')
    to_str = request.GET.get('to', '')

    from_date = None
    to_date = None

    try:
        if from_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        if to_str:
            to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    leaves = []
    employee = None

    if emp_id:
        employee = get_object_or_404(EmployeeRegister_Details, id=emp_id, company=company)
        leaves = EmployeeLeave.objects.filter(employee=employee)
        if from_date:
            leaves = leaves.filter(start_date__gte=from_date)
        if to_date:
            leaves = leaves.filter(end_date__lte=to_date)

    context = {
        'employees': employees,
        'employee': employee,
        'leaves': leaves,
        'from_date': from_date,
        'to_date': to_date,
        'company': company,
        'name': name,
    }
    return render(request, 'admin/leave_list.html', context)

def employee_schedules(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    employees = EmployeeRegister_Details.objects.select_related(
        'login', 'company', 'department', 'designation'
    ).filter(company=company)

    emp_id = request.GET.get('employee')
    from_str = request.GET.get('from', '')
    to_str = request.GET.get('to', '')

    from_date = to_date = None
    try:
        if from_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        if to_str:
            to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    schedules = []
    employee = None

    if emp_id:
        employee = get_object_or_404(EmployeeRegister_Details, id=emp_id, company=company)
        schedules = EmployeeSchedule.objects.filter(employee=employee)
        if from_date:
            schedules = schedules.filter(schedule_date__gte=from_date)
        if to_date:
            schedules = schedules.filter(schedule_date__lte=to_date)

    context = {
        'employees': employees,
        'employee': employee,
        'schedules': schedules,
        'from_date': from_date,
        'to_date': to_date,
        'company': company,
        'name': name,
    }
    return render(request, 'admin/schedule_list.html', context)

def employee_feedbacks(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    employees = EmployeeRegister_Details.objects.select_related(
        'login', 'company', 'department', 'designation'
    ).filter(company=company)

    emp_id = request.GET.get('employee')
    from_str = request.GET.get('from', '')
    to_str = request.GET.get('to', '')

    from_date = None
    to_date = None

    try:
        if from_str:
            from_date = datetime.strptime(from_str, '%Y-%m-%d').date()
        if to_str:
            to_date = datetime.strptime(to_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    feedbacks = []
    employee = None

    if emp_id:
        employee = get_object_or_404(EmployeeRegister_Details, id=emp_id, company=company)
        feedbacks = Feedback.objects.filter(employee=employee)
        if from_date:
            feedbacks = feedbacks.filter(feedback_date__gte=from_date)
        if to_date:
            feedbacks = feedbacks.filter(feedback_date__lte=to_date)

    context = {
        'employees': employees,
        'employee': employee,
        'feedbacks': feedbacks,
        'from_date': from_date,
        'to_date': to_date,
        'company': company,
        'name': name,
    }

    return render(request, 'admin/feedback.html', context)

def complaints(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()

    employees = EmployeeRegister_Details.objects.filter(company=company)
    complaints = Complaint.objects.all()

    selected_employee_id = request.GET.get('employee')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if selected_employee_id:
        complaints = complaints.filter(employee_id=selected_employee_id)

    if from_date:
        complaints = complaints.filter(complaint_date__gte=from_date)
    if to_date:
        complaints = complaints.filter(complaint_date__lte=to_date)

    employee = EmployeeRegister_Details.objects.filter(id=selected_employee_id).first() if selected_employee_id else None

    context = {
        'user':user,
        'company':company,
        'employees': employees,
        'complaints': complaints,
        'selected_employee_id': selected_employee_id,
        'employee': employee,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'admin/complaints.html', context)

def action_taken(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()

    employees = EmployeeRegister_Details.objects.filter(company=company)

    actions = ActionTaken.objects.all()

    selected_employee_id = request.GET.get('employee')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if selected_employee_id:
        actions = actions.filter(employee_id=selected_employee_id)

    if from_date:
        actions = actions.filter(action_date__gte=from_date)
    if to_date:
        actions = actions.filter(action_date__lte=to_date)

    employee = EmployeeRegister_Details.objects.filter(id=selected_employee_id).first() if selected_employee_id else None

    context = {
        'user':user,
        'company':company,
        'employees': employees,
        'actions': actions,
        'employee': employee,
        'selected_employee_id': selected_employee_id,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'admin/action_taken.html', context)

#--------------------------------------------DMHEAD-----------------------------    
def dmh_schedule(request):
    session_login_id = request.session.get("hid")  
    schedules = []
    schedules_json = "[]"
    name = None 

    if session_login_id:
        try:
            user = LogRegister_Details.objects.get(log_username=session_login_id)
            employee = EmployeeRegister_Details.objects.get(login=user)
            name = employee  
            employee_id = employee.id

            # print("Matched Employee ID for schedule:", employee_id, name)

            current_date = localdate()  

            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            if start_date and end_date:
                schedules = EmployeeSchedule.objects.filter(
                    employee_id=employee_id, 
                    schedule_date__range=[start_date, end_date]
                )
            else:
                schedules = EmployeeSchedule.objects.filter(
                    employee_id=employee_id, 
                    schedule_date=current_date
                )

            print("Today's Schedules:", schedules)  

            all_schedules = EmployeeSchedule.objects.filter(employee_id=employee_id)

            schedules_json = json.dumps([
                {
                    "id": schedule.id,
                    "schedule_date": str(schedule.schedule_date),
                    "start_time": schedule.start_time.strftime('%I:%M %p'),
                    "end_time": schedule.end_time.strftime('%I:%M %p'),
                    "schedule_head": schedule.schedule_head,
                    "todo_content": schedule.todo_content,
                    "schedule_status": schedule.schedule_status,
                } for schedule in all_schedules  
            ])

        except EmployeeRegister_Details.DoesNotExist:
            print("Employee record not found for LogRegister_Details ID:", session_login_id)


    return render(request, 'dmhead/dmh_schedule.html', {
        "schedules": schedules,  
        "schedules_json": schedules_json,  
        "start_date": request.GET.get("start_date"),
        "end_date": request.GET.get("end_date"),
        'name':name
    })

def dmh_add_my_schedule(request):
    if request.method == 'POST':
        session_login_id = request.session.get("hid")  
        print("Session Login ID:", session_login_id)  

        if not session_login_id:
            messages.error(request, "Your session has expired. Please log in again.")
            return redirect("dmh_schedule")

        try:
            employee = EmployeeRegister_Details.objects.get(login__log_username=session_login_id)
            print("Employee ID:", employee.id)  
        except EmployeeRegister_Details.DoesNotExist:
            messages.error(request, "Employee record not found. Please contact admin.")
            return redirect('dmh_schedule')

        date = request.POST.get('date')
        start_time_str = request.POST.get('startTime')
        end_time_str = request.POST.get('endTime')
        schedule_head = request.POST.get('shedule')  
        description = request.POST.get('description')

        if not all([date, start_time_str, end_time_str, schedule_head, description]):
            messages.error(request, "All fields are required.")
            return redirect('dmh_schedule')

        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('dmh_schedule')

        schedule_entry = EmployeeSchedule.objects.create(
            schedule_head=schedule_head,
            todo_content=description,
            schedule_date=date,
            start_time=start_time,
            end_time=end_time,
            employee_id=employee.id 
        )

        messages.success(request, "Schedule added successfully.")
        return redirect('dmh_schedule')

    return render(request, 'dmhead/dmh_schedule.html', {
        "login_id": request.session.get("hid")  
    })

def dmh_update_schedule_status(request):
    if request.method == "POST":
        data = json.loads(request.body)  
        schedule_id = data.get("schedule_id")
        is_checked = data.get("is_checked")  

        try:
            schedule = EmployeeSchedule.objects.get(id=schedule_id)
            
            # Set status to 'completed' or 'pending' based on the checkbox value
            schedule.schedule_status = 'completed' if is_checked else 'pending'
            schedule.save()

            return JsonResponse({"success": True, "schedule_status": schedule.schedule_status})
        except EmployeeSchedule.DoesNotExist:
            return JsonResponse({"success": False, "error": "Schedule not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

def dmh_edit_schedule_fun(request,schedule_id):
    if request.method ==  'POST':
        schedule = EmployeeSchedule.objects.get(id=schedule_id)
        schedule.schedule_date = request.POST.get('date')
        schedule.start_time = request.POST.get('startTime')
        schedule.end_time = request.POST.get('endTime')
        schedule.schedule_head = request.POST.get('shedule')
        schedule.todo_content = request.POST.get('description')
        schedule.save()
        messages.success(request,'Schedule edited Successfully')
        return redirect('dmh_schedule')
    return render(request,'dmhead/dmh_schedule.html',{'schedule':schedule})

def get_schedule_details(request, schedule_id):
    schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
    data = {
        "id": schedule.id,
        "schedule_date": str(schedule.schedule_date),
        "start_time": schedule.start_time.strftime('%H:%M'),
        "end_time": schedule.end_time.strftime('%H:%M'),
        "schedule_head": schedule.schedule_head,
        "todo_content": schedule.todo_content,
        "schedule_status": schedule.schedule_status,
    }
    return JsonResponse(data)
    
def dmh_edit_schedule(request,schedule_id):
    if request.method ==  'POST':
        schedule = EmployeeSchedule.objects.get(id=schedule_id)
        schedule.schedule_date = request.POST.get('date')
        schedule.start_time = request.POST.get('startTime')
        schedule.end_time = request.POST.get('endTime')
        schedule.schedule_head = request.POST.get('shedule')
        schedule.todo_content = request.POST.get('description')
        schedule.save()
        messages.success(request,'Schedule edited Successfully')
        return redirect('dmh_schedule')
    return render(request,'dmhead/dmh_schedule.html')

def dmh_delete_schedule(request, schedule_id):
    schedule1 = EmployeeSchedule.objects.get(id=schedule_id)
    schedule1.delete()
    messages.success(request,'Schedule deleted successfully')
    return redirect('dmh_schedule')

def dmh_schedule_search(request):
    search_query = request.GET.get('search', '').strip()
    log_username = request.session.get('hid')  

    employee_id = None
    if log_username:
        try:
            logged_in_employee = EmployeeRegister_Details.objects.get(login__log_username=log_username)
            employee_id = logged_in_employee.id
        except EmployeeRegister_Details.DoesNotExist:
            pass

    schedules = EmployeeSchedule.objects.all()

    # Default to text search
    date_filter_applied = False

    # Match date patterns
    date_pattern_dd = re.match(r'^(\d{1,2})$', search_query)  # Only day
    date_pattern_ddmm = re.match(r'^(\d{1,2})-(\d{1,2})$', search_query)  # Day-Month
    date_pattern_ddmmyyyy = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', search_query)  # Full date

    if date_pattern_ddmmyyyy:
        day, month, year = map(int, date_pattern_ddmmyyyy.groups())
        schedules = schedules.filter(schedule_date__day=day, schedule_date__month=month, schedule_date__year=year)
        date_filter_applied = True
    elif date_pattern_ddmm:
        day, month = map(int, date_pattern_ddmm.groups())
        schedules = schedules.filter(schedule_date__day=day, schedule_date__month=month)
        date_filter_applied = True
    elif date_pattern_dd:
        day = int(date_pattern_dd.group(1))
        schedules = schedules.filter(schedule_date__day=day)
        date_filter_applied = True

    if not date_filter_applied and search_query:
        # Fallback to text-based search
        schedules = schedules.filter(
            Q(schedule_head__icontains=search_query) |
            Q(todo_content__icontains=search_query) |
            Q(start_time__icontains=search_query) |
            Q(end_time__icontains=search_query)
        )

    if employee_id:
        schedules = schedules.filter(employee_id=employee_id)
    else:
        schedules = schedules.filter(schedule_date=datetime.today().date())

    schedules = schedules.order_by('-schedule_date')

    schedule_data = [
        {
            'id': schedule.id,
            'schedule_date': schedule.schedule_date,
            'start_time': str(schedule.start_time),
            'end_time': str(schedule.end_time),
            'schedule_head': schedule.schedule_head,
            'todo_content': schedule.todo_content,
            'schedule_status': schedule.schedule_status,
            'employee_name': schedule.employee.name
        }
        for schedule in schedules
    ]

    return JsonResponse(schedule_data, safe=False)

def dmh_employee_schedule(request):
    session_login_id = request.session.get('hid')
    employees = []
    schedules = []
    name = None
    current_date = localdate()

    if session_login_id:
        try:
            login_user = LogRegister_Details.objects.get(log_username=session_login_id)
            current_employee = EmployeeRegister_Details.objects.get(login=login_user)
            name = current_employee

            # Get employees from same department excluding current
            employees = EmployeeRegister_Details.objects.filter(
                login__is_staff=True,
                department=current_employee.department
            ).exclude(login=login_user)

            # Base queryset
            schedule_queryset = EmployeeSchedule.objects.filter(
                employee__department=current_employee.department
            ).exclude(employee=current_employee)

            # Apply filters
            selected_employee_id = request.GET.get("employee_id")
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            if selected_employee_id:
                schedule_queryset = schedule_queryset.filter(employee__id=selected_employee_id)
            if start_date and end_date:
                schedule_queryset = schedule_queryset.filter(schedule_date__range=[start_date, end_date])
            elif not selected_employee_id and not start_date and not end_date:
                # Default: show today's schedule only
                schedule_queryset = schedule_queryset.filter(schedule_date=current_date)

            # Final order
            schedules = schedule_queryset.order_by('-schedule_date', 'start_time')

        except LogRegister_Details.DoesNotExist:
            print("Logged-in user not found.")
        except EmployeeRegister_Details.DoesNotExist:
            print("Employee profile not found for logged-in user.")

    context = {
        'employees': employees,
        'schedules': schedules,
        'name': name,
        'selected_employee_id': request.GET.get('employee_id', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
    }

    return render(request, 'dmhead/dmh_employee_schedule.html', context)

def dmh_add_employee_schedule(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee')  

        if not employee_id:
            messages.error(request, "Please select an employee.")
            return redirect('dmh_employee_schedule')

        try:
            employee = EmployeeRegister_Details.objects.get(id=employee_id)  
        except EmployeeRegister_Details.DoesNotExist:
            messages.error(request, "Employee not found.")
            return redirect('dmh_employee_schedule')

        # Get other form data
        date = request.POST.get('date')
        startTime = request.POST.get('start_time')
        endTime = request.POST.get('end_time')
        schedule = request.POST.get('schedule_head')
        description = request.POST.get('todo_content')

        # Validate required fields
        if not all([date, startTime, endTime, schedule, description]):
            messages.error(request, "All fields are required.")
            return redirect('dmh_employee_schedule')

        # Create schedule entry
        schedule_entry = EmployeeSchedule(
            schedule_head=schedule,
            todo_content=description,
            schedule_date=date,
            start_time=startTime,
            end_time=endTime,
            employee_id=employee.id  
        )

        schedule_entry.save()
        messages.success(request, "Schedule added successfully.")
        return redirect('dmh_employee_schedule')

    return render(request, 'dmhead/dmh_employee_schedule.html')

def get_employee_schedule_details(request, schedule_id):
    try:
        schedule = EmployeeSchedule.objects.select_related('employee').get(id=schedule_id)
        return JsonResponse({
            "id": schedule.id,  
            "schedule_date": str(schedule.schedule_date),
            "start_time": str(schedule.start_time),
            "end_time": str(schedule.end_time),
            "schedule_head": schedule.schedule_head,
            "todo_content": schedule.todo_content,
            "employee": {
                "id": schedule.employee.id,
                "name": schedule.employee.name,
            }
        })
    except EmployeeSchedule.DoesNotExist:
        raise Http404("Schedule not found")

def dmh_edit_employee_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = EmployeeSchedule.objects.get(id=schedule_id)
        
        # Update fields
        employee_id = request.POST.get('employee')
        schedule.employee_id = employee_id
        schedule.schedule_date = request.POST.get('date')
        schedule.start_time = request.POST.get('start_time')
        schedule.end_time = request.POST.get('end_time')
        schedule.schedule_head = request.POST.get('schedule_head')
        schedule.todo_content = request.POST.get('todo_content')
        schedule.save()

        messages.success(request, 'Schedule edited successfully')
        return redirect('dmh_employee_schedule')

    return render(request, 'dmhead/dmh_employee_schedule.html')

def dmh_delete_employee_schedule(request,schedule_id):
    schedule1 = EmployeeSchedule.objects.get(id=schedule_id)
    schedule1.delete()
    messages.success(request,'Schedule deleted successfully')
    return redirect('dmh_employee_schedule')

def dmh_employee_schedule_search(request):
    search_query = request.GET.get('search', '').strip()
    log_username = request.session.get('hid') 
    exclude_employee_id = None

    # Default queryset
    schedules = EmployeeSchedule.objects.none()

    if log_username:
        try:
            logged_in_employee = EmployeeRegister_Details.objects.get(login__log_username=log_username)
            exclude_employee_id = logged_in_employee.id

            # Filter only schedules from same department and same company
            schedules = EmployeeSchedule.objects.filter(
                employee__department=logged_in_employee.department,
                employee__company_id=logged_in_employee.company_id
            )
        except EmployeeRegister_Details.DoesNotExist:
            logged_in_employee = None

    # Check if the search query is a valid date
    try:
        search_date = datetime.strptime(search_query, '%d-%m-%Y').date()
        schedules = schedules.filter(schedule_date=search_date)
    except ValueError:
        if search_query:
            schedules = schedules.filter(
                Q(schedule_date__icontains=search_query) |
                Q(schedule_head__icontains=search_query) |
                Q(todo_content__icontains=search_query) |
                Q(start_time__icontains=search_query) |
                Q(end_time__icontains=search_query) |
                Q(employee__name__icontains=search_query)
            )
        else:
            today = date.today()
            schedules = schedules.filter(schedule_date=today)

    # Exclude current user's schedule
    if exclude_employee_id:
        schedules = schedules.exclude(employee_id=exclude_employee_id)

    schedules = schedules.order_by('-schedule_date')

    data = [{
        'id': schedule.id,
        'employee_name': schedule.employee.name,
        'schedule_date': schedule.schedule_date,
        'start_time': schedule.start_time,
        'end_time': schedule.end_time,
        'schedule_head': schedule.schedule_head,
        'todo_content': schedule.todo_content,
        'schedule_status': schedule.schedule_status,
    } for schedule in schedules]

    return JsonResponse(data, safe=False)

def dmh_employee_schedule_filter_list(request):
    session_login_id = request.session.get('hid')
    employees = []
    schedules = []
    name = None
    selected_employee_name = ''
    current_date = localdate()

    if session_login_id:
        try:
            login_user = LogRegister_Details.objects.get(log_username=session_login_id)
            current_employee = EmployeeRegister_Details.objects.get(login=login_user)
            name = current_employee

            employees = EmployeeRegister_Details.objects.filter(
                login__is_staff=True,
                department=current_employee.department
            ).exclude(login=login_user)

            # Get filter parameters
            selected_employee_id = request.GET.get("employee_id")
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            # Base queryset
            schedule_queryset = EmployeeSchedule.objects.exclude(employee=current_employee)

            if selected_employee_id:
                schedule_queryset = schedule_queryset.filter(employee__id=selected_employee_id)
                try:
                    selected_employee = EmployeeRegister_Details.objects.get(id=selected_employee_id)
                    selected_employee_name = selected_employee.name
                except EmployeeRegister_Details.DoesNotExist:
                    selected_employee_name = ''

            if start_date and end_date:
                schedule_queryset = schedule_queryset.filter(schedule_date__range=[start_date, end_date])
            elif not selected_employee_id and not start_date and not end_date:
                # Show todayâ€™s schedule only
                schedule_queryset = schedule_queryset.filter(schedule_date=current_date)

            schedules = schedule_queryset.order_by('-schedule_date', 'start_time')

        except LogRegister_Details.DoesNotExist:
            print("Logged-in user not found.")
        except EmployeeRegister_Details.DoesNotExist:
            print("Employee profile not found for logged-in user.")

    context = {
        'employees': employees,
        'schedules': schedules,
        'name': name,
        'selected_employee_id': request.GET.get('employee_id', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'selected_employee_name': selected_employee_name,
    }
    return render(request, 'dmhead/employee_schedule_filter_list.html', context)

def dmhead_leads_page(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    all_allocs = LeadCateogry_TeamAllocate.objects.select_related(
        'lead_category', 'work_assign__client'
    ).filter(team_lead__company=company).order_by('work_assign__client__client_name', '-from_date')

    grouped = defaultdict(list)
    for alloc in all_allocs:
        client = alloc.work_assign.client
        grouped[client.id].append({
            'start_date': alloc.from_date,
            'end_date': alloc.due_date,
            'category_name': alloc.lead_category.collection_for,
            'lead_category_id': alloc.lead_category.id,
            'fields': LeadField_Register.objects.filter(lead_category_id=alloc.lead_category.id),
            'team_alloc_id': alloc.id
        })

    structured = []
    for idx, (client_id, records) in enumerate(grouped.items(), start=1):
        client_name = ClientRegister.objects.get(id=client_id).client_name
        structured.append({
            'no': idx,
            'client_id': client_id,
            'client_name': client_name,
            'records': records
        })

    return render(request, 'dmhead/leads.html', {
        'name':name,
        'user':user,
        'company':company, 
        'grouped_clients': structured
    })

def verify_leads_page(request, team_alloc_id, lead_category_id):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    required_fields = LeadField_Register.objects.filter(lead_category_id=lead_category_id)
    field_names = list(required_fields.values_list('name', flat=True))

    allocation = LeadCateogry_TeamAllocate.objects.select_related('work_assign__client').filter(id=team_alloc_id).first()
    client_name = allocation.work_assign.client.client_name if allocation and allocation.work_assign and allocation.work_assign.client else "Unknown Client"

    leads_qs = Leads.objects.filter(
        lead_category_id=lead_category_id
    ).select_related('collected_by')

    employees = EmployeeRegister_Details.objects.filter(
        id__in=leads_qs.values_list('collected_by_id', flat=True),
        designation__dashboard_id__in=['Executive', 'Team_Lead' ,'Digital_Marketing_Head']
    ).order_by('name')

    enriched_leads = []
    for lead in leads_qs:

        from_date = None
        due_date = None
        alloc = LeadCateogry_TeamAllocate.objects.filter(lead_category_id=lead.lead_category_id).first()
        if alloc:
            from_date = alloc.from_date
            due_date = alloc.due_date

        dynamic = LeadDetails.objects.filter(lead=lead)
        field_data = {d.field_name: d.field_data for d in dynamic}
        enriched_leads.append((lead, field_data, from_date, due_date))


    today = timezone.now().date()
    today_leads = Leads.objects.filter(added_date=today)
    
    day_report = {
        'total': today_leads.count(),
        'unverified': today_leads.filter(status=0).count(),
        'repeated': today_leads.filter(repeated_status=1).count(),
        'waste': today_leads.filter(waste_data=1).count(),
        'clean_unverified': today_leads.filter(status=0, repeated_status=0, waste_data=0).count(),
        'verified': today_leads.filter(status=1).count(),
        'transferred': today_leads.filter(transfer_status=1).count(),
        'pending_transfer': today_leads.filter(status=1, transfer_status=0).count(),
    }

    return render(request, 'dmhead/verify_leads.html', {
        'user':user,
        'name':name,
        'team_alloc_id': team_alloc_id,
        'lead_category_id': lead_category_id,
        'required_fields': field_names,
        'leads': enriched_leads,
        'employees': employees,
        'day_report': day_report,
        'client_name': client_name,
    })

def head_lead_transfer_page(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None


    leads = Leads.objects.filter(status=1, transfer_status=0, collected_by__company=company).select_related('collected_by', 'lead_category', 'work__client')
    employees = EmployeeRegister_Details.objects.filter(id__in=leads.values_list('collected_by_id', flat=True))
    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.all()

    success_message = request.session.pop('transfer_success', None)
    if success_message:
        messages.success(request, success_message)

    return render(request, 'dmhead/transfer_leads.html', {
        'user':user,
        'name':name,
        'leads': leads,
        'employees': employees,
        'clients': clients,
        'categories': categories,
    })

def transferred_leads_page(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    leads = Leads.objects.filter(transfer_status=1,collected_by__company=company).select_related('collected_by', 'lead_category', 'work__client')
    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.all()
    employees = EmployeeRegister_Details.objects.filter(id__in=leads.values_list('collected_by_id', flat=True))

    return render(request, 'dmhead/transferred_leads.html', {
        'user':user,
        'name':name,
        'leads': leads,
        'clients': clients,
        'categories': categories,
        'employees': employees
    })

# * helper modules

def upload_leads_excel_dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        employee_user=EmployeeRegister_Details.objects.filter(login=user).first()
        company = employee_user.company if employee_user else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    if request.method != 'POST':
        messages.error(request, "Invalid request.")
        return redirect('individual_work_main')

    
    team_alloc_id = request.POST.get('team_alloc_id')

    result = process_excel_upload(request, team_alloc_id, employee_user)

    if 'error' in result:
        messages.error(request, result['error'])
    else:
        if result['skipped']:
            messages.warning(request, f"{len(result['skipped'])} row(s) skipped.")
            for msg in result['skipped'][:5]:
                messages.warning(request, msg)
            if len(result['skipped']) > 5:
                messages.warning(request, f"...and {len(result['skipped']) - 5} more.")

        if result['created_count'] > 0:
            messages.success(request, f"{result['created_count']} lead(s) uploaded.")
        elif not result['skipped']:
            messages.error(request, "No valid data found.")


    return redirect('verify_leads_page', team_alloc_id=team_alloc_id, lead_category_id=result.get('lead_category_id', 0))

# ? js calls

@csrf_exempt
def change_lead_status(request):
    print("ðŸ“¥ Received request to change status")
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            lead_ids = body.get("leads", [])
            status = body.get("status")

            print("Lead IDs:", lead_ids)
            print("Status type:", status)

            if not lead_ids or not status:
                print("Missing lead IDs or status.")
                return JsonResponse({"success": False, "message": "Missing required data."})

            from .models import Leads  # Adjust if necessary

            update_fields = {}

            if status == "unverified":
                update_fields["status"] = 0
            elif status == "verified":
                update_fields["status"] = 1
            elif status == "waste":
                update_fields["waste_data"] = 1
            elif status == "not_waste":
                update_fields["waste_data"] = 0
            elif status == "incomplete":
                update_fields["incomplete_status"] = 1
            elif status == "not_incomplete":
                update_fields["incomplete_status"] = 0
            elif status == "repeated":
                update_fields["repeated_status"] = 1
            else:
                print("Invalid status type:", status)
                return JsonResponse({"success": False, "message": "Invalid status."})

            Leads.objects.filter(id__in=lead_ids).update(**update_fields)
            print("Status updated for leads:", lead_ids)

            return JsonResponse({"success": True})

        except Exception as e:
            print("Exception:", e)
            return JsonResponse({"success": False, "message": "Server error."})

    return JsonResponse({"success": False, "message": "Invalid request method."})

def download_lead_excel_format(request, lead_category_id):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Lead Format"
    
    headers = ['Name', 'Email', 'Contact Number', 'Course']
    additional_fields = LeadField_Register.objects.filter(
        lead_category_id=lead_category_id
    ).values_list('name', flat=True)
    headers.extend(additional_fields)

    for idx, header in enumerate(headers, start=1):
        sheet.cell(row=1, column=idx, value=header)

    category = LeadCategory_Register.objects.filter(id=lead_category_id).first()
    client_name = category.client_task.client.client_name.replace(" ", "_") if category and category.client_task and category.client_task.client else "Client"
    category_id = category.id if category else "Unknown"

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"{client_name}_{category_id}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    workbook.save(response)
    return response

@csrf_exempt
def transfer_selected_leads(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            lead_ids = body.get("leads", [])
            if not lead_ids:
                return JsonResponse({"success": False, "message": "No leads provided."})

            Leads.objects.filter(id__in=lead_ids, status=1).update(transfer_status=1, transfer_date=date.today())

            for lead_id in lead_ids:
                lead = Leads.objects.filter(id=lead_id, status=1).first()
                if lead and not DataBank.objects.filter(lead=lead).exists():
                    DataBank.objects.create(lead=lead)

            # Add the message
            request.session['transfer_success'] = f"{len(lead_ids)} lead(s) successfully transferred."

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})

def process_excel_upload(request, team_alloc_id, employee_user, force_save=False):
    excel = request.FILES.get('excel_file')
    category_alloc = LeadCateogry_TeamAllocate.objects.filter(id=team_alloc_id).first()

    if not category_alloc:
        return {'error': "Invalid team allocation."}

    lead_category = category_alloc.lead_category
    first_lf = LeadField_Register.objects.filter(lead_category=lead_category).first() if lead_category else None
    work_fk = first_lf.work if first_lf else None

    required_static = ['Name', 'Email', 'Contact Number', 'Course']
    required_dynamic = list(LeadField_Register.objects.filter(lead_category=lead_category).values_list('name', flat=True))
    expected_columns = required_static + required_dynamic
    allowed_columns = expected_columns + ['Lead Source']

    try:
        df = pd.read_excel(excel)
    except Exception:
        return {'error': "Invalid Excel file format."}

    actual_headers = list(df.columns)
    unknown_headers = [h for h in actual_headers if h not in allowed_columns]
    missing_headers = [h for h in expected_columns if h not in actual_headers]

    if missing_headers:
        return {'error': f"Missing required columns: {', '.join(missing_headers)}."}
    if unknown_headers:
        return {'error': f"Unrecognized columns: {', '.join(unknown_headers)}."}

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^\d{10}$'

    skipped = []
    created_count = 0
    duplicate_leads = []
    pending_rows = []

    for i, row in df.iterrows():
        try:
            data = row.to_dict()
            row_index = i + 2

            name = str(data.get('Name')).strip() if pd.notna(data.get('Name')) else ''
            email = str(data.get('Email')).strip().lower() if pd.notna(data.get('Email')) else ''
            raw_contact = data.get('Contact Number')
            contact = re.sub(r'\D', '', str(int(raw_contact))) if pd.notna(raw_contact) and str(raw_contact).strip() != '' else ''
            source = None

            if not name or not email or not contact:
                skipped.append(f"Row {row_index}: missing required static fields.")
                continue

            missing_dynamic = [field for field in required_dynamic if not str(data.get(field)).strip()]
            if missing_dynamic:
                skipped.append(f"Row {row_index}: missing dynamic field(s): {', '.join(missing_dynamic)}.")
                continue

            if not re.match(email_pattern, email):
                skipped.append(f"Row {row_index}: invalid email format.")
                continue

            if not re.match(phone_pattern, contact):
                skipped.append(f"Row {row_index}: invalid contact number.")
                continue

            existing_leads = Leads.objects.filter(
                Q(email=email) | Q(contact=contact)
            )

            existing_leads = Leads.objects.filter(
                Q(email=email) | Q(contact=contact)
            )

            is_repeated = existing_leads.exists()

            if is_repeated:

                for existing in existing_leads:
                    duplicate_leads.append({
                        "existing_name": existing.name,
                        "existing_email": existing.email,
                        "existing_contact": existing.contact,
                        "existing_source": existing.source,

                        "uploaded_name": name,
                        "uploaded_email": email,
                        "uploaded_contact": contact,
                        "uploaded_source": source,
                    })

                pending_rows.append({
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "source": source,
                    "dynamic_fields": {
                        field: str(data.get(field)).strip()
                        for field in required_dynamic
                    }
                })

                if not force_save:
                    continue  

            lead = Leads.objects.create(
                name=name,
                email=email,
                contact=contact,
                source=source,
                lead_category=lead_category,
                work=work_fk,
                collected_by_id=employee_user.id,
                repeated_status=1
                    if is_repeated else 0
            )

            # Save Course
            course_val = str(data.get('Course', '') or '').strip()
            if course_val and course_val.lower() != 'nan':
                LeadDetails.objects.create(
                    lead=lead,
                    field_name='Course',
                    field_data=course_val
                )

            for field in required_dynamic:
                LeadDetails.objects.create(
                    lead=lead,
                    field_name=field,
                    field_data=str(data.get(field)).strip()
                )

            created_count += 1
        except Exception as e:
            print(f"Row {row_index} Error:", e)

    return {
        'success': True,
        'created_count': created_count,
        'skipped': skipped,
        'duplicate_leads': duplicate_leads,
        "pending_rows": pending_rows,
        'lead_category_id': lead_category.id,
    }

#--------------------------------------------DMHEAD--END---------------------------
# -----------------------------EXECUTIVE-----------------------------------------------------------------------

def executive_action_taken(request):
    session_login_id = request.session.get('eid')


    if session_login_id:
        try:
            user = LogRegister_Details.objects.get(log_username=session_login_id)
            employee = EmployeeRegister_Details.objects.get(login=user)
            name = employee  
            employee_id = employee.id

            print("Matched Employee ID for schedule:", employee_id, name)

            actions = ActionTaken.objects.filter(employee_id=employee)

        except EmployeeRegister_Details.DoesNotExist:
            print("Employee record not found for LogRegister_Details ID:", session_login_id)


    return render(request,'executive/executive_action_taken.html',{'name':name,'actions':actions})

def executive_feedback(request):
    session_login_id = request.session.get('eid')
    feedback_receivers = []  
    feedback_given = []
    feedback_received = []

    if session_login_id:
        try:
            user = LogRegister_Details.objects.get(log_username=session_login_id)
            employee = EmployeeRegister_Details.objects.get(login=user)
            name = employee  
            employee_id = employee.id
            department = employee.department

            print("Matched Employee ID for schedule:", employee_id, name)

            # Filter for Digital_Marketing_Head and Data_Manager in same department, approved (is_staff=True)
            feedback_receivers = EmployeeRegister_Details.objects.filter(
                department=department,
                login__position__in=['Digital_Marketing_Head', 'Data_Manager'],
                login__is_staff=True
            )


            # Fetch feedbacks given by this employee
            feedback_given = Feedback.objects.filter(from_id=employee_id).select_related('employee')

            # Fetch feedbacks received by this employee
            feedback_received = Feedback.objects.filter(employee=employee).select_related('employee')

        except EmployeeRegister_Details.DoesNotExist:
            print("Employee record not found for LogRegister_Details ID:", session_login_id)
            name = None

    return render(request, 'executive/executive_feedback.html', {
        'name': name,
        'feedback_receivers': feedback_receivers,
        'feedback_given': feedback_given,
        'feedback_received': feedback_received

    })

def executive_add_feedback(request):
    if request.method == 'POST':
        session_login_id = request.session.get('eid')

        if session_login_id:
            try:
                user = LogRegister_Details.objects.get(log_username=session_login_id)
                employee = EmployeeRegister_Details.objects.get(login=user)
                from_id = employee.id
                from_name = employee.name

            except EmployeeRegister_Details.DoesNotExist:
                messages.error(request, "Logged-in employee not found.")
                return redirect('executive_feedback')

            feedback = request.POST.get('feedback')
            receiver_id = request.POST.get('receiver')

            try:
                receiver = EmployeeRegister_Details.objects.get(id=receiver_id)

                new_feedback = Feedback(
                    from_id=from_id,
                    from_name=from_name,
                    feedback_content=feedback,
                    feedback_date=now().date(),
                    employee=receiver
                )
                new_feedback.save()
                messages.success(request, "Feedback sent successfully.")
                return redirect('executive_feedback')
            except EmployeeRegister_Details.DoesNotExist:
                messages.error(request, "Selected receiver not found.")
                return redirect('executive_feedback')
    
    return render(request, 'executive/executive_feedback.html')

def executive_complaints(request):
    session_login_id = request.session.get('eid')
    if session_login_id:
        try:
            user = LogRegister_Details.objects.get(log_username=session_login_id)
            employee = EmployeeRegister_Details.objects.get(login=user)
            name = employee  
            employee_id = employee.id
            department = employee.department

        except EmployeeRegister_Details.DoesNotExist:
            print("Employee record not found for LogRegister_Details ID:", session_login_id)
            name = None

        complaints = Complaint.objects.filter(employee_id=employee)


    return render(request,'executive/executive_complaints.html',{'name':name,'complaints': complaints})

def executive_add_complaints(request):
    if request.method == 'POST':
        session_login_id = request.session.get('eid')

        if session_login_id:
            try:
                user = LogRegister_Details.objects.get(log_username=session_login_id)
                employee = EmployeeRegister_Details.objects.get(login=user)
                from_id = employee.id
                from_name = employee.name
            except EmployeeRegister_Details.DoesNotExist:
                messages.error(request, "Logged-in employee not found.")
                return redirect('executive_complaints')

            # Get complaint fields
            complaint_head = request.POST.get('complaint_head')
            details = request.POST.get('complaint_details')

            # Check if complaint fields are provided
            if not complaint_head or not details:
                messages.error(request, "Both complaint title and details are required.")
                return redirect('executive_complaints')  

            # Create and save the complaint
            reg_complaint = Complaint(
                compaint_head=complaint_head,
                compaint_content=details,
                # complaint_date=timezone.now().date(),  
                employee_id=employee.id  
            )
            reg_complaint.save()

            messages.success(request, 'Complaint successfully registered')
            return redirect('executive_complaints')  

    return render(request, 'executive/executive_complaints.html')
    
def emp_works(request):
    eid = request.session.get('eid')
    user = LogRegister_Details.objects.get(log_username=eid)
    employee = EmployeeRegister_Details.objects.get(login=user)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    today = date.today()
    today_schedules = EmployeeSchedule.objects.filter(employee=employee, schedule_date=today)

    return render(request, 'executive/emp_works.html', {
        'today_schedules': today_schedules,
        'today': today,  
        'user': user,
        'company': company,
        'name': name,
    })

def emp_new_works(request):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')  # redirect if not logged in

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    today = date.today()
    today_schedules = EmployeeSchedule.objects.filter(employee=employee, schedule_date=today)

    # Get tasks assigned to this executive
    tasks = TaskAssign.objects.filter(executive=employee, accept_status=0)

    return render(request, 'executive/emp_new_works.html', {
        'today_schedules': today_schedules,
        'today': today,
        'user': user,
        'company': company,
        'name': name,
        'tasks': tasks,  # pass task data to template
    })

from django.utils import timezone
def accept_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(TaskAssign, id=task_id)
        task.accept_status = 1
        task.accept_date = timezone.now().date()

        task.save()
    return redirect(request.META.get('HTTP_REFERER', 'executive/emp_new_works.html'))

def emp_ongoing_works(request):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')  # redirect if not logged in

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    today = date.today()
    today_schedules = EmployeeSchedule.objects.filter(employee=employee, schedule_date=today)

    # Get tasks assigned to this executive
    tasks = TaskAssign.objects.filter(executive=employee, accept_status=1).exclude(status=2)
    for task in tasks:
        if task.client_task.task_name.strip().lower() == "lead collection":
            task.lead_categories = LeadCategory_Register.objects.filter(client_task=task.client_task)
        else:
            task.lead_categories = None

    # Calculate target achieved percentage for each task
    for task in tasks:
        total_verified = TaskDetails.objects.filter(task_assign=task).aggregate(Sum('target'))['target__sum'] or 0
        task.percentage = round((total_verified / task.target) * 100, 2) if task.target > 0 else 0

    return render(request, 'executive/emp_ongoing_works.html', {
        'today_schedules': today_schedules,
        'today': today,
        'user': user,
        'company': company,
        'name': name,
        'tasks': tasks,  # includes percentage now
    })


def complete_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(TaskAssign, id=task_id)
        
        # 1. Check if task is verified
        if task.accept_status != 1:
            messages.error(request, "Task is not verified.")
            return redirect('emp_ongoing_works')

        # 2. Check if at least one daily work exists
        if not TaskDetails.objects.filter(task_assign=task).exists():
            messages.error(request, "No daily work found for this task.")
            return redirect('emp_ongoing_works')

        # 3. Check if target is achieved
        if task.target_achieved < task.target:
            messages.error(request, "Target not yet achieved.")
            return redirect('emp_ongoing_works')

        # All validations passed, mark as completed
        task.status = 2
        task.save()
        messages.success(request, "Task marked as completed.")
        return redirect('emp_ongoing_works')
    


def save_daily_work(request):
    if request.method == 'POST':
        task_assign_id = request.POST.get('task_assign_id')
        title = request.POST.get('title')
        description = request.POST.get('daily_work')
        target = request.POST.get('target')
        uploaded_file = request.FILES.get('files')  # single file upload

        task_assign = get_object_or_404(TaskAssign, id=task_assign_id)

        TaskDetails.objects.create(
            task_assign=task_assign,
            title=title,
            description=description,
            file=uploaded_file,
            target=int(target),
        )

        messages.success(request, "Daily work added successfully.")
        return redirect('emp_ongoing_works')

def emp_completed_works(request):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')  # redirect if not logged in

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    today = date.today()
    today_schedules = EmployeeSchedule.objects.filter(employee=employee, schedule_date=today)

    # Get tasks assigned to this executive
    tasks = TaskAssign.objects.filter(executive=employee, status=2)

    return render(request, 'executive/emp_completed_works.html', {
        'today_schedules': today_schedules,
        'today': today,
        'user': user,
        'company': company,
        'name': name,
        'tasks': tasks,  # pass task data to template
    })

def view_detail_ongoing_works(request, task_id):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    task = get_object_or_404(TaskAssign, id=task_id)

   
    

    # Get related task details for this task assignment
    task_details = TaskDetails.objects.filter(task_assign=task)
    client_task = task.client_task
    categories = LeadCategory_Register.objects.filter(client_task=client_task)

    # Calculate percentage for each detail
    for detail in task_details:
        if task.target > 0:
            detail.percentage = round((detail.target / task.target) * 100, 2)
        else:
            detail.percentage = 0

    context = {
        'name':employee,
        'task': task,
        'task_details': task_details,
        'categories':categories,
    }
    return render(request, 'executive/view_detail_ongoing_works.html', context)






def add_daily_lead_collection(request, task_id):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    task = get_object_or_404(TaskAssign, id=task_id)
    client_task = task.client_task

    task_details = TaskDetails.objects.filter(task_assign=task)

    for detail in task_details:
        if task.target > 0:
            detail.percentage = round((detail.target / task.target) * 100, 2)
        else:
            detail.percentage = 0

    total_verified = sum(detail.verified_target for detail in task_details)
    percentage = round((total_verified / task.target) * 100, 2) if task.target else 0

    # Get unique lead categories for this client and client_task
    lead_fields = LeadField_Register.objects.filter(
    lead_category__client_task=task.client_task)

    context = {
        'name':employee,
        'task': task,
        'client_task': client_task,
        'task_details': task_details,
        'required_fields': lead_fields,  # Updated to pass queryset instead of list
        'task_percentage': percentage,
    }
    return render(request, 'executive/add_daily_lead_collection.html', context)







def add_daily_work(request, task_id):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    task = get_object_or_404(TaskAssign, id=task_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        achieved_target = request.POST.get('target')

        # handle file upload
        uploaded_files = request.FILES.getlist('file')

        for f in uploaded_files:
            TaskDetails.objects.create(
                task_assign=task,
                title=title,
                description=description,
                target=task.target,
                achieved_target=int(achieved_target or 0),
                file=f,  # saves one file per row
            )

        return redirect('add_daily_work', task_id=task.id)  # or show success message

    task_details = TaskDetails.objects.filter(task_assign=task)
    today = date.today()

    context = {
        'name':employee,
        'task': task,
        'task_details': task_details,
        'today': today,
    }
    return render(request, 'executive/add_daily_work.html', context)





def lead_cat_view(request, task_id):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')
    
    task = get_object_or_404(TaskAssign, id=task_id)
    client_task = task.client_task
    categories = LeadCategory_Register.objects.filter(client_task=client_task)

    context = {
        'name':employee,
        'task': task,
        'categories': categories,
    }
    return render(request, 'executive/lead_categories.html', context)





def lead_list(request, category_id):
    eid = request.session.get('eid')
    if not eid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=eid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect('login')

    category = get_object_or_404(LeadCategory_Register, id=category_id)
    lead_fields = LeadField_Register.objects.filter(lead_category=category)

    if request.method == 'POST':

        confirm_duplicate = request.POST.get("confirm_duplicate", "0")

        name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        course = (request.POST.get('course') or '').strip()
        source = None

        if not course:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": "Course is required."}, status=400)
            messages.error(request, "Course is required.")
            return redirect('lead_list', category_id)

        duplicates = Leads.objects.filter(
            Q(email=email) | Q(contact=contact)
        ).order_by('-id')

        # Duplicate found and not confirmed
        if duplicates.exists() and confirm_duplicate != "1":

            duplicate_list = []

            for lead in duplicates:
                duplicate_list.append({
                    "id": lead.id,
                    "name": lead.name,
                    "email": lead.email,
                    "contact": lead.contact,
                    "source": lead.source,
                })

            return JsonResponse({
                "duplicate": True,
                "duplicates": duplicate_list
            })

        # Save Lead
        lead = Leads.objects.create(
            name=name,
            email=email,
            contact=contact,
            source=source,
            work=category.client_task.work if category.client_task else None,
            lead_category=category,
            collected_by=employee,
            repeated_status=1 if duplicates.exists() else 0
        )

        if course:
            LeadDetails.objects.create(
                lead=lead,
                field_name='Course',
                field_data=course,
            )

        # Save Dynamic Fields
        for field in lead_fields:
            field_input_name = slugify(field.name)
            value = request.POST.get(field_input_name)
            if value is not None and value.strip():
                LeadDetails.objects.create(
                    lead=lead,
                    field_name=field.name,
                    field_data=value.strip(),
                )

        # AJAX Request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True
            })

        messages.success(request, "Lead added successfully.")
        return redirect('lead_list', category_id)

    leads = Leads.objects.filter(lead_category=category,collected_by=employee).order_by('-id')
    lead_count = leads.count()
    lead_range = range(1, lead_count + 1)
    context = {
        'name':employee,
        'lead_fields': lead_fields,
        'category': category,
        'leads': leads,
        'category_id': category_id,
        'lead_count':lead_count,
        'lead_range':lead_range,
    }
    return render(request, 'executive/lead_list.html', context)

def remove_duplicates(request, category_id):
    if request.method == "POST":
        duplicates = Leads.objects.filter(lead_category_id=category_id,repeated_status=1)
        for dup in duplicates:
            dup.delete()
        return redirect('lead_list', category_id=category_id)

def remove_duplicate_TL(request, category_id):
    duplicates = Leads.objects.filter(lead_category_id=category_id,repeated_status=1)
    for dup in duplicates:
        dup.delete()
        messages.success(request,'Deleted..')
    return redirect('tl_all_leads')
    
def download_leads(request, category_id):
    leads = Leads.objects.filter(lead_category_id=category_id)
    category = LeadCategory_Register.objects.get(id=category_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads Data"

    # Write headers
    headers = ['No', 'Name', 'Email', 'Contact', 'Lead Source', 'Added Date']
    ws.append(headers)

    # Write data
    for i, lead in enumerate(leads, start=1):
        ws.append([
            i,
            lead.name,
            lead.email,
            lead.contact,
            lead.source,
            lead.added_date.strftime('%Y-%m-%d') if lead.added_date else '',
        ])

    # Prepare HTTP response
    client_name = category.client_task.client.client_name
    safe_filename = f"{slugify(client_name)}-leads.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'

    wb.save(response)
    return response

def upload_leads(request, category_id):

    if request.method != "POST":
        return redirect("lead_list", category_id=category_id)

    confirm_upload = request.POST.get("confirm_upload", "0")


    if confirm_upload == "0":

        if "excel_file" not in request.FILES:
            return JsonResponse({
                "success": False,
                "message": "Please select an Excel file."
            })

        excel_file = request.FILES["excel_file"]

        # Save file temporarily in session
        request.session["uploaded_excel"] = base64.b64encode(
            excel_file.read()
        ).decode("utf-8")

    else:

        file_data = request.session.get("uploaded_excel")

        if not file_data:
            return JsonResponse({
                "success": False,
                "message": "Uploaded file expired. Please upload again."
            })

        excel_file = BytesIO(base64.b64decode(file_data))


    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active

    category = LeadCategory_Register.objects.get(id=category_id)

    lead_field = LeadField_Register.objects.filter(
        lead_category=category
    ).first()

    eid = request.session.get("eid")

    employee = EmployeeRegister_Details.objects.get(
        login__log_username=eid
    )

    work_fk = lead_field.work if lead_field else None

    headers = [
        str(cell.value).strip() if cell.value else ""
        for cell in sheet[1]
    ]

    header_names_lower = [h.lower() for h in headers]
    if 'course' not in header_names_lower:
        return JsonResponse({
            "success": False,
            "message": "Missing required column: Course."
        })

    if confirm_upload == "0":

        duplicate_list = []

        for row_no, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True),
                start=2):

            name = str(row[1]).strip() if row[1] else ""
            email = str(row[2]).strip() if row[2] else ""
            contact = str(row[3]).strip() if row[3] else ""

            existing = Leads.objects.filter(
                Q(email=email) | Q(contact=contact)
            )

            if existing.exists():

                for lead in existing:

                    duplicate_list.append({

                        "excel_row": row_no,
                        "excel_name": name,

                        "id": lead.id,
                        "name": lead.name,
                        "email": lead.email,
                        "contact": lead.contact,
                        "source": lead.source,

                    })

        if duplicate_list:

            return JsonResponse({
                "duplicate": True,
                "duplicates": duplicate_list
            })



    new_count = 0

    dynamic_fields = LeadField_Register.objects.filter(
        lead_category=category,
        status=0
    )

    for row in sheet.iter_rows(min_row=2, values_only=True):

        row_data = dict(zip(headers, row))

        raw_name = row_data.get("Name") if "Name" in row_data else (row[1] if len(row) > 1 else "")
        raw_email = row_data.get("Email") if "Email" in row_data else (row[2] if len(row) > 2 else "")
        raw_contact = row_data.get("Contact") if "Contact" in row_data else (row[3] if len(row) > 3 else "")
        name = str(raw_name).strip() if raw_name else ""
        email = str(raw_email).strip() if raw_email else ""
        contact = str(raw_contact).strip() if raw_contact else ""
        source = None

        if not name or not email or not contact:
            continue

        is_repeated = Leads.objects.filter(
            Q(email=email) | Q(contact=contact)
        ).exists()

        lead = Leads.objects.create(

            name=name,
            email=email,
            contact=contact,
            source=source,
            lead_category=category,
            work=work_fk,
            collected_by=employee,
            repeated_status=1 if is_repeated else 0

        )

        course_val = str(row_data.get("Course") or row_data.get("course") or "").strip()
        if course_val:
            LeadDetails.objects.create(
                lead=lead,
                field_name='Course',
                field_data=course_val
            )

        for field in dynamic_fields:

            value = row_data.get(field.name)

            if value not in [None, ""]:

                LeadDetails.objects.create(

                    lead=lead,
                    field_name=field.name,
                    field_data=str(value)

                )

        new_count += 1

   
    request.session.pop("uploaded_excel", None)

    return JsonResponse({
        "success": True,
        "count": new_count
    })

def delete_lead(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    lead.delete()
    messages.success(request, "Lead deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'lead_list'))
# -----------------------------EXECUTIVE--END---------------------------------------------------------------------

# HR Dashboard View
def hr_dashboard(request):
    # Assuming 'tcid' is the session key for telecaller login
    tcid = request.session.get('tcid')
    
    if not tcid:
        return redirect('login')  # Redirect to login if not in session
    
    try:
        user = LogRegister_Details.objects.get(log_username=tcid)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        employee = None
    
    context = {
        'user': user,
        'employee': employee,
        'name': employee  # Assuming you're using 'name' in the template
    }
    
    return render(request, 'telecaller/telecallersidebar.html', context)

# HR Leave Management
def hr_leave(request):
    # Using correct session key 
    tcid = request.session.get('tcid')
    
    if not tcid:
        return redirect('login')
    
    try:
        user = LogRegister_Details.objects.get(log_username=tcid)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        employee = None
    
    # Fetch leaves only for logged-in employee
    all_leaves = []
    if employee:
        all_leaves = EmployeeLeave.objects.filter(employee=employee).order_by('-applied_date')
    
    return render(request, 'telecaller/hr_leave.html', {
        'all_leaves': all_leaves,
        'user': user,
        'employee': employee,
        'name': employee
    })

# Apply for Leave
def apply_leavehr(request):
    # Get user details from session using the correct session key
    tcid = request.session.get('tcid')
    
    if not tcid:
        messages.error(request, "You need to log in to apply for leave.")
        return redirect("login")
    
    # Get Employee Record using correct field names
    try:
        user = LogRegister_Details.objects.get(log_username=tcid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except LogRegister_Details.DoesNotExist:
        messages.error(request, "User not found in log register. Please contact admin.")
        return redirect("hr_leave")
    except EmployeeRegister_Details.DoesNotExist:
        messages.error(request, "Employee record not found. Please contact admin.")
        return redirect("hr_leave")
    
    if request.method == "POST":
        # Get form data
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        leave_type = request.POST.get("leave_type")
        reason = request.POST.get("leave_reason")  # Using the field name from the model
        request_file = request.FILES.get("leave_request_file", None)  # Using the field name from the model
        
        # Validate required fields
        if not (start_date and end_date and leave_type and reason):
            messages.error(request, "All fields are required except file upload.")
            return redirect("hr_leave")
        
        # Convert dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("hr_leave")
        
        # Validate dates
        if start_date_obj > end_date_obj:
            messages.error(request, "Start date cannot be after end date.")
            return redirect("hr_leave")
        
        number_of_days = (end_date_obj - start_date_obj).days + 1
        
        # Save Leave Application using correct field names
        try:
            leave_entry = EmployeeLeave.objects.create(
                employee=employee,
                start_date=start_date_obj,
                end_date=end_date_obj,
                leave_type=leave_type,
                reason=reason,  # Match the field name in model
                number_of_days=number_of_days,
                request_file=request_file  # Match the field name in model
            )
            messages.success(request, "Leave application submitted successfully.")
        except Exception as e:
            messages.error(request, f"Error while saving leave application: {str(e)}")
        
        return redirect("hr_leave")
    
    return redirect("hr_leave")

# Feedback Functionality
def add_feedbackhr(request):
    tcid = request.session.get('tcid')
    
    if not tcid:
        return redirect("login")
    
    try:
        user = LogRegister_Details.objects.get(log_username=tcid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return redirect("login")
    
    # Get filter type from query parameter
    filter_type = request.GET.get("filter_type", "all")
    
    # Filter feedback based on user selection
    if filter_type == "given":
        feedback_list = Feedback.objects.filter(from_id=user.id).order_by("-feedback_date")
    elif filter_type == "received":
        feedback_list = Feedback.objects.filter(employee=employee).order_by("-feedback_date")
    else:  # 'all' - both given and received
        feedback_list = Feedback.objects.filter(
            Q(from_id=user.id) | Q(employee=employee)
        ).order_by("-feedback_date")
    
    # Employees in same company & department (excluding self)
    company = employee.company
    department = employee.department
    
    approved_emps = EmployeeRegister_Details.objects.filter(
        active_status='Approved',
        company=company,
        department=department
    ).exclude(id=employee.id)
    
    if request.method == "POST":
        feedback_emp_id = request.POST.get("feedback_emp")
        feedback_content = request.POST.get("feedback_content")
        
        if feedback_emp_id and feedback_content:
            try:
                feedback_emp = EmployeeRegister_Details.objects.get(id=feedback_emp_id)
                Feedback.objects.create(
                    employee=feedback_emp,
                    from_id=user.id,
                    from_name=employee.name,
                    feedback_content=feedback_content,
                    feedback_date=timezone.now().date()  # Set current date
                )
                messages.success(request, "Feedback submitted successfully.")
                return redirect("add_feedbackhr")
            except EmployeeRegister_Details.DoesNotExist:
                messages.error(request, "Selected employee does not exist.")
        else:
            messages.error(request, "All fields are required.")
    
    context = {
        'approved_emps': approved_emps,
        'feedback_list': feedback_list,
        'current_user_name': employee.name,
        'current_user_id': user.id,
        'current_emp_id': employee.id,
        'user': user,
        'employee': employee,
        'filter_type': filter_type,
        'name': employee
    }
    
    return render(request, 'telecaller/hr_feedback.html', context)

def add_complaints(request):
    tcid = request.session.get('tcid')
    
    if not tcid:
        return redirect("login")

    try:
        user = LogRegister_Details.objects.get(log_username=tcid)
        employee = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        messages.error(request, "User or employee not found.")
        return redirect("login")

    company = employee.company
    department = employee.department

    # Get approved employees (excluding current user)
    approved_emps = EmployeeRegister_Details.objects.filter(
        active_status='Approved',
        company=company,
        department=department
    ).exclude(id=employee.id)

    complaints_list = Complaint.objects.filter(
        employee=employee
    ).order_by("-id")

    if request.method == "POST":
        # Match the field names from the HTML form
        complaint_head = request.POST.get("complaint_head")
        complaint_content = request.POST.get("complaint_content")
        # against_emp is collected from form but not used in model
        
        if complaint_head and complaint_content:
            try:
                Complaint.objects.create(
                    employee=employee,
                    compaint_head=complaint_head,  # Note: model field has typo
                    compaint_content=complaint_content,  # Note: model field has typo
                    status='pending'
                )
                messages.success(request, "Complaint submitted successfully.")
                return redirect("add_complaints")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'telecaller/hr_complaint.html', {
        "approved_emps": approved_emps,  # Still needed for the form
        "complaints_list": complaints_list,
        "user": user,
        "employee": employee,
        'name': employee
    })
    
def action_list(request):
    # Get login session ID
    aid = request.session.get('tcid')
    
    if not aid:
        return redirect('login')  # Redirect to login if session is not set

    try:
        # Get the logged-in user and employee details
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')  # User does not exist

    # If employee exists, get only their actions
    actions = []
    if employee:
        actions = ActionTaken.objects.filter(employee=employee).select_related('employee').order_by('-action_date')

    context = {
        'actions': actions,
        'user': user,
        'company': company,
        'name': employee
    }
    return render(request, 'telecaller/hr_action.html', context)
    
#End

# ======================================================== teamlead ================================================================
def teamlead_work(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    company = name.company if name else None

    context={
        'user': user,
        'company': company,
        'name': name,
    }
    return render(request, 'teamlead/tl_works.html', context)

def individual_work_main(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    company = name.company if name else None

    context={
        'user': user,
        'company': company,
        'name': name,
    }
    print(context)
    return render(request, 'teamlead/individual_work_main.html', context)

@csrf_exempt
def tl_new_works(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    company = name.company if name else None

    if request.method == 'POST':
        task_type = request.POST.get('type')
        object_id = request.POST.get('id')
        try:
            if task_type == 'normal':
                task = WorkAssign.objects.get(id=object_id)
                task.status = 2
                task.accept_date = date.today()
                task.save()
                print(f"[DEBUG] Accepted WorkAssign {object_id}")  #!========delete this line =============

            elif task_type == 'lead_collection':
                record = LeadCateogry_TeamAllocate.objects.get(id=object_id)
                record.status = 2
                record.accept_date = date.today()
                record.save()
                print(f"[DEBUG] Accepted LeadCateogry_TeamAllocate {object_id}")  #!========delete this line =============

        except Exception as e:
            print(f"[ERROR] Accept failed: {e}")  #!========delete this line =============
            
    all_data = []

    work_assigns = WorkAssign.objects.filter(team_lead=name, status=1 ,assign_type=0).select_related('client')
    
    for assign in work_assigns:
        for task in assign.client_task.all():
            if task.task_name.strip().lower() != "lead collection":
                all_data.append({
                    'type': 'normal',
                    'assign_id': assign.id,
                    'task_id': task.id,
                    'task_name': task.task_name,
                    'task_description': assign.description or '',
                    'start_date': assign.from_date,
                    'end_date': assign.due_date,
                    'assign_date': assign.assign_date,
                    'accept_date': assign.accept_date,
                    'client_name': assign.client.client_name if assign.client else '',
                    'target': assign.target,
                    'file_url': assign.file.url if assign.file else '',
    
                    # new fields
                    'is_instagram': int(assign.is_instagram),
                    'instagram_target': assign.instagram_target,
                    'is_facebook': int(assign.is_facebook),
                    'facebook_target': assign.facebook_target,
                    'is_x': int(assign.is_x),
                    'x_target': assign.x_target,
                })
    
    lead_tasks = LeadCateogry_TeamAllocate.objects.filter(team_lead=name, status=1).select_related('lead_category', 'work_assign__client')
    
    for record in lead_tasks:
        lead = record.lead_category
        assign = record.work_assign
    
        all_data.append({
            'type': 'lead_collection',
            'team_alloc_id': record.id,
            'assign_id': assign.id,
            'task_id': lead.id,
            'task_name': lead.collection_for or 'Lead Collection',
            'task_description': record.description or '',
            'start_date': record.from_date,
            'end_date': record.due_date,
            'assign_date': assign.assign_date,
            'client_name': assign.client.client_name if assign.client else '',
            'accept_date': record.accept_date,
            'target': record.target,
            'file_url': record.file.url if record.file else '',
    
            # new fields
            'is_instagram': int(assign.is_instagram),
            'instagram_target': assign.instagram_target,
            'is_facebook': int(assign.is_facebook),
            'facebook_target': assign.facebook_target,
            'is_x': int(assign.is_x),
            'x_target': assign.x_target,
        })


    context = {
        'user': user,
        'company': company,
        'name': name,
        'new_works': all_data,
    }

    return render(request, 'teamlead/tl_new_works.html', context)

def tl_ongoing_works(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    company = name.company if name else None

    #? ======================== POST: Save Daily Work Report =======================
    if request.method == 'POST':
        print("[POST DATA]", request.POST)  #!========delete this line =============

        try:
            assign_id = int(request.POST.get('task_assign_id'))
            is_category = request.POST.get('is_category') == 'true'
            title = request.POST.get('title')
            description = request.POST.get('work_description')
            achieved = int(request.POST.get('achieved') or 0)
            uploaded_file = request.FILES.get('work_file')

            if is_category:
                record = LeadCateogry_TeamAllocate.objects.get(id=assign_id)
                target = record.target
                task_detail = TaskDetails(
                    is_category=True,
                    category_assign=record,
                    target=target,
                    achieved_target=achieved,
                    title=title,
                    description=description,
                    status=0
                )
            else:
                record = WorkAssign.objects.get(id=assign_id)
                target = record.target
                task_detail = TaskDetails(
                    is_category=False,
                    work_assign=record,
                    target=target,
                    achieved_target=achieved,
                    title=title,
                    description=description,
                    status=0
                )

            if uploaded_file:
                task_detail.file = uploaded_file

            task_detail.save()
            messages.success(request, "Daily report added successfully.")
            print(f"[DEBUG] Daily work saved for {'CategoryAssign' if is_category else 'WorkAssign'} ID {assign_id}")  #!========delete this line =============
            return redirect('tl_ongoing_works')

        except Exception as e:
            messages.error(request, "Failed to submit daily report.")
            print(f"[ERROR] Failed to save daily work: {e}")  #!========delete this line =============
            return redirect('tl_ongoing_works')

    #? ======================== GET: Render Ongoing Works ==========================
    all_data = []

    work_assigns = WorkAssign.objects.filter(team_lead=name, status=2 ,assign_type=0).select_related('client')
    print(f'[DEBUG]=============================TL name : {name}========================================')
    for assign in work_assigns:
        for task in assign.client_task.all():
            if task.task_name.strip().lower() != "lead collection":
                all_data.append({
                    'type': 'normal',
                    'is_category': False,
                    'task_assign_id': assign.id,
                    'task_name': task.task_name,
                    'task_description': assign.description or '',
                    'start_date': assign.from_date,
                    'end_date': assign.due_date,
                    'assign_date': assign.assign_date,
                    'accept_date': assign.accept_date,
                    'client_name': assign.client.client_name if assign.client else '',
                    'target': assign.target,
                    'achieved': assign.target_achieved,
                    'file_url': assign.file.url if assign.file else '',
                    'progress': assign.progress,

                    # new fields
                    'is_instagram': int(assign.is_instagram),
                    'instagram_target': assign.instagram_target,
                    'is_facebook': int(assign.is_facebook),
                    'facebook_target': assign.facebook_target,
                    'is_x': int(assign.is_x),
                    'x_target': assign.x_target,
                })

    lead_tasks = LeadCateogry_TeamAllocate.objects.filter(team_lead=name, status=2).select_related('lead_category', 'work_assign__client')
    for record in lead_tasks:
        lead = record.lead_category
        assign = record.work_assign

        all_data.append({
            'type': 'lead_collection',
            'is_category': True,
            'task_assign_id': record.id,
            'task_name': lead.collection_for or 'Lead Collection',
            'task_description': record.description or '',
            'start_date': record.from_date,
            'end_date': record.due_date,
            'assign_date': assign.assign_date,
            'accept_date': record.accept_date,
            'client_name': assign.client.client_name if assign.client else '',
            'target': record.target,
            'achieved': record.target_achieved,
            'file_url': record.file.url if record.file else '',
            'progress': record.progress,

            # new fields
            'is_instagram': int(assign.is_instagram),
            'instagram_target': assign.instagram_target,
            'is_facebook': int(assign.is_facebook),
            'facebook_target': assign.facebook_target,
            'is_x': int(assign.is_x),
            'x_target': assign.x_target,
        })

    context = {
        'user': user,
        'company': company,
        'name': name,
        'ongoing_works': all_data,
        'today': date.today(),
    }

    print(f"[DEBUG] Ongoing Works Count for TL {name.name}: {len(all_data)}")  #!========delete this line =============
    return render(request, 'teamlead/tl_ongoing_works.html', context)

def tl_daily_work_leads(request, team_alloc_id):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            team_lead = EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

    if request.method == 'POST':
        try:
            assign_id = int(request.POST.get('team_alloc_id'))
            title = request.POST.get('title')
            description = request.POST.get('work_description')
            achieved = int(request.POST.get('achieved') or 0)
            uploaded_file = request.FILES.get('work_file')

            record = get_object_or_404(LeadCateogry_TeamAllocate, id=assign_id)
            target = record.target

            task_detail = TaskDetails(
                is_category=True,
                category_assign=record,
                target=target,
                achieved_target=achieved,
                title=title,
                description=description,
                status=0,
                verified_target=0
            )

            if uploaded_file:
                task_detail.file = uploaded_file

            task_detail.save()
            messages.success(request, "Lead Collection daily work added successfully.")
            print(f"[DEBUG] Saved daily work for CategoryAssign ID {assign_id}")  #!========delete this line =============
            return redirect('tl_daily_work_leads', team_alloc_id=assign_id)

        except Exception as e:
            messages.error(request, "Failed to save daily work.")
            print(f"[ERROR] Failed to save daily work: {e}")  #!========delete this line =============
            return redirect('tl_daily_work_leads', team_alloc_id=team_alloc_id)


    # ?=================== page rendering logic ==========================
    team_alloc = LeadCateogry_TeamAllocate.objects.select_related(
        'lead_category', 'work_assign__client'
    ).filter(id=team_alloc_id).first()

    if not team_alloc:
        messages.error(request, "Invalid team allocation ID.")
        return redirect('tl_ongoing_works')

    client = team_alloc.work_assign.client
    lead_category = team_alloc.lead_category

    custom_fields = LeadField_Register.objects.filter(
        lead_category=lead_category
    ).values_list('name', flat=True)

    context = {
        'name':name,
        'today': date.today(),
        'clients': [{
            'client_name': client.client_name,
            'from_date': team_alloc.from_date,
            'due_date': team_alloc.due_date,
            'progress': team_alloc.progress,
            'required_fields': list(custom_fields),
            'team_alloc_id': team_alloc.id,
            'lead_category_id': lead_category.id,
        }],
        'team_alloc_id': team_alloc.id,
        'lead_category_name': lead_category.collection_for,
        'task_name': 'Lead Collection',
    }

    return render(request, 'teamlead/tl_lead_daily_table.html', context)

def add_daily_work_task(request, task_assign_id):
    work = WorkAssign.objects.select_related('client').filter(id=task_assign_id).first()
    if not work:
        print(f"[ERROR] No WorkAssign found with ID {task_assign_id}")
        return redirect('tl_ongoing_works')

    # Get the first client_task (for task name)
    task_name = ''
    if work.client_task.exists():
        task_name = work.client_task.first().task_name

    # Prepare task data dictionary
    task_data = {
        'task_name': task_name,
        'task_description': work.description or '',
        'start_date': work.from_date,
        'end_date': work.due_date,
        'assign_date': work.assign_date,
        'accept_date': work.accept_date,
        'client_name': work.client.client_name if work.client else '',
        'target': work.target,
        'achieved': work.target_achieved,
        'file_url': work.file.url if work.file else '',
        'progress': work.progress,
    }

    # Determine platforms
    platforms = []
    if work.is_instagram:
        platforms.append('instagram')
    if work.is_facebook:
        platforms.append('facebook')
    if work.is_x:
        platforms.append('x')

    if request.method == 'POST':
        print("[POST DATA]", request.POST)  #!========delete this line =============

        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            achieved = int(request.POST.get('achieved') or 0)
            uploaded_file = request.FILES.get('file')
            target = work.target

            task_detail = TaskDetails(
                is_category=False,
                work_assign=work,
                target=target,
                achieved_target=achieved,
                title=title,
                description=description,
                status=0
            )

            if uploaded_file:
                task_detail.file = uploaded_file

            task_detail.save()
            print(f"[DEBUG] Daily work saved for WorkAssign ID {work.id}")  #!========delete this line =============

            # Save social media promotions only if platforms are assigned
            if platforms:
                for p in platforms:
                    if f'{p}_achieved_text' in request.POST:
                        urls = request.POST.getlist(f'{p}_urls[]')
                        urls_str = ','.join([u.strip() for u in urls if u.strip()])
                        SocialMediaPromotion.objects.create(
                            task_detail=task_detail,
                            platform=p,
                            achieved_text=request.POST.get(f'{p}_achieved_text'),
                            urls=urls_str,
                            screenshots=request.FILES.get(f'{p}_screenshot'),
                            remarks=request.POST.get(f'{p}_remarks'),
                            work_assign=work,
                            category_assign=None
                        )

            messages.success(request, "Daily report added successfully.")
            return redirect('tl_ongoing_works')

        except Exception as e:
            messages.error(request, "Failed to submit daily report.")
            print(f"[ERROR] Failed to save daily work: {e}")  #!========delete this line =============
            return redirect('tl_ongoing_works')

    return render(request, 'teamlead/add_daily_work.html', {
        'mode': 'task',
        'work': work,
        'task_data': task_data,
        'is_platform': bool(platforms),
        'platforms': platforms,
        'today': date.today(),
    })

def add_daily_work_lead(request, team_alloc_id, category_id):
    alloc = LeadCateogry_TeamAllocate.objects.select_related('lead_category').filter(id=team_alloc_id).first()
    if not alloc or alloc.lead_category.id != category_id:
        return redirect('tl_ongoing_works')

    work_assign = alloc.work_assign
    category = alloc.lead_category
    fields = LeadField_Register.objects.filter(lead_category=category).values_list('name', flat=True)

    # Determine active platforms
    platforms = []
    if work_assign:
        if work_assign.is_instagram:
            platforms.append('instagram')
        if work_assign.is_facebook:
            platforms.append('facebook')
        if work_assign.is_x:
            platforms.append('x')

    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            achieved = int(request.POST.get('achieved') or 0)
            file = request.FILES.get('file')

            # Save task details
            task_detail = TaskDetails.objects.create(
                is_category=True,
                category_assign=alloc,
                title=title,
                description=description,
                achieved_target=achieved,
                work_assign_id = alloc.work_assign_id,
                file=file,
            )

            # Save social media promotion only if any platform is enabled
            if work_assign.is_instagram or work_assign.is_facebook or work_assign.is_x:
                for p in platforms:
                    urls = request.POST.getlist(f'{p}_urls[]')
                    urls_str = ','.join([u.strip() for u in urls if u.strip()])
                    SocialMediaPromotion.objects.create(
                        task_detail=task_detail,
                        platform=p,
                        achieved_text=request.POST.get(f'{p}_achieved_text', '').strip(),
                        urls=urls_str,
                        screenshots=request.FILES.get(f'{p}_screenshot'),
                        remarks=request.POST.get(f'{p}_remarks', '').strip(),
                        work_assign=work_assign,
                        category_assign=alloc
                    )

            return redirect('tl_ongoing_works')

        except Exception as e:
            print(f"[ERROR] add_daily_work_lead: {e}")
            return JsonResponse({'error': 'Something went wrong while saving the data.'}, status=500)

    return render(request, 'teamlead/add_daily_work.html', {
        'mode': 'lead',
        'category_assign': alloc,
        'lead_category': category,
        'required_fields': fields,
        'is_platform': bool(platforms),
        'platforms': platforms,
        'lead_category_id': category_id,
        'today': date.today(),
    })
    
def tl_view_daily_work(request, task_assign_id):

    task = WorkAssign.objects.filter(id=task_assign_id).first()
    is_category = False

    if not task:
        task = LeadCateogry_TeamAllocate.objects.filter(id=task_assign_id).first()
        is_category = True if task else False
    if not task:
        messages.error(request, "Invalid Task Reference ID.")
        return redirect('tl_ongoing_works')
    if is_category:
        reports = TaskDetails.objects.filter(category_assign=task, is_category=True)
    else:
        reports = TaskDetails.objects.filter(work_assign=task, is_category=False)

    context = {
        'task': task,
        'reports': reports,
        'is_category': is_category,
    }

    return render(request, 'teamlead/tl_view_daily_work.html', context)

# completed page render
def tl_completed_works(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    all_data = []

    work_assigns = WorkAssign.objects.filter(team_lead=name, status=3).select_related('client')
    for assign in work_assigns:
        for task in assign.client_task.all():
            if task.task_name.strip().lower() != "lead collection":
                all_data.append({
                    'type': 'normal',
                    'task_name': task.task_name,
                    'start_date': assign.from_date,
                    'end_date': assign.due_date,
                    'assign_date': assign.assign_date,
                    'accept_date': assign.accept_date,
                    'client_name': assign.client.client_name if assign.client else '',
                    'task_description': assign.description or '',
                    'target': assign.target,
                    'achieved': assign.target_achieved,
                    'file_url': assign.file.url if assign.file else '',
                    'task_assign_id': assign.id,
                    'progress': assign.progress,
                })

    lead_records = LeadCateogry_TeamAllocate.objects.filter(team_lead=name, status=3).select_related('lead_category', 'work_assign__client')
    for record in lead_records:
        lead = record.lead_category
        assign = record.work_assign

        all_data.append({
            'type': 'lead_collection',
            'task_name': lead.collection_for or 'Lead Collection',
            'start_date': record.from_date,
            'end_date': record.due_date,
            'assign_date': assign.assign_date,
            'accept_date': record.accept_date,
            'client_name': assign.client.client_name if assign.client else '',
            'task_description': record.description or '',
            'target': record.target,
            'achieved': record.target_achieved,
            'file_url': record.file.url if record.file else '',
            'task_assign_id': record.id,
            'progress': record.progress,
        })

    context = {
        'completed_tasks': all_data
    }

    return render(request, 'teamlead/tl_completed_works.html', context)

def manage_leads_page(request, team_alloc_id, lead_category_id):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            team_lead = EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

    custom_fields_qs = LeadField_Register.objects.filter(lead_category_id=lead_category_id)
    field_names = list(custom_fields_qs.values_list('name', flat=True))
    leads_qs = Leads.objects.filter(lead_category_id=lead_category_id,collected_by=team_lead).order_by('-id')

    enriched_leads = []
    for lead in leads_qs:
        extra_fields = LeadDetails.objects.filter(lead=lead)
        field_map = {e.field_name: e.field_data for e in extra_fields}
        enriched_leads.append((lead, field_map))  # <-- Keep full dictionary for modal access

    duplicate_leads = request.session.pop("duplicate_leads", [])

    return render(request, 'teamlead/manage_leads.html', {
        'user':user,
        'name':name,
        'team_alloc_id': team_alloc_id,
        'lead_category_id': lead_category_id,
        'required_fields': field_names,
        'leads': enriched_leads,
        "duplicate_leads": duplicate_leads,
    })






def add_lead_manual(request):
    tid = request.session.get('tid')

    if not tid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=tid)
       
  
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        company = employee.company if employee else None 
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
                     
    if request.method == 'POST':
        try:
            team_alloc_id = request.POST.get('team_alloc_id')
            category_alloc = LeadCateogry_TeamAllocate.objects.filter(id=team_alloc_id).first()
            if not category_alloc:
                messages.error(request, "Invalid allocation ID.")
                return JsonResponse({'success': False})

            lead_category_fk = category_alloc.lead_category
            field_register = LeadField_Register.objects.filter(lead_category_id=lead_category_fk).first()
            work_fk = field_register.work if field_register else None

            employee_fk = employee

            email = request.POST.get('email', '').strip().lower()
            contact = request.POST.get('contact_number', '').strip()
            course = (request.POST.get('course') or '').strip()
            if not course:
                return JsonResponse({'success': False, 'message': 'Course is required.'}, status=400)



            is_repeated = Leads.objects.filter(
                    Q(email=email) | Q(contact=contact)
                ).exists()


            force_save = request.POST.get("force_save") == "1"

            duplicate_leads = Leads.objects.filter(
                Q(email=email) | Q(contact=contact)
            )

            if duplicate_leads.exists() and not force_save:

                duplicate_data = []

                for lead in duplicate_leads:
                    duplicate_data.append({
                        "name": lead.name,
                        "email": lead.email,
                        "contact": lead.contact,
                        "source": lead.source,
                    })

                return JsonResponse({
                    "duplicate": True,
                    "leads": duplicate_data
                })

            lead = Leads.objects.create(
                name=request.POST.get('name'),
                email=email,
                contact=contact,
                source=None,
                lead_category=lead_category_fk,
                work=work_fk,
                collected_by=employee_fk,
                repeated_status=1 if is_repeated else 0
            )

            if course:
                LeadDetails.objects.create(
                    lead=lead,
                    field_name='Course',
                    field_data=course,
                )

            for key, value in request.POST.items():
                if key.startswith('dynamic_'):
                    field_name = key.replace('dynamic_', '').replace('_', ' ').title()
                    LeadDetails.objects.create(
                        lead=lead,
                        field_name=field_name,
                        field_data=value
                    )

            messages.success(request, "Lead added successfully.")
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"[ERROR] Failed to save lead manually: {e}")
            messages.error(request, "Something went wrong while adding the lead.")
            return JsonResponse({'success': False})

    return JsonResponse({'success': False})







def upload_leads_excel(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request.")
        return redirect('individual_work_main')

    login_user = LogRegister_Details.objects.get(log_username=request.session.get('tid'))
    employee_user = EmployeeRegister_Details.objects.get(login=login_user)
    team_alloc_id = request.POST.get('team_alloc_id')

    result = process_excel_upload(request, team_alloc_id, employee_user)

    if result["duplicate_leads"]:
        request.session["duplicate_leads"] = result["duplicate_leads"]
        request.session["pending_rows"] = result["pending_rows"]

    if 'error' in result:
        messages.error(request, result['error'])
    else:
        if result['skipped']:
            messages.warning(request, f"{len(result['skipped'])} row(s) skipped.")
            for msg in result['skipped'][:5]:
                messages.warning(request, msg)
            if len(result['skipped']) > 5:
                messages.warning(request, f"...and {len(result['skipped']) - 5} more.")

        if result['created_count'] > 0:
            messages.success(request, f"{result['created_count']} lead(s) uploaded.")

        elif result["duplicate_leads"]:
            pass

        elif not result['skipped']:
            messages.error(request, "No valid data found.")


    return redirect('manage_leads_page', team_alloc_id=team_alloc_id, lead_category_id=result["lead_category_id"])


def download_leads_excel(request, lead_category_id, team_alloc_id):
    leads = Leads.objects.filter(lead_category_id=lead_category_id)

    if not leads.exists():
        messages.error(request, "No leads found to download.")
        return redirect('manage_leads_page', team_alloc_id=team_alloc_id, lead_category_id=lead_category_id)

    data = []
    for lead in leads:
        row = {
            'Name': lead.name,
            'Email': lead.email,
            'Contact Number': lead.contact,
            'Lead Source': lead.source
        }
        # Add all dynamic fields
        for detail in LeadDetails.objects.filter(lead=lead):
            row[detail.field_name] = detail.field_data
        data.append(row)

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    assign = LeadCateogry_TeamAllocate.objects.filter(id=team_alloc_id).select_related('work_assign__client').first()
    client_name = assign.work_assign.client.client_name.replace(' ', '_') if assign and assign.work_assign.client else 'Client'
    assign_id = assign.work_assign.id if assign and assign.work_assign else team_alloc_id
    filename = f"{client_name}_{assign_id}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    df.to_excel(response, index=False)
    return response
    
# fetch data from db
@csrf_exempt
def tl_get_data_workassign(request):
    tl_id = request.GET.get('id')
    status = request.GET.get('status')

    print(f"[DEBUG] WorkAssign fetch for TL: {tl_id} with status: {status}")  #!========delete this line =============

    try:
        data = []
        records = WorkAssign.objects.filter(team_lead_id=tl_id, status=status).select_related('client', 'team_lead')
        for rec in records:
            for task in rec.client_task.all():
                if task.task_name.strip().lower() != 'lead collection':
                    data.append({
                        'type': 'normal',
                        'assign_id': rec.id,
                        'task_id': task.id,
                        'task_name': task.task_name,
                        'task_description': task.task_description,
                        'start_date': rec.from_date,
                        'end_date': rec.due_date,
                        'assign_date': rec.assign_date,
                        'accept_date': rec.accept_date,
                        'client_name': rec.client.client_name if rec.client else '',
                        'target': rec.target,
                        'file_url': rec.file.url if rec.file else '',
                    })
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print(f"[ERROR] tl_get_data_workassign failed: {e}")  #!========delete this line =============
        return JsonResponse({'success': False, 'message': str(e)})
    
@csrf_exempt
def tl_get_data_leadcateogry_teamallocate(request):
    tl_id = request.GET.get('id')
    status = request.GET.get('status')

    print(f"[DEBUG] LeadCateogry_TeamAllocate fetch for TL: {tl_id} with status: {status}")  #!========delete this line =============

    try:
        data = []
        records = LeadCateogry_TeamAllocate.objects.filter(team_lead_id=tl_id, status=status).select_related('lead_category', 'work_assign__client')
        for rec in records:
            lead = rec.lead_category
            data.append({
                'type': 'lead_collection',
                'assign_id': rec.work_assign.id,
                'category_id': lead.id,
                'task_name': 'Lead Collection',
                'task_description': lead.description,
                'start_date': rec.from_date,
                'end_date': rec.due_date,
                'assign_date': rec.work_assign.assign_date,
                'accept_date': rec.work_assign.accept_date,
                'client_name': rec.work_assign.client.client_name if rec.work_assign.client else '',
                'target': rec.target,
                'file_url': rec.file.url if rec.file else '',
                'team_alloc_id': rec.id,
            })
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print(f"[ERROR] tl_get_data_leadcateogry_teamallocate failed: {e}")  #!========delete this line =============
        return JsonResponse({'success': False, 'message': str(e)})

def get_lead_details(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        extras = LeadDetails.objects.filter(lead=lead)

        extra_fields = [
            {"field_name": e.field_name, "field_data": e.field_data}
            for e in extras
        ]

        return JsonResponse({
            "success": True,
            "lead": {
                "name": lead.name,
                "email": lead.email,
                "contact": lead.contact,
                "verified": lead.status == 1,
                "waste": lead.waste_data == 1,
                "incomplete": lead.incomplete_status == 1
            },
            "details": extra_fields
        })

    except Leads.DoesNotExist:
        return JsonResponse({"success": False, "message": "Lead not found."}, status=404)
        
def teamlead_employeeschedule(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    emp = AllocationDetails.objects.filter(team_lead=name).select_related('employee')

    
    return render(request, 'teamlead/teamlead_employeeschedule.html', {
        'user': user,
        'company': company,
        'name':name,
        'employee':emp
    })

def tl_employee_schedule(request):
    aid = request.session.get('tid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    emp = AllocationDetails.objects.filter(team_lead=name).select_related('employee')

    if request.method == 'POST':
        emp_id = request.POST.get('employee')
        date = request.POST.get('schedule_date')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        head = request.POST.get('schedule_head')
        content = request.POST.get('todo_content')

        try:
            employee = EmployeeRegister_Details.objects.get(id=emp_id)
            EmployeeSchedule.objects.create(
                employee=employee,
                schedule_date=date,
                start_time=start,
                end_time=end,
                schedule_head=head,
                todo_content=content
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'teamlead/teamlead_employeeschedule.html', {
        'user': user,
        'company': company,
        'name': name,
        'employee': emp
    })

@require_POST
def teamlead_employee_schedule_list(request):
    aid = request.session.get('tid')
    if not aid:
        return JsonResponse({'success': False, 'message': 'Not logged in'}, status=401)

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

    emp_allocations = AllocationDetails.objects.filter(team_lead=name).select_related('employee')
    employee_ids = [alloc.employee.id for alloc in emp_allocations if alloc.employee]

    # POST data
    employee_filter = request.POST.get('employee_filter')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    schedules = EmployeeSchedule.objects.filter(employee__id__in=employee_ids)

    if employee_filter:
        schedules = schedules.filter(employee__id=employee_filter)

    if start_date and end_date:
        schedules = schedules.filter(schedule_date__range=[start_date, end_date])

    schedule_list = []
    for schedule in schedules:
        formatted_date = schedule.schedule_date.strftime('%B %d %Y')
        schedule_list.append({
            'id': schedule.id,
            'employee_id': schedule.employee.id,
            'employee_name': schedule.employee.name,
            'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
            'formatted_date': formatted_date,
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'start_time_formatted': schedule.start_time.strftime('%I:%M %p'),
            'end_time_formatted': schedule.end_time.strftime('%I:%M %p'),
            'schedule_head': schedule.schedule_head,
            'todo_content': schedule.todo_content,
            'schedule_status': getattr(schedule, 'schedule_status', 'pending')
        })

    return JsonResponse({'success': True, 'schedules': schedule_list})

@require_POST
def teamlead_employee_edit_schedule(request):
    schedule_id = request.POST.get('schedule_id')
        
    try:
        schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
        
        # Update schedule fields
        schedule.employee_id = request.POST.get('employee')
        schedule.schedule_date = request.POST.get('schedule_date')
        schedule.start_time = request.POST.get('start_time')
        schedule.end_time = request.POST.get('end_time')
        schedule.schedule_head = request.POST.get('schedule_head')
        schedule.todo_content = request.POST.get('todo_content')
        schedule.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def teamlead_employee_delete_schedule(request, schedule_id):
    try:
        schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
        schedule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def get_current_day_schedules_teamlead(request):
    aid = request.session.get('tid')
    if not aid:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        team_lead = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'User not found'})

    today = date.today()

    employees = AllocationDetails.objects.filter(team_lead=team_lead).select_related('employee')
    employee_ids = [e.employee.id for e in employees if e.employee]

    schedules = EmployeeSchedule.objects.filter(
        employee__id__in=employee_ids,
        schedule_date=today
    ).order_by('start_time')

    schedules_data = [{
        'id': s.id,
        'employee_id': s.employee.id,
        'employee_name': s.employee.name,
        'schedule_date': s.schedule_date.strftime("%Y-%m-%d"),
        'formatted_date': s.schedule_date.strftime('%B %d %Y'),
        'start_time': s.start_time.strftime("%H:%M") if s.start_time else "",
        'end_time': s.end_time.strftime("%H:%M") if s.end_time else "",
        'start_time_formatted': s.start_time.strftime("%I:%M %p") if s.start_time else "",
        'end_time_formatted': s.end_time.strftime("%I:%M %p") if s.end_time else "",
        'schedule_head': s.schedule_head,
        'todo_content': s.todo_content,
        'schedule_status': getattr(s, 'schedule_status', 'pending')
    } for s in schedules]

    return JsonResponse({'status': 'success', 'schedules': schedules_data})

@require_POST
def teamlead_empschedule_status(request):
    aid = request.session.get('tid')
    if not aid:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        team_lead = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'User not found'})

    try:
        schedule_id = request.POST.get('schedule_id')
        status = request.POST.get('status')
        
        if not schedule_id or not status:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            })
        
        # Get the schedule
        schedule = get_object_or_404(EmployeeSchedule, id=schedule_id)
        
        # Verify this schedule belongs to one of the team lead's employees
        if not AllocationDetails.objects.filter(
            team_lead=team_lead,
            employee=schedule.employee
        ).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Permission denied'
            })
            
        # Update the status
        schedule.schedule_status = status
        schedule.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Schedule status updated to {status}'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
    
# ////////////////////// teamlead - Leave ///////////////////////////////////////

def teamlead_leave(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login') 

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    emp = AllocationDetails.objects.filter(team_lead=name).select_related('employee')

    
    return render(request, 'teamlead/teamlead_leave.html', {
        'user': user,
        'company': company,
        'name':name,
        'employee':emp
    })

@require_POST
def teamlead_employee_leave_data(request):
    """
    AJAX view to fetch and filter employee leave data
    """
    try:
        # Get filter parameters
        employee_id = request.POST.get('employee_id', '')
        from_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
        
        # Start with all leave records
        leave_records = EmployeeLeave.objects.all()
        
        # Apply filters if they exist
        if employee_id:
            leave_records = leave_records.filter(employee_id=employee_id)
        
        # Date filtering
        if from_date:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            leave_records = leave_records.filter(
                Q(start_date__gte=from_date_obj) | Q(end_date__gte=from_date_obj)
            )
            
        if to_date:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            leave_records = leave_records.filter(
                Q(start_date__lte=to_date_obj) | Q(end_date__lte=to_date_obj)
            )
        
        # Convert queryset to list of dictionaries
        result = []
        for record in leave_records:
            result.append({
                'id': record.id,
                'employee_name': record.employee.name if record.employee else 'Unknown',
                'start_date': record.start_date.strftime('%Y-%m-%d') if record.start_date else '',
                'end_date': record.end_date.strftime('%Y-%m-%d') if record.end_date else '',
                'leave_type': record.leave_type or '',
                'reason': record.reason or '',
                'number_of_days': record.number_of_days,
                'status': record.status,
                'applied_date': record.applied_date.strftime('%Y-%m-%d') if record.applied_date else '',
            })
        
        return JsonResponse(result, safe=False)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in fetch_employee_leave_data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def teamlead_apply_leave(request):
    if request.method == 'POST':
        try:
            tid = request.session.get('tid')
            if not tid:
                return JsonResponse({'error': 'Session expired. Please log in again.'}, status=401)

            log_user = LogRegister_Details.objects.get(log_username=tid)
            employee = EmployeeRegister_Details.objects.get(login=log_user)
        except EmployeeRegister_Details.DoesNotExist:
            return JsonResponse({'error': 'Employee not found.'}, status=404)
        except LogRegister_Details.DoesNotExist:
            return JsonResponse({'error': 'User session invalid.'}, status=404)

        # Validate required fields
        required_fields = ['start_date', 'end_date', 'leave_type', 'reason']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({'error': f'{field.replace("_", " ").capitalize()} is required'}, status=400)

        try:
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            leave_type = request.POST['leave_type']
            reason = request.POST['reason']
            request_file = request.FILES.get('request_file')

            # Dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start > end:
                return JsonResponse({'error': 'End date must be after start date'}, status=400)

            # Number of leave days
            days = 1 if leave_type.lower() == 'half day' else (end - start).days + 1

            # Save
            EmployeeLeave.objects.create(
                employee=employee,
                start_date=start,
                end_date=end,
                leave_type=leave_type,
                reason=reason,
                number_of_days=days,
                request_file=request_file
            )

            return JsonResponse({'message': 'Leave request submitted successfully.'})

        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        except Exception as e:
            print("Exception:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def teamlead_view_leaves(request):
    if request.method == 'POST':
        try:
            tid = request.session.get('tid')
            if not tid:
                return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'}, status=401)

            log_user = LogRegister_Details.objects.get(log_username=tid)
            employee = EmployeeRegister_Details.objects.get(login=log_user)

            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')

            leaves = EmployeeLeave.objects.filter(employee=employee)

            if from_date:
                leaves = leaves.filter(start_date__gte=from_date)
            if to_date:
                leaves = leaves.filter(end_date__lte=to_date)

            leave_list = [{
                'id': leave.id,
                'start_date': leave.start_date.strftime('%Y-%m-%d'),
                'end_date': leave.end_date.strftime('%Y-%m-%d'),
                'leave_type': leave.leave_type,
                'reason': leave.reason,
                'status': leave.status.capitalize(),
            } for leave in leaves.order_by('-start_date')]

            return JsonResponse({'status': 'success', 'leaves': leave_list})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

#/////////////////////////////////////////// teamlead - Myschedule ////////////////////////////////////

def teamlead_myschedule(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login') 

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
    return render(request, 'teamlead/teamlead_myschedule.html', {
        'user': user,
        'company': company,
        'name':name
    })

@csrf_exempt
@require_POST
def teamlead_myschedule_add(request):
    print("Session data:", dict(request.session))
    log_user_id = request.session.get('tid')  # use 'aid' or 'tid' based on real context
    print("User ID from session:", log_user_id)

    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    print("Received POST data:", request.POST)

    required_fields = ['schedule_date', 'start_time', 'end_time', 'schedule_head']
    missing_fields = [field for field in required_fields if not request.POST.get(field)]

    if missing_fields:
        return JsonResponse({
            'status': 'error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }, status=400)

    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)  # use correct field
        employee = EmployeeRegister_Details.objects.get(login=log_user)

        schedule = EmployeeSchedule.objects.create(
            employee=employee,
            schedule_date=request.POST.get('schedule_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            schedule_head=request.POST.get('schedule_head'),
            todo_content=request.POST.get('todo_content', '')
        )

        return JsonResponse({'status': 'success', 'message': 'Schedule added successfully.'})

    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employee not found.'}, status=404)

    except LogRegister_Details.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Login session invalid.'}, status=404)

    except Exception as e:
        print(f"Error adding schedule: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt  
@require_POST
def get_teamlead_schedules(request):
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)

        # Date filter
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        schedules = EmployeeSchedule.objects.filter(employee=employee)

        if start_date and end_date:
            schedules = schedules.filter(schedule_date__range=[start_date, end_date])

        schedules = schedules.order_by('-schedule_date')

        schedule_data = [
            {
                 'id': s.id,
                'employee_name': employee.name,
                'schedule_head': s.schedule_head,
                'schedule_date': s.schedule_date.strftime('%Y-%m-%d'),
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'schedule_status': s.schedule_status,
                'todo_content': s.todo_content,
            }
            for s in schedules
        ]

        return JsonResponse({'status': 'success', 'schedules': schedule_data})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@require_POST
@csrf_protect
def get_teamleadschedule_details(request):
    schedule_id = request.POST.get('schedule_id')
    if not schedule_id:
        return JsonResponse({'status': 'error', 'message': 'Missing schedule_id'}, status=400)

    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)
        schedule = EmployeeSchedule.objects.get(id=schedule_id, employee=employee)

        schedule_data = {
            'id': schedule.id,
            'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'schedule_head': schedule.schedule_head,
            'todo_content': schedule.todo_content,
            'schedule_status': schedule.schedule_status,
        }

        return JsonResponse({'status': 'success', 'schedule': schedule_data})

    except EmployeeSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def update_teamlead_myschedule(request):
    """
    Update an existing schedule.
    """
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)
        
        schedule_id = request.POST.get('schedule_id')
        if not schedule_id:
            return JsonResponse({'status': 'error', 'message': 'Schedule ID required'}, status=400)
        
        # Get the schedule and verify it belongs to the user
        schedule = EmployeeSchedule.objects.get(id=schedule_id, employee=employee)
        
        # Update schedule fields
        if request.POST.get('schedule_date'):
            schedule.schedule_date = request.POST.get('schedule_date')
        
        if request.POST.get('start_time'):
            schedule.start_time = request.POST.get('start_time')
        
        if request.POST.get('end_time'):
            schedule.end_time = request.POST.get('end_time')
        
        if request.POST.get('schedule_head'):
            schedule.schedule_head = request.POST.get('schedule_head')
        
        if 'todo_content' in request.POST:
            schedule.todo_content = request.POST.get('todo_content')
        
        schedule.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Schedule updated successfully'
        })
    
    except EmployeeSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found'}, status=404)
    
    except Exception as e:
        print(f"Error updating schedule: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def delete_teamlead_myschedule(request):
    """
    Delete an existing schedule.
    """
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)
        
        schedule_id = request.POST.get('schedule_id')
        if not schedule_id:
            return JsonResponse({'status': 'error', 'message': 'Schedule ID required'}, status=400)
        
        # Get the schedule and verify it belongs to the user
        schedule = EmployeeSchedule.objects.get(id=schedule_id, employee=employee)
        
        # Delete the schedule
        schedule.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Schedule deleted successfully'
        })
    
    except EmployeeSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found'}, status=404)
    
    except Exception as e:
        print(f"Error deleting schedule: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def teamlead_myschedule_status(request):
    """
    Update the status of an existing schedule (pending/completed).
    """
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    try:
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)
        
        schedule_id = request.POST.get('schedule_id')
        new_status = request.POST.get('status')
        
        if not schedule_id:
            return JsonResponse({'status': 'error', 'message': 'Schedule ID required'}, status=400)
        
        if new_status not in ['pending', 'completed']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'}, status=400)
        
        # Get the schedule and verify it belongs to the user
        schedule = EmployeeSchedule.objects.get(id=schedule_id, employee=employee)
        
        # Update the status
        schedule.schedule_status = new_status
        schedule.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Schedule status updated to {new_status}'
        })
    
    except EmployeeSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found'}, status=404)
    
    except Exception as e:
        print(f"Error updating schedule status: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@csrf_protect
def get_teamlead_currentday_schedules(request):
    """
    Get the current day's schedules for the logged-in team lead
    """
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        import datetime
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        employee = EmployeeRegister_Details.objects.get(login=log_user)

        today = datetime.date.today()
        
        schedules = EmployeeSchedule.objects.filter(
            employee=employee,
            schedule_date=today
        ).order_by('start_time')

        schedule_data = [
            {
                'id': s.id,
                'employee_name': employee.name,
                'schedule_head': s.schedule_head,
                'schedule_date': s.schedule_date.strftime('%Y-%m-%d'),
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'schedule_status': s.schedule_status,
                'todo_content': s.todo_content,
            }
            for s in schedules
        ]

        return JsonResponse({
            'status': 'success', 
            'schedules': schedule_data
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# /////////////////////////////// teamlead - Messages (complaints and feedback) /////////////////////

def teamlead_complaints(request):
    aid = request.session.get('tid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    # Get all employees under this team lead
    emp_allocations = AllocationDetails.objects.filter(team_lead=name).select_related('employee')
    employees = [allocation.employee for allocation in emp_allocations]

    # Get all complaints for these employees
    complaints = Complaint.objects.filter(employee__in=employees)

    return render(request, 'teamlead/teamlead_complaint.html', {
        'user': user,
        'company': company,
        'name': name,
        'employee': emp_allocations,
        'complaints': complaints,
    })

def teamlead_submit_complaint_action(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        action_text = request.POST.get('action_text')

        try:
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.action = action_text
            complaint.action_date = timezone.now().date()
            complaint.save()
            return JsonResponse({'status': 'success'})
        except Complaint.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Complaint not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_POST
def teamlead_view_complaints(request):
    log_user_id = request.session.get('tid')
    if not log_user_id:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        # Find the team lead's login object using their username
        log_user = LogRegister_Details.objects.get(log_username=log_user_id)
        # Then find the EmployeeRegister_Details linked to that login
        team_lead = EmployeeRegister_Details.objects.get(login=log_user)

        # Get all employees allocated to this team lead
        employee_ids = AllocationDetails.objects.filter(
            team_lead=team_lead, allocate_status=1
        ).values_list('employee_id', flat=True)

        # Filter complaints by those employees
        complaints = Complaint.objects.filter(employee_id__in=employee_ids).order_by('-complaint_date')

        # Build JSON response
        complaint_list = []
        for comp in complaints:
            time_diff = (now().date() - comp.complaint_date).days
            time_ago = "Today" if time_diff == 0 else f"{time_diff}d ago"

            # Only check if action exists
            if comp.action:
                action_html = f'<span > {comp.action}</span>'
            else:
                action_html = '<span><i class="fas fa-exclamation-circle"></i> No Action Taken</span>'

            complaint_list.append({
                "date": comp.complaint_date.strftime("%b %d, %Y"),
                "head": comp.compaint_head or "No Title",
                "content": comp.compaint_content or "No details provided.",
                "action_html": action_html,
                "time_ago": time_ago
            })
        return JsonResponse({"status": "success", "complaints": complaint_list}, status=200)

    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Team Lead not found'}, status=404)

def teamlead_feedback(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    # Get distinct employee objects under this team lead
    employees = EmployeeRegister_Details.objects.filter(
        id__in=AllocationDetails.objects.filter(team_lead=name)
        .values_list('employee', flat=True)
        .distinct()
    )

    return render(request, 'teamlead/teamlead_feedback.html', {
        'user': user,
        'company': company,
        'name': name,
        'employee': employees
    })

def teamlead_add_feedback(request):
    if request.method == 'POST':
        try:
            aid = request.session.get('tid')
            if not aid:
                return JsonResponse({'success': False, 'error': 'Not logged in'})
            
            # Fetch user and sender
            user = LogRegister_Details.objects.get(log_username=aid)
            sender = EmployeeRegister_Details.objects.filter(login=user).first()
            
            if not sender:
                return JsonResponse({'success': False, 'error': 'Employee not found for user'})
            
            # Parse form data
            employee_id = request.POST.get('employee_id')
            feedback_text = request.POST.get('feedback_details')
            
            # Debug logging
            # print(f"DEBUG - employee_id received: '{employee_id}'")
            # print(f"DEBUG - feedback_text received: '{feedback_text}'")
            # print(f"DEBUG - All POST data: {request.POST}")
            
            if not employee_id or not employee_id.isdigit():
                return JsonResponse({'success': False, 'error': 'Invalid employee ID'})
            
            receiver = EmployeeRegister_Details.objects.filter(id=int(employee_id)).first()
            if not receiver:
                return JsonResponse({'success': False, 'error': 'Receiver not found'})
            
            # Create feedback
            feedback = Feedback.objects.create(
                employee=receiver,
                from_id=sender.id,
                from_name=sender.name,
                feedback_content=feedback_text,
                feedback_date=date.today()
            )
            
            print(f"DEBUG - Created feedback with ID: {feedback.id}")
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            import traceback
            print("Submit Feedback ERROR:\n", traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@require_POST
@csrf_protect  
def teamlead_view_feedback(request):
    aid = request.session.get('tid')
    if not aid:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        team_lead = EmployeeRegister_Details.objects.get(login=user)
    except (LogRegister_Details.DoesNotExist, EmployeeRegister_Details.DoesNotExist):
        return JsonResponse({'error': 'Team Lead not found.'}, status=404)
    
    # Parse JSON data from request body
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    print('Selected Employee ID:', employee_id)
    
    # Get employees allocated to this Team Lead
    allocated_employee_ids = AllocationDetails.objects.filter(
        team_lead=team_lead,
        allocate_status=1
    ).values_list('employee_id', flat=True)
    
    feedback_qs = Feedback.objects.filter(employee__id__in=allocated_employee_ids)
    
    if employee_id and employee_id != '':
        feedback_qs = feedback_qs.filter(employee_id=employee_id)
    if from_date and from_date != '':
        feedback_qs = feedback_qs.filter(feedback_date__gte=datetime.strptime(from_date, '%Y-%m-%d').date())
    if to_date and to_date != '':
        feedback_qs = feedback_qs.filter(feedback_date__lte=datetime.strptime(to_date, '%Y-%m-%d').date())
    
    feedback_data = [{
        'date': fb.feedback_date.strftime('%Y-%m-%d'),
        'employee': fb.employee.name,
        'feedback': fb.feedback_content
    } for fb in feedback_qs.order_by('-feedback_date')]
    
    return JsonResponse({'feedbacks': feedback_data})

# ////////////////////////////// teamlead - Action Taken /////////////////////////////////////

def teamlead_actiontaken(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login') 

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    employees = EmployeeRegister_Details.objects.filter(
        id__in=AllocationDetails.objects.filter(team_lead=name)
        .values_list('employee', flat=True)
        .distinct()
    )


    return render(request, 'teamlead/teamlead_actiontaken.html', {
        'user': user,
        'company': company,
        'name':name,
        'employee':employees
    })

def teamlead_submit_action(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        action_head = request.POST.get('action_head')
        action_reason = request.POST.get('action_reason')
        action_detail = request.POST.get('action_detail')
        action_date = request.POST.get('action_date')  # should be in 'YYYY-MM-DD' format

        tl_username = request.session.get('tid')  # assuming TL ID is stored in session as 'tid'
        if not tl_username:
            return JsonResponse({'success': False, 'error': 'Session expired or not logged in'})

        try:
            from_user = EmployeeRegister_Details.objects.get(login__log_username=tl_username)
        except EmployeeRegister_Details.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid team lead'})

        try:
            employee = EmployeeRegister_Details.objects.get(id=employee_id)
        except EmployeeRegister_Details.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid employee selected'})

        action = ActionTaken.objects.create(
            employee=employee,
            from_id=from_user.id,
            from_name=from_user.name,
            act_head=action_head,
            act_reason=action_reason,
            act_content=action_detail,
            action_date=datetime.strptime(action_date, '%Y-%m-%d').date() if action_date else None,
            status='pending'
        )

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@require_POST
@csrf_protect
def teamlead_view_actions(request):
    tl_id = request.session.get('tid')  # Team Lead session ID
    try:
        tl = EmployeeRegister_Details.objects.get(login__log_username=tl_id)
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({"actions": []})

    actions = ActionTaken.objects.filter(from_id=tl.id).order_by('-action_date')
    
    action_list = []
    for act in actions:
        action_list.append({
            "id": act.id,  # Added action ID for editing
            "date": act.action_date.strftime('%Y-%m-%d') if act.action_date else "",
            "head": act.act_head or "No Title",
            "reason": act.act_reason or "",
            "content": act.act_content or "",
            "status": act.status,
            "time_ago": timesince(act.action_date) + " ago" if act.action_date else "",
            "from_name": act.from_name or "Unknown",
            "employee_name": act.employee.name if act.employee and act.employee.name else "Unknown",
            "employee_id": act.employee.id if act.employee else None  # Added employee ID for editing
        })

    return JsonResponse({"actions": action_list})

@require_POST  # Ensures only POST requests are accepted
@csrf_protect  # Enforces CSRF protection
def teamlead_received_actions(request):
    email = request.session.get('tid')
    if not email:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    tl_login = LogRegister_Details.objects.filter(log_username=email).first()
    if not tl_login:
        return JsonResponse({"error": "Invalid user"}, status=400)

    try:
        tl_employee = EmployeeRegister_Details.objects.get(login=tl_login)
    except EmployeeRegister_Details.DoesNotExist:
        return JsonResponse({"error": "Team Lead employee record not found"}, status=400)

    actions = ActionTaken.objects.filter(employee=tl_employee).select_related('employee').order_by('-action_date')

    data = [
        {
            "date": action.action_date.strftime("%Y-%m-%d") if action.action_date else "N/A",
            "action_type": action.act_head or "No Title",
            "act_reason": action.act_reason,
            "act_content": action.act_content,
            "from_name": action.from_name,
            "status": action.get_status_display() if hasattr(action, 'get_status_display') else action.status,
            "employee_name": action.employee.name if action.employee else "N/A",
        }
        for action in actions
    ]

    return JsonResponse({"actions": data}, status=200)

@csrf_exempt
def teamlead_edit_action(request):
    if request.method == 'POST':
        action_id = request.POST.get('action_id')
        employee_id = request.POST.get('employee_id')
        action_head = request.POST.get('action_head')
        action_reason = request.POST.get('action_reason')
        action_detail = request.POST.get('action_detail')
        action_date = request.POST.get('action_date')

        tl_username = request.session.get('tid')
        if not tl_username:
            return JsonResponse({'success': False, 'error': 'Session expired or not logged in'})

        try:
            from_user = EmployeeRegister_Details.objects.get(login__log_username=tl_username)
        except EmployeeRegister_Details.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid team lead'})

        try:
            # Get the action to edit and verify it belongs to the current team lead
            action = ActionTaken.objects.get(id=action_id, from_id=from_user.id)
        except ActionTaken.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Action not found or not authorized'})

        try:
            employee = EmployeeRegister_Details.objects.get(id=employee_id)
        except EmployeeRegister_Details.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid employee selected'})

        # Update the action
        action.employee = employee
        action.act_head = action_head
        action.act_reason = action_reason
        action.act_content = action_detail
        action.action_date = datetime.strptime(action_date, '%Y-%m-%d').date() if action_date else None
        action.save()

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def tl_work_allocate_view(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
    assigned_work = WorkAssign.objects.filter(
       team_lead=name,
        assign_type=1
    ).select_related('client', 'team_lead').prefetch_related('client_task')

    allocation = AllocationDetails.objects.filter(team_lead=name).order_by('-id')
    context = {
        'user': user,
        'name':name,
        'company': company,
        'assigned_work':assigned_work,
        'allocation':allocation
    }
    return render(request,'teamlead/tl_work_allocate_view.html',context)

def tl_assign_task_employee(request, work_id):
    if request.method == 'POST':
        work = get_object_or_404(WorkAssign, id=work_id)

        employee_id = request.POST['employee_id']
        task_id = request.POST['task']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        target = request.POST['target']
        description = request.POST['description']
        category = request.POST.get('category') 
        file = request.FILES.get('work_file')
        
        instagram_target = request.POST.get('instagram_target', 0)
        facebook_target = request.POST.get('facebook_target', 0)
        x_target = request.POST.get('x_target', 0)
        #  Check if this task is already assigned to the employee for this work
        already_assigned = TaskAssign.objects.filter(
            work_assign=work,
            executive_id=employee_id,
            client_task_id=task_id
        ).exists()

        if already_assigned:
            messages.warning(request, "This task has already been assigned to the this employee.")
            return redirect('tl_work_allocate_view')

        
        task_assign = TaskAssign.objects.create(
            work_assign=work,
            executive_id=employee_id,
            client_task_id=task_id,
            start_date=start_date,
            due_date=end_date,
            target=target,
            description=description,
            allocate_date=start_date,
            file=file,
            status=0
        )

        if work.is_instagram and instagram_target:
            work.instagram_target = instagram_target
        if work.is_facebook and facebook_target:
            work.facebook_target = facebook_target
        if work.is_x and x_target:
            work.x_target = x_target

        work.co_workers.add(employee_id)
        work.save()
  

        if category:
            team_allocation = LeadCateogry_TeamAllocate.objects.filter(
                work_assign=work,
            ).first()
            LeadCategory_Assign.objects.create(
                from_date=start_date,
                due_date=end_date,
                target=target,
                executive_id=employee_id,
                task_assign=task_assign,
                team_allocation=team_allocation,
                status=0
            )

        messages.success(request, 'Task assigned successfully!')
        return redirect('tl_work_allocate_view')

def tl_pending_works_view(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            team_lead = EmployeeRegister_Details.objects.filter(login=user).first()
            company = team_lead.company
        except (LogRegister_Details.DoesNotExist, AttributeError):
            user = None
            company = None
            team_lead = None
            
    if team_lead:
        
        allocated_employees = AllocationDetails.objects.filter(
            team_lead=team_lead,
            allocate_status=1  
        ).values_list('employee', flat=True)
        
        
        pending_work = TaskAssign.objects.filter(
            status=0,accept_status=1,
            executive__in=allocated_employees
        ).select_related(
            'work_assign__client', 
            'executive', 
            'client_task'
        ).prefetch_related(
            'client_task__leadcategory_register_set'  
        )
    else:
        pending_work = []
      
    context = {
        'user': user,
        'name': team_lead,
        'company': company,
        'pending_work': pending_work,
    }
    return render(request, 'teamlead/tl_pending_works_view.html', context)

def tl_remove_task(request, work_id):
    if request.method == 'POST':
        task = get_object_or_404(TaskAssign, id=work_id)
        LeadCategory_Assign.objects.filter(task_assign=task).delete()
        task.delete()
        return redirect('tl_pending_works_view')  
    return redirect('tl_pending_works_view')

def tl_work_progress(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            name=EmployeeRegister_Details.objects.filter(login=user).first()
            team_lead = EmployeeRegister_Details.objects.filter(login=user).first()
            company = name.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None
    
    if team_lead:
        
        allocated_employees = AllocationDetails.objects.filter(
            team_lead=team_lead
        ).values_list('employee', flat=True)
        
        
        assigned_work = TaskAssign.objects.filter(
            executive__in=allocated_employees
        ).select_related(
            'work_assign__client', 
            'executive', 
            'client_task',
            'work_assign',
        ).prefetch_related(
            'client_task__leadcategory_register_set'  
        )
    else:
        assigned_work = []
      

    context = {
        'user': user,
        'name':name,
        'company': company,
        'assigned_work':assigned_work,
    }
    return render(request,'teamlead/tl_work_progress.html',context)

def tl_completed_work(request):
    username = request.session.get('tid','')
    if not username:
        return redirect('login')
    else:
        try:
            user = LogRegister_Details.objects.filter(log_username=username).first()
            team_lead = EmployeeRegister_Details.objects.filter(login=user).first()
            company = team_lead.company
        except (LogRegister_Details.DoesNotExist, AttributeError):
            user = None
            company = None
            team_lead = None
            
    if team_lead:
        # Get all employees allocated to this team lead
        allocated_employees = AllocationDetails.objects.filter(
            team_lead=team_lead
        ).values_list('employee', flat=True)
        
        
        completed_work = TaskAssign.objects.filter(
            status=2,
            executive__in=allocated_employees
        ).select_related(
            'work_assign__client', 
            'executive', 
            'executive__login',  
            'executive__company',  
            'client_task'
        ).prefetch_related(
            'client_task__leadcategory_register_set'  
        )
    else:
        completed_work = []
      
    context = {
        'user': user,
        'name': team_lead,
        'company': company,
        'completed_work': completed_work,
    }
    return render(request,'teamlead/tl_completed_work.html',context)

# ======================================================== teamlead ================================================================

def exe_work(request):
    session_login_id = request.session.get('eid')
    
    user = LogRegister_Details.objects.get(log_username=session_login_id)
    employee = EmployeeRegister_Details.objects.get(login=user)
    name = employee  
    return render(request,'executive/exe_work.html',{'name':name})

def weekly_pro(request):
    if request.method == 'POST':
        progress_type = request.POST.get('progressType')
        session_login_id = request.session.get('eid')
        user = LogRegister_Details.objects.get(log_username=session_login_id)
        employee = EmployeeRegister_Details.objects.get(login=user)
        try:
            progress = WorkProgress.objects.create(
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date'),
                progress=request.POST.get('progress'),
                description=request.POST.get('description'),
                progress_type=progress_type,
                employee=employee
                
            )

            uploaded_files_info = []
            files = request.FILES.getlist('files')  

            for file in files:
                save_path = os.path.join('weekly_prog', file.name)
                full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                uploaded_files_info.append({
                    'name': file.name,
                    'url': settings.MEDIA_URL + save_path,
                    'type': file.content_type,
                })

            progress.files = json.dumps(uploaded_files_info)
            progress.save()

            
            return redirect('weekly_pro')

        except Exception as e:
           
            return redirect('weekly_pro')

    session_login_id = request.session.get('eid')
    
    user = LogRegister_Details.objects.get(log_username=session_login_id)
    employee = EmployeeRegister_Details.objects.get(login=user)
    name = employee  
    progresses = WorkProgress.objects.filter(progress_type='weekly', employee=employee)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")

    # Decode file JSON for rendering in template
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []
    
    return render(request, 'executive/weekly_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })

def monthly_pro(request):
    if request.method == 'POST':
        progress_type = request.POST.get('progressType')
        session_login_id = request.session.get('eid')
        user = LogRegister_Details.objects.get(log_username=session_login_id)
        employee = EmployeeRegister_Details.objects.get(login=user)
        try:
            progress = WorkProgress.objects.create(
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date'),
                progress=request.POST.get('progress'),
                description=request.POST.get('description'),
                progress_type=progress_type,
                employee=employee
            )

            uploaded_files_info = []
            files = request.FILES.getlist('files')  

            for file in files:
                save_path = os.path.join('monthly_pro', file.name)
                full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                uploaded_files_info.append({
                    'name': file.name,
                    'url': settings.MEDIA_URL + save_path,
                    'type': file.content_type,
                })

            progress.files = json.dumps(uploaded_files_info)
            progress.save()

            
            return redirect('monthly_pro')

        except Exception as e:
           
            return redirect('monthly_pro')

    session_login_id = request.session.get('eid')
    
    user = LogRegister_Details.objects.get(log_username=session_login_id)
    employee = EmployeeRegister_Details.objects.get(login=user)
    name = employee  
    progresses = WorkProgress.objects.filter(progress_type='monthly', employee=employee)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")

    # Decode file JSON for rendering in template
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []
    
    return render(request, 'executive/monthly_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'name':name
    })

def tl_progress(request):
    aid = request.session.get('tid')
    user = LogRegister_Details.objects.get(log_username=aid)
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    return render(request,'teamlead/tl_progress.html',{'name':name})

def tl_week_pro(request):
    if request.method == 'POST':
        progress_type = request.POST.get('progressType')
        aid = request.session.get('tid')
        user = LogRegister_Details.objects.get(log_username=aid)
        team_lead = EmployeeRegister_Details.objects.filter(login=user).first()

        try:
            progress = WorkProgress.objects.create(
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date'),
                progress=request.POST.get('progress'),
                description=request.POST.get('description'),
                progress_type=progress_type,
                employee=team_lead
            )

            uploaded_files_info = []
            files = request.FILES.getlist('files')

            for file in files:
                save_path = os.path.join('tl_week_pro', file.name)
                full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                uploaded_files_info.append({
                    'name': file.name,
                    'url': settings.MEDIA_URL + save_path,
                    'type': file.content_type,
                })

            progress.files = json.dumps(uploaded_files_info)
            progress.save()

            return redirect('tl_week_pro')

        except Exception as e:
            return redirect('tl_week_pro')

    aid = request.session.get('tid')
    user = LogRegister_Details.objects.get(log_username=aid)
    team_lead = EmployeeRegister_Details.objects.filter(login=user).first()

    # Get employees allocated to this TL
    allocated_employees_ids = AllocationDetails.objects.filter(team_lead=team_lead).values_list('employee', flat=True)
    allocated_employees = EmployeeRegister_Details.objects.filter(id__in=allocated_employees_ids)

  
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    employee_id = request.GET.get('employee_id')

 
    progresses = WorkProgress.objects.filter(progress_type='weekly', employee_id__in=allocated_employees_ids)

    if employee_id:
        progresses = progresses.filter(employee_id=employee_id)

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")

    # Load file info
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []

    return render(request, 'teamlead/tl_week_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'selected_employee_id': employee_id,
        'employees': allocated_employees,
        'name': team_lead,
    })

def verify_progress(request, progress_id):
    if request.method == 'POST':
        new_progress = request.POST.get('progress')
        try:
            progress_obj = get_object_or_404(WorkProgress, id=progress_id)
            progress_obj.progress = new_progress
            progress_obj.status = 1  # Mark as verified
            progress_obj.save()
            return redirect('tl_week_pro')
        except Exception as e:
            return redirect('tl_week_pro')

def tl_mon_pro(request):
    if request.method == 'POST':
        progress_type = request.POST.get('progressType')
        aid = request.session.get('tid')
        user = LogRegister_Details.objects.get(log_username=aid)
        team_lead = EmployeeRegister_Details.objects.filter(login=user).first()

        try:
            progress = WorkProgress.objects.create(
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date'),
                progress=request.POST.get('progress'),
                description=request.POST.get('description'),
                progress_type=progress_type,
                employee=team_lead
            )

            uploaded_files_info = []
            files = request.FILES.getlist('files')

            for file in files:
                save_path = os.path.join('tl_mon_pro', file.name)
                full_path = os.path.join(settings.MEDIA_ROOT, save_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                uploaded_files_info.append({
                    'name': file.name,
                    'url': settings.MEDIA_URL + save_path,
                    'type': file.content_type,
                })

            progress.files = json.dumps(uploaded_files_info)
            progress.save()

            return redirect('tl_mon_pro')

        except Exception as e:
            return redirect('tl_mon_pro')

    aid = request.session.get('tid')
    user = LogRegister_Details.objects.get(log_username=aid)
    team_lead = EmployeeRegister_Details.objects.filter(login=user).first()

    # Get employees allocated to this TL
    allocated_employees_ids = AllocationDetails.objects.filter(team_lead=team_lead).values_list('employee', flat=True)
    allocated_employees = EmployeeRegister_Details.objects.filter(id__in=allocated_employees_ids)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    employee_id = request.GET.get('employee_id')
    progresses = WorkProgress.objects.filter(progress_type='monthly', employee_id__in=allocated_employees_ids)

    if employee_id:
        progresses = progresses.filter(employee_id=employee_id)

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")

    # Load file info
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []

    return render(request, 'teamlead/tl_mon_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'selected_employee_id': employee_id,
        'employees': allocated_employees,
        'name': team_lead,
    })

def verify_mon_progress(request, progress_id):
    if request.method == 'POST':
        new_progress = request.POST.get('progress')
        try:
            progress_obj = get_object_or_404(WorkProgress, id=progress_id)
            progress_obj.progress = new_progress
            progress_obj.status = 1  # Mark as verified
            progress_obj.save()
            return redirect('tl_mon_pro')
        except Exception as e:
            return redirect('tl_mon_pro')
    
def dm_week_pro(request):
    hid = request.session.get('hid')
    user = LogRegister_Details.objects.get(log_username=hid)
    head = EmployeeRegister_Details.objects.filter(login=user).first()

    if not head:
        return render(request, 'dmhead/dm_week_pro.html', {})

    # Get all Team Leads under this Head by company and designation
    team_leads = EmployeeRegister_Details.objects.filter(
        company=head.company,
        designation__name='Team_Lead',
       
    )

    # Get IDs of these team leads
    tl_ids = team_leads.values_list('id', flat=True)

    # Get all Executives allocated to those TLs from AllocationDetails
    executive_ids = AllocationDetails.objects.filter(team_lead_id__in=tl_ids).values_list('employee', flat=True)

    # Combine TLs + Executives IDs
    all_employee_ids = list(tl_ids) + list(executive_ids)

    # Filter input from GET params
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    employee_id = request.GET.get('employee_id')

    # Query WorkProgress for weekly progress of those employees
    progresses = WorkProgress.objects.filter(progress_type='weekly', employee_id__in=all_employee_ids)

    if employee_id:
        progresses = progresses.filter(employee_id=employee_id)

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")

    # Parse file list JSON for each progress
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []

    # Employees for dropdown
    employee_list = EmployeeRegister_Details.objects.filter(id__in=all_employee_ids)

    return render(request, 'dmhead/dm_week_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'selected_employee_id': employee_id,
        'employees': employee_list,
        'name': head,
    })

def dm_week_progress(request, progress_id):
    if request.method == 'POST':
        new_progress = request.POST.get('progress')
        try:
            progress_obj = get_object_or_404(WorkProgress, id=progress_id)
            progress_obj.progress = new_progress
            progress_obj.status = 1  # Mark as verified
            progress_obj.save()
            return redirect('dm_week_pro')
        except Exception as e:
            return redirect('dm_week_pro')
        
def update_work_progress(request):
    if request.method == 'POST':
        progress_id = request.POST.get('progress_id')
        progress_value = request.POST.get('progress_value')

        if progress_id and progress_value is not None:
            work_progress = get_object_or_404(WorkProgress, id=progress_id)
            work_progress.progress = int(progress_value)
            work_progress.save()

    return redirect('dm_week_pro') 
    
def dm_mon_pro(request):
    hid = request.session.get('hid')
    user = LogRegister_Details.objects.get(log_username=hid)
    head = EmployeeRegister_Details.objects.filter(login=user).first()

    if not head:
        return render(request, 'dmhead/dm_mon_pro.html', {})

    team_leads = EmployeeRegister_Details.objects.filter(
        company=head.company,
        designation__name='Team_Lead',
       
    )
    tl_ids = team_leads.values_list('id', flat=True)

    executive_ids = AllocationDetails.objects.filter(team_lead_id__in=tl_ids).values_list('employee', flat=True)
    all_employee_ids = list(tl_ids) + list(executive_ids)
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    employee_id = request.GET.get('employee_id')
    progresses = WorkProgress.objects.filter(progress_type='monthly', employee_id__in=all_employee_ids)

    if employee_id:
        progresses = progresses.filter(employee_id=employee_id)

    if from_date and to_date:
        try:
            progresses = progresses.filter(from_date__gte=from_date, to_date__lte=to_date)
        except ValueError:
            messages.error(request, "Invalid date format.")
    for progress in progresses:
        try:
            progress.file_list = json.loads(progress.files)
        except Exception:
            progress.file_list = []
    employee_list = EmployeeRegister_Details.objects.filter(id__in=all_employee_ids)

    return render(request, 'dmhead/dm_mon_pro.html', {
        'progresses': progresses,
        'from_date': from_date,
        'to_date': to_date,
        'selected_employee_id': employee_id,
        'employees': employee_list,
        'name': head,
    })

def dm_mon_progress(request, progress_id):
    if request.method == 'POST':
        new_progress = request.POST.get('progress')
        try:
            progress_obj = get_object_or_404(WorkProgress, id=progress_id)
            progress_obj.progress = new_progress
            progress_obj.status = 1 
            progress_obj.save()
            return redirect('dm_mon_pro')
        except Exception as e:
            return redirect('dm_mon_pro')
        
def update_mon_progress(request):
    if request.method == 'POST':
        progress_id = request.POST.get('progress_id')
        progress_value = request.POST.get('progress_value')

        if progress_id and progress_value is not None:
            work_progress = get_object_or_404(WorkProgress, id=progress_id)
            work_progress.progress = int(progress_value)
            work_progress.save()

    return redirect('dm_mon_pro') 

def get_leaves_json(request):
    user_id = request.session.get('hid')
    user = LogRegister_Details.objects.get(log_username=user_id)
    employee = EmployeeRegister_Details.objects.get(login=user)
    leaves = EmployeeLeave.objects.filter(employee=employee)

    leave_data = []
    for leave in leaves:
        leave_data.append({
            'status': leave.status,
            'start_date': leave.start_date.strftime('%Y-%m-%d'),
            'end_date': leave.end_date.strftime('%Y-%m-%d'),
            'leave_type': leave.leave_type,
            'reason': leave.reason,
            'status_changed_date': leave.status_changed_date.strftime('%Y-%m-%d') if leave.status_changed_date else '',
            'request_file_url': leave.request_file.url if leave.request_file else '',  # <<--- Important
        })

    return JsonResponse({'leaves': leave_data})
    
# ======================================================== Data Manager ================================================================

def _data_bank_manager(request):
    login_name = request.session.get('did')
    if not login_name:
        return None, None
    login_user = (
        LogRegister_Details.objects.filter(log_username=login_name, position='Data_Manager').first()
        or LogRegister_Details.objects.filter(log_username=login_name).first()
    )
    employee = EmployeeRegister_Details.objects.filter(login=login_user).select_related('company').first() if login_user else None
    if not employee or not employee.company:
        return None, None
    return employee, employee.company


@require_GET
def data_bank_leads_api(request):
    from django.core.paginator import Paginator
    from django.db.models import Exists, OuterRef
    from django.utils.dateparse import parse_date
    from .serializers import LeadsSerializer

    manager, company = _data_bank_manager(request)
    if not manager:
        return JsonResponse({'success': False, 'message': 'Please log in as a Data Manager.'}, status=403)

    leads = Leads.objects.filter(collected_by__company=company).select_related(
        'work__client', 'collected_by', 'task_assign', 'lead_category__client_task__client'
    ).prefetch_related('leaddetails_set').annotate(
        is_confused=Exists(LeadConfused.objects.filter(lead_id=OuterRef('pk'))),
        interview_email_sent=Exists(LeadConfused.objects.filter(lead_id=OuterRef('pk'), interview_email_sent=True))
    ).order_by('-added_date', '-added_time', '-id')

    client_id = request.GET.get('client')
    category_id = request.GET.get('category')
    executive_id = request.GET.get('hr')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status', '').strip()
    search = request.GET.get('search', '').strip()

    if client_id:
        leads = leads.filter(
            Q(lead_category__client_task__client_id=client_id) | Q(work__client_id=client_id)
        )
    if category_id:
        leads = leads.filter(lead_category_id=category_id)
    if executive_id:
        leads = leads.filter(collected_by_id=executive_id)
    if date_from:
        parsed = parse_date(date_from)
        if parsed:
            leads = leads.filter(added_date__gte=parsed)
    if date_to:
        parsed = parse_date(date_to)
        if parsed:
            leads = leads.filter(added_date__lte=parsed)
    if status:
        if status.lstrip('-').isdigit():
            leads = leads.filter(status=int(status))
        else:
            leads = leads.filter(databank__lead_status__iexact=status)
    if search:
        leads = leads.filter(
            Q(name__icontains=search) | Q(email__icontains=search) | Q(contact__icontains=search)
        )

    try:
        page_size = int(request.GET.get('page_size', 25))
    except (TypeError, ValueError):
        page_size = 25
    page_size = min(max(page_size, 1), 100)
    paginator = Paginator(leads.distinct(), page_size)
    page = paginator.get_page(request.GET.get('page', 1))
    return JsonResponse({
        'count': paginator.count,
        'page': page.number,
        'page_size': page_size,
        'num_pages': paginator.num_pages,
        'results': LeadsSerializer(page.object_list, many=True).data,
    })


@require_POST
def send_lead_interview(request, pk):
    from datetime import timedelta
    from django.core.exceptions import ValidationError
    from django.core.mail import EmailMultiAlternatives
    from django.db import transaction
    from django.utils.html import escape
    from django.utils import timezone
    import logging
    import smtplib
    import socket
    from .utils import (
        get_lead_missing_interview_questions,
        make_interview_link,
        resolve_lead_work_id,
        get_lead_work_fields,
    )
    from .validators import (
        is_valid_email,
        is_valid_phone,
        normalize_phone_e164,
        mask_email,
        mask_phone,
    )
    from .sms import get_sms_backend

    manager, company = _data_bank_manager(request)
    if not manager:
        return JsonResponse({'success': False, 'message': 'Please log in as a Data Manager.'}, status=403)

    lead = Leads.objects.filter(
        pk=pk, collected_by__company=company
    ).select_related('collected_by', 'work__client', 'lead_category__client_task__work').first()
    if not lead:
        return JsonResponse({'success': False, 'message': 'Lead not found.'}, status=404)

    # 1. Confused check
    if not LeadConfused.objects.filter(lead=lead).exists():
        return JsonResponse({'success': False, 'message': 'This lead is not marked as confused.'}, status=400)

    # 2. Completed check
    if LeadDetails.objects.filter(lead=lead, field_name='AI Interview Status', field_data='Completed').exists():
        return JsonResponse({'success': False, 'message': 'The interview is already completed.'}, status=409)

    # 3. Channel determination
    has_email = is_valid_email(lead.email)
    has_phone = is_valid_phone(lead.contact)

    if not has_email and not has_phone:
        return JsonResponse({'success': False, 'message': 'This lead does not have a valid email or phone number.'}, status=400)
    elif has_phone and not has_email:
        channel = 'sms'
    elif has_email and not has_phone:
        channel = 'email'
    else:
        channel = getattr(settings, 'INTERVIEW_PREFERRED_CHANNEL', 'email').lower()

    # 4. Check missing interview questions
    missing_questions = get_lead_missing_interview_questions(lead)
    if not missing_questions:
        return JsonResponse({
            'success': False,
            'message': 'All fields are already filled, there is nothing to ask',
        }, status=422)

    # 5. API key check
    if settings.INTERVIEW_LINK_SIGN and not settings.AI_HR_API_KEY:
        return JsonResponse({
            'success': False,
            'message': 'AI_HR_API_KEY is not configured. Set AI_HR_API_KEY in .env before sending interview links.',
        }, status=503)

    link, payload = make_interview_link(lead)

    logger = logging.getLogger(__name__)

    def recently_sent():
        from datetime import datetime
        last_sent = LeadDetails.objects.filter(
            lead=lead, field_name='Interview Link Sent'
        ).order_by('-id').first()
        if not last_sent or not last_sent.field_data:
            return False
        try:
            raw = last_sent.field_data.strip()
            iso_str = raw.split(':', 1)[1] if raw.startswith(('sms:', 'email:')) else raw
            sent_at = datetime.fromisoformat(iso_str)
            if timezone.is_naive(sent_at):
                sent_at = timezone.make_aware(sent_at, timezone.get_current_timezone())
            return timezone.now() - sent_at < timedelta(minutes=10)
        except (TypeError, ValueError):
            return False

    if recently_sent():
        return JsonResponse({'success': False, 'message': 'An interview link was sent within the last 10 minutes.'}, status=409)

    with transaction.atomic():
        Leads.objects.select_for_update().filter(pk=lead.pk).first()
        if recently_sent():
            return JsonResponse({'success': False, 'message': 'An interview link was sent within the last 10 minutes.'}, status=409)

        if channel == 'sms':
            try:
                norm_phone = normalize_phone_e164(lead.contact)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot normalise phone number for sending: invalid phone format.',
                    'channel': 'sms',
                }, status=400)

            candidate_name = (lead.name or '').strip() or 'Candidate'
            sms_text = f"Hello {candidate_name}, please complete your interview: {link}"
            backend = get_sms_backend()
            sent_success, send_info = backend.send_sms(norm_phone, sms_text)
            if not sent_success:
                return JsonResponse({
                    'success': False,
                    'message': f'Failed to send SMS: {send_info}',
                    'channel': 'sms',
                }, status=502)
            masked_dest = mask_phone(norm_phone)
            success_msg = f'SMS sent to {masked_dest}'

        else:  # email
            subject = 'Interview Invitation'
            candidate_name = lead.name or ''
            body = f'Hello {candidate_name},\n\nConduct your interview by clicking the link below:\n{link}'
            html_body = (
                f'<p>Hello {escape(candidate_name)},</p>'
                f'<p>Conduct your interview by clicking <a href="{escape(link)}">this link</a>.</p>'
            )
            email = EmailMultiAlternatives(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [lead.email],
            )
            email.attach_alternative(html_body, 'text/html')
            try:
                sent_count = email.send(fail_silently=False)
            except Exception as exc:
                logger.exception(
                    'Interview invitation email failed for lead_id=%s', lead.pk
                )
                if isinstance(exc, socket.gaierror):
                    error_message = 'Could not resolve the Gmail SMTP server. Check DNS and network access to smtp.gmail.com.'
                elif isinstance(exc, smtplib.SMTPAuthenticationError):
                    error_message = 'Gmail rejected the SMTP credentials. Check the sender address and Google App Password.'
                elif isinstance(exc, smtplib.SMTPServerDisconnected):
                    error_message = 'Gmail closed the SMTP session during login. Check the Gmail sender address, Google App Password, and account SMTP access.'
                elif isinstance(exc, (OSError, TimeoutError)):
                    error_message = 'Could not connect to the Gmail SMTP server. Check network access to smtp.gmail.com:587.'
                else:
                    error_message = 'The email provider failed to send the interview invitation.'
                return JsonResponse({'success': False, 'message': error_message, 'channel': 'email'}, status=502)
            if not sent_count:
                return JsonResponse({'success': False, 'message': 'The interview email could not be sent.', 'channel': 'email'}, status=500)

            masked_dest = mask_email(lead.email)
            success_msg = f'Email sent to {masked_dest}'

        # Record link sent with channel and timestamp
        LeadDetails.objects.create(
            lead=lead,
            field_name='Interview Link Sent',
            field_data=f"{channel}:{timezone.now().isoformat()}",
        )
        LeadConfused.objects.filter(lead=lead).update(interview_email_sent=True)

    return JsonResponse({'success': True, 'message': success_msg, 'channel': channel})

from rest_framework.response import Response
from rest_framework.views import APIView
from django.core import signing
from .utils import get_lead_work_fields, read_interview_token, resolve_lead_work_id


class InterviewAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def authenticate_api_key(self, request):
        expected = settings.AI_HR_API_KEY
        supplied = request.headers.get('X-API-Key', '')
        if not expected or not supplied or not hmac.compare_digest(expected, supplied):
            return Response({'error': 'Unauthorized'}, status=401)
        return None

    def get_interview_lead(self, request, reject_completed=True, token=None):
        token = token or request.headers.get('X-Interview-Token', '') or request.query_params.get('token', '')
        if not isinstance(token, str) or not token:
            return None, Response({'error': 'Invalid link'}, status=400)
        try:
            payload = read_interview_token(token)
        except signing.SignatureExpired:
            return None, Response({'error': 'Link expired'}, status=410)
        except signing.BadSignature:
            return None, Response({'error': 'Invalid link'}, status=400)
        try:
            if not isinstance(payload, dict):
                raise Leads.DoesNotExist
            lead = Leads.objects.get(pk=payload.get('lead'))
        except (Leads.DoesNotExist, TypeError, ValueError):
            return None, Response({'error': 'Lead not found'}, status=404)
        if reject_completed and LeadDetails.objects.filter(lead=lead, field_name='AI Interview Status', field_data='Completed').exists():
            return None, Response({'error': 'Interview already completed'}, status=409)
        return lead, None


class InterviewSessionAPIView(InterviewAPIView):
    def get(self, request):
        unauthorized = self.authenticate_api_key(request)
        if unauthorized:
            return unauthorized
        lead, error = self.get_interview_lead(request)
        if error:
            return error
        from .utils import get_lead_missing_interview_questions
        questions = get_lead_missing_interview_questions(lead)
        if not questions:
            logging.getLogger(__name__).warning(
                'No interview questions are mapped or needed for lead_id=%s', lead.pk
            )
        return Response({
            'candidate': {'name': lead.name or ''},
            'questions': questions,
        })


class InterviewAnswerAPIView(InterviewAPIView):
    def post(self, request):
        unauthorized = self.authenticate_api_key(request)
        if unauthorized:
            return unauthorized
        lead, error = self.get_interview_lead(request, token=request.data.get('token'))
        if error:
            return error

        # Accept either {"answers": [...]} or single answer payload {"question_id": ..., "answer": ...}
        raw_answers = request.data.get('answers')
        if raw_answers is None and 'question_id' in request.data:
            answers = [request.data]
        elif isinstance(raw_answers, list):
            answers = raw_answers
        else:
            return Response({'error': 'answers must be a list'}, status=400)

        from .utils import COURSE_QUESTION_ID, LEAD_SOURCE_QUESTION_ID
        from .validators import is_valid_email, is_valid_phone, normalize_phone_e164
        from django.db import transaction

        work_fields = list(get_lead_work_fields(lead).order_by('id'))
        mapped_fields = {
            field.question_id: field
            for field in work_fields
            if field.question_id is not None
        }
        fields_by_id = {field.pk: field for field in work_fields}
        fields_by_name = {
            (field.name or '').strip().lower(): field
            for field in work_fields
            if field.name
        }

        lead_updated_fields = set()

        with transaction.atomic():
            for item in answers:
                if not isinstance(item, dict):
                    return Response({'error': 'Each answer must include question_id and answer'}, status=400)

                answer_val = item.get('answer')
                if not isinstance(answer_val, str) or not answer_val.strip():
                    return Response({'error': 'Answer must be a non-empty string'}, status=400)
                clean_answer = answer_val.strip()[:855]

                if 'question_id' in item:
                    question_id = item.get('question_id')
                    if isinstance(question_id, bool) or not isinstance(question_id, int) or question_id not in QUESTION_BY_ID:
                        return Response({'error': f'Unknown question id: {question_id}'}, status=400)

                    # Handle default fields: 1, 2, 3, COURSE_QUESTION_ID
                    if question_id == 1:
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name='Full Name',
                            defaults={'field_data': clean_answer},
                        )
                        if not lead.name or not lead.name.strip():
                            lead.name = clean_answer
                            lead_updated_fields.add('name')

                    elif question_id == 2:
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name='Email',
                            defaults={'field_data': clean_answer},
                        )
                        if (not lead.email or not lead.email.strip()) and is_valid_email(clean_answer):
                            lead.email = clean_answer
                            lead_updated_fields.add('email')

                    elif question_id == 3:
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name='Contact Number',
                            defaults={'field_data': clean_answer},
                        )
                        if not lead.contact or not lead.contact.strip():
                            try:
                                lead.contact = normalize_phone_e164(clean_answer)
                                lead_updated_fields.add('contact')
                            except ValueError:
                                pass

                    elif question_id == COURSE_QUESTION_ID:
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name='Course',
                            defaults={'field_data': clean_answer},
                        )
                        # Also check if there is a custom field mapped to COURSE_QUESTION_ID
                        field = mapped_fields.get(question_id)
                        if field and (field.name or '').strip().lower() != 'course':
                            LeadDetails.objects.update_or_create(
                                lead=lead,
                                field_name=field.name,
                                defaults={'field_data': clean_answer},
                            )

                    elif question_id == LEAD_SOURCE_QUESTION_ID:
                        field = mapped_fields.get(question_id)
                        target_field_name = field.name if field else 'Lead Source'
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name=target_field_name,
                            defaults={'field_data': clean_answer},
                        )
                        if not lead.source or not lead.source.strip():
                            lead.source = clean_answer[:255]
                            lead_updated_fields.add('source')
                        if field and (field.name or '').strip().lower() not in ('lead source', 'source', 'lead_source'):
                            LeadDetails.objects.update_or_create(
                                lead=lead,
                                field_name='Lead Source',
                                defaults={'field_data': clean_answer},
                            )

                    else:
                        field = mapped_fields.get(question_id)
                        if not field:
                            return Response({'error': f'Question id {question_id} is not mapped to this lead'}, status=400)
                        LeadDetails.objects.update_or_create(
                            lead=lead,
                            field_name=field.name,
                            defaults={'field_data': clean_answer},
                        )

                    # If custom field also happened to be mapped to 1, 2, or 3
                    if question_id in (1, 2, 3):
                        c_field = mapped_fields.get(question_id)
                        if c_field and (c_field.name or '').strip().lower() not in ('full name', 'email', 'contact number', 'phone'):
                            LeadDetails.objects.update_or_create(
                                lead=lead,
                                field_name=c_field.name,
                                defaults={'field_data': clean_answer},
                            )

                elif any(k in item for k in ('field_id', 'field', 'field_name')):
                    field = None
                    if 'field_id' in item:
                        try:
                            field = fields_by_id.get(int(item['field_id']))
                        except (TypeError, ValueError):
                            field = None
                    else:
                        legacy_name = item.get('field') or item.get('field_name')
                        if isinstance(legacy_name, str):
                            field = fields_by_name.get(legacy_name.strip().lower())
                    if not field:
                        return Response({'error': 'Field is not mapped to this lead'}, status=400)
                    LeadDetails.objects.update_or_create(
                        lead=lead,
                        field_name=field.name,
                        defaults={'field_data': clean_answer},
                    )
                else:
                    return Response({'error': 'Each answer must include question_id and answer'}, status=400)

            if lead_updated_fields:
                lead.save(update_fields=list(lead_updated_fields))

        return Response({'success': True})

class InterviewCompleteAPIView(InterviewAPIView):
    def post(self, request):
        unauthorized = self.authenticate_api_key(request)
        if unauthorized:
            return unauthorized
        lead, error = self.get_interview_lead(request, reject_completed=False)
        if error:
            return error
        LeadDetails.objects.update_or_create(
            lead=lead,
            field_name='AI Interview Status',
            defaults={'field_data': 'Completed'},
        )
        return Response({'success': True})


def data_bank_view(request):
    name, company = _data_bank_manager(request)
    if not name:
        return redirect('login')

    user = name.login
    clients = ClientRegister.objects.filter(company=company)
    categories = LeadCategory_Register.objects.filter(client_task__client__company=company)
    executive_ids = Leads.objects.filter(
        collected_by__company=company
    ).values_list('collected_by_id', flat=True).distinct()
    hrs = EmployeeRegister_Details.objects.filter(id__in=executive_ids).order_by('name')

    context = {
        'user':user,
        'name':name,
        'leads': [],
        'clients': clients,
        'categories': categories,
        'hrs': hrs
    }
    return render(request, 'datamanager/data_bank.html', context)

def allocation_leads_page(request):
    try:
        user = LogRegister_Details.objects.get(log_username=request.session.get('did'))
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        company = employee.company if employee else None
        if not company:
            raise Exception("No company found for user.")
    except Exception as e:
        print(f"Auth error: {e}")
        return redirect('/login')
    
    # databank_qs = DataBank.objects.select_related(
    #     'lead', 'lead_workclient', 'leadlead_category', 'lead_collected_by'
    # ).filter(lead_work_company=company)
    databank_qs = DataBank.objects.filter(lead__collected_by__company=company)
    google_leads = GoogleFormApplication.objects.filter(employee__company=company,transferred_status=0)

    assigned_map = {
        obj.databank_id: obj.telecaller_id
        for obj in LeadAssignedToTC.objects.select_related('databank', 'telecaller')
    }

    leads_list = []
    for i, row in enumerate(databank_qs, start=1):
        hr_id = str(assigned_map.get(row.id, ''))
        exec_id = str(row.lead.collected_by.id) if row.lead.collected_by else ''
        is_allocated = bool(hr_id)

        leads_list.append({
            'row': row,
            'hr_id': hr_id,
            'exec_id': exec_id,
            'is_allocated': is_allocated
        })

    for g in google_leads:
        leads_list.append({
            'row': {
                'id': g.id,
                'generated_date': g.created_at,
                'lead_status': 'Not Allocated',

           
                'lead': {
                    'id': g.id,
                    'name': g.name,
                    'email': g.email,
                    'contact': g.phone,
                    'added_date': g.created_at,
                    'collected_by': g.employee,
                },

             
                'lead_workclient': None,
                'leadlead_category': None,
            },

            'hr_id': '',
            'exec_id': str(g.employee.id) if g.employee else '',
            'is_allocated': False,
            'is_google_form': True,
        })

    status = request.GET.get('status', '').strip()
    hr = request.GET.get('hr', '').strip()

    clients = ClientRegister.objects.filter(company=company)

    # all_db_ids = DataBank.objects.filter(lead_work_company=company).values_list('id', flat=True)
    # hr_ids = LeadAssignedToTC.objects.filter(
    #     databank_id__in=all_db_ids
    # ).values_list('telecaller_id', flat=True).distinct()
    # hrs = EmployeeRegister_Details.objects.filter(id__in=hr_ids, designation_id=42)
    hrs = EmployeeRegister_Details.objects.filter(designation__dashboard_id='Telecaller',company=company)

    exec_ids = DataBank.objects.filter(
        lead__collected_by__company=company
    ).values_list('lead__collected_by_id', flat=True).distinct()
    executives = EmployeeRegister_Details.objects.filter(
        id__in=exec_ids,
        designation__dashboard_id__in=['Executive', 'Team_Lead','Digital_Marketing_Head']
    )

    categories = LeadCategory_Register.objects.filter(client_task__client__company=company)

    return render(request, 'datamanager/allocationleads.html', {
        'user':user,
        'name':employee,
        'leads': leads_list,
        'clients': clients,
        'hrs': hrs,
        'executives': executives,
        "categories": categories,
        # 'not_allocated': DataBank.objects.filter(
        #     lead_work_company=company,
        #     lead_status='Not Allocated'
        # ).count()
    })

def follow_up_view(request):

    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        name = None

    leads = LeadAssignedToTC.objects.select_related(
        'lead',
        'databank',
        'telecaller'
    ).filter(
        databank__lead_allocate_status=1 ,lead__collected_by__company=company
    )

    followup_statuses = FollowupStatus.objects.all()

    hrs = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id='Telecaller',company=company
    )

    for entry in leads:

        entry.normalized_followup = ''

        if entry.response:

            status = entry.response.strip()

            if status == 'No Data Availale':
                status = 'No Updation'

            elif status == 'Waste Lead':
                status = 'Marked as Waste'

            entry.normalized_followup = status.lower()

    return render(request, 'datamanager/followup.html', {
        'user':user,
        'name':name,
        'leads': leads,
        'hrs': hrs,
        'followup_statuses': followup_statuses
    })

def hr_telecallers_view(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

    employees = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id='Telecaller',company=company
    ).select_related('login', 'department', 'designation')

    return render(request, 'datamanager/hr_telecallers.html', {
        'name':employee,
        'employees': employees,     
        })

def data_executives_view(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

    employees = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id__in=['Executive', 'Team_Lead'], company=company
    ).select_related('login', 'department', 'designation')
    return render(request, 'datamanager/data_executives.html', {
        'name':employee,
        'employees': employees
        })


#* functions

def get_categories_for_client(request, client_id):
    from .models import LeadCategory_Register
    categories = LeadCategory_Register.objects.filter(client_task__client_id=client_id)
    data = [{'id': c.id, 'name': c.collection_for} for c in categories]
    return JsonResponse(data, safe=False)

def get_lead_details_dm(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        databank_entry = DataBank.objects.filter(lead=lead).first()
        client = lead.work.client if lead.work and lead.work.client else None
        extra_fields = LeadDetails.objects.filter(lead=lead)
        extra_data = [{"label": d.field_name, "value": d.field_data} for d in extra_fields]

        return JsonResponse({
            "lead": {
                "name": lead.name,
                "email": lead.email,
                "contact": lead.contact,
            },
            "client": {
                "name": client.client_name if client else "-",
                "info": client.client_business_name if client else "-"
            },
            "more_details": extra_data,
            "followups": [
                {
                    "collected_by": lead.collected_by.name if lead.collected_by else "Unknown"
                }
            ],
            "history": [
                {
                    "date": lead.added_date.strftime("%B %d, %Y") if lead.added_date else "-",
                    "time": lead.added_time.strftime("%I:%M %p") if lead.added_time else "-"
                }
            ]
        })

    except Leads.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)

@csrf_exempt
def allocate_leads(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        leads=data.get("leads",[])
        category_id=data.get("category")
        hr_id = data.get('hr_id')

        hr = EmployeeRegister_Details.objects.filter(id=hr_id).first()
        if not hr:
            return JsonResponse({"success": False, "message": "Invalid HR selected."})

        count = 0
        for item in leads:

            lead_id=item["id"]
            source=item["source"]

            if source=="databank":
                try:
                    lead = Leads.objects.get(id=lead_id)
                    databank = DataBank.objects.get(lead=lead)

                    LeadAssignedToTC.objects.create(
                        lead=lead,
                        databank=databank,
                        telecaller=hr,
                        client=lead.work.client if lead.work else None,
                        # allocated_date=date.today()
                    )

                    databank.lead_allocate_status = 1
                    databank.lead_status = "Allocated"
                    databank.allocated_date = date.today()
                    databank.save()
                    count += 1

                except (Leads.DoesNotExist, DataBank.DoesNotExist):
                    continue
            else:
                google = GoogleFormApplication.objects.get(id=lead_id)

                category = LeadCategory_Register.objects.get(id=category_id)

                lead = Leads.objects.create(
                    lead_category=category,
                    work=category.client_task.work,
                    collected_by=google.employee,
                    name=google.name,
                    email=google.email,
                    contact=google.phone,
                    source=google.source,
                    transfer_status=1
)

                details = {

                    "Qualification":google.qualification,
                    "Year of Passout":google.year_of_passout,
                    "Location":google.location,
                    "Applied For":google.applied_for,
                    "Internship":google.done_any_internship,
                    "Internship Start":google.internship_startdate,
                    "Internship End":google.internship_enddate,
                    "Experience":google.experience,

                }

                for field,value in details.items():

                    if value:

                        LeadDetails.objects.create(
                            lead=lead,
                            field_name=field,
                            field_data=value)
                    
                databank = DataBank.objects.create(
                lead=lead,
                lead_allocate_status=1,
                allocated_date=date.today(),
                lead_status="Allocated")

                LeadAssignedToTC.objects.create(
                lead=lead,
                databank=databank,
                telecaller=hr,
                client=category.client_task.client)

                google.transferred_status = 1
                google.save()

        return JsonResponse({
            "success": True,
            "message": f"{count} lead(s) allocated successfully."
        })

    return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def deallocate_followups(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])

        for lid in lead_ids:
            obj = LeadAssignedToTC.objects.filter(id=lid).first()
            if obj:
                if obj.databank:
                    obj.databank.lead_allocate_status = 0
                    obj.databank.lead_status = 'Not Allocated'
                    obj.allocated_date= 'null'
                    obj.databank.save()
                obj.delete()

        return JsonResponse({'success': True, 'message': f"{len(lead_ids)} leads deallocated."})
    return JsonResponse({'success': False})

@csrf_exempt
def add_followup_status(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        name = None

    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status', '').strip()
        if status:
    
            FollowupStatus.objects.create(status_name=status, company=company)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def get_followup_statuses(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        name = None

    statuses = FollowupStatus.objects.filter(company=company).values('id', 'status_name')
    return JsonResponse(list(statuses), safe=False)


@csrf_exempt
def delete_followup_status(request, status_id):
    FollowupStatus.objects.filter(id=status_id).delete()
    return JsonResponse({'success': True})

# ======================================================== Data Manager ================================================================

# ======================================================== telecaller ================================================================

def telecaller_all_leads(request):
    username = request.session.get('tcid')
    if not username:
        return redirect('login')

    login_user = LogRegister_Details.objects.filter(log_username=username).first()
    telecaller = EmployeeRegister_Details.objects.filter(login=login_user).first()

    all_allocs = LeadAssignedToTC.objects.filter(telecaller=telecaller).select_related(
        'lead', 'databank'
    ).order_by('-assign_date')

    context = {
        'leads': all_allocs,
        'name': telecaller,
        'lead_count': all_allocs.count()
    }

    return render(request, 'telecaller/all_leads.html', context)

def telecaller_followups_page(request):
    username = request.session.get('tcid')
    if not username:
        return redirect('login')

    telecaller = LogRegister_Details.objects.filter(log_username=username).first()
    emp = EmployeeRegister_Details.objects.filter(login=telecaller).first()
    company = emp.company
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)

    leads = LeadAssignedToTC.objects.filter(
        status=1 , lead__collected_by__company = company, telecaller=emp
    ).exclude(
        response__in=["Waste Lead", "Lead Closed"]
    )


    context = {
        "name": emp,
        "statuses": statuses,
        "leads": leads,
    }
    return render(request, 'telecaller/followup_leads.html', context)


def telecaller_waste_leads(request):
    if 'tcid' not in request.session:
        return redirect('login')

    login_user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
    employee = EmployeeRegister_Details.objects.get(login=login_user)

    waste_leads = WasteLead.objects.filter(telecaller=employee).select_related(
        'lead',
        'databank',
        'client'
    )

    context = {
        'name':employee,
        'leads': waste_leads
    }
    return render(request, 'telecaller/waste_leads.html', context)

def closed_leads_page(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company

    leads = LeadAssignedToTC.objects.filter(status=3,lead__collected_by__company=company).select_related(
        'lead', 'lead__work', 'lead__lead_category', 'telecaller', 
    ).order_by('-assign_date')

    return render(request, 'telecaller/closed_leads.html', {
        'leads': leads,
        'name': employee
    })

def telecaller_leads_report(request):
    username = request.session.get('tcid')
    if not username:
        return redirect('login')

    login_user = LogRegister_Details.objects.filter(log_username=username).first()
    telecaller = EmployeeRegister_Details.objects.filter(login=login_user).first()

    assigned_dates = LeadAssignedToTC.objects.filter(
        telecaller=telecaller
    ).values('assign_date').annotate(count=Count('id')).order_by('-assign_date')

    return render(request, 'telecaller/leads_report.html', {
        'assigned_dates': assigned_dates,
        'name': telecaller
    })

# * js calls
@csrf_exempt
def accept_leads(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('lead_ids', [])

        if not ids:
            return JsonResponse({'success': False, 'message': 'No leads selected'})

        updated = LeadAssignedToTC.objects.filter(id__in=ids).update(status=1)
        return JsonResponse({'success': True, 'updated': updated})

@csrf_exempt
def lead_data_collection_hr(request, lead_id):
    try:
        lead = Leads.objects.select_related('work__client', 'collected_by').get(id=lead_id)
        databank_entry = lead.databank_set.first()
        assigned_obj = LeadAssignedToTC.objects.filter(lead=lead).select_related('telecaller').first()

        client = lead.lead_category.client_task.client if lead.lead_category.client_task and lead.lead_category.client_task.client else None
        telecaller = assigned_obj.telecaller if assigned_obj else None
        collected_by = lead.collected_by
        databank = DataBank.objects.filter(lead=lead).select_related('lead__lead_category').first()
        category_name = databank.lead.lead_category.collection_for if databank and databank.lead and databank.lead.lead_category else "-"
        status = databank.lead_status if databank else "-"
        next_followup = assigned_obj.next_update_date if assigned_obj and assigned_obj.next_update_date else (databank.followup_date if databank and databank.followup_date else "-")

        extra_fields = LeadDetails.objects.filter(lead=lead)
        extra_data = [
            {"field_name": d.field_name, "field_data": d.field_data}
            for d in extra_fields
        ]

        return JsonResponse({
            "success": True,
            "lead": {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "contact": lead.contact,
                "added_date": lead.added_date.strftime("%Y-%m-%d") if lead.added_date else "-"
            },
            "client": {
                "name": client.client_name if client else "-",
                "business": client.client_business_name if client else "-",
            },
            "telecaller": {
                "id": telecaller.id if telecaller else "-",
                "name": telecaller.name if telecaller else "Unknown",
            },
            "collected_by": {
                "id": collected_by.id if collected_by else "-",
                "name": collected_by.name if collected_by else "Unknown"
            },
            "extra_fields": extra_data,
            "category": category_name,
            "current_status": status,
            "next_followup": next_followup.strftime("%Y-%m-%d") if isinstance(next_followup, date) else next_followup,
        })

    except Leads.DoesNotExist:
        return JsonResponse({"success": False, "message": "Lead not found"})

    except Exception as e:
        print("Error in lead_data_collection_hr:", e)
        return JsonResponse({"success": False, "message": str(e)})

@csrf_exempt
def get_leads_by_date(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        username = request.session.get('tcid')
        login_user = LogRegister_Details.objects.filter(log_username=username).first()
        telecaller = EmployeeRegister_Details.objects.filter(login=login_user).first()

        if date:
            leads = LeadAssignedToTC.objects.filter(
                telecaller=telecaller,
                assign_date=date
            ).select_related('lead')
        else:
            leads = LeadAssignedToTC.objects.filter(
                telecaller=telecaller
            ).select_related('lead')

        data = []
        for i, entry in enumerate(leads, start=1):
            lead = entry.lead
            databank = DataBank.objects.filter(lead=lead).first()
            data.append({
                'no': i,
                'id': lead.id,
                'assigned_date': entry.assign_date.strftime("%Y-%m-%d"),
                'name': lead.name,
                'email': lead.email,
                'contact': lead.contact,
                'status': databank.current_status if databank else 'N/A'
            })

        return JsonResponse({'success': True, 'leads': data})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def get_lead_details_hr(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        assignment = LeadAssignedToTC.objects.filter(lead=lead).first()
        client = assignment.client if assignment else None
        databank_entry = assignment.databank if assignment else None

        field_data = LeadDetails.objects.filter(lead=lead).values('field_name', 'field_data')
        history = FollowupHistory.objects.filter(lead=lead).values('allocated_date', 'note', 'final_status')
        followups = FollowupDetails.objects.filter(lead=lead).values('response', 'next_followup_date', 'response_status')
        recordings = LeadCallRecord.objects.filter(lead=lead).first()

        return JsonResponse({
            "success": True,
            "lead": {
                "name": lead.name,
                "email": lead.email,
                "contact": lead.contact
            },
            "client": {
                "name": client.client_name if client else "-",
                "info": client.client_business_name if client else "-"
            },
            "more_details": list(field_data),
            "history": [
                {
                    "date": str(h['allocated_date']),
                    "note": h['note'],
                    "status": h['final_status']
                }
                for h in history
            ],
            "followups": [
                {
                    "response": f["response"],
                    "date": str(f["next_followup_date"]),
                    "status": f["response_status"]
                }
                for f in followups
            ],
            "recording": recordings.record_file.url if recordings and recordings.record_file else None
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def submit_followup_update(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        response = request.POST.get('response')
        next_date = request.POST.get('next_followup')
        reason = request.POST.get('reason')
        file = request.FILES.get('call_recording')

        try:
            lead = Leads.objects.get(id=lead_id)
            user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company if employee else None

            followup = FollowupDetails.objects.create(
                lead=lead,
                company=company,
                telecaller=employee,
                response=reason,
                next_followup_date=next_date,
                response_status=response
            )

            assigned = LeadAssignedToTC.objects.filter(lead=lead, telecaller=employee).first()
            if assigned:
                assigned.response = response
                assigned.reason = reason
                assigned.update_date = date.today()
                assigned.next_update_date = next_date
                assigned.save()

            databank = DataBank.objects.filter(lead=lead).first()
            if databank:
                databank.followup_date = next_date
                databank.current_status = response
                databank.save()

            if file:
                LeadCallRecord.objects.create(
                    assignment=assigned,
                    lead=lead,
                    record_file=file
                )

            save_followup_history(
                lead=lead,
                company=company,
                telecaller=employee,
                status=response,
            )

            return JsonResponse({'success': True})
        except Exception as e:
            print("Error saving follow-up:", e)
            return JsonResponse({'success': False, 'message': str(e)})

def save_followup_history(lead, telecaller, company, status):
    try:
        assignment = LeadAssignedToTC.objects.filter(lead=lead, telecaller=telecaller).first()
        allocated_date = assignment.assign_date if assignment else None
        note = f"Lead status has been changed to {status}"

        FollowupHistory.objects.create(
            lead=lead,
            company=company,
            telecaller=telecaller,
            allocated_date=allocated_date,
            note=note,
            final_status=status
        )

    except Exception as e:
        print("Error saving followup history:", e)

def get_followup_data(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)

        details = FollowupDetails.objects.filter(lead=lead).order_by('-id')
        history = FollowupHistory.objects.filter(lead=lead).order_by('-id')
        recordings = LeadCallRecord.objects.filter(lead=lead).order_by('-id')

        lead_details = LeadDetails.objects.filter(lead=lead)

        more_details = {
            "source": lead.source,
            "fields": [
                {
                    "field_name": d.field_name,
                    "field_data": d.field_data
                }
                for d in lead_details
            ]
        }

        details_data = [{
            "date": str(d.response_date),
            "response": d.response,
            "next": str(d.next_followup_date) if d.next_followup_date else "-",
            "status": d.response_status,
            "telecaller": d.telecaller.name if d.telecaller else "-"
        } for d in details]

        history_data = [{
            "date": str(h.allocated_date),
            "note": h.note,
            "status": h.final_status,
            "telecaller": h.telecaller.name if h.telecaller else "-",
            "client": h.lead.name if h.lead else "-"
        } for h in history]

        recordings_data = [{
            "date": str(r.record_date),
            "url": r.record_file.url if r.record_file else ""
        } for r in recordings]

        return JsonResponse({
            "success": True,
            "details": details_data,
            "history": history_data,
            "recordings": recordings_data,
            "more_details": more_details,
        })
    except Exception as e:
        print("Error in get_followup_data:", str(e))
        return JsonResponse({"success": False, "message": str(e)})

#// 3 btns
@csrf_exempt
def update_lead_status(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('status')
        reason = request.POST.get('reason', '')

        try:
            lead = Leads.objects.get(id=lead_id)
            user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company if employee else None

            assigned = LeadAssignedToTC.objects.filter(lead=lead, telecaller=employee).first()
            if assigned:
                assigned.response = new_status
                assigned.reason = reason if new_status == "Waste Lead" else ""
                assigned.status = 2 if new_status == "Waste Lead" else 3   #*== leadassignedtotc.status == 2 : waste lead, 3 : Lead Closed
                assigned.update_date = date.today()
                assigned.save()

            databank = DataBank.objects.filter(lead=lead).first()
            if databank:
                databank.current_status = new_status
                databank.save()

            if new_status == "Waste Lead":
                WasteLead.objects.create(
                    reason=reason,
                    status=1,
                    assignment_id=assigned.id,
                    client_id=assigned.client_id,
                    databank_id=assigned.databank_id,
                    lead_id=assigned.lead_id,
                    telecaller_id=assigned.telecaller_id
                )

            FollowupHistory.objects.create(
                lead=lead,
                company=company,
                telecaller=employee,
                allocated_date=timezone.now(),
                note=f"Lead status has been changed to {new_status}",
                final_status=new_status
            )

            return JsonResponse({"success": True})

        except Exception as e:
            print("Status update error:", e)
            return JsonResponse({"success": False, "message": str(e)})
            
@csrf_exempt
def bulk_update_leads(request):
    if request.method == 'POST':
        try:
            lead_ids = json.loads(request.POST.get('lead_ids', '[]'))
            new_status = request.POST.get('status')
            reason = request.POST.get('reason', '')

            user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company if employee else None

            for lid in lead_ids:
                lead = Leads.objects.get(id=lid)
                assigned = LeadAssignedToTC.objects.filter(lead=lead, telecaller=employee).first()
                if assigned:
                    assigned.response = new_status
                    assigned.reason = reason if new_status == "Waste Lead" else ""
                    assigned.status = 2 if new_status == "Waste Lead" else 3
                    assigned.save()

                databank = DataBank.objects.filter(lead=lead).first()
                if databank:
                    databank.current_status = new_status
                    databank.save()

                if new_status == "Waste Lead":
                    WasteLead.objects.create(
                        reason=reason,
                        status=1,
                        assignment_id=assigned.id,
                        client_id=assigned.client_id,
                        databank_id=assigned.databank_id,
                        lead_id=assigned.lead_id,
                        telecaller_id=assigned.telecaller_id
                    )

                FollowupHistory.objects.create(
                    lead=lead,
                    company=company,
                    telecaller=employee,
                    allocated_date=timezone.now(),
                    note=f"Lead status has been changed to {new_status}",
                    final_status=new_status
                )

            return JsonResponse({'success': True})
        except Exception as e:
            print("Bulk status update error:", e)
            return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def recall_lead(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
        employee = EmployeeRegister_Details.objects.filter(login=user).first()

        assigned = LeadAssignedToTC.objects.filter(lead=lead, telecaller=employee).first()
        if assigned:
            assigned.status = 1
            assigned.response = "Recalled"
            assigned.reason = ""
            assigned.save()

        WasteLead.objects.filter(lead_id=lead.id, telecaller_id=employee.id).delete()

        databank = DataBank.objects.filter(lead=lead).first()
        if databank:
            databank.current_status = "Recalled"
            databank.save()

        FollowupHistory.objects.create(
            lead=lead,
            company=employee.company,
            telecaller=employee,
            allocated_date=timezone.now(),
            note="Lead was recalled.",
            final_status="Recalled"
        )

        return JsonResponse({"success": True})
    except Exception as e:
        print("Recall failed:", e)
        return JsonResponse({"success": False, "message": str(e)})

@csrf_exempt
def get_all_leads_for_telecaller(request):
    username = request.session.get('tcid')

    if not username:
        return JsonResponse({'success': False, 'message': 'Not logged in'})

    login_user = LogRegister_Details.objects.filter(log_username=username).first()
    telecaller = EmployeeRegister_Details.objects.filter(login=login_user).first()

    all_assignments = LeadAssignedToTC.objects.filter(
        telecaller=telecaller
    ).select_related('lead', 'databank').order_by('-assign_date')

    results = []
    for i, entry in enumerate(all_assignments, 1):
        lead = entry.lead
        databank = entry.databank  # now directly from select_related

        results.append({
            'no': i,
            'id': lead.id,
            'assigned_date': entry.assign_date.strftime('%Y-%m-%d'),
            'name': lead.name,
            'email': lead.email,
            'contact': lead.contact,
            'status': databank.current_status if databank else 'N/A'
        })

    return JsonResponse({'success': True, 'leads': results})

# ======================================================== end telecaller ============================================================

def data_reports(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')
    user = None
    company = None  
    employee = None
    telecallers = []
    report_data = []
    total_count = 0

    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')


    date_filter = Q()
    hist_filter = Q()
    followup_filter = Q()
    waste_filter = Q()

    if from_date and to_date:
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

      
        date_filter = Q(assign_date__range=(from_date_obj, to_date_obj))
        hist_filter = Q(allocated_date__range=(from_date_obj, to_date_obj))
        followup_filter = Q(response_date__range=(from_date_obj, to_date_obj))
        waste_filter = Q(waste_marked_date__range=(from_date_obj, to_date_obj))

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login_id=user).first()  

        telecallers = EmployeeRegister_Details.objects.filter(
            company=employee.company,
            designation__name__iexact="Telecaller"
        )

        for tc in telecallers:
          
            allocated_qs = LeadAssignedToTC.objects.filter(telecaller=tc).filter(date_filter)
            allocated_count = allocated_qs.count()

            if allocated_count == 0:
                continue  

          
            pending_count = allocated_qs.filter(status=0).count()

            
            followup_qs = FollowupDetails.objects.filter(telecaller=tc).filter(followup_filter)
            followup_count = followup_qs.count()

          
            closed_qs = FollowupHistory.objects.filter(
                telecaller=tc, final_status='Closed'
            ).filter(hist_filter)
            closed_count = closed_qs.values('lead').distinct().count()

            
            joined_qs = FollowupHistory.objects.filter(
                telecaller=tc, final_status='Joined'
            ).filter(hist_filter)
            joined_count = joined_qs.values('lead').distinct().count()

           
            waste_qs = WasteLead.objects.filter(telecaller=tc).filter(waste_filter)
            waste_count = waste_qs.count()

            report_data.append({
                'name': tc.name,
                'allocated': allocated_count,
                'pending': pending_count,
                'followup': followup_count,
                'closed': closed_count,
                'joined': joined_count,
                'waste': waste_count,
            })
            total_count = len(report_data)

    return render(request, "datamanager/data_reports.html", {
        "user": user,
        "employee": employee,
        'name': employee,
        "telecallers": telecallers,
        "report_data": report_data,
        "from_date": from_date,
        "to_date": to_date,
        "total_count":total_count
    })

def get_telecaller_stats(request, telecaller_id):
    allocated = LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id).count()
    pending = LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id, status=0).count()
    closed = LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id, status=2).count()
    followup = FollowupDetails.objects.filter(telecaller_id=telecaller_id).count()
    joined = DataBank.objects.filter(
        id__in=LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id).values_list('databank_id', flat=True),
        lead_status__iexact="Joined"
    ).count()
    wasted = WasteLead.objects.filter(telecaller_id=telecaller_id).count()

    return JsonResponse({
        'allocated': allocated,
        'pending': pending,
        'closed': closed,
        'followup': followup,
        'joined': joined,
        'wasted': wasted,
    })

def get_telecaller_dates(request, telecaller_id):
    date_data = (
        LeadAssignedToTC.objects
        .filter(telecaller_id=telecaller_id)
        .values('assign_date')
        .annotate(lead_count=Count('id'))
        .order_by('-assign_date')
    )
    return JsonResponse({'dates': list(date_data)})

def get_telecaller_stats_by_date(request, telecaller_id, selected_date):

    assigned_qs = LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id, assign_date=selected_date)
    

    allocated = assigned_qs.count()
    pending = assigned_qs.filter(status=0).count()
    closed = assigned_qs.filter(status=2).count()

    followup = FollowupDetails.objects.filter(
        telecaller_id=telecaller_id,
        response_date=selected_date
    ).count()

    joined = FollowupHistory.objects.filter(
        telecaller_id=telecaller_id,
        allocated_date=selected_date,
        final_status="Joined"
    ).values('lead_id').distinct().count()

    closed_final = FollowupHistory.objects.filter(
        telecaller_id=telecaller_id,
        allocated_date=selected_date,
        final_status="Closed"
    ).values('lead_id').distinct().count()

    wasted = WasteLead.objects.filter(
        telecaller_id=telecaller_id,
        waste_marked_date=selected_date
    ).count()

    return JsonResponse({
        'allocated': allocated,
        'pending': pending,
        'closed': closed,
        'followup': followup,
        'joined': joined,
        'final_closed': closed_final,
        'wasted': wasted
    })

def get_telecaller_leads_by_date(request, telecaller_id, selected_date=None):
 
    is_latest = selected_date in [None, "latest"]

    
    if is_latest:
        latest_date = LeadAssignedToTC.objects.filter(
            telecaller_id=telecaller_id
        ).aggregate(Max('assign_date'))['assign_date__max']
    else:
        latest_date = selected_date

    leads = LeadAssignedToTC.objects.filter(
        telecaller_id=telecaller_id,
        assign_date=latest_date
    ).select_related('databank', 'lead')

    lead_data = []
    for lead in leads:
        db = lead.lead
        lead_data.append({
            'assign_date': lead.assign_date.strftime('%Y-%m-%d'),
            'lead_name': db.name if db else '',
            'email': db.email if db else '',
            'contact': db.contact if db else '',
            'status': lead.databank.current_status if lead.databank else 'Unknown'
        })


    if is_latest:
        all_leads = LeadAssignedToTC.objects.filter(telecaller_id=telecaller_id)
        allocated = all_leads.count()
        pending = all_leads.filter(status=0).count()
        closed = all_leads.filter(status=2).count()

        followup = FollowupDetails.objects.filter(
            telecaller_id=telecaller_id
        ).count()

        joined = FollowupHistory.objects.filter(
            telecaller_id=telecaller_id,
            final_status="Joined"
        ).values('lead_id').distinct().count()

        closed_final = FollowupHistory.objects.filter(
            telecaller_id=telecaller_id,
            final_status="Closed"
        ).values('lead_id').distinct().count()

        wasted = WasteLead.objects.filter(
            telecaller_id=telecaller_id
        ).count()
    else:
        leads_by_date = LeadAssignedToTC.objects.filter(
            telecaller_id=telecaller_id, assign_date=latest_date
        )

        allocated = leads_by_date.count()
        pending = leads_by_date.filter(status=0).count()
        closed = leads_by_date.filter(status=2).count()

        followup = FollowupDetails.objects.filter(
            telecaller_id=telecaller_id, response_date=latest_date
        ).count()

        joined = FollowupHistory.objects.filter(
            telecaller_id=telecaller_id, allocated_date=latest_date, final_status="Joined"
        ).values('lead_id').distinct().count()

        closed_final = FollowupHistory.objects.filter(
            telecaller_id=telecaller_id, allocated_date=latest_date, final_status="Closed"
        ).values('lead_id').distinct().count()

        wasted = WasteLead.objects.filter(
            telecaller_id=telecaller_id, waste_marked_date=latest_date
        ).count()

    return JsonResponse({
        'leads': lead_data,
        'stats': {
            'allocated': allocated,
            'pending': pending,
            'closed': closed,
            'followup': followup,
            'joined': joined,
            'final_closed': closed_final,
            'wasted': wasted
        }
    })

def dm_employees(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')  
    user = None
    company = None  
    if user_id:
        data_managers = LogRegister_Details.objects.filter(log_username=user_id)
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login_id=user).first()  

        telecallers = EmployeeRegister_Details.objects.filter(
                company=employee.company,
                designation__name__iexact="Telecaller"
            )

    else:
        data_managers = []

    return render(request, "datamanager/dm_employees.html", {
        "data_managers": data_managers,
        "user": user,
        "name":employee,
        "employee":employee,
        "telecallers":telecallers,
        })

def dm_emp_leads(request, emp_id):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login') 
    user = None
    employee = None  
    telecallers = None
    assigned_leads = LeadAssignedToTC.objects.none()

    if user_id:
      
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()  
        telecallers = EmployeeRegister_Details.objects.get(id=emp_id)

        assigned_leads = LeadAssignedToTC.objects.filter(telecaller=telecallers)

        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        status = request.GET.get('status')

        if from_date:
            assigned_leads = assigned_leads.filter(assign_date__gte=parse_date(from_date))
        if to_date:
            assigned_leads = assigned_leads.filter(assign_date__lte=parse_date(to_date))
        if status:
            assigned_leads = assigned_leads.filter(databank__lead_status__iexact=status)

    return render(request, "datamanager/dm_emp_leads.html", {
        "user": user,
        "name": employee,
        "employee": employee,
        "telecallers": telecallers,
        "assigned_leads": assigned_leads,
    })

def get_latest_unique_followups(followups):
    seen_statuses = set()
    unique_followups = []

    for f in followups:
        if f.final_status not in seen_statuses:
            unique_followups.append(f)
            seen_statuses.add(f.final_status)

    return unique_followups

def dm_lead_details(request, assign_id):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')
    user = None
    employee = None
    assigned_lead = None
    databank = None
    followup_details = None
    followup_history = []
    call_records = []
    collected_fields = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        tele_caller = LogRegister_Details.objects.filter(log_username=user_id).first()
        assigned_lead = DataBank.objects.select_related(
            "lead__lead_category",  "lead__collected_by"
        ).filter(id=assign_id).first()
        
        if assigned_lead:

            collected_fields = LeadDetails.objects.filter(lead=assigned_lead.lead)

     
            followup_details = FollowupDetails.objects.filter(lead=assigned_lead.lead).order_by('-response_date').first()
            
           
            raw_history = FollowupHistory.objects.filter(lead=assigned_lead.lead).order_by('-id')
            followup_history = get_latest_unique_followups(raw_history)
            

            call_records = LeadCallRecord.objects.filter(lead=assigned_lead.lead).order_by('-record_date')

    context = {
        "user": user,
        "name":employee,
        "employee": employee,
        "assigned_lead": assigned_lead,
        "databank": databank,
        "collected_fields": collected_fields,
        "followup_details": followup_details,
        "followup_history": followup_history,
        "call_records": call_records,
    }
    return render(request, "datamanager/dm_lead_details.html", context)

@csrf_exempt
def dm_delete_lead(request, lead_id):
    if request.method == "POST":
        try:

            if FollowupHistory.objects.filter(lead__id=lead_id).exists():
                FollowupHistory.objects.filter(lead__id=lead_id).delete()

            if FollowupDetails.objects.filter(lead__id=lead_id).exists():
                FollowupDetails.objects.filter(lead__id=lead_id).delete()


            LeadAssignedToTC.objects.filter(lead__id=lead_id).delete()


            DataBank.objects.filter(lead__id=lead_id).update(
                used_count=0,
                lead_allocate_status=0,
                allocated_date=None,
                lead_status='Not Attended'
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def dm_notification_management(request): 
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        name = None


    today = date.today()


    today_new_leads = DataBank.objects.filter(generated_date=today,lead__collected_by__company=company).count()
    today_allocations = DataBank.objects.filter(lead_status='Allocated', allocated_date=today,lead__collected_by__company=company).count()



    today_followups = FollowupDetails.objects.filter(company=name.company,response_date=today).count()



    return render(request, 'datamanager/dm_notification_management.html', {
        'user': user,
        'name': name,
        'today_new_leads': today_new_leads,
        'today_allocations': today_allocations,
        'today_followups': today_followups,
    })

@csrf_exempt
def dm_today_new_lead(request): 
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

  
    today = date.today()


    leads = DataBank.objects.select_related("lead").filter(generated_date=today,lead__collected_by__company=company)


    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    executive_id = request.GET.get("executive")
    source = request.GET.get("status")

    if client_id:
        leads = leads.filter(lead__lead_category__client_task__client=client_id)
    if category_id:
        leads = leads.filter(lead__lead_category_id=category_id)
    if executive_id:
        leads = leads.filter(lead__collected_by=executive_id)
    if source:
        leads = leads.filter(lead__source__iexact=source)

    leads = leads.order_by("-id")


    clients = ClientRegister.objects.filter(company=employee.company)
    executives = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id__in=['Executive', 'Team_Lead','Digital_Marketing_Head'],company=employee.company
    )

    return render(request, "datamanager/dm_today_new_lead.html", {
        "user": user,
        'name': employee,
        "employee": employee,
        "leads": leads,
        "clients": clients,
        "executives": executives,
    })

@csrf_exempt
def dm_today_allocated_lead(request): 
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)

            employee = EmployeeRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

 
    today = date.today()

 
    leads = LeadAssignedToTC.objects.select_related("lead").filter(
    assign_date=today,)

 

    hr_id = request.GET.get("hr")
    status = request.GET.get("status")

    if hr_id:
        leads = leads.filter(telecaller=hr_id)
    if status:
        leads = leads.filter(databank__lead_status__iexact=status)

    leads = leads.order_by("-id")


    clients = ClientRegister.objects.filter(company=employee.company)
    hrs = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id='Telecaller',company=employee.company)

    return render(request, "datamanager/dm_today_allocated_lead.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "leads": leads,
        "clients": clients,
        "hrs": hrs,
    })

@csrf_exempt
def dm_today_followup(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None
    company = None

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            user = None
            


    today = date.today()

   
    followup_leads = FollowupDetails.objects.filter(
        response_date=today,company=employee.company)

 
    leads = LeadAssignedToTC.objects.select_related(
        "lead", "telecaller", "client"
    ).filter(
        lead__in=followup_leads.values("lead")
    ).order_by("-id")

  
    hr_id = request.GET.get("hr")

    if hr_id:
        leads = leads.filter(telecaller=hr_id)


    clients = ClientRegister.objects.filter(company=employee.company)
    hrs = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id='Telecaller',company=employee.company
    )

    return render(request, "datamanager/dm_today_followup.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "leads": leads,
        "clients": clients,
        "hrs": hrs,
    })
    
def dm_clients(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')  
    user = None
    employee = None
    leads = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        company = employee.company

        if employee:
            clients = ClientRegister.objects.filter(company=employee.company)
            leads = LeadAssignedToTC.objects.select_related(
                'lead', 'client', 'telecaller'
            ).filter(lead__collected_by__company=company).order_by('assign_date')

            client_id = request.GET.get('client_id')
            category_id = request.GET.get('category_id')

            if client_id:
                leads = leads.filter(lead__lead_category__client_task__client=int(client_id))

            if category_id:
                leads = leads.filter(lead__lead_category__id=int(category_id))

    return render(request, "datamanager/dm_clients.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "leads": leads,
        "clients":clients
    })

def get_lead_categories_dm(request, client_id):
    print("Client ID:", client_id)
    categories = LeadCategory_Register.objects.filter(
        client_task__client__id=client_id
    ).distinct()
    print("Query:", categories.query)
    print("Found categories:", categories.count())

    result = [
        {'id': cat.id, 'name': cat.collection_for}
        for cat in categories
    ]
    print("Result:", result)
    return JsonResponse({'categories': result})

def dm_platform(request): 
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None
    sources = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        company = employee.company

        if employee:
            sources = Platforms.objects.filter(company=employee.company)

            
            for src in sources:
                lead_count = DataBank.objects.filter(
                    lead__source__iexact=src.platform_name, lead__collected_by__company=company
                ).count()
                src.platform_total_count = lead_count  
    
    return render(request, "datamanager/dm_platform.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "sources": sources
    })

@csrf_exempt
def save_dm_platform(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            platform_name = data.get("platform_name")

            if not platform_name:
                return JsonResponse({"status": "error", "message": "Platform name is required"})

      
            user_id = (
                request.session.get("tid")
                or request.session.get("hid")
                or request.session.get("did")
            )

            if not user_id:
                return JsonResponse({"status": "error", "message": "User not found in session"})

            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()

            if not employee or not employee.company:
                return JsonResponse({"status": "error", "message": "Company not found"})

           
            Platforms.objects.create(
                company=employee.company,
                platform_name=platform_name
            )

            return JsonResponse({"status": "success", "message": "Platform added successfully"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"})

@csrf_exempt
def dm_platform_lead_details(request): 
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  
    company = None

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
    
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            pass

   
    platform_name = request.GET.get("platform", "").strip()
   

    leads = DataBank.objects.select_related("lead").filter(lead__collected_by__company=company)


    if platform_name:
        leads = leads.filter(lead__source__iexact=platform_name)


    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        try:
            from_date_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
            leads = leads.filter(generated_date__gte=from_date_parsed)
        except ValueError:
            pass

    if to_date:
        try:
            to_date_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()
            leads = leads.filter(generated_date__lte=to_date_parsed)
        except ValueError:
            pass

    leads = leads.order_by("-id")

    return render(request, "datamanager/dm_platform_lead_details.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "leads": leads,
        "platform_name": platform_name,
    })

def dm_platform_report(request): 
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')
    user = None
    employee = None
    platform_summary = []
    total_leads = 0

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()

        if employee:
          
            sources = PlatformData.objects.filter(company=employee.company)

  
            if from_date and to_date:
                sources = sources.filter(data_add_date__range=[from_date, to_date])
            elif from_date:
                sources = sources.filter(data_add_date__gte=from_date)
            elif to_date:
                sources = sources.filter(data_add_date__lte=to_date)

            grouped_data = defaultdict(list)
            for s in sources:
                grouped_data[s.platform_name].append({
                    "date": s.data_add_date,
                    "count": s.platform_data_count or 0,
                })

   
            for platform_name, entries in grouped_data.items():
                total_collected = sum(item["count"] for item in entries)
                platform_summary.append({
                    "platform_name": platform_name,
                    "entries": sorted(entries, key=lambda x: x["date"], reverse=True),
                    "total_collected": total_collected,
                })

            total_leads = sum(p["total_collected"] for p in platform_summary)

    return render(request, "datamanager/dm_platform_report.html", {
        "user": user,
        "name":employee,
        "employee": employee,
        "platform_summary": platform_summary,
        "from_date": from_date or "",
        "to_date": to_date or "",
        "total_leads": total_leads,
    })

def dm_wastedata(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login') 

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        name=EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    return render(request, 'datamanager/dm_wastedata.html', {
        'user': user,
        'company': company,
        'name':name
    })

def dm_approved_wastedata(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            company = BusinessRegister_Details.objects.filter(login=user).first()
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None

 
    hr_id = request.GET.get("hr")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")


    waste_leads = WasteLead.objects.filter(
        status=2, 
        lead__collected_by__company=employee.company
    ).select_related(
        'lead',
        'databank',
        'client',
        'telecaller',
        'assignment'
    )


    if hr_id:
        waste_leads = waste_leads.filter(telecaller_id=hr_id)

    if from_date and to_date:
        try:
            from_date_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()
            waste_leads = waste_leads.filter(waste_marked_date__range=[from_date_parsed, to_date_parsed])
        except ValueError:
            pass  

    elif from_date:
        try:
            from_date_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
            waste_leads = waste_leads.filter(waste_marked_date__gte=from_date_parsed)
        except ValueError:
            pass

    elif to_date:
        try:
            to_date_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()
            waste_leads = waste_leads.filter(waste_marked_date__lte=to_date_parsed)
        except ValueError:
            pass


    hrs = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id='Telecaller',
        company=employee.company
    )

    context = {
        "name":employee,
        'leads': waste_leads,
        'hrs': hrs
    }
    return render(request, 'datamanager/dm_approved_wastedata.html', context)

@csrf_exempt
def dm_pending_wastedata(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None


    waste_leads = WasteLead.objects.filter(status=1,lead__collected_by__company=company).select_related(
        "lead", "databank", "client", "telecaller"
    )

   
    hr_id = request.GET.get("hr")
    status_filter = request.GET.get("status")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

  
    if hr_id:
        waste_leads = waste_leads.filter(telecaller_id=hr_id)

    
    if status_filter:
        if status_filter == "Not Confirmed":
            waste_leads = waste_leads.filter(confirmation=0)
        elif status_filter == "Confirmed":
            waste_leads = waste_leads.filter(confirmation=1)
        elif status_filter == "Reject":
            waste_leads = waste_leads.filter(confirmation=2)

 
    if from_date and to_date:
        waste_leads = waste_leads.filter(
            waste_marked_date__range=[from_date, to_date]
        )
    elif from_date:
        waste_leads = waste_leads.filter(waste_marked_date__gte=from_date)
    elif to_date:
        waste_leads = waste_leads.filter(waste_marked_date__lte=to_date)

 
    hrs = EmployeeRegister_Details.objects.filter(
        designation__dashboard_id="Telecaller", company=employee.company
    )

    context = {
        "name":employee,
        "leads": waste_leads,
        "hrs": hrs,
    }
    return render(request, "datamanager/dm_pending_wastedata.html", context)

@csrf_exempt
def dm_wastelead_approve(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lead_id = data.get("id")

            waste_lead = get_object_or_404(WasteLead, id=lead_id)

          
            if waste_lead.confirmation == 1:
                waste_lead.status = 2
                waste_lead.save()

               
                if waste_lead.lead:
                    lead_obj = waste_lead.lead
                    lead_obj.waste_data = 1
                    lead_obj.waste_data_reason = waste_lead.reason
                    lead_obj.save()

                return JsonResponse({"success": True, "message": "Lead approved successfully."})
            else:
                return JsonResponse({"success": False, "message": "Confirmation missing!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})

@csrf_exempt
def dm_wastelead_reject(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lead_id = data.get("id")

        waste_lead = get_object_or_404(WasteLead, id=lead_id)

      
        if waste_lead.assignment:
            waste_lead.assignment.status = 1
            waste_lead.assignment.save()


        waste_lead.delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request"})

def dm_repeat_data(request):
    user_id = request.session.get('did')

    if not user_id:
        return redirect('login')

    user = None
    employee = None  

    if user_id:
        try:
            user = LogRegister_Details.objects.get(log_username=user_id)
            employee = EmployeeRegister_Details.objects.filter(login=user).first()
            company = employee.company
        except LogRegister_Details.DoesNotExist:
            user = None
            company = None


    duplicate_emails = Leads.objects.values('email').annotate(email_count=Count('email')).filter(email_count__gt=1)
    duplicate_phones = Leads.objects.values('contact').annotate(phone_count=Count('contact')).filter(phone_count__gt=1)
    
    duplicate_values = set(
        [item['email'] for item in duplicate_emails] +
        [item['contact'] for item in duplicate_phones]
    )


    leads_qs = DataBank.objects.filter(
    (
        Q(lead__email__in=duplicate_values) |
        Q(lead__contact__in=duplicate_values) |
        Q(lead__repeated_status=1)
    ),
    lead__collected_by__company=employee.company
).select_related(
    'lead',
    'lead__lead_category__client_task__client',
    'lead__lead_category'
).order_by('-generated_date')


    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if client_id:
        leads_qs = leads_qs.filter(lead__lead_category__client_task__client=client_id)

    if category_id:
        leads_qs = leads_qs.filter(lead__lead_category__id=category_id)

    if from_date:
        try:
            from_date_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
            leads_qs = leads_qs.filter(generated_date__gte=from_date_parsed)
        except ValueError:
            pass

    if to_date:
        try:
            to_date_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()
            leads_qs = leads_qs.filter(generated_date__lte=to_date_parsed)
        except ValueError:
            pass


    clients = ClientRegister.objects.filter(company=company).order_by('client_name')
    categories = LeadCategory_Register.objects.all().order_by('collection_for')


    context = {
        'name':employee,
        'leads': leads_qs,
        'clients': clients,
        'categories': categories,
    }
    return render(request, 'datamanager/dm_repeat_data.html', context)

@csrf_exempt
def update_repeated_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lead_id = data.get("id")

        try:
            lead = Leads.objects.get(id=lead_id)
            lead.repeated_status = 1
            lead.save()
            return JsonResponse({"success": True})
        except Leads.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lead not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})
    
@csrf_exempt
def dm_delete_lead2(request, lead_id):
    if request.method == "POST":
        try:

            if FollowupHistory.objects.filter(lead__id=lead_id).exists():
                FollowupHistory.objects.filter(lead__id=lead_id).delete()

            if FollowupDetails.objects.filter(lead__id=lead_id).exists():
                FollowupDetails.objects.filter(lead__id=lead_id).delete()


            LeadAssignedToTC.objects.filter(lead__id=lead_id).delete()


            DataBank.objects.filter(lead__id=lead_id).delete()
            Leads.objects.filter(id=lead_id).delete()

            if LeadDetails.objects.filter(lead__id=lead_id).exists():
                LeadDetails.objects.filter(lead__id=lead_id).delete()

            

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
def tl_all_leads(request):
    user_id = request.session.get('tid')

    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()

        if employee:
            
            allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list('employee', flat=True)

            
            allowed_user_ids = list(allocated_employee_ids)
            allowed_user_ids.append(employee.id)

            
            lead_categories = LeadCategory_Register.objects.all()

            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")

      
            leads = Leads.objects.filter(collected_by__in=allowed_user_ids)

            company_id = employee.company.id if employee.company else None
            if executive_id:
                leads = leads.filter(collected_by=executive_id)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(client_task__in=task_ids).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids)

            if category_id:
                leads = leads.filter(lead_category_id=category_id)

            if lead_status:
                if lead_status.lower() == 'unverify':
                    leads = leads.filter(status=0, waste_data=0)
                elif lead_status.lower() == 'verified':
                    leads = leads.filter(status=1, waste_data=0)
                elif lead_status.lower() == 'waste':
                    leads = leads.filter(waste_data=1)
                elif lead_status.lower() == 'repeated':
                    leads = leads.filter(repeated_status=1)  
                elif lead_status.lower() == 'transfered':
                    leads = leads.filter(transfer_status=1)  

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date])
            elif from_date:
                leads = leads.filter(added_date__gte=from_date)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date)

            leads = leads.order_by("-added_date", "-added_time")


            clients = ClientRegister.objects.filter(company=company_id)
            employee_list = EmployeeRegister_Details.objects.filter(id__in=allowed_user_ids)



            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related('client')
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

      
            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [{"id": cat.id, "name": cat.collection_for} for cat in client_categories_map.get(client.id, [])]
                for client in clients
}


    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    

    return render(request, 'teamlead/tl_all_leads.html', {
        "user": user,
        "name": employee,
        "employee": employee,
        "client_name": client_name,
        "leads": page_obj,
        "per_page": per_page,
        "lead_categories": lead_categories,
        "total_leads":total_leads,
        "clients": clients,
        "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),
        "employee_list":employee_list
    })

from openpyxl.utils import get_column_letter
def export_leads_excel(request):
    user_id = (
        request.session.get("tid")
        or request.session.get("hid")
        or request.session.get("did")
    )

    leads = Leads.objects.all().order_by("-added_date", "-added_time")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"


    headers = ["Collected By", "Added Date", "Added Time", "Name", "Email", "Contact", "Lead Source"]
    ws.append(headers)

    
    for lead in leads:
        ws.append([
            str(lead.collected_by),
            str(lead.added_date),
            str(lead.added_time.strftime("%H:%M:%S") if lead.added_time else ''),
            lead.name,
            lead.email,
            lead.contact,
            lead.source if hasattr(lead, 'source') else '',
        ])

    
    for col_num, _ in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(col_num)].width = 20

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename=leads.xlsx'
    wb.save(response)
    return response

def export_leads_pdf(request):
    user_id = (
        request.session.get("tid")
        or request.session.get("hid")
        or request.session.get("did")
    )
    user = LogRegister_Details.objects.get(log_username=user_id)
    employee = EmployeeRegister_Details.objects.filter(login=user).first()

    allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list('employee', flat=True)

    allowed_user_ids = list(allocated_employee_ids)
    allowed_user_ids.append(employee.id)

    leads = Leads.objects.filter(collected_by__in=allowed_user_ids).order_by("-added_date", "-added_time")

    leads_data = []
    for lead in leads:
        leads_data.append({
            "collected_by": str(lead.collected_by) if lead.collected_by else "",  
            "added_date": lead.added_date.strftime("%Y-%m-%d") if lead.added_date else "",
            "added_time": lead.added_time.strftime("%I:%M %p") if lead.added_time else "",
            "name": lead.name or "",
            "email": lead.email or "",
            "contact": lead.contact or "",
            "lead_source": lead.source or "",
        })

    return JsonResponse({"leads": leads_data})

def get_lead_details_tl(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        details = LeadDetails.objects.filter(lead=lead)

        extra_fields = {}
        if lead.source:
            extra_fields["Source"] = lead.source

        for detail in details:
            extra_fields[detail.field_name] = detail.field_data  
        
        

        data = {
            "name": lead.name,
            "email": lead.email,
            "contact": lead.contact,
            "verified": lead.status,  
            "waste_data": lead.waste_data,
            "incomplete_status": lead.incomplete_status,
            "extra_fields": extra_fields
        }
        return JsonResponse(data)

    except Leads.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    
def lead_details(request, lead_id):
    try:
        lead = Leads.objects.get(id=lead_id)
        lead_details = LeadDetails.objects.filter(lead=lead)
        followups = FollowupDetails.objects.filter(lead=lead).order_by('-response_date')
        history = FollowupHistory.objects.filter(lead=lead).order_by('-allocated_date')
        assigned_to = LeadAssignedToTC.objects.filter(lead=lead).order_by('-assign_date').first()

        client_name = None
        lead_category_name = None

        if lead.lead_category:
            lead_category_name = lead.lead_category.collection_for
            if lead.lead_category.client_task and lead.lead_category.client_task.client:
                client_name = lead.lead_category.client_task.client.client_name

     
        more_details = []
        if lead.source:
            more_details.append({"field_name": "Source", "field_data": lead.source})
        for d in lead_details:
            more_details.append({"field_name": d.field_name, "field_data": d.field_data})

       
        followup_data = []
        for f in followups:
            followup_data.append({
                "connected_on": f.response_date.strftime("%b %d, %Y") if f.response_date else "",
                "contact_by": f.telecaller.name if f.telecaller else "",
                "status": f.response_status or "",
                "response": f.response or "",
            })

 
        history_data = []
        for h in history:
            history_data.append({
                "allocated_on": h.allocated_date.strftime("%b %d, %Y") if h.allocated_date else "",
                "allocated_to": h.telecaller.name if h.telecaller else "",
                "note": h.note or "",
                "final_status": h.final_status or "",
            })

        waste_data = WasteLead.objects.filter(lead=lead).first()
        waste_data_dict = None
        if waste_data:
            waste_data_dict = {
                "reason": waste_data.reason or "",
                "head_reason": waste_data.head_reason or "",
                "confirmation": waste_data.confirmation,
                "telecaller_name": waste_data.telecaller.name if waste_data.telecaller else "",
                "marked_date": waste_data.waste_marked_date.strftime("%b %d, %Y") if waste_data.waste_marked_date else "",
            }

        data = {
            "name": lead.name,
            "email": lead.email,
            "contact": lead.contact,
            "collected_by": lead.collected_by.name if lead.collected_by else "",
            "added_date": lead.added_date.strftime("%b %d, %Y") if lead.added_date else "",
            "added_time": lead.added_time.strftime("%I:%M %p") if lead.added_time else "",
            "allocated_to": assigned_to.telecaller.name if assigned_to and assigned_to.telecaller else "",
            "allocated_date": assigned_to.assign_date.strftime("%b %d, %Y") if assigned_to and assigned_to.assign_date else "",
            "allocated_time": assigned_to.allocate_time.strftime("%I:%M %p") if assigned_to and assigned_to.allocate_time else "",
            "waste_data": lead.waste_data,
            "waste_data_reason": lead.waste_data_reason,
            "client_details": {
                "client_name": client_name,
                "lead_category": lead_category_name
            },
            "more_details": more_details,
            "followup_track": followup_data,
            "history_track": history_data,
            "waste_data": waste_data_dict,
        }

        return JsonResponse({"success": True, "lead": data})

    except Leads.DoesNotExist:
        return JsonResponse({"success": False, "message": "Lead not found."})
    
def tl_waste_leads(request):
    user_id = request.session.get('tid')

    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()

        if employee:
           
            allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list('employee', flat=True)

            allowed_user_ids = list(allocated_employee_ids)
            allowed_user_ids.append(employee.id)

            
            lead_categories = LeadCategory_Register.objects.all()

            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")

          
            leads = Leads.objects.filter(collected_by__in=allowed_user_ids, waste_data=1)
            company_id = employee.company if employee.company else None
       
            if executive_id:
                leads = leads.filter(collected_by=executive_id,waste_data=1)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(client_task__in=task_ids).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids,waste_data=1)

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date],waste_data=1)
            elif from_date:
                leads = leads.filter(added_date__gte=from_date,waste_data=1)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date,waste_data=1)

            leads = leads.order_by("-added_date", "-added_time")


            
            clients = ClientRegister.objects.filter(company=company_id)
            employee_list = EmployeeRegister_Details.objects.filter(id__in=allowed_user_ids)


            
            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related('client')
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

            
            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [{"id": cat.id, "name": cat.collection_for} for cat in client_categories_map.get(client.id, [])]
                for client in clients
}


    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    

    return render(request, 'teamlead/tl_waste_leads.html', {
        "user": user,
        "name":employee,
        "employee": employee,
        "client_name": client_name,
        "leads": page_obj,
        "per_page": per_page,
        "lead_categories": lead_categories,
        "total_leads":total_leads,
        "clients": clients,
        "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),
        "employee_list":employee_list
    })

def tl_leads_tracker(request):
    user_id = request.session.get('tid')

    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
      

        if employee:
            allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list("employee", flat=True)

            allowed_user_ids = list(allocated_employee_ids)
            allowed_user_ids.append(employee.id)

            lead_categories = LeadCategory_Register.objects.all()
            company_id = employee.company.id if employee.company else None


            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")
            telecaller_id = request.GET.get("telecaller_id")
            from_date2 = request.GET.get("from_date2")
            to_date2 = request.GET.get("to_date2")
            followup_status2 = request.GET.get("followup_status")

            followup_status = FollowupStatus.objects.values_list("status_name", flat=True)

           
            leads = Leads.objects.filter(
                collected_by__in=allowed_user_ids, transfer_status=1
            )

          
            if executive_id:
                leads = leads.filter(collected_by=executive_id)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(
                    client_task__in=task_ids
                ).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids)

            if category_id:
                leads = leads.filter(lead_category_id=category_id)

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date])
            elif from_date:
                leads = leads.filter(added_date__gte=from_date)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date)

            leads = leads.order_by("-added_date", "-added_time")


            lead_assigned_qs = LeadAssignedToTC.objects.all()

        
            if lead_status and lead_status.lower().strip() == "not attended":
                assigned_lead_ids = LeadAssignedToTC.objects.values_list("lead_id", flat=True)
                leads = leads.exclude(id__in=assigned_lead_ids)
            else:
               
                if lead_status:
                    lead_status_lower = lead_status.lower().strip()
                    if lead_status_lower == "allocated":
                        lead_assigned_qs = lead_assigned_qs.filter(status=0)
                    elif lead_status_lower == "opened":
                        lead_assigned_qs = lead_assigned_qs.filter(status=1)
                    elif lead_status_lower == "recalled":
                        lead_assigned_qs = lead_assigned_qs.filter(response="Recalled")
                    elif lead_status_lower == "joined":
                        lead_assigned_qs = lead_assigned_qs.filter(response="Lead Joined")
                    elif lead_status_lower == "closed":
                        lead_assigned_qs = lead_assigned_qs.filter(status=3)

         
                if telecaller_id:
                    lead_assigned_qs = lead_assigned_qs.filter(telecaller_id=telecaller_id)

     
                if from_date2 and to_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__range=[from_date2, to_date2])
                elif from_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__gte=from_date2)
                elif to_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__lte=to_date2)

      
                if followup_status2:
                    if followup_status2 == "Marked as waste":
                        lead_assigned_qs = lead_assigned_qs.filter(lead__waste_data=1)
                    elif followup_status2 == "No Updation":
                        lead_assigned_qs = lead_assigned_qs.filter(response="No Data Availale")
                    else:
                        followup_obj = FollowupStatus.objects.filter(
                             Q(status_name=followup_status2),
                            company=employee.company
                        ).first()
                        if followup_obj:
                            lead_assigned_qs = lead_assigned_qs.filter(response=followup_obj.status_name)

         
                if lead_status or telecaller_id or from_date2 or to_date2 or followup_status2:
                    filtered_lead_ids = list(lead_assigned_qs.values_list("lead_id", flat=True))
                    leads = Leads.objects.filter(
                        id__in=filtered_lead_ids,
                        collected_by__in=allowed_user_ids,
                        transfer_status=1
                    )


            clients = ClientRegister.objects.filter(company=company_id)
            employee_list = EmployeeRegister_Details.objects.filter(id__in=allowed_user_ids)
            telecaller_list = EmployeeRegister_Details.objects.filter(
                company=employee.company, designation__dashboard_id="Telecaller"
            )

           
            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related("client")
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [
                    {"id": cat.id, "name": cat.collection_for}
                    for cat in client_categories_map.get(client.id, [])
                ]
                for client in clients
            }

    per_page = int(request.GET.get("per_page", 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    return render(
        request,
        "teamlead/tl_leads_tracker.html",
        {
            "user": user,
            "name":employee,
            "employee": employee,
            "client_name": client_name,
            "leads": page_obj,
            "per_page": per_page,
            "lead_categories": lead_categories,
            "total_leads": total_leads,
            "clients": clients,
            "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),
            "employee_list": employee_list,
            "followup_status": followup_status,
            "telecaller_list": telecaller_list,
        },
    )
    
def exec_all_leads(request):


    session_login_id = request.session.get('eid')

    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if session_login_id:
        user = LogRegister_Details.objects.get(log_username=session_login_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        name=employee

        if employee:        
            lead_categories = LeadCategory_Register.objects.all()

            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")

      
            leads = Leads.objects.filter(collected_by=employee)

            company_id = employee.company.id if employee.company else None
            if executive_id:
                leads = leads.filter(collected_by=executive_id)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(client_task__in=task_ids).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids)

            if category_id:
                leads = leads.filter(lead_category_id=category_id)

            if lead_status:
                if lead_status.lower() == 'unverify':
                    leads = leads.filter(status=0, waste_data=0)
                elif lead_status.lower() == 'verified':
                    leads = leads.filter(status=1, waste_data=0)
                elif lead_status.lower() == 'waste':
                    leads = leads.filter(waste_data=1)
                elif lead_status.lower() == 'repeated':
                    leads = leads.filter(repeated_status=1)  
                elif lead_status.lower() == 'transfered':
                    leads = leads.filter(transfer_status=1)  

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date])
            elif from_date:
                leads = leads.filter(added_date__gte=from_date)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date)

            leads = leads.order_by("-added_date", "-added_time")


            clients = ClientRegister.objects.filter(company=company_id)




            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related('client')
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

      
            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [{"id": cat.id, "name": cat.collection_for} for cat in client_categories_map.get(client.id, [])]
                for client in clients
}


    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    

    return render(request, 'executive/exec_all_leads.html', {
        "user": user,
        "employee": employee,
        "name":name,
        "client_name": client_name,
        "leads": page_obj,
        "per_page": per_page,
        "lead_categories": lead_categories,
        "total_leads":total_leads,
        "clients": clients,
        "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),

    })

def exec_leads_tracker(request):
    session_login_id = request.session.get('eid')
    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if session_login_id:
        user = LogRegister_Details.objects.get(log_username=session_login_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        name = employee

        if employee:
            allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list("employee", flat=True)

            allowed_user_ids = list(allocated_employee_ids)
            allowed_user_ids.append(employee.id)

            lead_categories = LeadCategory_Register.objects.all()
            company_id = employee.company.id if employee.company else None


            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")
            telecaller_id = request.GET.get("telecaller_id")
            from_date2 = request.GET.get("from_date2")
            to_date2 = request.GET.get("to_date2")
            followup_status2 = request.GET.get("followup_status")

            followup_status = FollowupStatus.objects.values_list("status_name", flat=True)

           
            leads = Leads.objects.filter(
                collected_by__in=allowed_user_ids, transfer_status=1
            )

          
            if executive_id:
                leads = leads.filter(collected_by=executive_id)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(
                    client_task__in=task_ids
                ).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids)

            if category_id:
                leads = leads.filter(lead_category_id=category_id)

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date])
            elif from_date:
                leads = leads.filter(added_date__gte=from_date)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date)

            leads = leads.order_by("-added_date", "-added_time")


            lead_assigned_qs = LeadAssignedToTC.objects.all()

        
            if lead_status and lead_status.lower().strip() == "not attended":
                assigned_lead_ids = LeadAssignedToTC.objects.values_list("lead_id", flat=True)
                leads = leads.exclude(id__in=assigned_lead_ids)
            else:
               
                if lead_status:
                    lead_status_lower = lead_status.lower().strip()
                    if lead_status_lower == "allocated":
                        lead_assigned_qs = lead_assigned_qs.filter(status=0)
                    elif lead_status_lower == "opened":
                        lead_assigned_qs = lead_assigned_qs.filter(status=1)
                    elif lead_status_lower == "recalled":
                        lead_assigned_qs = lead_assigned_qs.filter(response="Recalled")
                    elif lead_status_lower == "joined":
                        lead_assigned_qs = lead_assigned_qs.filter(response="Lead Joined")
                    elif lead_status_lower == "closed":
                        lead_assigned_qs = lead_assigned_qs.filter(status=3)

         
                if telecaller_id:
                    lead_assigned_qs = lead_assigned_qs.filter(telecaller_id=telecaller_id)

     
                if from_date2 and to_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__range=[from_date2, to_date2])
                elif from_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__gte=from_date2)
                elif to_date2:
                    lead_assigned_qs = lead_assigned_qs.filter(assign_date__lte=to_date2)

      
                if followup_status2:
                    if followup_status2 == "Marked as waste":
                        lead_assigned_qs = lead_assigned_qs.filter(lead__waste_data=1)
                    elif followup_status2 == "No Updation":
                        lead_assigned_qs = lead_assigned_qs.filter(response="No Data Availale")
                    else:
                        followup_obj = FollowupStatus.objects.filter(
                             Q(status_name=followup_status2),
                            company=employee.company
                        ).first()
                        if followup_obj:
                            lead_assigned_qs = lead_assigned_qs.filter(response=followup_obj.status_name)

         
                if lead_status or telecaller_id or from_date2 or to_date2 or followup_status2:
                    filtered_lead_ids = list(lead_assigned_qs.values_list("lead_id", flat=True))
                    leads = Leads.objects.filter(
                        id__in=filtered_lead_ids,
                        collected_by__in=allowed_user_ids,
                        transfer_status=1
                    )


            clients = ClientRegister.objects.filter(company=company_id)
            employee_list = EmployeeRegister_Details.objects.filter(id__in=allowed_user_ids)
            telecaller_list = EmployeeRegister_Details.objects.filter(
                company=employee.company, designation__dashboard_id="Telecaller"
            )

           
            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related("client")
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [
                    {"id": cat.id, "name": cat.collection_for}
                    for cat in client_categories_map.get(client.id, [])
                ]
                for client in clients
            }

    per_page = int(request.GET.get("per_page", 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    return render(
        request,
        "executive/exec_leads_tracker.html",
        {
            "user": user,
            "employee": employee,
            "name":name,
            "client_name": client_name,
            "leads": page_obj,
            "per_page": per_page,
            "lead_categories": lead_categories,
            "total_leads": total_leads,
            "clients": clients,
            "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),
            "employee_list": employee_list,
            "followup_status": followup_status,
            "telecaller_list": telecaller_list,
        },
    )

def exec_waste_leads(request):
    session_login_id = request.session.get('eid')
    user = None
    employee = None
    client_name = None
    lead_fields = []
    leads = []
    lead_categories = []

    if session_login_id:
        user = LogRegister_Details.objects.get(log_username=session_login_id)
        employee = EmployeeRegister_Details.objects.filter(login=user).first()
        name = employee

        if employee:
           
            allocated_employee_ids = AllocationDetails.objects.filter(
                team_lead=employee
            ).values_list('employee', flat=True)

            allowed_user_ids = list(allocated_employee_ids)
            allowed_user_ids.append(employee.id)

            
            lead_categories = LeadCategory_Register.objects.all()

            client_id = request.GET.get("client_id")
            category_id = request.GET.get("category_id")
            executive_id = request.GET.get("executive_id")
            lead_status = request.GET.get("lead_status")
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")

          
            leads = Leads.objects.filter(collected_by__in=allowed_user_ids, waste_data=1)
            company_id = employee.company if employee.company else None
       
            if executive_id:
                leads = leads.filter(collected_by=executive_id,waste_data=1)

            if client_id:
                task_ids = ClientTask_Register.objects.filter(client=client_id).values_list("id", flat=True)
                lead_category_ids = LeadCategory_Register.objects.filter(client_task__in=task_ids).values_list("id", flat=True)
                leads = leads.filter(lead_category_id__in=lead_category_ids,waste_data=1)

            if from_date and to_date:
                leads = leads.filter(added_date__range=[from_date, to_date],waste_data=1)
            elif from_date:
                leads = leads.filter(added_date__gte=from_date,waste_data=1)
            elif to_date:
                leads = leads.filter(added_date__lte=to_date,waste_data=1)

            leads = leads.order_by("-added_date", "-added_time")


            
            clients = ClientRegister.objects.filter(company=company_id)
            


            
            client_categories_map = {}
            client_tasks = ClientTask_Register.objects.select_related('client')
            for ct in client_tasks:
                categories = LeadCategory_Register.objects.filter(client_task=ct)
                if ct.client.id not in client_categories_map:
                    client_categories_map[ct.client.id] = []
                client_categories_map[ct.client.id] += list(categories)

            
            from django.core.serializers.json import DjangoJSONEncoder
            import json

            client_category_json = {
                str(client.id): [{"id": cat.id, "name": cat.collection_for} for cat in client_categories_map.get(client.id, [])]
                for client in clients
}


    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(leads, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_leads = leads.count()

    

    return render(request, 'executive/exec_waste_leads.html', {
        "user": user,
        "employee": employee,
        "name":name,
        "client_name": client_name,
        "leads": page_obj,
        "per_page": per_page,
        "lead_categories": lead_categories,
        "total_leads":total_leads,
        "clients": clients,
        "client_category_json": json.dumps(client_category_json, cls=DjangoJSONEncoder),
        
    })
    
def pendingworks(request):    
    user_id = request.session.get('hid')

    pending = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        log_emp = EmployeeRegister_Details.objects.filter(login=user).first()
        cmp_id = log_emp.company

        # WorkAssign pending works
        work_pending = WorkAssign.objects.filter(
            status=2,
            company=cmp_id
        )

        for i in work_pending:
            pending.append({
                'type': 'work',
                'client': i.client,
                'from_date': i.from_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.assign_date,
                'team_lead': i.team_lead,
                'client_task': i.client_task.all(),
                'assign_type': i.assign_type,
                'co_workers': i.co_workers.all(),
            })

        # TaskAssign accepted pending works
        task_pending = TaskAssign.objects.filter(
            accept_status=1,
            work_assign__company=cmp_id
        )

        for i in task_pending:
            pending.append({
                'type': 'task',
                'client': i.work_assign.client,
                'from_date': i.start_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.allocate_date,
                'team_lead': i.work_assign.team_lead,
                'client_task': [i.client_task],
                'assign_type': i.work_assign.assign_type,
                'co_workers': i.work_assign.co_workers.all(),
            })

        # Lead Category pending works
        lead_category_work_pending = LeadCateogry_TeamAllocate.objects.filter(
            status=2,
            work_assign__company=cmp_id
        )

        for i in lead_category_work_pending:
            pending.append({
                'type': 'lead',
                'client': i.work_assign.client,
                'from_date': i.from_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.accept_date,
                'team_lead': i.team_lead,
                'client_task': [i.lead_category],
                'assign_type': 0,
                'co_workers': [],
            })

    return render(request, 'dmhead/pendingworks.html', {
        'pending': pending,
        'name': log_emp
    })

def dm_completedwork(request): 
    user_id = request.session.get('hid')

    complete = []

    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        log_emp = EmployeeRegister_Details.objects.filter(login=user).first()
        cmp_id = log_emp.company

        # store added work ids to avoid duplicates
        added_work_ids = set()

        # WorkAssign completed works
        work_completed = WorkAssign.objects.filter(
            status=3,
            company=cmp_id
        )

        for i in work_completed:

            added_work_ids.add(i.id)

            complete.append({
                'type': 'work',
                'client': i.client,
                'from_date': i.from_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.assign_date,
                'team_lead': i.team_lead,
                'status': i.status,
            })

        # TaskAssign completed works
        task_completed = TaskAssign.objects.filter(
            status=2,
            work_assign__company=cmp_id
        )

        for i in task_completed:

            # skip duplicate WorkAssign
            if i.work_assign.id in added_work_ids:
                continue

            added_work_ids.add(i.work_assign.id)

            complete.append({
                'type': 'task',
                'client': i.work_assign.client,
                'from_date': i.start_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.allocate_date,
                'team_lead': i.work_assign.team_lead,
                'status': i.status,
            })

        # Lead category completed works
        lead_completed = LeadCateogry_TeamAllocate.objects.filter(
            status=3,
            work_assign__company=cmp_id
        )

        for i in lead_completed:

            # skip duplicate WorkAssign
            if i.work_assign.id in added_work_ids:
                continue

            added_work_ids.add(i.work_assign.id)

            complete.append({
                'type': 'lead',
                'client': i.work_assign.client,
                'from_date': i.from_date,
                'due_date': i.due_date,
                'progress': i.progress,
                'assign_date': i.accept_date,
                'team_lead': i.team_lead,
                'status': i.status,
            })

    return render(request, 'dmhead/dm_completedwork.html', {
        'complete': complete,
        'name': log_emp
    })

def workprogress(request):
    user_id = request.session.get('hid')
    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        log_emp = EmployeeRegister_Details.objects.filter(login=user).first()
        cmp_id = log_emp.company
        clients=ClientRegister.objects.filter(company=cmp_id)
    return render(request,'dmhead/workprogress.html',{'clients':clients,'name': log_emp})


def clientworkdetails(request,pk):
    user_id = request.session.get('hid')
    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        log_emp = EmployeeRegister_Details.objects.filter(login=user).first()
        cmp_id = log_emp.company

    client=ClientRegister.objects.get(id=pk)
    wrk_reg=WorkRegister.objects.get(client=pk)
    
    tasks=ClientTask_Register.objects.filter(client=pk)
    return render(request,'dmhead/clientworkdetails.html',{'name': log_emp,'client':client,'tasks':tasks,'wrkreg':wrk_reg})

def clienttaskdetails(request, pk):
    user_id = request.session.get('hid')
    if user_id:
        user = LogRegister_Details.objects.get(log_username=user_id)
        log_emp = EmployeeRegister_Details.objects.filter(login=user).first()
        cmp_id = log_emp.company

    task = ClientTask_Register.objects.get(id=pk)

    tl = WorkAssign.objects.filter(client_task=pk)
    executive = TaskAssign.objects.filter(client_task=pk)

    tad = TaskDetails.objects.filter(
        Q(work_assign__in=tl) | Q(task_assign__in=executive)
    ).distinct()

    employee = request.GET.get("executive")
    date_filter = request.GET.get("from")

    if employee:
        tad = tad.filter(
            Q(task_assign__executive__name__icontains=employee) |
            Q(work_assign__team_lead__name__icontains=employee)
        ).distinct()

    if date_filter:
        try:
            selected_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            tad = tad.filter(collect_date=selected_date)
        except ValueError:
            pass

    # unique employee names
    employee_names = set()

    for i in tl:
        if i.team_lead:
            employee_names.add(i.team_lead.name)

        for j in i.co_workers.all():
            employee_names.add(j.name)
    
    total_target = tl.aggregate(total=Sum('target'))['total'] or 0


    total_achieved = tad.aggregate(total=Sum('verified_target'))['total'] or 0

  
    if total_target > 0:
        task_progress = round((total_achieved / total_target) * 100, 2)
    else:
        task_progress = 0

    return render(request, 'dmhead/clienttaskdetails.html', {
        'name': log_emp,
        'task': task,
        'tl': tl,
        'executive': executive,
        'tad': tad,
        'employee_names': sorted(employee_names),
        'task_progress': task_progress,
        'total_target': total_target,
        'total_achieved': total_achieved,
    })
    
def admin_resigned_employees_list(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
    except LogRegister_Details.DoesNotExist:
        messages.error(request, "Invalid admin session.")
        return redirect('login')

    company = (
        BusinessRegister_Details.objects.filter(email=str(user.id)).first()
        or BusinessRegister_Details.objects.filter(login=user).first()
    )

    resigned_list = EmployeeRegister_Details.objects.none()
    if company:
        resigned_list = (
            EmployeeRegister_Details.objects
            .select_related('company', 'department', 'designation', 'login')
            .filter(company_id=company.id)
            .exclude(active_status__in=['approved', 'pending', 'Approved', 'Pending'])
            .order_by('name')
        )

    context = {
        'user': user,
        'company': company,
        'resigned_list': resigned_list,
        'company_name': company.company_name if company else '',
    }
    return render(request, 'admin/admin_resigned_employees_list.html', context)


@require_GET
def admin_employee_details(request):
    company, resp = _get_admin_company(request)
    if resp:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    emp_id = request.GET.get("emp_id")
    if not emp_id:
        return JsonResponse({"success": False, "message": "emp_id required"}, status=400)

    emp = EmployeeRegister_Details.objects.filter(id=emp_id, company=company).first()
    if not emp:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    data = {
        "id": emp.id,
        "name": emp.name or "",
        "employee_code": getattr(emp, "employee_code", "") or "",
        "contact_number": getattr(emp, "contact_number", "") or "",
        "email": getattr(emp, "email", "") or "",
        "address_line1": getattr(emp, "address_line1", "") or "",
        "address_line2": getattr(emp, "address_line2", "") or "",
        "address_line3": getattr(emp, "address_line3", "") or "",
        "pin": getattr(emp, "pin", "") or "",
        "location": getattr(emp, "location", "") or "",
        "district": getattr(emp, "district", "") or "",
        "state": getattr(emp, "state", "") or "",
        "active_status": getattr(emp, "active_status", "") or "",
        "verification_status": 1 if getattr(emp, "verification_status", False) else 0,
    }
    return JsonResponse({"success": True, "employee": data})


@require_POST
def admin_employee_update(request):
    company, resp = _get_admin_company(request)
    if resp:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    emp_id = payload.get("emp_id")
    if not emp_id:
        return JsonResponse({"success": False, "message": "emp_id required"}, status=400)

    emp = EmployeeRegister_Details.objects.filter(id=emp_id, company=company).first()
    if not emp:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    editable_fields = [
        "name",
        "contact_number",
        "email",
        "address_line1",
        "address_line2",
        "address_line3",
        "pin",
        "location",
        "district",
        "state",
    ]

    dirty = []

    for f in editable_fields:
        if f in payload:
            setattr(emp, f, payload.get(f) or "")
            dirty.append(f)

    if payload.get("activate") is True:
        emp.active_status = "approved"
        dirty.append("active_status")

    if dirty:
        emp.save(update_fields=list(set(dirty)))

    return JsonResponse({"success": True, "message": "Updated", "active_status": emp.active_status})


def _get_admin_company(request):
    aid = request.session.get("aid")
    if not aid:
        return None, redirect("login")

    try:
        admin_user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=admin_user).first()
        if not company:
            return None, redirect("login")
        return company, None
    except LogRegister_Details.DoesNotExist:
        return None, redirect("login")


def _get_cached_designation_ids(request, company_id):
    cached = request.session.get("works_desig_ids")
    if not cached:
        return None

    if cached.get("company_id") != company_id:
        return None

    return {
        "dmh": cached.get("dmh"),
        "tl": cached.get("tl"),
        "exe": cached.get("exe"),
    }


def _set_cached_designation_ids(request, company_id, ids_map):
    request.session["works_desig_ids"] = {
        "company_id": company_id,
        "dmh": ids_map.get("dmh") or [],
        "tl": ids_map.get("tl") or [],
        "exe": ids_map.get("exe") or [],
    }


@require_GET
def admin_works(request):
    company, resp = _get_admin_company(request)
    if resp:
        return resp

    return render(request, "admin/admin_works.html", {"company": company})


@require_POST
def admin_works_counts(request):
    company, resp = _get_admin_company(request)
    if resp:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    posted_company_id = payload.get("company_id")
    if posted_company_id and str(posted_company_id) != str(company.id):
        return JsonResponse({"success": False, "message": "Company mismatch"}, status=400)

    cached_ids = _get_cached_designation_ids(request, company.id)

    if cached_ids is None:
        desigs = DesignationRegister_Details.objects.filter(
            business=company,
            dashboard_id__in=["Digital_Marketing_Head", "Team_Lead", "Executive"],
        ).values("id", "dashboard_id")

        ids_map = {"dmh": [], "tl": [], "exe": []}
        for d in desigs:
            if d["dashboard_id"] == "Digital_Marketing_Head":
                ids_map["dmh"].append(d["id"])
            elif d["dashboard_id"] == "Team_Lead":
                ids_map["tl"].append(d["id"])
            elif d["dashboard_id"] == "Executive":
                ids_map["exe"].append(d["id"])

        _set_cached_designation_ids(request, company.id, ids_map)
        cached_ids = ids_map

    head_count = EmployeeRegister_Details.objects.filter(
        company=company,
        active_status="approved",
        designation_id__in=cached_ids.get("dmh") or [],
    ).count()

    tl_count = EmployeeRegister_Details.objects.filter(
        company=company,
        active_status="approved",
        designation_id__in=cached_ids.get("tl") or [],
    ).count()

    exe_count = EmployeeRegister_Details.objects.filter(
        company=company,
        active_status="approved",
        designation_id__in=cached_ids.get("exe") or [],
    ).count()
    client_count = ClientRegister.objects.filter(company=company).count()

    return JsonResponse(
        {
            "success": True,
            "counts": {
                "head": head_count,
                "team_lead": tl_count,
                "executive": exe_count,
                "client": client_count,
            },
        }
    )


def _admin_company_from_session(request):
    aid = request.session.get("aid")
    if not aid:
        return None, None, redirect("login")
    try:
        user = LogRegister_Details.objects.get(log_username=aid)
    except LogRegister_Details.DoesNotExist:
        return None, None, redirect("login")
    company = BusinessRegister_Details.objects.filter(login=user).first()
    return user, company, None


def _parse_date_ymd(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except Exception:
        return None


def admin_head_works_page(request):
    user, company, redir = _admin_company_from_session(request)
    if redir:
        return redir

    context = {
        "user": user,
        "company": company,
        "name": EmployeeRegister_Details.objects.filter(login=user).first(),
    }
    return render(request, "admin/admin_head_works.html", context)


@require_GET
def admin_head_works_heads_api(request):
    user, company, redir = _admin_company_from_session(request)
    if redir:
        return redir

    if not company:
        return JsonResponse({"success": True, "heads": []})

    head_designations = DesignationRegister_Details.objects.filter(
        business=company,
        dashboard_id="Digital_Marketing_Head",
    ).values_list("id", flat=True)

    heads_qs = EmployeeRegister_Details.objects.filter(
        company=company,
        designation_id__in=list(head_designations),
        active_status__iexact="Approved",
    ).order_by("name")

    heads = [{"id": h.id, "name": h.name or "-"} for h in heads_qs]
    return JsonResponse({"success": True, "heads": heads})


@require_GET
def admin_head_works_clients_api(request):
    user, company, redir = _admin_company_from_session(request)
    if redir:
        return redir

    if not company:
        return JsonResponse({"success": True, "rows": []})

    from_date = _parse_date_ymd(request.GET.get("from"))
    to_date = _parse_date_ymd(request.GET.get("to"))

    qs = ClientRegister.objects.filter(company=company).order_by("-client_reg_date", "-id")

    if from_date:
        qs = qs.filter(client_reg_date__gte=from_date)
    if to_date:
        qs = qs.filter(client_reg_date__lte=to_date)

    rows = []
    for c in qs:
        rows.append({
            "registered_date": c.client_reg_date.strftime("%Y-%m-%d") if c.client_reg_date else "",
            "name": c.client_name or "-",
            "email": c.client_email_primary or "-",
            "phone": c.client_phone or "-",
            "place": c.client_place or "-",
            "district": c.client_district or "-",
            "state": c.client_state or "-",
        })

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_head_works_client_works_api(request):
    user, company, redir = _admin_company_from_session(request)
    if redir:
        return redir

    if not company:
        return JsonResponse({"success": True, "rows": []})

    from_date = _parse_date_ymd(request.GET.get("from"))
    to_date = _parse_date_ymd(request.GET.get("to"))

    work_qs = (
        WorkRegister.objects
        .filter(company=company)
        .select_related("client")
        .order_by("-work_create_date", "-id")
    )

    rows = []

    for w in work_qs:
        client = w.client
        if not client:
            continue

        tasks_qs = ClientTask_Register.objects.filter(
            company=company,
            client=client,
            work=w
        ).order_by("-task_create_date", "-id")

        if from_date:
            tasks_qs = tasks_qs.filter(task_create_date__gte=from_date)
        if to_date:
            tasks_qs = tasks_qs.filter(task_create_date__lte=to_date)

        for t in tasks_qs:
            tname = (t.task_name or "-").strip() or "-"
            client_name = client.client_name or "-"

            progress = int(t.task_total_progress or 0)
            status_text = "Completed" if int(t.task_status or 0) == 1 else "Ongoing"

            lead_cats = LeadCategory_Register.objects.filter(client_task_id=t.id)

            is_lead = (tname.lower() == "lead collection") or lead_cats.exists()

            if not is_lead:
                rows.append({
                    "registered_date": t.task_create_date.strftime("%Y-%m-%d") if t.task_create_date else "",
                    "client_name": client_name,
                    "task_name": tname,
                    "category_name": "",
                    "description": t.task_description or "-",
                    "progress": progress,
                    "work_status": status_text,
                })
                continue

            if not lead_cats.exists():
                rows.append({
                    "registered_date": t.task_create_date.strftime("%Y-%m-%d") if t.task_create_date else "",
                    "client_name": client_name,
                    "task_name": "Lead Collection",
                    "category_name": "",
                    "description": t.task_description or "-",
                    "progress": progress,
                    "work_status": status_text,
                })
                continue

            for cat in lead_cats:
                cat_name = "-"

                cf = getattr(cat, "collection_for", None)
                if cf is not None:
                    cat_name = getattr(cf, "category_name", None) or getattr(cf, "name", None) or str(cf) or "-"
                else:
                    cat_name = getattr(cat, "category_name", None) or getattr(cat, "lead_category_name", None) or "-"

                rows.append({
                    "registered_date": t.task_create_date.strftime("%Y-%m-%d") if t.task_create_date else "",
                    "client_name": client_name,
                    "task_name": "Lead Collection",
                    "category_name": cat_name,
                    "description": t.task_description or "-",
                    "progress": progress,
                    "work_status": status_text,
                })

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_head_works_assigned_api(request):
    user, company, redir = _admin_company_from_session(request)
    if redir:
        return redir

    if not company:
        return JsonResponse({"success": True, "rows": []})

    head_id = request.GET.get("head_id")
    from_date = _parse_date_ymd(request.GET.get("from"))
    to_date = _parse_date_ymd(request.GET.get("to"))

    if not head_id or not str(head_id).isdigit():
        return JsonResponse({"success": True, "rows": []})

    head_emp = (
        EmployeeRegister_Details.objects
        .filter(id=int(head_id), company=company)
        .select_related("department")
        .first()
    )

    if not head_emp or not head_emp.department_id:
        return JsonResponse({"success": True, "rows": []})

    tl_designation_ids = list(
        DesignationRegister_Details.objects.filter(
            business=company,
            dashboard_id="Team_Lead"
        ).values_list("id", flat=True)
    )

    tl_qs = EmployeeRegister_Details.objects.filter(
        company=company,
        department_id=head_emp.department_id,
        designation_id__in=tl_designation_ids,
        active_status__iexact="Approved",
    )

    tl_ids = list(tl_qs.values_list("id", flat=True))
    if not tl_ids:
        return JsonResponse({"success": True, "rows": []})

    qs = (
        WorkAssign.objects
        .filter(company=company, team_lead_id__in=tl_ids)
        .select_related("client", "work_register", "team_lead")
        .prefetch_related("co_workers")
        .order_by("-assign_date", "-id")
    )

    if from_date:
        qs = qs.filter(assign_date__gte=from_date)
    if to_date:
        qs = qs.filter(assign_date__lte=to_date)

    grouped = {}

    for w in qs:
        key = (
            w.client_id,
            w.work_register_id,
            w.assign_date,
            w.due_date,
        )

        if key not in grouped:
            grouped[key] = {
                "created_date": w.assign_date.strftime("%Y-%m-%d") if w.assign_date else "",
                "end_date": w.due_date.strftime("%Y-%m-%d") if w.due_date else "",
                "client": w.client.client_name if w.client else "-",
                "assigned_team_leads_set": set(),
                "progress": int(w.progress or 0),
                "work_status": "Completed" if int(w.status or 0) == 2 else "Ongoing",
            }

        if w.team_lead and w.team_lead.designation_id in tl_designation_ids:
            if w.team_lead.name:
                grouped[key]["assigned_team_leads_set"].add(w.team_lead.name)

        for cw in w.co_workers.all():
            if cw.designation_id in tl_designation_ids and cw.name:
                grouped[key]["assigned_team_leads_set"].add(cw.name)

        grouped[key]["progress"] = max(grouped[key]["progress"], int(w.progress or 0))
        if int(w.status or 0) == 3:
            grouped[key]["work_status"] = "Completed"

    rows = []
    for _, val in grouped.items():
        tls = sorted(list(val["assigned_team_leads_set"]))
        val["assigned_team_leads"] = ", ".join(tls) if tls else "-"
        del val["assigned_team_leads_set"]
        rows.append(val)

    return JsonResponse({"success": True, "rows": rows})

# ! admin : Team Lead

@require_GET
def admin_team_lead_works(request):
    aid = request.session.get("aid")
    if not aid:
        return render(request, "admin/admindash.html", {})

    user = LogRegister_Details.objects.filter(log_username=aid).first()
    company = BusinessRegister_Details.objects.filter(login=user).first() if user else None

    team_leads = EmployeeRegister_Details.objects.none()
    if company:
        teamlead_designation = DesignationRegister_Details.objects.filter(
            business=company,
            dashboard_id="Team_Lead",
        ).first()

        if teamlead_designation:
            team_leads = (
                EmployeeRegister_Details.objects
                .select_related("designation", "department")
                .filter(company=company, designation=teamlead_designation)
                .order_by("name")
            )

    return render(
        request,
        "admin/admin_team_lead_works.html",
        {"company": company, "team_leads": team_leads},
    )


def _parse_date_filters(request):
    return (request.GET.get("from_date") or ""), (request.GET.get("to_date") or "")


def _date_range_q(from_date, to_date, field_name="from_date"):
    q = Q()
    if from_date:
        q &= Q(**{f"{field_name}__gte": from_date})
    if to_date:
        q &= Q(**{f"{field_name}__lte": to_date})
    return q


def _tl_name(emp):
    return (emp.name or "-") if emp else "-"


def _get_exec_names_for_workassign(wa):
    exec_ids = set()

    exec_ids.update(
        TaskAssign.objects
        .filter(work_assign=wa)
        .exclude(executive__isnull=True)
        .values_list("executive_id", flat=True)
    )

    exec_ids.update(
        LeadCategory_Assign.objects
        .filter(
            Q(team_allocation__work_assign=wa) |
            Q(task_assign__work_assign=wa)
        )
        .exclude(executive__isnull=True)
        .values_list("executive_id", flat=True)
    )

    if not exec_ids:
        return []

    return list(
        EmployeeRegister_Details.objects
        .filter(id__in=list(exec_ids))
        .order_by("name")
        .values_list("name", flat=True)
    )


def _get_lead_categories_for_workassign(wa, tl_id):
    qs = (
        LeadCateogry_TeamAllocate.objects
        .select_related("lead_category")
        .filter(work_assign=wa, team_lead_id=tl_id)
        .order_by("id")
    )

    out = []
    for obj in qs:
        if obj.lead_category and obj.lead_category.collection_for:
            out.append(obj.lead_category.collection_for)
    return out


@require_GET
def admin_tl_works_assigned(request):
    company, resp = _get_admin_company(request)
    if resp:
        return resp

    tl_id = request.GET.get("team_lead_id")
    if not tl_id:
        return JsonResponse({"success": False, "message": "team_lead_id required"}, status=400)

    if not EmployeeRegister_Details.objects.filter(id=tl_id, company=company).exists():
        return JsonResponse({"success": True, "rows": []})

    from_date, to_date = _parse_date_filters(request)

    qs = (
        WorkAssign.objects
        .select_related("team_lead")
        .filter(company=company, team_lead_id=tl_id)
        .filter(_date_range_q(from_date, to_date, field_name="from_date"))
        .order_by("-id")
    )

    rows = []
    idx = 1
    for wa in qs:
        lead_categories = _get_lead_categories_for_workassign(wa, tl_id)

        if wa.assign_type == 0:
            executives_assigned = _tl_name(wa.team_lead)
        else:
            names = _get_exec_names_for_workassign(wa)
            executives_assigned = ", ".join([n for n in names if n]) if names else "Not allocated"

        rows.append({
            "no": idx,
            "start_date": wa.from_date.strftime("%d-%m-%Y") if wa.from_date else "-",
            "end_date": wa.due_date.strftime("%d-%m-%Y") if wa.due_date else "-",
            "executives_assigned": executives_assigned,
            "task": wa.description or "-",
            "target": wa.target if wa.target is not None else 0,
            "achieved_target": wa.target_achieved if wa.target_achieved is not None else 0,
            "progress": wa.progress if wa.progress is not None else 0,
            "lead_categories": lead_categories,
        })
        idx += 1

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_tl_works_ongoing(request):
    company, resp = _get_admin_company(request)
    if resp:
        return resp

    tl_id = request.GET.get("team_lead_id")
    if not tl_id:
        return JsonResponse({"success": False, "message": "team_lead_id required"}, status=400)

    if not EmployeeRegister_Details.objects.filter(id=tl_id, company=company).exists():
        return JsonResponse({"success": True, "rows": []})

    from_date, to_date = _parse_date_filters(request)

    qs = (
        WorkAssign.objects
        .select_related("team_lead")
        .filter(company=company, team_lead_id=tl_id, status=1)
        .filter(_date_range_q(from_date, to_date, field_name="from_date"))
        .order_by("-id")
    )

    rows = []
    idx = 1
    for wa in qs:
        rows.append({
            "no": idx,
            "id": wa.id,
            "start_date": wa.from_date.strftime("%d-%m-%Y") if wa.from_date else "-",
            "end_date": wa.due_date.strftime("%d-%m-%Y") if wa.due_date else "-",
            "task_name": wa.description or "-",
            "progress": wa.progress if wa.progress is not None else 0,
            "status_text": "Ongoing",
        })
        idx += 1

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_tl_works_completed(request):
    company, resp = _get_admin_company(request)
    if resp:
        return resp

    tl_id = request.GET.get("team_lead_id")
    if not tl_id:
        return JsonResponse({"success": False, "message": "team_lead_id required"}, status=400)

    if not EmployeeRegister_Details.objects.filter(id=tl_id, company=company).exists():
        return JsonResponse({"success": True, "rows": []})

    from_date, to_date = _parse_date_filters(request)

    qs = (
        WorkAssign.objects
        .select_related("team_lead")
        .filter(company=company, team_lead_id=tl_id, status=2)
        .filter(_date_range_q(from_date, to_date, field_name="from_date"))
        .order_by("-id")
    )

    rows = []
    idx = 1
    for wa in qs:
        rows.append({
            "no": idx,
            "id": wa.id,
            "start_date": wa.from_date.strftime("%d-%m-%Y") if wa.from_date else "-",
            "end_date": wa.due_date.strftime("%d-%m-%Y") if wa.due_date else "-",
            "task_name": wa.description or "-",
            "progress": wa.progress if wa.progress is not None else 0,
            "status_text": "Completed",
        })
        idx += 1

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_tl_work_daily_details(request):
    company, resp = _get_admin_company(request)
    if resp:
        return resp

    work_assign_id = request.GET.get("work_assign_id")
    if not work_assign_id:
        return JsonResponse({"success": False, "message": "work_assign_id required"}, status=400)

    if not WorkAssign.objects.filter(id=work_assign_id, company=company).exists():
        return JsonResponse({"success": True, "rows": []})

    qs = (
        TaskDetails.objects
        .filter(work_assign_id=work_assign_id, work_assign__company=company)
        .order_by("-id")
    )

    rows = []
    idx = 1
    for d in qs:
        rows.append({
            "no": idx,
            "date": d.collect_date.strftime("%d-%m-%Y") if d.collect_date else "-",
            "title": d.title or "-",
            "description": d.description or "-",
            "achieved_target": d.achieved_target if d.achieved_target is not None else 0,
            "verified_target": d.verified_target if d.verified_target is not None else 0,
            "status": d.status,
        })
        idx += 1

    return JsonResponse({"success": True, "rows": rows})


# ! admin : Executive
@require_GET
def executive_works(request):
    aid = request.session.get("aid")
    if not aid:
        return redirect("/")

    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    executives = EmployeeRegister_Details.objects.none()
    if company:
        executives = (
            EmployeeRegister_Details.objects
            .select_related("designation")
            .filter(company=company, designation__dashboard_id="Executive")
            .order_by("name")
        )

    return render(request, "admin/admin_executive_works.html", {
        "user": user,
        "company": company,
        "name": name,
        "executives": executives,
    })


@require_GET
def executive_works_list(request):
    company, resp = _get_admin_company(request)
    if resp:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    executive_id = request.GET.get("executive_id")
    mode = (request.GET.get("mode") or "ongoing").lower()
    from_date = request.GET.get("from") or None
    to_date = request.GET.get("to") or None

    if not executive_id:
        return JsonResponse({"success": False, "message": "executive_id required"}, status=400)

    exec_emp = EmployeeRegister_Details.objects.filter(id=executive_id, company=company).first()
    if not exec_emp:
        return JsonResponse({"success": False, "message": "Executive not found"}, status=404)

    completed = (mode == "completed")

    ta = TaskAssign.objects.filter(executive=exec_emp, work_assign__company=company)
    ta = ta.filter(status=2) if completed else ta.exclude(status=2)

    if from_date:
        ta = ta.filter(start_date__gte=from_date)
    if to_date:
        ta = ta.filter(start_date__lte=to_date)

    lca = LeadCategory_Assign.objects.filter(
        executive=exec_emp
    ).filter(
        Q(team_allocation__work_assign__company=company) | Q(task_assign__work_assign__company=company)
    )
    lca = lca.filter(status=1) if completed else lca.exclude(status=1)

    if from_date:
        lca = lca.filter(from_date__gte=from_date)
    if to_date:
        lca = lca.filter(from_date__lte=to_date)

    rows = []

    for x in ta:
        rows.append({
            "start_date": x.start_date.isoformat() if x.start_date else "",
            "end_date": x.due_date.isoformat() if x.due_date else "",
            "task_name": (x.description or "").strip() or "-",
            "description": x.description or "",
            "progress": int(x.progress or 0),
            "task_assign_id": x.id,
        })

    for x in lca:
        category = ""
        ta_id = x.team_allocation_id
        if ta_id:
            alloc = LeadCateogry_TeamAllocate.objects.filter(id=ta_id, work_assign__company=company).first()
            if alloc and alloc.lead_category_id:
                cat = LeadCategory_Register.objects.filter(id=alloc.lead_category_id).first()
                if cat:
                    category = cat.collection_for or ""

        rows.append({
            "start_date": x.from_date.isoformat() if x.from_date else "",
            "end_date": x.due_date.isoformat() if x.due_date else "",
            "task_type": "lead",
            "category": category,
            "progress": int(x.progress or 0),
            "task_assign_id": x.task_assign_id if x.task_assign_id else None,
        })

    rows.sort(key=lambda r: r["start_date"] or "0000-00-00", reverse=True)

    return JsonResponse({
        "success": True,
        "rows": rows,
        "status_text": "Completed" if completed else "Ongoing",
        "status_class": "text-success" if completed else "text-warning",
    })


@require_GET
def executive_daily_works(request):
    company, resp = _get_admin_company(request)
    if resp:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    task_assign_id = request.GET.get("task_assign_id")
    mode = (request.GET.get("mode") or "ongoing").lower()

    if not task_assign_id:
        return JsonResponse({"success": False, "message": "task_assign_id required"}, status=400)

    if not TaskAssign.objects.filter(id=task_assign_id, work_assign__company=company).exists():
        return JsonResponse({"success": True, "items": []})

    qs = TaskDetails.objects.filter(task_assign_id=task_assign_id, task_assign__work_assign__company=company).order_by("-collect_date", "-id")
    status_label = "Verified" if mode == "completed" else "Pending"

    items = []
    for d in qs:
        items.append({
            "date": d.collect_date.isoformat() if d.collect_date else "",
            "title": d.title or "",
            "description": d.description or "",
            "achieved_target": int(d.achieved_target or 0),
            "verified_target": int(d.verified_target or 0),
            "status": status_label,
        })

    return JsonResponse({"success": True, "items": items})

# ! Admin Clients
def _get_int_param(request, key):
    v = request.GET.get(key)
    if v is None or str(v).strip() == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _require_client_id(request):
    cid = _get_int_param(request, "client_id")
    if cid is None:
        return None, JsonResponse({"success": False, "message": "client_id required"}, status=400)
    return cid, None
    
def admin_clients(request):
    user, company = _get_admin_user_company(request)
    if not user or not company:
        return redirect("login")

    work_count_sq = (
        WorkRegister.objects
        .filter(company=company, client=OuterRef("pk"))
        .values("client").annotate(c=Count("id")).values("c")
    )
    work_done_sq = (
        WorkRegister.objects
        .filter(company=company, client=OuterRef("pk"), work_status=1)
        .values("client").annotate(c=Count("id")).values("c")
    )
    work_alloc_sq = (
        WorkRegister.objects
        .filter(company=company, client=OuterRef("pk"), work_allocate_status=1)
        .values("client").annotate(c=Count("id")).values("c")
    )

    task_count_sq = (
        ClientTask_Register.objects
        .filter(company=company, client=OuterRef("pk"))
        .values("client").annotate(c=Count("id")).values("c")
    )
    task_done_sq = (
        ClientTask_Register.objects
        .filter(company=company, client=OuterRef("pk"), task_status=1)
        .values("client").annotate(c=Count("id")).values("c")
    )
    task_alloc_sq = (
        ClientTask_Register.objects
        .filter(company=company, client=OuterRef("pk"), task_allocate_status=1)
        .values("client").annotate(c=Count("id")).values("c")
    )

    qs = (
        ClientRegister.objects
        .filter(company=company)
        .annotate(
            work_count=Coalesce(Subquery(work_count_sq, output_field=IntegerField()), Value(0)),
            work_done=Coalesce(Subquery(work_done_sq, output_field=IntegerField()), Value(0)),
            work_alloc=Coalesce(Subquery(work_alloc_sq, output_field=IntegerField()), Value(0)),
            task_count=Coalesce(Subquery(task_count_sq, output_field=IntegerField()), Value(0)),
            task_done=Coalesce(Subquery(task_done_sq, output_field=IntegerField()), Value(0)),
            task_alloc=Coalesce(Subquery(task_alloc_sq, output_field=IntegerField()), Value(0)),
        )
    )

    completed_q = (
        Q(work_count__gt=0, work_done=F("work_count")) |
        Q(work_count=0, task_count__gt=0, task_done=F("task_count"))
    )

    new_count = qs.filter(work_count=0, task_count=0).count()
    completed_count = qs.filter(completed_q).count()
    ongoing_count = (
        qs.exclude(work_count=0, task_count=0)
          .exclude(completed_q)
          .filter(Q(work_alloc__gt=0) | Q(task_alloc__gt=0))
          .count()
    )

    return render(request, "admin/admin_clients.html", {
        "new_count": new_count,
        "ongoing_count": ongoing_count,
        "completed_count": completed_count,
    })


def _get_admin_user_company(request):
    aid = request.session.get("aid")
    if not aid:
        return None, None

    user = LogRegister_Details.objects.filter(log_username=aid).first()
    if not user:
        return None, None

    company = BusinessRegister_Details.objects.filter(login=user).first()
    return user, company


def admin_clients_new(request):
    user, company = _get_admin_user_company(request)
    if not user or not company:
        return redirect("login")

    return render(
        request,
        "admin/admin_clients_new.html",
        {
            "company": company,
        },
    )


@require_GET
def admin_clients_new_data(request):
    user, company = _get_admin_user_company(request)
    if not user or not company:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    from_date = request.GET.get("from_date") or ""
    to_date = request.GET.get("to_date") or ""

    has_task_qs = ClientTask_Register.objects.filter(client=OuterRef("pk"))

    qs = (
        ClientRegister.objects.filter(company=company)
        .annotate(has_task=Exists(has_task_qs))
        .filter(has_task=False)
    )

    if from_date and to_date:
        qs = qs.filter(client_reg_date__range=[from_date, to_date])
    elif from_date:
        qs = qs.filter(client_reg_date__gte=from_date)
    elif to_date:
        qs = qs.filter(client_reg_date__lte=to_date)

    qs = qs.order_by("-id")

    rows = []
    for c in qs:
        rows.append(
            {
                "id": c.id,
                "reg_date": c.client_reg_date.strftime("%Y-%m-%d") if c.client_reg_date else "",
                "name": c.client_name or "-",
                "email": c.client_email_primary or "-",
                "phone": c.client_phone or "-",
                "place": c.client_place or "-",
                "district": c.client_district or "-",
                "state": c.client_state or "-",
                "status": int(c.client_status or 0),
            }
        )

    return JsonResponse({"success": True, "data": rows})


def _get_company_from_aid(request):
    aid = request.session.get("aid") or getattr(getattr(request, "user", None), "email", None)
    if not aid:
        return None
    return BusinessRegister_Details.objects.filter(email=aid).first()


def _parse_date(s):
    s = (s or "").strip()
    return s if s else None


def _date_range_filter(qs, field_name, from_date, to_date):
    if from_date:
        qs = qs.filter(**{f"{field_name}__gte": from_date})
    if to_date:
        qs = qs.filter(**{f"{field_name}__lte": to_date})
    return qs


def _clamp_progress(v):
    try:
        v = int(v or 0)
    except Exception:
        v = 0
    return max(0, min(100, v))


def _assigned_people_for_work(work):

    workassign_qs = WorkAssign.objects.filter(work_register_id=work.id)

    seen = set()
    names = []

    def add_emp(emp, label):
        if not isinstance(emp, EmployeeRegister_Details):
            return
        eid = emp.id
        if eid in seen:
            return
        seen.add(eid)
        nm = getattr(emp, "name", None)
        if isinstance(nm, str) and nm.strip():
            names.append(nm.strip())

    def to_int(v):
        try:
            if v is None:
                return 0
            if isinstance(v, str):
                v = v.strip()
                if not v:
                    return 0
            return int(float(v))
        except Exception:
            return 0

    target_sum = 0
    achieved_sum = 0

    for wa in workassign_qs:

        add_emp(getattr(wa, "team_lead", None), "workassign.team_lead")

        for cw in wa.co_workers.all():
            add_emp(cw, "workassign.co_workers")

        target_sum += to_int(getattr(wa, "target", 0))
        achieved_sum += to_int(getattr(wa, "target_achieved", 0))

        ta_qs = TaskAssign.objects.filter(work_assign_id=wa.id).select_related("executive")

        for ta in ta_qs:
            add_emp(getattr(ta, "executive", None), "taskassign.executive")

    people = ", ".join(names) if names else "-"
    return people, target_sum, achieved_sum


def _team_lead_names_only(company, allocated_m2m):
    tl_desig_ids = set(
        DesignationRegister_Details.objects.filter(business=company, dashboard_id="Team_Lead")
        .values_list("id", flat=True)
    )
    names = []
    try:
        for emp in allocated_m2m.all():
            if emp and emp.designation_id in tl_desig_ids:
                if emp.name:
                    names.append(emp.name)
    except Exception:
        pass
    return ", ".join(names) if names else "Not Assigned"


@require_GET
def admin_ongoing_clients_page(request):
    return render(request, "admin/admin_ongoing_clients.html")


@require_GET
def admin_api_ongoing_clients_dropdown(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "clients": [], "message": "Company not found"}, status=401)

    client_ids = (
        WorkAssign.objects
        .filter(company=company)
        .exclude(status=2)
        .values_list("client_id", flat=True)
        .distinct()
    )

    qs = (
        ClientRegister.objects
        .filter(company=company, id__in=client_ids)
        .order_by("client_name")
        .values("id", "client_name")
    )

    clients = [{"id": c["id"], "name": c["client_name"] or f"Client #{c['id']}"} for c in qs]
    return JsonResponse({"success": True, "clients": clients})

def _assigned_people_for_workassign(company, wa, tl_desig_ids, exec_desig_ids):
    seen = set()
    names = []

    def add_emp(emp):
        if not isinstance(emp, EmployeeRegister_Details):
            return
        if emp.id in seen:
            return
        if emp.name and str(emp.name).strip():
            seen.add(emp.id)
            names.append(emp.name.strip())

    if wa.team_lead_id:
        if not tl_desig_ids or wa.team_lead.designation_id in tl_desig_ids:
            add_emp(wa.team_lead)

    for cw in wa.co_workers.all():
        if not tl_desig_ids or cw.designation_id in tl_desig_ids:
            add_emp(cw)

    if int(wa.assign_type or 0) == 1:
        ta_qs = (
            TaskAssign.objects
            .filter(work_assign_id=wa.id)
            .select_related("executive")
        )
        for ta in ta_qs:
            ex = getattr(ta, "executive", None)
            if not ex:
                continue
            if exec_desig_ids and ex.designation_id not in exec_desig_ids:
                continue
            add_emp(ex)

    return ", ".join(names) if names else "-"


def _workassign_rows(company, client_id, from_date, to_date, extra_filters):
    tl_desig_ids = set(
        DesignationRegister_Details.objects
        .filter(business=company, dashboard_id="Team_Lead")
        .values_list("id", flat=True)
    )
    exec_desig_ids = set(
        DesignationRegister_Details.objects
        .filter(business=company, dashboard_id="Executive")
        .values_list("id", flat=True)
    )

    qs = (
        WorkAssign.objects
        .filter(company=company, client_id=client_id, **extra_filters)
        .select_related("team_lead")
        .prefetch_related("co_workers")
        .order_by("-assign_date", "-id")
    )
    qs = _date_range_filter(qs, "assign_date", from_date, to_date)

    lead_allocs = (
        LeadCateogry_TeamAllocate.objects
        .filter(work_assign__in=qs)
        .select_related("lead_category")
        .values("work_assign_id", "lead_category__collection_for")
    )

    lead_map = {}
    for row in lead_allocs:
        wid = row.get("work_assign_id")
        nm = row.get("lead_category__collection_for") or ""
        if not wid:
            continue
        if wid not in lead_map:
            lead_map[wid] = []
        if nm.strip():
            lead_map[wid].append(nm.strip())

    rows = []
    for wa in qs:
        target_sum = int(wa.target or 0)
        achieved_sum = int(wa.target_achieved or 0)
        progress = _calc_progress_from_target(target_sum, achieved_sum)

        lead_names = lead_map.get(wa.id, [])
        people = _assigned_people_for_workassign(company, wa, tl_desig_ids, exec_desig_ids)

        rows.append({
            "assigned_date": str(wa.assign_date) if wa.assign_date else "-",
            "start_date": str(wa.from_date) if wa.from_date else "-",
            "end_date": str(wa.due_date) if wa.due_date else "-",
            "task_name": wa.description or "-",
            "executives_assigned": people,
            "target": target_sum,
            "achieved": achieved_sum,
            "progress": progress,
            "lead_collections": lead_names,
            "is_lead_collection": True if lead_names else False,
        })

    return rows
    
@require_GET
def admin_api_oc_registered_works(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "rows": [], "message": "Company not found"}, status=401)

    client_id = request.GET.get("client_id")
    if not client_id:
        return JsonResponse({"success": True, "rows": []})

    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    qs = WorkRegister.objects.filter(company=company, client_id=client_id).order_by("-work_create_date")
    qs = _date_range_filter(qs, "work_create_date", from_date, to_date)

    rows = []
    for w in qs:
        rows.append({
            "create_date": str(w.work_create_date) if w.work_create_date else "-",
            "end_date": str(w.work_end_date) if w.work_end_date else "-",
            "team_leads": _team_lead_names_only(company, w.allocated_employees),
            "progress": _clamp_progress(w.work_progress),
            "work_status": int(w.work_status or 0),
        })

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_api_oc_client_tasks(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "rows": [], "message": "Company not found"}, status=401)

    client_id, err = _require_client_id(request)
    if err:
        return err

    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    qs = (
        ClientTask_Register.objects
        .filter(company=company, client_id=client_id)
        .order_by("-task_create_date")
    )
    qs = _date_range_filter(qs, "task_create_date", from_date, to_date)

    cats = (
        LeadCategory_Register.objects
        .filter(client_task__in=qs)
        .values("client_task_id", "collection_for")
        .order_by("collection_for")
    )

    cat_map = {}
    for c in cats:
        tid = c.get("client_task_id")
        nm = (c.get("collection_for") or "").strip()
        if not tid:
            continue
        cat_map.setdefault(tid, [])
        if nm:
            cat_map[tid].append(nm)

    rows = []
    for t in qs:
        rows.append({
            "register_date": str(t.task_create_date) if t.task_create_date else "-",
            "task_name": t.task_name or "-",
            "description": t.task_description or "-",
            "progress": _clamp_progress(t.task_total_progress),
            "task_status": int(t.task_status or 0),
            "lead_categories": cat_map.get(t.id, []),
            "is_lead_collection": True if cat_map.get(t.id) else False,
        })

    return JsonResponse({"success": True, "rows": rows})


def _calc_progress_from_target(target_sum, achieved_sum):
    try:
        t = int(target_sum or 0)
        a = int(achieved_sum or 0)
    except Exception:
        return 0
    if t <= 0:
        return 0
    pct = int(round((a * 100) / t))
    return max(0, min(100, pct))


@require_GET
def admin_api_oc_assigned_works(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "rows": [], "message": "Company not found"}, status=401)

    client_id, err = _require_client_id(request)
    if err:
        return err

    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    rows = _workassign_rows(company, client_id, from_date, to_date, extra_filters={"status": 0})
    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_api_oc_ongoing_works(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "rows": [], "message": "Company not found"}, status=401)

    client_id, err = _require_client_id(request)
    if err:
        return err

    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    rows = _workassign_rows(company, client_id, from_date, to_date, extra_filters={"status": 1})
    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_api_oc_completed_works(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "rows": [], "message": "Company not found"}, status=401)

    client_id, err = _require_client_id(request)
    if err:
        return err

    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    rows = _workassign_rows(company, client_id, from_date, to_date, extra_filters={"status": 2})
    return JsonResponse({"success": True, "rows": rows})


@require_GET
def admin_completed_clients_page(request):
    
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    return render(request, 'admin/admin_completed_clients.html', {
        'user': user,
        'company': company,
        'name': name,
    })


@require_GET
def admin_completed_clients_data(request):
    company = _get_company_from_aid(request)
    if not company:
        return JsonResponse({"success": False, "clients": [], "rows": [], "message": "Company not found"}, status=401)

    client_id = request.GET.get("client_id") or ""
    from_date = _parse_date(request.GET.get("from_date"))
    to_date = _parse_date(request.GET.get("to_date"))

    base = (
        ClientRegister.objects
        .filter(company=company)
        .annotate(
            total_works=Count("workregister", filter=Q(workregister__company=company)),
            completed_works=Count("workregister", filter=Q(workregister_company=company, workregister_work_status=1)),
        )
        .filter(total_works__gt=0, total_works=F("completed_works"))
        .order_by("client_name")
    )

    clients = list(base.values("id", "client_name"))

    qs = base
    if client_id:
        qs = qs.filter(id=client_id)

    if from_date:
        qs = qs.filter(client_reg_date__gte=from_date)
    if to_date:
        qs = qs.filter(client_reg_date__lte=to_date)

    rows = []
    for c in qs:
        rows.append({
            "registered_date": str(c.client_reg_date) if c.client_reg_date else "-",
            "client_name": c.client_name or "-",
            "email": c.client_email_primary or "-",
            "phone": c.client_phone or "-",
            "place": c.client_place or "-",
            "district": c.client_district or "-",
            "state": c.client_state or "-",
            "status": "Completed",
        })

    return JsonResponse({"success": True, "clients": clients, "rows": rows})
    
def _get_head_scope(request):
    print("[TL_SCOPE] called")

    user_id = request.session.get("hid")
    if not user_id:
        print("[TL_SCOPE] hid missing in session")
        return None, None, None, None

    try:
        user = LogRegister_Details.objects.get(log_username=user_id)
    except LogRegister_Details.DoesNotExist:
        print("[TL_SCOPE] LogRegister not found for hid:", user_id)
        return None, None, None, None

    head = EmployeeRegister_Details.objects.filter(login=user).first()
    if not head:
        print("[TL_SCOPE] EmployeeRegister not found for login user")
        return None, None, None, None

    company_id = head.company_id
    department_id = head.department_id

    if not company_id or not department_id:
        print("[TL_SCOPE] company_id / department_id missing on head")
        return head, None, None, None

    tl_desig = DesignationRegister_Details.objects.filter(
        business_id=company_id,
        department_id=department_id,
        dashboard_id="Team_Lead"
    ).first()

    if not tl_desig:
        print("[TL_SCOPE] TL designation not found")
        return head, company_id, department_id, []

    tl_ids = list(
        EmployeeRegister_Details.objects.filter(
            company_id=company_id,
            department_id=department_id,
            designation_id=tl_desig.id
        ).values_list("id", flat=True)
    )

    if not tl_ids:
        print("[TL_SCOPE] No Team Leads found for designation:", tl_desig.id)

    return head, company_id, department_id, tl_ids


@require_GET
def tl_individual_works_page(request):
    print("[TL_PAGE] page hit")

    user_id = request.session.get("hid")
    if not user_id:
        print("[TL_PAGE] hid missing")
        return render(request, "dmhead/tl_individual_works.html", {"name": None})

    user = LogRegister_Details.objects.get(log_username=user_id)
    log_emp = EmployeeRegister_Details.objects.filter(login=user).first()

    if not log_emp:
        print("[TL_PAGE] employee not found")

    return render(request, "dmhead/tl_individual_works.html", {"name": log_emp})


@require_GET
def tl_individual_works_data(request):
    head, company_id, dept_id, tl_ids = _get_head_scope(request)
    if not company_id:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    if not tl_ids:
        return JsonResponse({"success": True, "rows": []})

    qs = WorkAssign.objects.filter(
        company=company_id,
        assign_type=0,
        team_lead_id__in=tl_ids
    ).select_related("client").order_by("-id")

    rows = []
    for w in qs:
        emp_name = ""
        if getattr(w, "team_lead_id", None):
            emp = EmployeeRegister_Details.objects.filter(id=w.team_lead_id).first()
            emp_name = emp.name if emp else ""

        client_name = ""
        if getattr(w, "client", None):
            client_name = getattr(w.client, "client_name", "") or ""
        elif getattr(w, "client_id", None):
            c = ClientRegister.objects.filter(id=w.client_id).first()
            client_name = c.client_name if c else ""

        task_text = ""
        task_html = ""

        tasks = []
        try:
            tasks = list(w.client_task.all())
        except Exception:
            print("[TL_DATA] client_task relation failed for WorkAssign:", w.id)

        lead_task = None
        normal_task_names = []

        for t in tasks:
            nm = (getattr(t, "task_name", "") or "").strip()
            if nm.lower() == "lead collection":
                lead_task = nm or "Lead Collection"
            elif nm:
                normal_task_names.append(nm)

        if lead_task:

            cat_names = []
            try:
                cats_qs = LeadCateogry_TeamAllocate.objects.filter(
                    work_assign_id=w.id
                ).select_related("lead_category")

                for rec in cats_qs:
                    lead = getattr(rec, "lead_category", None)
                    nm = (getattr(lead, "collection_for", "") or "").strip()
                    if nm:
                        cat_names.append(nm)
            except Exception:
                print("[TL_DATA] LeadCateogry_TeamAllocate failed for WorkAssign:", w.id)

            title = escape(lead_task)
            if cat_names:
                li = "".join([f"<li>{escape(x)}</li>" for x in cat_names])
                task_html = f"{title}<ul class='lc_list mb-0 ps-3'>{li}</ul>"
            else:
                task_html = title

            task_text = lead_task  # fallback (not used if task_html present)

        else:
            if normal_task_names:
                task_text = normal_task_names[0]
            else:
                task_text = (getattr(w, "description", "") or "").strip()

        rows.append({
            "id": w.id,
            "employee": emp_name,
            "client_name": client_name,
            "task": task_text,
            "task_html": task_html,  # only filled for Lead Collection
            "start_date": w.from_date.strftime("%d-%b-%y") if getattr(w, "from_date", None) else "",
            "due_date": w.due_date.strftime("%d-%b-%y") if getattr(w, "due_date", None) else "",
            "progress": int(getattr(w, "progress", 0) or 0),
        })

    return JsonResponse({"success": True, "rows": rows})


@require_GET
def tl_individual_task_details(request, work_id):
    print("[TL_TASK_DETAILS] work_id:", work_id)

    head, company_id, dept_id, tl_ids = _get_head_scope(request)

    w = WorkAssign.objects.filter(
        company=company_id,
        assign_type=0,
        id=work_id,
        team_lead_id__in=tl_ids
    ).first()

    if not w:
        print("[TL_TASK_DETAILS] work not found / out of scope")
        return JsonResponse({"success": False}, status=404)

    client = ClientRegister.objects.filter(id=w.client_id).first()

    task_names = list(w.client_task.values_list("task_name", flat=True))
    task_names = [(t or "").strip() for t in task_names if (t or "").strip()]
    has_lead = any(t.lower() == "lead collection" for t in task_names)

    task_text = ""
    task_html = ""

    if not has_lead:
        task_text = ", ".join(task_names) if task_names else (w.description or "")
    else:
        cats = []
        qs = LeadCateogry_TeamAllocate.objects.filter(work_assign_id=w.id).select_related("lead_category")
        for rec in qs:
            lead = getattr(rec, "lead_category", None)
            name = ""
            if lead:
                name = getattr(lead, "collection_for", "") or getattr(lead, "category_name", "") or getattr(lead, "name", "")
            name = (name or "").strip()
            if name:
                cats.append(name)

        task_text = "Lead Collection"
        if cats:
            li = "".join([f"<li>{c}</li>" for c in cats])
            task_html = f"""
              <div class="lc_wrap">
                <div class="fw-semibold">Lead Collection</div>
                <ul class="lc_list ps-3 mb-0">{li}</ul>
              </div>
            """.strip()
        else:
            task_html = """
              <div class="lc_wrap">
                <div class="fw-semibold">Lead Collection</div>
              </div>
            """.strip()

    promo = []
    if w.is_instagram:
        promo.append({"platform": "Instagram", "target": w.instagram_target})
    if w.is_facebook:
        promo.append({"platform": "Facebook", "target": w.facebook_target})
    if w.is_x:
        promo.append({"platform": "Twitter", "target": w.x_target})

    return JsonResponse({
        "success": True,
        "data": {
            "client_name": client.client_name if client else "",
            "task_name": task_text,
            "task_text": task_text,
            "task_html": task_html,
            "allocated_date": w.assign_date.strftime("%d %B %Y") if w.assign_date else "",
            "accepted_date": w.accept_date.strftime("%d %B %Y") if w.accept_date else "",
            "description": w.description or "",
            "task_target": int(getattr(w, "target", 0) or 0),
            "achieved_target": int(getattr(w, "target_achieved", 0) or 0),
            "promo_any": bool(promo),
            "promo": promo,
        }
    })


@require_GET
def tl_individual_work_details(request, work_id):
    print("[TL_WORK_DETAILS] work_id:", work_id)

    head, company_id, dept_id, tl_ids = _get_head_scope(request)

    w = WorkAssign.objects.filter(
        company=company_id,
        assign_type=0,
        id=work_id,
        team_lead_id__in=tl_ids
    ).first()

    if not w:
        print("[TL_WORK_DETAILS] work not found / out of scope")
        return JsonResponse({"success": False}, status=404)

    qs = TaskDetails.objects.filter(work_assign=w).order_by("-collect_date")

    print("[TL_WORK_DETAILS] task details count:", qs.count())
    

    rows = []

   
    is_lead_collection = False

    try:
        is_lead_collection = w.client_task.filter(
            task_name__iexact="Lead Collection"
        ).exists()
    except:
        pass

    for t in qs:

        target_value = int(getattr(t, "target", 0) or 0)

       
        if is_lead_collection and target_value == 0:
            category_target = LeadCateogry_TeamAllocate.objects.filter(
                work_assign=w
            ).aggregate(total=Sum('target'))

            target_value = category_target['total'] or 0

        rows.append({
            "id": t.id,
            "date": t.collect_date.strftime("%d-%b-%y") if t.collect_date else "",
            "title": t.title or "",
            "description": t.description or "",
            "file": t.file.url if t.file else "",
            "target": target_value,
            "achieved_targets": int(
                getattr(t, "achieved_target", 0)
                or getattr(t, "achieved_targets", 0)
                or 0
            ),
            "verified_targets": int(
                getattr(t, "verified_target", 0)
                or getattr(t, "verified_targets", 0)
                or 0
            ),
            "status": int(getattr(t, "status", 0) or 0),
            "has_promo": SocialMediaPromotion.objects.filter(task_detail=t).exists(),
        })

    return JsonResponse({"success": True, "rows": rows})

@require_GET
def tl_individual_promotion_details(request, task_detail_id):
    print("[TL_PROMO] task_detail_id:", task_detail_id)

    head, company_id, dept_id, tl_ids = _get_head_scope(request)

    td = TaskDetails.objects.filter(id=task_detail_id).first()
    if not td:
        print("[TL_PROMO] task detail not found")
        return JsonResponse({"success": False}, status=404)

    w = getattr(td, "work_assign", None)
    if not w:
        w = WorkAssign.objects.filter(id=getattr(td, "work_assign_id", None)).first()

    promos = SocialMediaPromotion.objects.filter(task_detail=td)

    if not promos.exists():
        print("[TL_PROMO] no promotion rows")

    def get_target_for_platform(platform):
        p = (platform or "").strip().lower()

        if p in ["instagram", "insta"]:
            if getattr(w, "is_instagram", False):
                return int(getattr(w, "instagram_target", 0) or 0)
            return 0

        if p in ["facebook", "fb"]:
            if getattr(w, "is_facebook", False):
                return int(getattr(w, "facebook_target", 0) or 0)
            return 0

        if p in ["twitter", "x"]:
            if getattr(w, "is_x", False):
                return int(getattr(w, "x_target", 0) or 0)
            return 0

        return 0

    rows = []
    for p in promos:
        rows.append({
            "platform": p.platform,
            "target": get_target_for_platform(p.platform),
            "achieved_text": p.achieved_text,
            "remarks": p.remarks,
            "urls": p.urls,
            "screenshots": p.screenshots.url if p.screenshots else "",
        })

    return JsonResponse({"success": True, "rows": rows})



@require_POST
def tl_individual_verify_save(request):
    head, company_id, dept_id, tl_ids = _get_head_scope(request)
    if not company_id:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    task_detail_id = (request.POST.get("task_detail_id") or "").strip()
    verified_val = (request.POST.get("verified_targets") or "").strip()

    try:
        task_detail_id = int(task_detail_id)
        new_verified = int(verified_val)
    except:
        return JsonResponse({"success": False, "message": "Invalid data"}, status=400)

    td = TaskDetails.objects.filter(id=task_detail_id).first()
    if not td:
        return JsonResponse({"success": False, "message": "Task detail not found"}, status=404)

    work_id = getattr(td, "work_assign_id", None)
    if not work_id:
        return JsonResponse({"success": False, "message": "Task not found"}, status=404)

    w = WorkAssign.objects.filter(
        company_id=company_id,
        assign_type=0,
        id=work_id,
        team_lead_id__in=tl_ids
    ).first()
    if not w:
        return JsonResponse({"success": False, "message": "Task not found"}, status=404)

    old_verified = int(getattr(td, "verified_target", 0) or 0)
    delta = new_verified - old_verified

    td_target = getattr(td, "target", None)
    if td_target is None:
        td_target = getattr(td, "task_target", 0)
    td_target = int(td_target or 0)

    ach = getattr(td, "achieved_target", None)
    if ach is None:
        ach = getattr(td, "achieved_targets", 0)
    ach = int(ach or 0)

    td.verified_target = new_verified
    td.status = 1 if ach == new_verified else 0
    td.save(update_fields=["verified_target", "status"])

    current_ach = int(getattr(w, "target_achieved", 0) or 0)
    new_ach = current_ach + delta
    w.target_achieved = new_ach

    target = int(getattr(w, "target", 0) or 0)

    # Lead Collection handling
    is_lead_collection = False

    try:
        is_lead_collection = w.client_task.filter(
            task_name__iexact="Lead Collection"
        ).exists()
    except Exception:
        pass

    if is_lead_collection:

        cat_allocations = LeadCateogry_TeamAllocate.objects.filter(
            work_assign=w
        )

        for cat in cat_allocations:

            cat_current_ach = int(cat.target_achieved or 0)
            cat_new_ach = cat_current_ach + delta

            cat_target = int(cat.target or 0)

            cat_progress = (
                round((cat_new_ach / cat_target) * 100)
                if cat_target > 0 else 0
            )

            cat_progress = max(0, min(100, cat_progress))

            cat.target_achieved = cat_new_ach
            cat.progress = cat_progress

            cat.save(update_fields=[
                "target_achieved",
                "progress"
            ])

        # calculate WorkAssign progress from category totals
        total_target = sum(cat.target or 0 for cat in cat_allocations)

        progress = (
            round((new_ach / total_target) * 100)
            if total_target > 0 else 0
        )

    else:

        progress = (
            round((new_ach / target) * 100)
            if target > 0 else 0
        )

    progress = max(0, min(100, progress))

    w.progress = progress

    w.save(update_fields=[
        "target_achieved",
        "progress"
    ])

    return JsonResponse({
        "success": True,
        "task_detail_status": td.status,
        "task_detail_target": td_target,
        "task_detail_verified": new_verified,
        "target_achieved": new_ach,
        "progress": progress
    })


@require_POST
def tl_individual_remove_task(request):
    head, company_id, dept_id, tl_ids = _get_head_scope(request)
    if not company_id:
        return JsonResponse({"success": False, "message": "Invalid session"}, status=401)

    work_id = (request.POST.get("work_id") or "").strip()
    try:
        work_id = int(work_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid task"}, status=400)

    w = WorkAssign.objects.filter(
        company=company_id,
        assign_type=0,
        id=work_id,
        team_lead_id__in=tl_ids
    ).first()
    if not w:
        return JsonResponse({"success": False, "message": "Task not found"}, status=404)

    w.delete()
    return JsonResponse({"success": True})
    
def admin_databank(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    return render(request,'admin/databank.html',{
         'user': user,
        'company': company,
        'name': name,
    })


def databank_platform(request):  
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    from_date = request.GET.get('from_date') or None
    to_date = request.GET.get('to_date') or None

    sources = Platforms.objects.filter(company=company)


    if from_date and to_date:
        sources = sources.filter(created_date__range=(from_date, to_date))
    elif from_date:
        sources = sources.filter(created_date__gte=from_date)
    elif to_date:
        sources = sources.filter(created_date__lte=to_date)


    for src in sources:
        src.platform_total_count = DataBank.objects.filter(
            lead__source__iexact=src.platform_name,
            lead__work__company=company
        ).count()

    return render(request, "admin/databank_platform.html", {
        "user": user,
        "company": company,
        "name": name,
        "sources": sources,
        "from_date": from_date,
        "to_date": to_date
    })



from django.db.models import Prefetch
@csrf_exempt
def admin_db_platform_lead_details(request): 
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    platform_name = request.GET.get("platform", "").strip()
    employee_id = request.GET.get("employee")
    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    leads = DataBank.objects.select_related(
        "lead",
        "lead__lead_category",
        "lead__work__client"
    ).prefetch_related(
        Prefetch(
            "lead__leaddetails_set",
            queryset=LeadDetails.objects.all()
        )
    )


    if platform_name:
        leads = leads.filter(lead__source__iexact=platform_name)

 
    if employee_id:
        leads = leads.filter(lead__collected_by_id=employee_id)

  
    if client_id:
        leads = leads.filter(lead__work__client_id=client_id)

  
    if category_id:
        leads = leads.filter(lead__lead_category_id=category_id)

    
    if from_date:
        leads = leads.filter(generated_date__gte=from_date)

    if to_date:
        leads = leads.filter(generated_date__lte=to_date)

    leads = leads.order_by("-id")

    clients = ClientRegister.objects.filter(company=company)

    employee = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id__in=[
            'Digital_Marketing_Head',
            'Executive',
            'Team_Lead'
        ]
    )

    return render(request, "admin/platform_lead_details.html", {
        "user": user,
        "company": company,
        "name": name,
        "leads": leads,
        "platform_name": platform_name,
        "clients": clients,
        "employee": employee,

      
        "selected_employee": employee_id,
        "selected_client": client_id,
        "selected_category": category_id,
    })



def admin_db_leads(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    clients = ClientRegister.objects.filter(company=company)
    return render(request,'admin/databank_all_leads.html',{
         'user': user,
        'company': company,
        'name': name,
        'clients':clients,
    })


def get_client_related_data(request):
    client_id = request.GET.get('client_id')

    employees = Leads.objects.filter(
        lead_category__client_task__client_id=client_id
    ).values(
        'collected_by__id',
        'collected_by__name'
    ).distinct()

    categories = LeadCategory_Register.objects.filter(
        client_task__client_id=client_id
    ).values(
        'id',
        'collection_for'
    ).distinct()

    return JsonResponse({
        'employees': list(employees),
        'categories': list(categories)
    })

from django.utils.dateparse import parse_date
def get_client_databank_leads(request):
    client_id = request.GET.get('client_id')
    employee_id = request.GET.get('employee')
    category_id = request.GET.get('category')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    databanks = DataBank.objects.filter(
        lead__lead_category__client_task__client_id=client_id
    ).select_related(
        'lead',
        'lead__collected_by',
        'lead__lead_category'
    )

    if employee_id:
        databanks = databanks.filter(lead__collected_by_id=employee_id)

    if category_id:
        databanks = databanks.filter(lead__lead_category_id=category_id)

    if from_date:
        databanks = databanks.filter(
            lead__added_date__gte=parse_date(from_date)
        )

    if to_date:
        databanks = databanks.filter(
            lead__added_date__lte=parse_date(to_date)
        )

    data = []

    for db in databanks:
        lead = db.lead
        details = LeadDetails.objects.filter(lead=lead)

        data.append({
            'date': lead.added_date.strftime('%Y-%m-%d'),
            'employee': lead.collected_by.name if lead.collected_by else '',
            'category': lead.lead_category.collection_for if lead.lead_category else '',
            'name': lead.name,
            'email': lead.email,
            'contact': lead.contact,
            'source': lead.source,
            'client_required': [
                f"{d.field_name}: {d.field_data}" for d in details
            ]
        })

    return JsonResponse({'leads': data})


def admin_db_foolowup_leads(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    clients = ClientRegister.objects.filter(company=company)
    hrs = EmployeeRegister_Details.objects.filter(designation__dashboard_id='Telecaller',company=company)
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)
    return render(request,'admin/databank_followup_leads.html',{
         'user': user,
        'company': company,
        'name': name,
        'clients':clients,
        'hrs':hrs,
        'statuses':statuses
    })




@require_GET
def get_followup_leads_by_client(request):
    client_id = request.GET.get('client_id')
    category_id = request.GET.get('category')
    hr_id = request.GET.get('hr')
    status = request.GET.get('status')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    search = request.GET.get('search')

    followups = FollowupDetails.objects.filter(
        lead__lead_category__client_task__client_id=client_id
    ).select_related(
        'lead',
        'lead__lead_category__client_task__client',
        'lead__lead_category',
        'telecaller'
    )



    if category_id:
        followups = followups.filter(lead__lead_category_id=category_id)

   
    if hr_id:
        followups = followups.filter(telecaller_id=hr_id)


    if status:
        followups = followups.filter(response_status=status)

  
    if from_date and to_date:
        followups = followups.filter(
            response_date__range=[from_date, to_date]
        )


    if search:
        followups = followups.filter(
            Q(lead__name__icontains=search) |
            Q(lead__email__icontains=search) |
            Q(lead__contact__icontains=search) |
            Q(lead__source__icontains=search) |


            Q(lead__collected_by__name__icontains=search) |

           
            Q(lead__work__client__client_name__icontains=search) |

          
            Q(lead__lead_category__collection_for__icontains=search) |

            
            Q(telecaller__name__icontains=search)
        )

    data = []
    for i, f in enumerate(followups, start=1):
        data.append({
            'id': f.id,
            'no': i,
            'date': f.response_date.strftime('%Y-%m-%d') if f.response_date else '',
            'client': f.lead.lead_category.client_task.client.client_name if f.lead else '',
            'category': f.lead.lead_category.collection_for if f.lead and f.lead.lead_category else '',
            'name': f.lead.name if f.lead else '',
            'email': f.lead.email if f.lead else '',
            'contact': f.lead.contact if f.lead else '',
            'source': f.lead.source if f.lead else '',
            'status': f.response_status,
            'telecaller': f.lead.collected_by.name if f.telecaller else '',
        })

    return JsonResponse({'leads': data})


def followup_lead_details(request, followup_id):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    
    followup = FollowupDetails.objects.select_related(
        'lead',
        'lead__work__client',
        'lead__lead_category',
        'telecaller'
    ).get(id=followup_id)

    history = FollowupHistory.objects.filter(
        lead=followup.lead
    ).select_related('telecaller').order_by('-allocated_date')

    lead_details = LeadDetails.objects.filter(lead=followup.lead)

    context = {
        'user': user,
        'company': company,
        'name': name,
        'followup': followup,
        'lead': followup.lead,
        'history': history,
        'lead_details': lead_details
    }
    return render(request, 'admin/followup_lead_details.html', context)



def admin_db_waste_leads(request):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name=EmployeeRegister_Details.objects.filter(login=user).first()
    clients = ClientRegister.objects.filter(company=company)
    return render(request,'admin/databank_waste_leads.html',{
         'user': user,
        'company': company,
        'name': name,
        'clients':clients,
    })

def get_client_waste_leads(request):
    client_id = request.GET.get('client_id')
    employee_id = request.GET.get('employee')
    category_id = request.GET.get('category')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    waste_leads = WasteLead.objects.select_related(
        'lead',
        'lead__collected_by',
        'lead__lead_category',
        'lead__lead_category__client_task__client'
    ).filter(
        lead__lead_category__client_task__client_id=client_id
    )


    if employee_id:
        waste_leads = waste_leads.filter(lead__collected_by_id=employee_id)

    if category_id:
        waste_leads = waste_leads.filter(lead__lead_category_id=category_id)

    if from_date:
        waste_leads = waste_leads.filter(
            lead__added_date__gte=parse_date(from_date)
        )

    if to_date:
        waste_leads = waste_leads.filter(
            lead__added_date__lte=parse_date(to_date)
        )

    data = []

    for waste in waste_leads:
        lead = waste.lead
        details = LeadDetails.objects.filter(lead=lead)

        data.append({
            'date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else '',
            'employee': lead.collected_by.name if lead.collected_by else '',
            'category': lead.lead_category.collection_for if lead.lead_category else '',
            'name': lead.name,
            'email': lead.email,
            'contact': lead.contact,
            'source': lead.source,
            'client_required': [
                f"{d.field_name}: {d.field_data}" for d in details
            ]
        })

    return JsonResponse({'leads': data})


@csrf_exempt
def admin_report(request): 
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    print(company)
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    platform_name = request.GET.get("platform", "").strip()
    employee_id = request.GET.get("hr")
    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    status = request.GET.get("status")


    leads = DataBank.objects.select_related(
        "lead",
        "lead__lead_category",
        "lead__lead_category__client_task__client"
    ).prefetch_related(
        Prefetch(
            "lead__leaddetails_set",
            queryset=LeadDetails.objects.all()
        )
    ).filter(
    lead__collected_by__company=company
)


    if platform_name:
        leads = leads.filter(lead__source__iexact=platform_name)


    if employee_id:
        leads = leads.filter(
            leadassignedtotc__telecaller_id=employee_id
        ).distinct()


    if client_id:
        leads = leads.filter(lead__lead_category__client_task__client_id=client_id)


    if category_id:
        leads = leads.filter(lead__lead_category_id=category_id)


    if from_date:
        leads = leads.filter(generated_date__gte=from_date)

    if to_date:
        leads = leads.filter(generated_date__lte=to_date)

    leads = leads.order_by("-id")

    if status:
        followup_lead_ids = FollowupDetails.objects.filter(
            company=company,
            response_status=status
        ).values_list("lead_id", flat=True)

        leads = leads.filter(lead_id__in=followup_lead_ids)

    clients = ClientRegister.objects.filter(company=company)

    employee = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id='Telecaller')
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)

    platforms = Leads.objects.filter(source__isnull=False
    ).exclude(
    source=""
    ).values_list("source", flat=True).distinct().order_by("source")
    
    today = now().date()

    total_leads_count = leads.count()

    today_new_leads = leads.filter(generated_date=today).count()

    allocation_pending = leads.filter(
        lead_allocate_status=0
    ).count()

    followups = FollowupDetails.objects.filter(
    company=company
)
    total_followup = followups.count()
    today_followup = followups.filter(response_date=today).count()

    

    return render(request, "admin/report.html", {
        "user": user,
        "company": company,
        "name": name,
        "leads": leads,
        "platform_name": platform_name,
        "clients": clients,
        "employee": employee,
        "statuses":statuses,
        "platforms": platforms,
        "total_leads_count": total_leads_count,
        "today_new_leads": today_new_leads,
        "allocation_pending": allocation_pending,
        "total_followup": total_followup,
        "today_followup": today_followup,
        "selected_employee": employee_id,
        "selected_client": client_id,
        "selected_category": category_id,
    })


def databank_lead_details(request, followup_id):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
   
    name = EmployeeRegister_Details.objects.filter(login=user).first()
    followup = DataBank.objects.select_related(
        'lead',
        'lead__lead_category__client_task__client',
        'lead__lead_category',
    ).get(id=followup_id)

    history = FollowupHistory.objects.filter(
        lead=followup.lead
    ).select_related('telecaller').order_by('-allocated_date')

    lead_details = LeadDetails.objects.filter(lead=followup.lead)

    context = {
        "company": company,
        "name": name,
        'followup': followup,
        'lead': followup.lead,
        'history': history,
        'lead_details': lead_details
    }
    return render(request, 'admin/followup_lead_details.html', context)



@csrf_exempt
def admin_hr_analysis(request): 
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
   
    name = EmployeeRegister_Details.objects.filter(login=user).first()


    employee_id = request.GET.get("hr")
    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    status = request.GET.get("status")


    hr_leads = LeadAssignedToTC.objects.select_related(
    "lead",
    "databank",
    "lead__lead_category",
    "lead__lead_category__client_task__client",
    "telecaller"
).filter(
    databank__lead_allocate_status=1,lead__collected_by__company=company
)


    if employee_id:
        hr_leads = hr_leads.filter(telecaller_id=employee_id)


    if client_id:
        hr_leads = hr_leads.filter(lead__lead_category__client_task__client_id=client_id)


    if category_id:
        hr_leads = hr_leads.filter(lead__lead_category_id=category_id)

  
    if from_date:
        hr_leads = hr_leads.filter(lead__added_date__gte=from_date)

    if to_date:
        hr_leads = hr_leads.filter(lead__added_date__lte=to_date)

 
    if status:
        followup_ids = FollowupDetails.objects.filter(
            company=company,
            response_status=status
        ).values_list("lead_id", flat=True)

        hr_leads = hr_leads.filter(lead_id__in=followup_ids)

    hr_leads = hr_leads.order_by("-id")
    total_leads_count = hr_leads.count()

    clients = ClientRegister.objects.filter(company=company)

    employee = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id='Telecaller')
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)

    allocated_count = hr_leads.count()
    accepted_count = hr_leads.filter(status=1).count()
    hr_pending = hr_leads.filter(status=0).count()

    not_allocated_count = DataBank.objects.filter(
        lead_allocate_status=0
    ).count()

    wasted_count = WasteLead.objects.filter(lead__collected_by__company=company).count()

    followup_count = FollowupDetails.objects.filter(
    company=company).count
    
    joined_count = LeadAssignedToTC.objects.filter(
    response="Joined").count()

    overall_percentage = 0
    if allocated_count > 0:
        overall_percentage = round((joined_count / allocated_count) * 100, 2)

    

    return render(request, "admin/analysis.html", {
        "user": user,
        "company": company,
        "name": name,
        "hr_leads":hr_leads,
        "total_leads_count":total_leads_count,
        "clients": clients,
        "employee": employee,
        "statuses":statuses,
       
        "selected_employee": employee_id,
        "selected_client": client_id,
        "selected_category": category_id,

        "allocated_count":allocated_count,
        "accepted_count":accepted_count,
        "hr_pending":hr_pending,
        "not_allocated_count":not_allocated_count,
        "wasted_count":wasted_count,
        "followup_count":followup_count,
        "joined_count":joined_count,
        "overall_percentage": overall_percentage,
    })


from django.core.paginator import Paginator

@csrf_exempt
def admin_employee_analysis(request): 
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()


    employee_id = request.GET.get("employee")
    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")



    leads = Leads.objects.select_related(
    "lead_category",
    "lead_category__client_task__client",
    "collected_by").filter(collected_by__company=company)


    if employee_id:
        leads = leads.filter(collected_by=employee_id)


    if client_id:
        leads = leads.filter(lead_category__client_task__client_id=client_id)


    if category_id:
        leads = leads.filter(lead_category_id=category_id)

 
    if from_date:
        leads = leads.filter(added_date__gte=from_date)

    if to_date:
        leads = leads.filter(added_date__lte=to_date)



    leads = leads.order_by("-id")

    total_leads_count = leads.count()

   
    paginator = Paginator(leads, 5)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    clients = ClientRegister.objects.filter(company=company)

    employee = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id__in=[
            'Digital_Marketing_Head',
            'Executive',
            'Team_Lead'
        ]
    )


    collected_count = leads.count()


    wasted_count = WasteLead.objects.filter(lead__collected_by__company=company).count()



    total_leads = collected_count + wasted_count

    overall_percentage = 0
    if total_leads > 0:
        overall_percentage = round((collected_count / total_leads) * 100, 2)

    

    return render(request, "admin/employee_analysis.html", {
        "user": user,
        "company": company,
        "name": name,
        "leads": page_obj,
        "page_obj": page_obj,
        "total_leads_count":total_leads_count,
        "clients": clients,
        "employee": employee,
  
       
        "selected_employee": employee_id,
        "selected_client": client_id,
        "selected_category": category_id,

        "collected_count":collected_count,

        "wasted_count":wasted_count,

        "overall_percentage": overall_percentage,
    })




@csrf_exempt
def admin_comparison_analysis(request):

    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    client_id = request.GET.get("client")
    category_id = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    clients = ClientRegister.objects.filter(company=company)


    base_filter = Q()

    if client_id:
        base_filter &= Q(lead__lead_category__client_task__client_id=client_id)

    if category_id:
        base_filter &= Q(lead__lead_category_id=category_id)

    if from_date:
        base_filter &= Q(lead__added_date__gte=from_date)

    if to_date:
        base_filter &= Q(lead__added_date__lte=to_date)



    hr_queryset = LeadAssignedToTC.objects.filter(
        databank__lead_allocate_status=1
    ).filter(base_filter,lead__collected_by__company=company)

    hr_performance = hr_queryset.values(
        "telecaller_id",
        "telecaller__name"
    ).annotate(

        allocated=Count("id", distinct=True),

        joined=Count(
            "id",
            filter=Q(response__iexact="Lead Joined"),
            distinct=True
        ),

        followup=Count(
            "lead__followupdetails",
            distinct=True
        ),

        waste=Count(
            "lead__wastelead",
            distinct=True
        )

    )

    for hr in hr_performance:
        allocated = hr["allocated"]
        joined = hr["joined"]
        hr["overall"] = round((joined / allocated) * 100, 2) if allocated else 0

    hr_count = hr_performance.count()



    employee_queryset = Leads.objects.filter(
        collected_by__isnull=False,collected_by__company=company
    )

    if category_id:
        employee_queryset = employee_queryset.filter(lead_category_id=category_id)

    if from_date:
        employee_queryset = employee_queryset.filter(added_date__gte=from_date)

    if to_date:
        employee_queryset = employee_queryset.filter(added_date__lte=to_date)

    if client_id:
        employee_queryset = employee_queryset.filter(lead_category__client_task__client_id=client_id)

    employee_performance = employee_queryset.values(
        "collected_by_id",
        "collected_by__name"
    ).annotate(

        collected=Count("id", distinct=True),

        waste=Count(
            "wastelead",
            distinct=True
        )

    )

    for emp in employee_performance:
        collected = emp["collected"]
        waste = emp["waste"]
        emp["overall"] = round(((collected - waste) / collected) * 100, 2) if collected else 0

    employee_count = employee_performance.count()

 
    return render(request, "admin/comparison_analysis.html", {
        "user": user,
        "company": company,
        "name": name,
        "clients": clients,

        "selected_client": client_id,
        "selected_category": category_id,

        "hr_performance": hr_performance,
        "employee_performance": employee_performance,

        "hr_count": hr_count,
        "employee_count": employee_count,
    })

 

def analysis_lead_details(request, followup_id):
    aid = request.session.get('aid')
    user = LogRegister_Details.objects.get(log_username=aid)
    company = BusinessRegister_Details.objects.filter(login=user).first()
    name = EmployeeRegister_Details.objects.filter(login=user).first()

    followup = Leads.objects.select_related(
        'lead_category__client_task__client',
        'lead_category',
    ).get(id=followup_id)

    history = FollowupHistory.objects.filter(
        lead=followup
    ).select_related('telecaller').order_by('-allocated_date')

    lead_details = LeadDetails.objects.filter(lead=followup)

    context = {
        "user": user,
        "company": company,
        "name": name,
        'followup': followup,
        'lead': followup,
        'history': history,
        'lead_details': lead_details
    }
    return render(request, 'admin/followup_lead_details.html', context)

# ------------------------------------------------- Admin Dashboard Card work -------------------------------------------------

def admindash_client_details(request, client_id):
    aid = request.session.get('aid')
    user = get_object_or_404(LogRegister_Details, log_username=aid)
    company = get_object_or_404(BusinessRegister_Details, login=user)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    return render(request, 'admin/admindash_client_details.html', {
        'company': company,
        'client': client
    })



def admindash_executives(request, company_id, client_id):
    company = get_object_or_404(BusinessRegister_Details, id=company_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    executives = EmployeeRegister_Details.objects.filter(
        company=company, 
        login__position='Executive'
    ).annotate(
        total_leads=Count(
            'leads', 
            filter=Q(leads__lead_category__client_task__client=client),
            distinct=True
        ), 
        confused_leads_count=Count(
            'leadconfused',
            filter=Q(leadconfused__lead__lead_category__client_task__client=client),
            distinct=True
        )
    )

    return render(request, 'admin/admindash_executives.html', {
        'executives': executives,
        'company': company,
        'client': client,
    })


def admindash_telecallers(request, company_id, client_id):
    company = get_object_or_404(BusinessRegister_Details, id=company_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    telecallers = EmployeeRegister_Details.objects.filter(
        company=company, 
        login__position='Telecaller'
    )

    return render(request, 'admin/admindash_telecallers.html', {
        'telecallers': telecallers,
        'company': company,
        'client': client
    })



def admindash_executive_leads(request, exec_id, client_id):
    executive = get_object_or_404(EmployeeRegister_Details, id=exec_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    aid = request.session.get('aid')
    company = None
    if aid:
        try:
            user = LogRegister_Details.objects.get(log_username=aid)
            company = BusinessRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            pass

    return render(request, 'admin/admindash_executive_leads.html', {
        'executive': executive,
        'client': client,
        'company': company,  
    })




def admindash_executive_leads_list(request, exec_id, client_id):
    aid = request.session.get('aid')
    company = None
    if aid:
        try:
            user = LogRegister_Details.objects.get(log_username=aid)
            company = BusinessRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            pass

    executive = get_object_or_404(EmployeeRegister_Details, id=exec_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    category_id = request.GET.get('category_id') 
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    lead_status = request.GET.get('lead_status')
    followup_query = request.GET.get('followup_status')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10) 

    latest_tc_res_subquery = LeadAssignedToTC.objects.filter(
        lead=OuterRef('pk')
    ).order_by('-id').values('response')[:1]

    allocated_subquery = LeadAssignedToTC.objects.filter(lead=OuterRef('pk'))

    leads_queryset = Leads.objects.filter(
        collected_by=executive,
        lead_category__client_task__client_id=client_id  
    ).annotate(
        is_allocated=Exists(allocated_subquery),
        tc_response=Subquery(latest_tc_res_subquery)
    )

    if category_id:
        leads_queryset = leads_queryset.filter(lead_category_id=category_id)

    if from_date:
        leads_queryset = leads_queryset.filter(added_date__gte=from_date)
    if to_date:
        leads_queryset = leads_queryset.filter(added_date__lte=to_date)

    if lead_status:
        if lead_status == "Allocated":
            leads_queryset = leads_queryset.filter(
                Q(is_allocated=True) & (Q(tc_response='No Data Available') | Q(tc_response=''))
            )
        elif lead_status == "Not Allocated":
            leads_queryset = leads_queryset.filter(is_allocated=False)
        else:
            leads_queryset = leads_queryset.filter(tc_response=lead_status)

    if followup_query:
        leads_queryset = leads_queryset.filter(tc_response=followup_query)

    leads_queryset = leads_queryset.order_by('-added_date').distinct()

    paginator = Paginator(leads_queryset, per_page)
    try:
        leads_list = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        leads_list = paginator.page(1)

    available_categories = LeadCategory_Register.objects.filter(client_task__client=client)
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)
    
    context = {
        'executive': executive,
        'leads_list': leads_list, 
        'total_leads_count': leads_queryset.count(),
        'followup_statuses': statuses,
        'available_categories': available_categories, 
        'from_date': from_date,
        'to_date': to_date,
        'selected_lead_status': lead_status,
        'selected_category': category_id,
        'selected_followup': followup_query,
        'per_page': int(per_page),
        'client': client,
        'company': company
    }

    return render(request, 'admin/admindash_executive_leads_list.html', context)



def executive_get_lead_details(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    
    assignment = LeadAssignedToTC.objects.filter(lead=lead).order_by('-id').first()


    client_id = request.GET.get('client_id')
    client = None
    if client_id:
        client = ClientRegister.objects.filter(id=client_id).first()
    
    if not client and hasattr(lead, 'lead_category') and lead.lead_category:
        client = getattr(lead.lead_category, 'client', None)
    
    followups = FollowupDetails.objects.filter(lead=lead).order_by('-response_date')
    followup_list = []
    for f in followups:
        followup_list.append({
            'telecaller': f.telecaller.name if f.telecaller else "N/A",
            'date': f.response_date.strftime('%Y-%m-%d') if f.response_date else "N/A",
            'response': f.response,
            'next_date': f.next_followup_date.strftime('%Y-%m-%d') if f.next_followup_date else "N/A",
            'status': f.response_status
        })
    
    history = FollowupHistory.objects.filter(lead=lead).order_by('-id')
    history_data = [{
        'telecaller': h.telecaller.name if h.telecaller else "N/A",
        'date': h.allocated_date.strftime('%Y-%m-%d') if h.allocated_date else "N/A",
        'note': h.note or "No note provided",
        'status': h.final_status
    } for h in history]

    recordings = LeadCallRecord.objects.filter(lead=lead).order_by('-id')
    recordings_data = [{
        'date': r.record_date.strftime('%Y-%m-%d'),
        'time': r.record_time.strftime('%H:%M') if r.record_time else "",
        'file_url': r.record_file.url if r.record_file else ""
    } for r in recordings]

    data = {
        'name': lead.name or "Unnamed",
        'email': lead.email or "N/A",
        'phone': lead.contact or "N/A",
        'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else "N/A",
        'category': lead.lead_category.collection_for if lead.lead_category else "N/A",

        'client_name': client.client_name if client else "N/A",
        'client_business': client.client_business_name if client else "N/A",
        'client_phone': client.client_phone if client else "N/A",
        'client_place': client.client_place if client else "N/A",

        'collected_by': lead.collected_by.name if lead.collected_by else "N/A",
        'assigned_to': assignment.telecaller.name if assignment and assignment.telecaller else "Not Assigned",
        'current_status': assignment.response if assignment else "Unverified",
        'next_followup': assignment.next_update_date.strftime('%Y-%m-%d') if assignment and assignment.next_update_date else "N/A",
        'followups': followup_list,
        'history': history_data,
        'recordings': recordings_data
    }
    return JsonResponse(data)




def admindash_telecaller_leads_list(request, tele_id, client_id):
    aid = request.session.get('aid')
    company = None
    if aid:
        try:
            user = LogRegister_Details.objects.get(log_username=aid)
            company = BusinessRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            pass

    telecaller = get_object_or_404(EmployeeRegister_Details, id=tele_id)
    client = get_object_or_404(ClientRegister, id=client_id)

    category_id = request.GET.get('category_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    followup_query = request.GET.get('followup_status')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10) 


    assigned_leads_queryset = LeadAssignedToTC.objects.filter(
        telecaller=telecaller,
        status__in=[1, 2, 3],
        lead__lead_category__client_task__client_id=client_id 
    ).select_related('lead', 'lead__lead_category').order_by('-assign_date')

    if category_id:
        assigned_leads_queryset = assigned_leads_queryset.filter(lead__lead_category_id=category_id)

    if from_date:
        assigned_leads_queryset = assigned_leads_queryset.filter(assign_date__gte=from_date)
    if to_date:
        assigned_leads_queryset = assigned_leads_queryset.filter(assign_date__lte=to_date)

    if followup_query:
        if followup_query in ["Lead Joined", "Lead Closed", "Waste Lead"]:
            assigned_leads_queryset = assigned_leads_queryset.filter(response__iexact=followup_query)
        else:
            assigned_leads_queryset = assigned_leads_queryset.filter(response=followup_query)

    paginator = Paginator(assigned_leads_queryset, per_page)
    try:
        assigned_leads = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        assigned_leads = paginator.page(1)

    available_categories = LeadCategory_Register.objects.filter(client_task__client=client)
    statuses = FollowupStatus.objects.values_list('status_name', flat=True)

    context = {
        'telecaller': telecaller,
        'assigned_leads': assigned_leads, 
        'total_leads_count': assigned_leads_queryset.count(),
        'followup_statuses': statuses,
        'available_categories': available_categories,
        'from_date': from_date,
        'to_date': to_date,
        'selected_followup': followup_query,
        'selected_category': category_id,
        'per_page': int(per_page),
        'client': client,
        'company': company
    }

    return render(request, 'admin/admindash_telecaller_leads_list.html', context)



def telecaller_get_lead_details(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    
    assignment = LeadAssignedToTC.objects.filter(lead=lead).order_by('-id').first()


    client_id = request.GET.get('client_id')
    client = None
    if client_id:
        client = ClientRegister.objects.filter(id=client_id).first()
    
    if not client and hasattr(lead, 'lead_category') and lead.lead_category:
        client = getattr(lead.lead_category, 'client', None)
    
    followups = FollowupDetails.objects.filter(lead=lead).order_by('-response_date')
    followup_list = []
    for f in followups:
        followup_list.append({
            'telecaller': f.telecaller.name if f.telecaller else "N/A",
            'date': f.response_date.strftime('%Y-%m-%d') if f.response_date else "N/A",
            'response': f.response,
            'next_date': f.next_followup_date.strftime('%Y-%m-%d') if f.next_followup_date else "N/A",
            'status': f.response_status
        })
    
    history = FollowupHistory.objects.filter(lead=lead).order_by('-id')
    history_data = [{
        'telecaller': h.telecaller.name if h.telecaller else "N/A",
        'date': h.allocated_date.strftime('%Y-%m-%d') if h.allocated_date else "N/A",
        'note': h.note or "No note provided",
        'status': h.final_status
    } for h in history]

    recordings = LeadCallRecord.objects.filter(lead=lead).order_by('-id')
    recordings_data = [{
        'date': r.record_date.strftime('%Y-%m-%d'),
        'time': r.record_time.strftime('%H:%M') if r.record_time else "",
        'file_url': r.record_file.url if r.record_file else ""
    } for r in recordings]

    data = {
        'name': lead.name or "Unnamed",
        'email': lead.email or "N/A",
        'phone': lead.contact or "N/A",
        'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else "N/A",
        'category': lead.lead_category.collection_for if lead.lead_category else "N/A",

        'client_name': client.client_name if client else "N/A",
        'client_business': client.client_business_name if client else "N/A",
        'client_phone': client.client_phone if client else "N/A",
        'client_place': client.client_place if client else "N/A",

        'collected_by': lead.collected_by.name if lead.collected_by else "N/A",
        'assigned_to': assignment.telecaller.name if assignment and assignment.telecaller else "Not Assigned",
        'current_status': assignment.response if assignment else "Unverified",
        'next_followup': assignment.next_update_date.strftime('%Y-%m-%d') if assignment and assignment.next_update_date else "N/A",
        'followups': followup_list,
        'history': history_data,
        'recordings': recordings_data
    }
    return JsonResponse(data)

# --------------------------------------------- End Admin Dashboard Card work -------------------------------------------------

def hr(request):
    aid = request.session.get('hrid')

    if not aid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
    print("hello")
    notifications = LeadMeet.objects.filter(is_seen_hr=False,lead__collected_by__company=company).order_by('-created_at')
    return render(request, 'hr/hrdash.html', {
        'user': user,
        'company': company,
        'name':name,
        "notifications": notifications,
        "notify_count": notifications.count()
    })


def save_meet(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        lead_assign_id = request.POST.get("lead_assign_id")
        meet_date = request.POST.get("meet_date")
        mode = request.POST.get("mode")

        lead = Leads.objects.get(id=lead_id)
        assign = LeadAssignedToTC.objects.get(id=lead_assign_id)

        log_user = LogRegister_Details.objects.get(log_username=request.session.get('tcid'))
        employee_fk = EmployeeRegister_Details.objects.filter(login=log_user).first()

        LeadMeet.objects.create(
            lead=lead,
            assign = assign,
            meet_date=meet_date,
            mode=mode,
            created_by=employee_fk  
        )

    return redirect('telecaller_followups_page')



def meeting_details(request):
    username = request.session.get('tcid')
    if not username:
        return redirect('login')

    telecaller = LogRegister_Details.objects.filter(log_username=username).first()
    emp = EmployeeRegister_Details.objects.filter(login=telecaller).first()
    print(emp)
    meetings = LeadMeet.objects.filter(assign__telecaller=emp)

    status = request.GET.get('status')
    if status == 'Conducted':
        meetings = meetings.filter(status=1)
    elif status == 'Pending':
        meetings = meetings.filter(status=0)

    mode = request.GET.get('mode')
    if mode == 'Google Meet':
        meetings = meetings.filter(mode='Google Meet')
    elif mode == 'Direct Meet':
        meetings = meetings.filter(mode='Direct Meet')

    


    context = {
        "name": emp,
        "meetings": meetings,
        
    }
    return render(request, 'telecaller/meeting_details.html', context)


def meeting_hr(request):
    username = request.session.get('hrid')
    if not username:
        return redirect('login')

    user = LogRegister_Details.objects.filter(log_username=username).first()
    emp = EmployeeRegister_Details.objects.filter(login=user).first()
    company = emp.company if emp else None
    print(company)
    print(emp)
    meetings = LeadMeet.objects.filter(lead__collected_by__company=company)

    status = request.GET.get('status')
    if status == 'Conducted':
        meetings = meetings.filter(status=1)
    elif status == 'Pending':
        meetings = meetings.filter(status=0)

    mode = request.GET.get('mode')
    if mode == 'Google Meet':
        meetings = meetings.filter(mode='Google Meet')
    elif mode == 'Direct Meet':
        meetings = meetings.filter(mode='Direct Meet')

    notifications = LeadMeet.objects.filter(is_seen_hr=False).order_by('-created_at')


    context = {
        "name": emp,
        "meetings": meetings,
        "notifications": notifications,
        "notify_count": notifications.count()
    }
    return render(request, 'hr/meetings.html', context)


def save_meeting_details(request):
    if request.method == "POST":
        meet_id = request.POST.get("meet_id")
        chance = request.POST.get("joining_chance")
        description = request.POST.get("description")

        meet = LeadMeet.objects.get(id=meet_id)

        # ONLY UPDATE ONCE
        if meet.status == 0:
            meet.joining_chance = chance
            meet.description = description
            meet.status = 1

            meet.updated_at = timezone.now()
            meet.is_update_notification = True
            meet.save()

        return JsonResponse({"status": "success"})
    
def mark_hr_notifications_seen(request):
    LeadMeet.objects.filter(is_seen_hr=False).update(is_seen_hr=True)
    return JsonResponse({"status": "ok"})

def mark_dm_notifications_seen(request):
    LeadMeet.objects.filter(is_seen_dm=False).update(is_seen_dm=True)

    LeadMeet.objects.filter(is_update_notification=True).update(is_update_notification=False)

    
    return JsonResponse({"status": "ok"})



def dmhead_meetings(request):
    user_id = request.session.get('hid')  
    user = None
    company = None  
    if user_id:

        user = LogRegister_Details.objects.get(log_username=user_id)
      
        employee = EmployeeRegister_Details.objects.filter(login_id=user).first() 
        company = employee.company if employee else None 
        print(company)

        telecallers = EmployeeRegister_Details.objects.filter(
                company=employee.company,
                designation__name__iexact="Telecaller"
            )
        
        meetings = LeadMeet.objects.all()

        notifications = []

        for m in meetings:
          
            if not m.is_seen_dm:
                notifications.append({
                    "message": f"{m.lead.name} meeting scheduled by {m.created_by}",
                    "time": m.created_at
                })

            
            if m.is_update_notification:
                notifications.append({
                    "message": f"{m.lead.name} meeting is updated",
                    "time": m.updated_at
                })

        # sort latest first
        notifications = sorted(notifications, key=lambda x: x["time"], reverse=True)



    return render(request, "dmhead/dmhead_meetings.html", {
        "name": employee,
        "user": user,
        "employee":employee,
        "telecallers":telecallers,
        "notifications": notifications,
        "notify_count": len(notifications)
        })





def dmhead_leads_meet(request, emp_id):
    user_id = request.session.get('hid')  
    user = None
    company = None  
    if user_id:

        user = LogRegister_Details.objects.get(log_username=user_id)
        company = BusinessRegister_Details.objects.filter(login=user).first()
        emp = EmployeeRegister_Details.objects.filter(login_id=user).first()  

        telecallers = EmployeeRegister_Details.objects.get(id=emp_id)

        meetings = LeadMeet.objects.filter(assign__telecaller=telecallers)

        status = request.GET.get('status')
        if status == 'Conducted':
            meetings = meetings.filter(status=1)
        elif status == 'Pending':
            meetings = meetings.filter(status=0)

        mode = request.GET.get('mode')
        if mode == 'Google Meet':
            meetings = meetings.filter(mode='Google Meet')
        elif mode == 'Direct Meet':
            meetings = meetings.filter(mode='Direct Meet')


        meeting = LeadMeet.objects.all()

        notifications = []

        for m in meeting:
          
            if not m.is_seen_dm:
                notifications.append({
                    "message": f"{m.lead.name} meeting scheduled by {m.created_by}",
                    "time": m.created_at
                })

            
            if m.is_update_notification:
                notifications.append({
                    "message": f"{m.lead.name} meeting is updated",
                    "time": m.updated_at
                })

        # sort latest first
        notifications = sorted(notifications, key=lambda x: x["time"], reverse=True)


    context = {
        "name": emp,
        "meetings": meetings,
        "telecallers": telecallers,
        "notifications": notifications,
        "notify_count": len(notifications)
        
    }
    return render(request, 'dmhead/leads_meet.html', context)
    
def check_telecaller_followups():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    lead_groups = (
        LeadAssignedToTC.objects
        .filter(assign_date=yesterday)
        .values('telecaller')
        .distinct()
    )

    for group in lead_groups:
        telecaller_id = group['telecaller']

        assigned_leads = LeadAssignedToTC.objects.filter(
            telecaller_id=telecaller_id,
            assign_date=yesterday
        )

        followed_leads = FollowupDetails.objects.filter(
            telecaller_id=telecaller_id,
            response_date__gte=yesterday
        ).values_list('lead_id', flat=True)

        no_followup_count = assigned_leads.exclude(
            lead__in=followed_leads
        ).count()

        employee = EmployeeRegister_Details.objects.filter(
            id=telecaller_id
        ).select_related('login').first()

        if not (employee and employee.login and employee.login.is_staff):
            continue

        current_status = employee.login.status

        print(employee.name, no_followup_count)

       
        if no_followup_count < 5:
            if current_status == 2:
                employee.login.status = 1
                employee.login.save()
                print(f"{employee.name} activated")

        
        elif no_followup_count >= 5:
            if current_status == 1:
                employee.login.status = 0
                employee.login.save()
                print(f"{employee.name} blocked")


def module_unlock_dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
       
  
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 
        print(company)
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    employees = EmployeeRegister_Details.objects.filter(company=company,login__status=0)


    return render(request, 'dmhead/module_unlock.html', {
        'user': user,
        'company': company,
        'name':name,
        'employees':employees
    })


def unlock_employee_dmhead(request, id):
    employee = get_object_or_404(EmployeeRegister_Details, id=id)

    if employee.login:
        employee.login.status = 2 
        employee.login.save()

    return redirect('module_unlock_dmhead')



def add_target_dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    employees = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__name__iexact="Executive"
    )

   
    if request.method == "POST":
        execute_id = request.POST.get('execute')
        month = request.POST.get('month')
        year = request.POST.get('year')
        target_count = request.POST.get('target_count')
        description = request.POST.get('description')

        if not execute_id or not month or not year or not target_count:
            messages.error(request, "All required fields must be filled!")
            return redirect('add_target_dmhead')

        try:
            executive = EmployeeRegister_Details.objects.get(id=execute_id)

            already_exists = TargetAssign.objects.filter(
                executive=executive,
                month=month,
                year=year
            ).exists()

            if already_exists:
                messages.error(request, "Target already assigned for this month!")
                return redirect('add_target_dmhead')

            TargetAssign.objects.create(
                company=company,
                executive=executive,
                month=month,
                year=year,
                target_count=target_count,
                description=description
            )

            messages.success(request, "Target Added Successfully")
            return redirect('add_target_dmhead')

        except EmployeeRegister_Details.DoesNotExist:
            messages.error(request, "Invalid employee selected!")

    return render(request, 'dmhead/add_target_dmhead.html', {
        'user': user,
        'company': company,
        'name': name,
        'employees': employees
    })



from django.db.models.functions import TruncDate
from django.db.models.functions import ExtractMonth, ExtractYear

def view_target_dmhead(request):

    hid = request.session.get('hid')

    if not hid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None

    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

   
    if request.method == "POST":

        target_id = request.POST.get('target_id')
        action_taken = request.POST.get('action_taken')

        try:
            target_obj = TargetAssign.objects.get(id=target_id)

            TargetAction.objects.create(
                company=company,
                target=target_obj,
                executive=target_obj.executive,
                action_taken=action_taken
            )

            messages.success(request, "Action submitted successfully!")

            return redirect('view_target_dmhead')

        except TargetAssign.DoesNotExist:
            messages.error(request, "Invalid target!")

    # FILTER VALUES
    selected_executive = request.GET.get('executive')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

 
    executive = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id='Executive'
    )

   
    target = TargetAssign.objects.filter(
        company=company
    )

    # EXECUTIVE FILTER
    if selected_executive:
        target = target.filter(
            executive_id=selected_executive
        )

   
    if from_date:
        target = target.filter(
            created_at__date__gte=from_date
        )

    if to_date:
        target = target.filter(
            created_at__date__lte=to_date
        )

    target = target.order_by('-created_at')


    leads_query = Leads.objects.all()

  
    if selected_executive:
        leads_query = leads_query.filter(
            collected_by_id=selected_executive
        )


    if from_date:
        leads_query = leads_query.filter(
            added_date__gte=from_date
        )

    if to_date:
        leads_query = leads_query.filter(
            added_date__lte=to_date
        )

  
    achieved_data = (
        leads_query
        .annotate(
            month_num=ExtractMonth('added_date'),
            year_num=ExtractYear('added_date')
        )
        .values(
            'collected_by',
            'month_num',
            'year_num'
        )
        .annotate(total=Count('id'))
    )

    month_map = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    achieved_dict = {
        (
            item['collected_by'],
            month_map.get(item['month_num']),
            item['year_num']
        ): item['total']
        for item in achieved_data
    }


    for t in target:

        key = (
            t.executive.id,
            t.month,
            t.year
        )

        t.achieved = achieved_dict.get(key, 0)

    return render(request, 'dmhead/view_target_dmhead.html', {

        'user': user,
        'company': company,
        'name': name,

        'target': target,
        'executive': executive,

        'selected_executive': selected_executive,
        'from_date': from_date,
        'to_date': to_date,
    })



def add_promtwork_exec(request):
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

   
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        media = request.FILES.get('media')

        PromotionalWork.objects.create(
            title=title,
            content=content,
            media=media,
            created_by=name,
            status=0   # Pending
        )

        messages.success(request, "Promotional Work Submitted Successfully!")
        return redirect('add_promtwork_exec')  

    return render(request, 'executive/add_promotional_work.html', {
        'user': user,
        'company': company,
        'name': name
    })



def view_promtwork_exec(request):
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    promotion_work = PromotionalWork.objects.filter(
        created_by=name
    ).order_by('-created_at')  

    return render(request, 'executive/view_promotional_work.html', {
        'user': user,
        'company': company,
        'name': name,
        'promotion_work': promotion_work,
    })


def promotional_works_tl(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login') 

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    print("hello")

    allocations = AllocationDetails.objects.filter(team_lead=name)
    employee_ids = allocations.values_list('employee_id', flat=True)

   
    promotion_work = PromotionalWork.objects.filter(
        created_by_id__in=employee_ids
    ).select_related('created_by').order_by('-created_at')

    return render(request, 'teamlead/promotional_works_tl.html', {
        'user': user,
        'company': company,
        'name':name,
        'promotion_work':promotion_work
    })



def update_promotional_status(request, id, status):
   
    work = get_object_or_404(PromotionalWork, id=id)

    work.status = status  # 1 = approve, 2 = reject
    work.save()

    return redirect('promotional_works_tl')


def poster_upload_tl(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        media = request.FILES.get('media')

        if media:
            if not media.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed!")
                return redirect('poster_upload_tl')

        Posters.objects.create(
            title=title,
            content=content,
            media=media,
            created_by=name
        )

        messages.success(request, "Poster uploaded successfully!")
        return redirect('poster_upload_tl')

    return render(request, 'teamlead/poster_upload.html', {
        'user': user,
        'company': company,
        'name': name
    })


def view_posters_tl(request):
    aid = request.session.get('tid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    posters = Posters.objects.filter(created_by=name)

    return render(request, 'teamlead/view_posters.html', {
        'user': user,
        'company': company,
        'name': name,
        'posters':posters
    })



def poster_upload_exec(request):
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        media = request.FILES.get('media')

        if media:
            if not media.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed!")
                return redirect('poster_upload_exec')

        Posters.objects.create(
            title=title,
            content=content,
            media=media,
            created_by=name
        )

        messages.success(request, "Poster uploaded successfully!")
        return redirect('poster_upload_exec')

    return render(request, 'executive/poster_upload.html', {
        'user': user,
        'company': company,
        'name': name
    })


def view_posters_exec(request):
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    posters = Posters.objects.filter(created_by=name)

    return render(request, 'executive/view_poster.html', {
        'user': user,
        'company': company,
        'name': name,
        'posters':posters
    })



def viewposters_dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    posters = Posters.objects.filter(created_by__company=company)



    return render(request, 'dmhead/viewposters.html', {
        'user': user,
        'company': company,
        'name': name,
        'posters': posters
    })


def update_posters_status(request, id, status):
   
    posters = get_object_or_404(Posters, id=id)

    posters.status = status  # 1 = approve, 2 = reject
    posters.save()

    return redirect('viewposters_dmhead')
     
# ---------------------------------------------- Admin Dashboard Card work Balance ---------------------------------------------------


def admindash_telecaller_leads(request, telecaller_id, client_id):
    telecaller = get_object_or_404(EmployeeRegister_Details, id=telecaller_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    company = telecaller.company 

    total_leads_handled = LeadAssignedToTC.objects.filter(telecaller=telecaller,status__in=[1, 2, 3],lead__lead_category__client_task__client=client).count()

    total_meetings = LeadMeet.objects.filter(created_by=telecaller,lead__lead_category__client_task__client=client).count()

    total_joined = LeadAssignedToTC.objects.filter(telecaller=telecaller, response='Lead Joined',lead__lead_category__client_task__client=client).count()

    return render(request, 'admin/admindash_telecaller_leads.html', {
        'telecaller': telecaller,
        'company': company,
        'client': client,
        'total_leads_handled': total_leads_handled,
        'total_meetings': total_meetings,
        'total_joined': total_joined,
    })




def admindash_telecaller_meet_details(request, telecaller_id, client_id):
    telecaller = get_object_or_404(EmployeeRegister_Details, id=telecaller_id)
    client = get_object_or_404(ClientRegister, id=client_id)

    meetings_list = LeadMeet.objects.filter(created_by=telecaller,lead__lead_category__client_task__client_id=client_id).order_by('-id')


    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    per_page = request.GET.get('per_page', 10) 
    page_number = request.GET.get('page')

    if from_date:
        meetings_list = meetings_list.filter(meet_date__gte=from_date)
    if to_date:
        meetings_list = meetings_list.filter(meet_date__lte=to_date)

    paginator = Paginator(meetings_list, per_page)
    meetings = paginator.get_page(page_number)

    context = {
        'telecaller': telecaller,
        'client': client,
        'meetings': meetings, 
        'total_meetings': meetings_list.count(),
        'from_date': from_date,
        'to_date': to_date,
        'per_page': int(per_page),
    }
    return render(request, 'admin/admindash_telecaller_meet_details.html', context)







def admindash_telecaller_joined_leads(request, telecaller_id, client_id):
    telecaller = get_object_or_404(EmployeeRegister_Details, id=telecaller_id)
    client = get_object_or_404(ClientRegister, id=client_id)

    joined_leads_list = LeadAssignedToTC.objects.filter(telecaller=telecaller, response='Lead Joined',lead__lead_category__client_task__client=client ).order_by('-assign_date')


    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    per_page = request.GET.get('per_page', 10) 
    page_number = request.GET.get('page')

    if from_date:
        joined_leads_list = joined_leads_list.filter(assign_date__gte=from_date)
    if to_date:
        joined_leads_list = joined_leads_list.filter(assign_date__lte=to_date)

    paginator = Paginator(joined_leads_list, per_page)
    joined_leads = paginator.get_page(page_number)

    context = {
        'telecaller': telecaller,
        'client': client,
        'joined_leads': joined_leads, 
        'total_joined': joined_leads_list.count(),
        'from_date': from_date,
        'to_date': to_date,
        'per_page': int(per_page),
    }
    return render(request, 'admin/admindash_telecaller_joined_leads.html', context)




def admindash_telecaller_joined_leads_follow_up_details(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    
    assignment = LeadAssignedToTC.objects.filter(lead=lead).order_by('-id').first()

    client = None
    if lead.lead_category and hasattr(lead.lead_category, 'client_task'):
        if lead.lead_category.client_task:
            client = lead.lead_category.client_task.client
    
    followups = FollowupDetails.objects.filter(lead=lead).order_by('-response_date')
    followup_list = [{
        'telecaller': f.telecaller.name if f.telecaller else "N/A",
        'date': f.response_date.strftime('%Y-%m-%d') if f.response_date else "N/A",
        'response': f.response or "No response",
        'next_date': f.next_followup_date.strftime('%Y-%m-%d') if f.next_followup_date else "N/A",
        'status': f.response_status or "N/A"
    } for f in followups]
    
    history = FollowupHistory.objects.filter(lead=lead).order_by('-id')
    history_data = [{
        'telecaller': h.telecaller.name if h.telecaller else "N/A",
        'date': h.allocated_date.strftime('%Y-%m-%d') if h.allocated_date else "N/A",
        'note': h.note or "No note provided",
        'status': h.final_status or "N/A"
    } for h in history]

    recordings = LeadCallRecord.objects.filter(lead=lead).order_by('-id')
    recordings_data = [{
        'date': r.record_date.strftime('%Y-%m-%d') if r.record_date else "N/A",
        'time': r.record_time.strftime('%H:%M') if r.record_time else "",
        'file_url': r.record_file.url if r.record_file else ""
    } for r in recordings]

    data = {
        'name': lead.name or "Unnamed",
        'email': lead.email or "N/A",
        'phone': lead.contact or "N/A",
        'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else "N/A",
        'category': lead.lead_category.collection_for if lead.lead_category else "N/A",
        'client_name': client.client_name if client else "N/A",
        'client_business': client.client_business_name if client else "N/A",
        'collected_by': lead.collected_by.name if lead.collected_by else "N/A",
        'assigned_to': assignment.telecaller.name if assignment and assignment.telecaller else "Not Assigned",
        'current_status': assignment.response if assignment else "Unverified",
        'next_followup': assignment.next_update_date.strftime('%Y-%m-%d') if assignment and assignment.next_update_date else "N/A",
        'followups': followup_list,
        'history': history_data,
        'recordings': recordings_data
    }
    
    return JsonResponse(data)



def excutive_lead_mark_confused(request):
    print("--- Mark Confused View Triggered ---")
    
    if 'eid' not in request.session:
        messages.error(request, "Please login as an Executive to continue.")
        return redirect('login') 

    if request.method == "POST":
        lead_id = request.POST.get('lead_id')
        reason = request.POST.get('reason')
        session_username = request.session.get('eid')

        try:
            lead_obj = Leads.objects.get(id=lead_id)
            
            if hasattr(lead_obj, 'lead_category') and lead_obj.lead_category:
                cat_id = lead_obj.lead_category.id
            else:
                return redirect(request.META.get('HTTP_REFERER', '/'))

            try:
                executive = EmployeeRegister_Details.objects.get(login__log_username=session_username)

                from .validators import has_valid_email_or_phone
                if not has_valid_email_or_phone(lead_obj):
                    messages.error(request, "Add an email or a phone number before marking this lead as confused")
                    return redirect('lead_list', category_id=cat_id)

                LeadConfused.objects.create(
                    lead=lead_obj,
                    reason=reason,
                    executive_id=executive
                )
                
                messages.success(request, f"Lead {lead_obj.name} marked as confused.")
                
                return redirect('lead_list', category_id=cat_id)

            except EmployeeRegister_Details.DoesNotExist:
                messages.error(request, "Executive profile not found.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        except Leads.DoesNotExist:
            messages.error(request, "Lead not found.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
            
    return redirect(request.META.get('HTTP_REFERER', '/'))






def admindash_executive_confused_leads(request, exec_id, client_id):
    executive = get_object_or_404(EmployeeRegister_Details, id=exec_id)
    client = get_object_or_404(ClientRegister, id=client_id)
    
    confused_leads_list = LeadConfused.objects.filter(executive_id=executive,lead__lead_category__client_task__client=client).select_related('lead', 'lead__lead_category').order_by('-created_at')


    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    per_page = request.GET.get('per_page', 10) 
    page_number = request.GET.get('page')


    if from_date:
        confused_leads_list = confused_leads_list.filter(lead__added_date__gte=from_date)
    if to_date:
        confused_leads_list = confused_leads_list.filter(lead__added_date__lte=to_date)

    total_confused = confused_leads_list.count()

    paginator = Paginator(confused_leads_list, per_page)
    confused_leads = paginator.get_page(page_number)

    aid = request.session.get('aid')
    company = None
    if aid:
        try:
            user = LogRegister_Details.objects.get(log_username=aid)
            company = BusinessRegister_Details.objects.filter(login=user).first()
        except LogRegister_Details.DoesNotExist:
            pass

    context = {
        'executive': executive,
        'client': client,
        'company': company,
        'confused_leads': confused_leads,
        'total_confused': total_confused,
        'from_date': from_date,
        'to_date': to_date,
        'per_page': int(per_page),
    }

    return render(request, 'admin/admindash_executive_confused_leads.html', context)





def admindash_convert_confused_lead(request):
    if request.method == "POST":
        lead_id = request.POST.get('lead_id')
        confused_id = request.POST.get('confused_entry_id')
        exec_id = request.POST.get('exec_id')
        client_id = request.POST.get('client_id')
        
        lead = get_object_or_404(Leads, id=lead_id)
        lead.name = request.POST.get('name')
        lead.email = request.POST.get('email')
        lead.contact = request.POST.get('contact')
        lead.source = request.POST.get('source')
        lead.save()
        
        LeadConfused.objects.filter(id=confused_id).delete()
        
        messages.success(request, f"Lead '{lead.name}' successfully corrected and moved.")
        
        if exec_id and client_id:
            return redirect('admindash_executive_confused_leads', exec_id=exec_id, client_id=client_id)
    

    return redirect('admindash_executive_confused_leads', exec_id=exec_id, client_id=client_id)




def admindash_leads_report(request):
    session_username = request.session.get('aid')
    
    if not session_username:
        return redirect('login') 

    try:
        current_business = BusinessRegister_Details.objects.get(login__log_username=session_username)
    except BusinessRegister_Details.DoesNotExist:
        messages.error(request, "Business/Company record not found.")
        return redirect('login')

    leads_response = LeadAssignedToTC.objects.filter(
        lead=OuterRef('pk')
    ).order_by('-id').values('response')[:1]

    allocated = LeadAssignedToTC.objects.filter(lead=OuterRef('pk'))

    leads = Leads.objects.filter(
        collected_by__company=current_business
    ).annotate(
        is_allocated=Exists(allocated),
        dynamic_tc_response=Subquery(leads_response) 
    ).order_by('-added_date')

    clients_list = ClientRegister.objects.filter(company=current_business)
    categories_list = LeadCategory_Register.objects.filter(
        client_task__client__company=current_business
    ).distinct()
    
    employees_list = EmployeeRegister_Details.objects.filter(
        Q(company=current_business) & 
        (Q(designation__name__icontains='Digital_Marketing_Head') | 
         Q(designation__name__icontains='Team_Lead') | 
         Q(designation__name__icontains='Executive'))
    )
    
    telecallers_list = EmployeeRegister_Details.objects.filter(
        company=current_business, 
        designation__name__icontains='Telecaller'
    )
    followup_statuses = FollowupStatus.objects.values_list('status_name', flat=True)
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    selected_lead_status = request.GET.get('lead_status')
    selected_followup = request.GET.get('followup_status')
    selected_client = request.GET.get('client_filter')
    selected_category = request.GET.get('category_filter')
    selected_added_by = request.GET.get('added_by')
    selected_tc = request.GET.get('telecaller')
    per_page = request.GET.get('per_page', 10)
    page_number = request.GET.get('page')

    if from_date:
        leads = leads.filter(added_date__gte=from_date)
    if to_date:
        leads = leads.filter(added_date__lte=to_date)

    if selected_client:
        leads = leads.filter(lead_category__client_task__client_id=selected_client)
    if selected_category:
        leads = leads.filter(lead_category_id=selected_category)
    
    if selected_added_by:
        leads = leads.filter(collected_by_id=selected_added_by)
    
    if selected_tc:
        leads = leads.filter(leadassignedtotc__telecaller_id=selected_tc)

    if selected_lead_status:
        if selected_lead_status == "Allocated":
            leads = leads.filter(is_allocated=True)
        elif selected_lead_status == "Not Allocated":
            leads = leads.filter(is_allocated=False)
        elif selected_lead_status == "Verified":
            leads = leads.filter(status=1)
        elif selected_lead_status == "Unverified":
            leads = leads.filter(status=0)
        else:
            leads = leads.filter(dynamic_tc_response=selected_lead_status)

    if selected_followup:
        leads = leads.filter(dynamic_tc_response=selected_followup)

    leads = leads.distinct()
    total_leads_count = leads.count()
    
    try:
        per_page = int(per_page)
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(leads, per_page)
    leads_list = paginator.get_page(page_number)

    context = {
        'leads_list': leads_list,
        'total_leads_count': total_leads_count,
        'from_date': from_date,
        'to_date': to_date,
        'selected_lead_status': selected_lead_status,
        'selected_followup': selected_followup,
        'selected_client': selected_client,
        'selected_category': selected_category,
        'selected_added_by': selected_added_by,
        'selected_tc': selected_tc,
        'per_page': per_page,
        'company': current_business,
        'clients': clients_list,
        'categories': categories_list,
        'employees': employees_list,
        'telecallers': telecallers_list,
        'followup_statuses': followup_statuses,
    }
    return render(request, 'admin/admindash_leads_report.html', context)





def admindash_get_lead__report_details(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    
    assignment = LeadAssignedToTC.objects.filter(lead=lead).order_by('-id').first()

    client = None
    if lead.lead_category and hasattr(lead.lead_category, 'client_task'):
        client = lead.lead_category.client_task.client
    
    followups = FollowupDetails.objects.filter(lead=lead).order_by('-response_date')
    followup_list = [{
        'telecaller': f.telecaller.name if f.telecaller else "N/A",
        'date': f.response_date.strftime('%Y-%m-%d') if f.response_date else "N/A",
        'response': f.response,
        'next_date': f.next_followup_date.strftime('%Y-%m-%d') if f.next_followup_date else "N/A",
        'status': f.response_status
    } for f in followups]
    
    history = FollowupHistory.objects.filter(lead=lead).order_by('-id')
    history_data = [{
        'telecaller': h.telecaller.name if h.telecaller else "N/A",
        'date': h.allocated_date.strftime('%Y-%m-%d') if h.allocated_date else "N/A",
        'note': h.note or "No note provided",
        'status': h.final_status
    } for h in history]

    recordings = LeadCallRecord.objects.filter(lead=lead).order_by('-id')
    recordings_data = [{
        'date': r.record_date.strftime('%Y-%m-%d'),
        'time': r.record_time.strftime('%H:%M') if r.record_time else "",
        'file_url': r.record_file.url if r.record_file else ""
    } for r in recordings]

    data = {
        'name': lead.name or "Unnamed",
        'email': lead.email or "N/A",
        'phone': lead.contact or "N/A",
        'added_date': lead.added_date.strftime('%Y-%m-%d') if lead.added_date else "N/A",
        'category': lead.lead_category.collection_for if lead.lead_category else "N/A",
        'client_name': client.client_name if client else "N/A",
        'client_business': client.client_business_name if client else "N/A",
        'collected_by': lead.collected_by.name if lead.collected_by else "N/A",
        'assigned_to': assignment.telecaller.name if assignment and assignment.telecaller else "Not Assigned",
        'current_status': assignment.response if assignment else "Unverified",
        'next_followup': assignment.next_update_date.strftime('%Y-%m-%d') if assignment and assignment.next_update_date else "N/A",
        'followups': followup_list,
        'history': history_data,
        'recordings': recordings_data
    }
    return JsonResponse(data)



# ---------------------------------------------- End Admin Dashboard Card work Balance ---------------------------------------------------

from django.db.models.functions import TruncDate
from django.db.models.functions import ExtractMonth, ExtractYear

def admin_target_executive(request):

    aid = request.session.get('aid')

    user = LogRegister_Details.objects.get(
        log_username=aid
    )

    company = BusinessRegister_Details.objects.filter(
        login=user
    ).first()

    name = EmployeeRegister_Details.objects.filter(
        login=user
    ).first()


    executive = EmployeeRegister_Details.objects.filter(
        company=company, designation__dashboard_id='Executive'
    )

  

    selected_executive = request.GET.get('executive')

    from_date = request.GET.get('from_date')

    to_date = request.GET.get('to_date')

 

    target = TargetAssign.objects.filter(
        company=company
    )

  

    if selected_executive:

        target = target.filter(
            executive_id=selected_executive
        )



    if from_date:

        target = target.filter(
            created_at__date__gte=from_date
        )

    if to_date:

        target = target.filter(
            created_at__date__lte=to_date
        )

    target = target.order_by('-year')

  

    leads = Leads.objects.filter(
        collected_by__company=company
    )


   

    if from_date:

        leads = leads.filter(
            added_date__gte=from_date
        )

  

    if to_date:

        leads = leads.filter(
            added_date__lte=to_date
        )



    achieved_data = (

        leads.annotate(
            month_num=ExtractMonth('added_date'),
            year_num=ExtractYear('added_date')
        )

        .values(
            'collected_by',
            'month_num',
            'year_num'
        )

        .annotate(
            total=Count('id')
        )

    )



    month_map = {

        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'

    }



    achieved_dict = {

        (
            item['collected_by'],
            month_map.get(item['month_num']),
            item['year_num']

        ): item['total']

        for item in achieved_data

    }

   

    for t in target:

        key = (
            t.executive.id,
            t.month,
            t.year
        )

        t.achieved = achieved_dict.get(key, 0)

    return render(request, 'admin/admin_target_executive.html', {

        'user': user,
        'company': company,
        'name': name,

        'target': target,
        'executive': executive,

        'selected_executive': selected_executive,
        'from_date': from_date,
        'to_date': to_date,

    })


def get_target_actions(request, id):

    actions = TargetAction.objects.filter(target_id=id).order_by('-created_at')

    data = []

    for i in actions:
        data.append({
            'executive': i.executive.name,
            'action_taken': i.action_taken,
            'date': i.created_at.strftime('%d-%m-%Y %I:%M %p')
        })

    return JsonResponse({
        'status': 'success',
        'data': data
    })



def admin_target_telecaller(request):

    aid = request.session.get('aid')

    user = LogRegister_Details.objects.get(
        log_username=aid
    )

    company = BusinessRegister_Details.objects.filter(
        login=user
    ).first()

    name = EmployeeRegister_Details.objects.filter(
        login=user
    ).first()

    employee = EmployeeRegister_Details.objects.filter(
        company=company,
        designation__dashboard_id='Telecaller'
    )



    selected_employee = request.GET.get('telecaller')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

   

    target = LeadAssignedToTC.objects.filter(
        telecaller__company=company
    )



    if selected_employee:
        target = target.filter(
            telecaller_id=selected_employee
        )

  

    if from_date:
        target = target.filter(
            assign_date__gte=from_date
        )

    if to_date:
        target = target.filter(
            assign_date__lte=to_date
        )



    target = target.values(
        'telecaller__id',
        'telecaller__name',
        'assign_date'
    ).annotate(

        allocated_count=Count(
            'id',
            distinct=True
        ),

        followup_count=Count(
            'telecaller__followupdetails',
            distinct=True
        )

    ).order_by('-assign_date')

    return render(request, 'admin/admin_target_telecaller.html', {

        'user': user,
        'company': company,
        'name': name,

        'target': target,
        'employee': employee,

        'selected_employee': selected_employee,
        'from_date': from_date,
        'to_date': to_date,

    })




def graphics_designer(request):
    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    return render(request, 'graphic_designer/graphic_designer_dash.html', {
        'user': user,
        'company': company,
        'name':name,

    })


def image_analysis(request):
    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    return render(request, 'graphic_designer/image_analysis.html', {
        'user': user,
        'company': company,
        'name':name,

    })


def image_analyzer_page(request):
    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None


    return render(request, 'graphic_designer/image_analyzer_page.html' , {
        'user': user,
        'company': company,
        'name':name,

    })


from PIL import Image as PILImage



def upload_image(request):
    """Handle image upload and enhanced marketing analysis"""

    
    if request.method == 'POST':
        print(f"Request method: {request.method}")
        print(f"Request FILES: {request.FILES}")
        print(f"Request POST: {request.POST}")
        
        try:
            # Check if image was uploaded
            if 'image' not in request.FILES:
                print("No image in request.FILES")
                messages.error(request, 'Please select an image to upload.')
                return redirect('image_analysis')
            
            uploaded_file = request.FILES['image']
            print(f"Uploaded file: {uploaded_file.name}, size: {uploaded_file.size}")
            
            # Validate file
            if not uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                print("Invalid file type")
                messages.error(request, 'Please upload a valid image file (JPG, PNG, GIF, BMP, or WebP).')
                return redirect('image_analysis')
            
            # Validate file size (10MB max)
            if uploaded_file.size > 10 * 1024 * 1024:
                print("File too large")
                messages.error(request, 'File size must be less than 10MB.')
                return redirect('image_analysis')
            
            # Get image dimensions
            try:
                pil_image = PILImage.open(uploaded_file)
                width, height = pil_image.size
                print(f"Image dimensions: {width}x{height}")
            except Exception as e:
                print(f"Invalid image file: {str(e)}")
                messages.error(request, f'Invalid image file: {str(e)}')
                return redirect('image_analysis')
            
            # Create MarketingImage instance with marketing context
            marketing_image = MarketingImage(
                title=request.POST.get('title', 'Marketing Image'),
                image=uploaded_file,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                width=width,
                height=height,
                target_audience=request.POST.get('target_audience', ''),
                campaign_type=request.POST.get('campaign_type', ''),
                industry=request.POST.get('industry', ''),
                call_to_action=request.POST.get('call_to_action', '')
            )
            marketing_image.save()
            
            # Perform enhanced marketing analysis
            try:
                analysis_service = MarketingAnalysisService()
                analysis_result = analysis_service.analyze_image(marketing_image)
                
                # Save analysis results with improvement suggestions
                suggestions = analysis_result['improvement_suggestions']
                image_analysis = ImageAnalysis(
                    marketing_image=marketing_image,
                    visual_clarity_score=75,  # Default scores since we're focusing on suggestions
                    color_usage_score=75,
                    layout_score=75,
                    balance_score=75,
                    visual_overall_score=75,
                    brand_consistency_score=75,
                    message_clarity_score=75,
                    visual_hierarchy_score=75,
                    emotional_impact_score=75,
                    conversion_optimization_score=75,
                    audience_relevance_score=75,
                    marketing_overall_score=75,
                    overall_score=75,
                    
                    # NEW: Store suggestions in dedicated fields
                    visual_clarity_suggestion=suggestions['visual_clarity'],
                    font_size_suggestion=suggestions['font_size'],
                    font_style_suggestion=suggestions['font_style'],
                    font_color_suggestion=suggestions['font_color'],
                    text_alignment_suggestion=suggestions['text_alignment'],
                    background_color_suggestion=suggestions['background_color'],
                    text_visibility_suggestion=suggestions['text_visibility'],
                    color_harmony_suggestion=suggestions['color_harmony'],
                    element_placement_suggestion=suggestions['element_placement'],
                    text_image_balance_suggestion=suggestions['text_image_balance'],
                    spacing_white_space_suggestion=suggestions['spacing_white_space'],
                    
                    # Keep original fields for backward compatibility
                    marketing_strategy_insights=suggestions['visual_clarity'],
                    competitive_positioning=suggestions['font_size'],
                    psychological_triggers=suggestions['font_style'],
                    cultural_considerations=suggestions['font_color'],
                    platform_optimization=suggestions['text_alignment'],
                    visual_improvements=suggestions['background_color'],
                    marketing_improvements=suggestions['text_visibility'],
                    strategic_recommendations=suggestions['color_harmony'],
                    accessibility_compliance=suggestions['element_placement'],
                    legal_considerations=suggestions['text_image_balance'],
                    platform_guidelines=suggestions['spacing_white_space'],
                    analysis_duration=analysis_result['analysis_duration'],
                    llm_tokens_used=analysis_result['llm_tokens_used']
                )
                image_analysis.save()
                
                # Generate and save design-only improvement prompt
                design_prompt = _generate_design_prompt_from_analysis(image_analysis)
                image_analysis.design_improvement_prompt = design_prompt
                
                image_analysis.save()
                
                # Update analyzed timestamp
                marketing_image.analyzed_at = image_analysis.created_at
                marketing_image.save()
                
                messages.success(request, 'Image uploaded and analyzed successfully!')
                return redirect('analysis_results', image_id=marketing_image.id)
                
            except Exception as analysis_error:
                # If analysis fails, still save the image but show error
                marketing_image.analyzed_at = None
                marketing_image.save()
                messages.error(request, f'Image uploaded but analysis failed: {str(analysis_error)}. Please try analyzing again.')
                return redirect('analysis_results', image_id=marketing_image.id)
            
        except Exception as e:
            messages.error(request, f'Error uploading image: {str(e)}')
            return redirect('image_analysis')
    
    return redirect('image_analyzer_page')

def analysis_results(request, image_id):
    """Display enhanced marketing analysis results"""

    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None


    try:
        marketing_image = MarketingImage.objects.get(id=image_id)
        
        # Check if analysis exists
        try:
            analysis = ImageAnalysis.objects.get(marketing_image=marketing_image)
        except ImageAnalysis.DoesNotExist:
            messages.warning(request, 'Analysis not available for this image. The image was uploaded but analysis failed or is still processing.')
            # Create default scores for display
            context = {
                'marketing_image': marketing_image,
                'analysis': None,
                'visual_scores': {
                    'visual_clarity': 0,
                    'color_usage': 0,
                    'layout': 0,
                    'balance': 0,
                    'visual_overall': 0
                },
                'marketing_scores': {
                    'brand_consistency': 0,
                    'message_clarity': 0,
                    'visual_hierarchy': 0,
                    'emotional_impact': 0,
                    'conversion_optimization': 0,
                    'audience_relevance': 0,
                    'marketing_overall': 0
                },
                'overall_score': 0
            }
            return render(request, 'graphic_designer/improvement_results.html', context)
        
        context = {
            'user': user,
            'company': company,
            'name':name,
            'marketing_image': marketing_image,
            'analysis': analysis,
            'visual_scores': {
                'visual_clarity': analysis.visual_clarity_score or 0,
                'color_usage': analysis.color_usage_score or 0,
                'layout': analysis.layout_score or 0,
                'balance': analysis.balance_score or 0,
                'visual_overall': analysis.visual_overall_score or 0
            },
            'marketing_scores': {
                'brand_consistency': analysis.brand_consistency_score or 0,
                'message_clarity': analysis.message_clarity_score or 0,
                'visual_hierarchy': analysis.visual_hierarchy_score or 0,
                'emotional_impact': analysis.emotional_impact_score or 0,
                'conversion_optimization': analysis.conversion_optimization_score or 0,
                'audience_relevance': analysis.audience_relevance_score or 0,
                'marketing_overall': analysis.marketing_overall_score or 0
            },
            'overall_score': analysis.overall_score or 0
        }
        return render(request, 'graphic_designer/improvement_results.html', context)
        
    except MarketingImage.DoesNotExist:
        messages.error(request, 'Image not found.')
        return redirect('image_analysis')




def retry_analysis(request, image_id):
    """Retry analysis for an existing image"""
    try:
        marketing_image = MarketingImage.objects.get(id=image_id)
        
        # Delete existing analysis if it exists
        try:
            existing_analysis = ImageAnalysis.objects.get(marketing_image=marketing_image)
            existing_analysis.delete()
        except ImageAnalysis.DoesNotExist:
            pass
        
        # Perform new analysis
        try:
            analysis_service = MarketingAnalysisService()
            analysis_result = analysis_service.analyze_image(marketing_image)
            
            # Save new analysis results
            image_analysis = ImageAnalysis(
                marketing_image=marketing_image,
                visual_clarity_score=analysis_result['visual_scores']['visual_clarity'],
                color_usage_score=analysis_result['visual_scores']['color_usage'],
                layout_score=analysis_result['visual_scores']['layout'],
                balance_score=analysis_result['visual_scores']['balance'],
                visual_overall_score=analysis_result['visual_scores']['visual_overall'],
                brand_consistency_score=analysis_result['marketing_scores']['brand_consistency'],
                message_clarity_score=analysis_result['marketing_scores']['message_clarity'],
                visual_hierarchy_score=analysis_result['marketing_scores']['visual_hierarchy'],
                emotional_impact_score=analysis_result['marketing_scores']['emotional_impact'],
                conversion_optimization_score=analysis_result['marketing_scores']['conversion_optimization'],
                audience_relevance_score=analysis_result['marketing_scores']['audience_relevance'],
                marketing_overall_score=analysis_result['marketing_scores']['marketing_overall'],
                overall_score=analysis_result['overall_score'],
                marketing_strategy_insights=analysis_result['insights']['marketing_strategy_insights'],
                competitive_positioning=analysis_result['insights']['competitive_positioning'],
                psychological_triggers=analysis_result['insights']['psychological_triggers'],
                cultural_considerations=analysis_result['insights']['cultural_considerations'],
                platform_optimization=analysis_result['insights']['platform_optimization'],
                visual_improvements=analysis_result['recommendations']['visual_improvements'],
                marketing_improvements=analysis_result['recommendations']['marketing_improvements'],
                strategic_recommendations=analysis_result['recommendations']['strategic_recommendations'],
                accessibility_compliance=analysis_result['compliance']['accessibility_compliance'],
                legal_considerations=analysis_result['compliance']['legal_considerations'],
                platform_guidelines=analysis_result['compliance']['platform_guidelines'],
                analysis_duration=analysis_result['analysis_duration'],
                llm_tokens_used=analysis_result['llm_tokens_used']
            )
            image_analysis.save()
            
            # Update analyzed timestamp
            marketing_image.analyzed_at = image_analysis.created_at
            marketing_image.save()
            
            messages.success(request, 'Analysis completed successfully!')
            return redirect('analysis_results', image_id=marketing_image.id)
            
        except Exception as analysis_error:
            marketing_image.analyzed_at = None
            marketing_image.save()
            messages.error(request, f'Analysis failed: {str(analysis_error)}. Please try again.')
            return redirect('analysis_results', image_id=marketing_image.id)
            
    except MarketingImage.DoesNotExist:
        messages.error(request, 'Image not found.')
        return redirect('image_analysis')


@csrf_exempt
def api_analyze_image(request):
    """API endpoint for enhanced marketing image analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        # Process similar to upload_image but return JSON
        pil_image = PILImage.open(uploaded_file)
        width, height = pil_image.size
        
        marketing_image = MarketingImage(
            title=request.POST.get('title', ''),
            image=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            width=width,
            height=height,
            target_audience=request.POST.get('target_audience', ''),
            campaign_type=request.POST.get('campaign_type', ''),
            industry=request.POST.get('industry', ''),
            call_to_action=request.POST.get('call_to_action', '')
        )
        marketing_image.save()
        
        analysis_service = MarketingAnalysisService()
        analysis_result = analysis_service.analyze_image(marketing_image)
        
        image_analysis = ImageAnalysis(
            marketing_image=marketing_image,
            visual_clarity_score=analysis_result['visual_scores']['visual_clarity'],
            color_usage_score=analysis_result['visual_scores']['color_usage'],
            layout_score=analysis_result['visual_scores']['layout'],
            balance_score=analysis_result['visual_scores']['balance'],
            visual_overall_score=analysis_result['visual_scores']['visual_overall'],
            brand_consistency_score=analysis_result['marketing_scores']['brand_consistency'],
            message_clarity_score=analysis_result['marketing_scores']['message_clarity'],
            visual_hierarchy_score=analysis_result['marketing_scores']['visual_hierarchy'],
            emotional_impact_score=analysis_result['marketing_scores']['emotional_impact'],
            conversion_optimization_score=analysis_result['marketing_scores']['conversion_optimization'],
            audience_relevance_score=analysis_result['marketing_scores']['audience_relevance'],
            marketing_overall_score=analysis_result['marketing_scores']['marketing_overall'],
            overall_score=analysis_result['overall_score'],
            marketing_strategy_insights=analysis_result['insights']['marketing_strategy_insights'],
            competitive_positioning=analysis_result['insights']['competitive_positioning'],
            psychological_triggers=analysis_result['insights']['psychological_triggers'],
            cultural_considerations=analysis_result['insights']['cultural_considerations'],
            platform_optimization=analysis_result['insights']['platform_optimization'],
            visual_improvements=analysis_result['recommendations']['visual_improvements'],
            marketing_improvements=analysis_result['recommendations']['marketing_improvements'],
            strategic_recommendations=analysis_result['recommendations']['strategic_recommendations'],
            accessibility_compliance=analysis_result['compliance']['accessibility_compliance'],
            legal_considerations=analysis_result['compliance']['legal_considerations'],
            platform_guidelines=analysis_result['compliance']['platform_guidelines'],
            analysis_duration=analysis_result['analysis_duration'],
            llm_tokens_used=analysis_result['llm_tokens_used']
        )
        image_analysis.save()
        
        return JsonResponse({
            'success': True,
            'image_id': marketing_image.id,
            'analysis': {
                'overall_score': image_analysis.overall_score,
                'visual_scores': {
                    'visual_clarity': image_analysis.visual_clarity_score,
                    'color_usage': image_analysis.color_usage_score,
                    'layout': image_analysis.layout_score,
                    'balance': image_analysis.balance_score,
                    'visual_overall': image_analysis.visual_overall_score
                },
                'marketing_scores': {
                    'brand_consistency': image_analysis.brand_consistency_score,
                    'message_clarity': image_analysis.message_clarity_score,
                    'visual_hierarchy': image_analysis.visual_hierarchy_score,
                    'emotional_impact': image_analysis.emotional_impact_score,
                    'conversion_optimization': image_analysis.conversion_optimization_score,
                    'audience_relevance': image_analysis.audience_relevance_score,
                    'marketing_overall': image_analysis.marketing_overall_score
                },
                'insights': {
                    'strategy_insights': image_analysis.marketing_strategy_insights,
                    'competitive_positioning': image_analysis.competitive_positioning,
                    'psychological_triggers': image_analysis.psychological_triggers,
                    'cultural_considerations': image_analysis.cultural_considerations,
                    'platform_optimization': image_analysis.platform_optimization
                },
                'recommendations': {
                    'visual_improvements': image_analysis.visual_improvements,
                    'marketing_improvements': image_analysis.marketing_improvements,
                    'strategic_recommendations': image_analysis.strategic_recommendations
                },
                'compliance': {
                    'accessibility_compliance': image_analysis.accessibility_compliance,
                    'legal_considerations': image_analysis.legal_considerations,
                    'platform_guidelines': image_analysis.platform_guidelines
                },
                'metadata': {
                    'analysis_duration': image_analysis.analysis_duration,
                    'llm_tokens_used': image_analysis.llm_tokens_used
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


import time
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class MarketingAnalysisService:
    """Service for AI-powered marketing image analysis"""
    
    def analyze_image(self, marketing_image):
        """Perform comprehensive marketing analysis using Groq Vision AI with fallback to text-only"""
        start_time = time.time()
        
        try:
            # Try vision model first
            print(f"DEBUG: Attempting vision analysis for image {marketing_image.id}")
            
            # Encode image to base64 for vision model
            image_base64 = _encode_image_to_base64(marketing_image.image)
            
            if not image_base64:
                raise Exception("Failed to encode image")
            
            print(f"DEBUG: Image encoded successfully, attempting vision API call")
            
            # Construct vision analysis prompt
            analysis_prompt = f"""Analyze this marketing image as an expert visual marketing consultant and provide specific improvement suggestions to increase reach and effectiveness:

Image Information:
- Title: {marketing_image.title}
- Campaign Type: {marketing_image.campaign_type}
- Industry: {marketing_image.industry}
- Call to Action: {marketing_image.call_to_action}

Please respond with a JSON object in this exact format:

{{
  "VISUAL CLARITY & READABILITY": {{
    "Text clarity and font readability": "specific suggestion here",
    "Image sharpness and resolution": "specific suggestion here",
    "Overall visual clarity issues": "specific suggestion here"
  }},
  "FONT & TYPOGRAPHY IMPROVEMENTS": {{
    "Font size recommendations for headlines and body text": "specific suggestion here",
    "Font style suggestions for better readability": "specific suggestion here",
    "Font color and contrast improvements": "specific suggestion here",
    "Text alignment and spacing recommendations": "specific suggestion here",
    "Hierarchy improvements for better visual flow": "specific suggestion here"
  }},
  "COLOR USAGE & CONTRAST": {{
    "Background color effectiveness": "specific suggestion here",
    "Text color visibility and contrast": "specific suggestion here",
    "Color harmony and psychology": "specific suggestion here",
    "Specific color palette suggestions": "specific suggestion here",
    "Contrast improvements for better readability": "specific suggestion here"
  }},
  "LAYOUT & COMPOSITION": {{
    "Element placement and alignment": "specific suggestion here",
    "Balance between text and imagery": "specific suggestion here",
    "Spacing and white space usage": "specific suggestion here",
    "Visual hierarchy improvements": "specific suggestion here",
    "Layout structure suggestions": "specific suggestion here"
  }},
  "IMAGE SIZE & SCALING": {{
    "Current image size appropriateness": "specific suggestion here",
    "Scaling recommendations for different platforms": "specific suggestion here",
    "Resolution and quality improvements": "specific suggestion here",
    "Aspect ratio considerations": "specific suggestion here"
  }},
  "CALL-TO-ACTION EFFECTIVENESS": {{
    "CTA visibility and prominence": "specific suggestion here",
    "CTA design and placement suggestions": "specific suggestion here",
    "Button or link effectiveness": "specific suggestion here",
    "Action-oriented text improvements": "specific suggestion here"
  }},
  "OVERALL ATTRACTIVENESS": {{
    "Visual appeal improvements": "specific suggestion here",
    "Engagement factor enhancements": "specific suggestion here",
    "Brand consistency suggestions": "specific suggestion here",
    "Modern design recommendations": "specific suggestion here"
  }}
}}

Focus on actionable, specific recommendations that can be implemented to increase reach and marketing effectiveness. Replace the placeholder text with actual specific suggestions based on the actual image you see."""

            # Make API call to Groq Vision model
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            print(f"DEBUG: Vision API call successful")
            analysis_text = response.choices[0].message.content
            
        except Exception as vision_error:
            print(f"DEBUG: Vision model failed: {str(vision_error)}")
            print(f"DEBUG: Falling back to text-only model")
            
            # Fallback to text-only model
            analysis_prompt = f"""Analyze this marketing image as an expert visual marketing consultant and provide specific improvement suggestions to increase reach and effectiveness:

Image Information:
- Title: {marketing_image.title}
- Campaign Type: {marketing_image.campaign_type}
- Industry: {marketing_image.industry}
- Call to Action: {marketing_image.call_to_action}

Please respond with a JSON object in this exact format:

{{
  "VISUAL CLARITY & READABILITY": {{
    "Text clarity and font readability": "specific suggestion here",
    "Image sharpness and resolution": "specific suggestion here",
    "Overall visual clarity issues": "specific suggestion here"
  }},
  "FONT & TYPOGRAPHY IMPROVEMENTS": {{
    "Font size recommendations for headlines and body text": "specific suggestion here",
    "Font style suggestions for better readability": "specific suggestion here",
    "Font color and contrast improvements": "specific suggestion here",
    "Text alignment and spacing recommendations": "specific suggestion here",
    "Hierarchy improvements for better visual flow": "specific suggestion here"
  }},
  "COLOR USAGE & CONTRAST": {{
    "Background color effectiveness": "specific suggestion here",
    "Text color visibility and contrast": "specific suggestion here",
    "Color harmony and psychology": "specific suggestion here",
    "Specific color palette suggestions": "specific suggestion here",
    "Contrast improvements for better readability": "specific suggestion here"
  }},
  "LAYOUT & COMPOSITION": {{
    "Element placement and alignment": "specific suggestion here",
    "Balance between text and imagery": "specific suggestion here",
    "Spacing and white space usage": "specific suggestion here",
    "Visual hierarchy improvements": "specific suggestion here",
    "Layout structure suggestions": "specific suggestion here"
  }},
  "IMAGE SIZE & SCALING": {{
    "Current image size appropriateness": "specific suggestion here",
    "Scaling recommendations for different platforms": "specific suggestion here",
    "Resolution and quality improvements": "specific suggestion here",
    "Aspect ratio considerations": "specific suggestion here"
  }},
  "CALL-TO-ACTION EFFECTIVENESS": {{
    "CTA visibility and prominence": "specific suggestion here",
    "CTA design and placement suggestions": "specific suggestion here",
    "Button or link effectiveness": "specific suggestion here",
    "Action-oriented text improvements": "specific suggestion here"
  }},
  "OVERALL ATTRACTIVENESS": {{
    "Visual appeal improvements": "specific suggestion here",
    "Engagement factor enhancements": "specific suggestion here",
    "Brand consistency suggestions": "specific suggestion here",
    "Modern design recommendations": "specific suggestion here"
  }}
}}

Focus on actionable, specific recommendations that can be implemented to increase reach and marketing effectiveness. Replace the placeholder text with actual specific suggestions based on the image information provided."""

            # Make API call to text-only model
            print(f"DEBUG: Making text-only fallback API call")
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert marketing analyst and visual communication specialist. Provide detailed, actionable insights for marketing images."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            print(f"DEBUG: Text-only fallback successful")
            analysis_text = response.choices[0].message.content
            
        # Extract JSON from response (common for both vision and fallback)
        try:
            # Find JSON in the response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = analysis_text[json_start:json_end]
                ai_response = json.loads(json_str)
                
                # Transform AI response to expected format (handle both lowercase and capitalized keys)
                def get_section(section_name, capitalized_name):
                    return ai_response.get(section_name, ai_response.get(capitalized_name, {}))
                
                def get_score(section, key, default=70):
                    value = section.get(key, default)
                    # Handle arrays (convert to string)
                    if isinstance(value, list):
                        return ', '.join(str(item) for item in value)
                    # For numeric scores, return as int
                    if isinstance(value, (int, float)):
                        return int(value)
                    return value
                
                visual_section = get_section('visual_analysis', 'Visual Analysis')
                marketing_section = get_section('marketing_effectiveness', 'Marketing Effectiveness')
                insights_section = get_section('strategic_insights', 'Strategic Insights')
                recommendations_section = get_section('improvement_recommendations', 'Improvement Recommendations')
                compliance_section = get_section('compliance_check', 'Compliance Check')
                
                # Transform AI response to expected format for improvement suggestions
                def get_suggestion(section, key, default='No specific suggestions available'):
                    value = section.get(key, default)
                    # Handle arrays (convert to string)
                    if isinstance(value, list):
                        return ', '.join(str(item) for item in value)
                    return str(value)
                
                # Get improvement suggestion sections
                clarity_section = get_section('VISUAL CLARITY & READABILITY', 'VISUAL CLARITY & READABILITY')
                font_section = get_section('FONT & TYPOGRAPHY IMPROVEMENTS', 'FONT & TYPOGRAPHY IMPROVEMENTS')
                color_section = get_section('COLOR USAGE & CONTRAST', 'COLOR USAGE & CONTRAST')
                layout_section = get_section('LAYOUT & COMPOSITION', 'LAYOUT & COMPOSITION')
                size_section = get_section('IMAGE SIZE & SCALING', 'IMAGE SIZE & SCALING')
                cta_section = get_section('CALL-TO-ACTION EFFECTIVENESS', 'CALL-TO-ACTION EFFECTIVENESS')
                attractiveness_section = get_section('OVERALL ATTRACTIVENESS', 'OVERALL ATTRACTIVENESS')
                
                # Transform AI response to improvement-focused format
                analysis_data = {
                    "improvement_suggestions": {
                        "visual_clarity": get_suggestion(clarity_section, 'Text clarity and font readability'),
                        "image_sharpness": get_suggestion(clarity_section, 'Image sharpness and resolution'),
                        "overall_clarity": get_suggestion(clarity_section, 'Overall visual clarity issues'),
                        
                        "font_size": get_suggestion(font_section, 'Font size recommendations for headlines and body text'),
                        "font_style": get_suggestion(font_section, 'Font style suggestions for better readability'),
                        "font_color": get_suggestion(font_section, 'Font color and contrast improvements'),
                        "text_alignment": get_suggestion(font_section, 'Text alignment and spacing recommendations'),
                        "text_hierarchy": get_suggestion(font_section, 'Hierarchy improvements for better visual flow'),
                        
                        "background_color": get_suggestion(color_section, 'Background color effectiveness'),
                        "text_visibility": get_suggestion(color_section, 'Text color visibility and contrast'),
                        "color_harmony": get_suggestion(color_section, 'Color harmony and psychology'),
                        "color_palette": get_suggestion(color_section, 'Specific color palette suggestions'),
                        "contrast_improvements": get_suggestion(color_section, 'Contrast improvements for better readability'),
                        
                        "element_placement": get_suggestion(layout_section, 'Element placement and alignment'),
                        "text_image_balance": get_suggestion(layout_section, 'Balance between text and imagery'),
                        "spacing_white_space": get_suggestion(layout_section, 'Spacing and white space usage'),
                        "visual_hierarchy": get_suggestion(layout_section, 'Visual hierarchy improvements'),
                        "layout_structure": get_suggestion(layout_section, 'Layout structure suggestions'),
                        
                        "image_size": get_suggestion(size_section, 'Current image size appropriateness'),
                        "scaling_recommendations": get_suggestion(size_section, 'Scaling recommendations for different platforms'),
                        "resolution_quality": get_suggestion(size_section, 'Resolution and quality improvements'),
                        "aspect_ratio": get_suggestion(size_section, 'Aspect ratio considerations'),
                        
                        "cta_visibility": get_suggestion(cta_section, 'CTA visibility and prominence'),
                        "cta_design": get_suggestion(cta_section, 'CTA design and placement suggestions'),
                        "cta_effectiveness": get_suggestion(cta_section, 'Button or link effectiveness'),
                        "action_text": get_suggestion(cta_section, 'Action-oriented text improvements'),
                        
                        "visual_appeal": get_suggestion(attractiveness_section, 'Visual appeal improvements'),
                        "engagement_factor": get_suggestion(attractiveness_section, 'Engagement factor enhancements'),
                        "brand_consistency": get_suggestion(attractiveness_section, 'Brand consistency suggestions'),
                        "modern_design": get_suggestion(attractiveness_section, 'Modern design recommendations')
                    }
                }
                
                # Add metadata
                analysis_data['analysis_duration'] = time.time() - start_time
                analysis_data['llm_tokens_used'] = len(analysis_text.split())
                
                return analysis_data
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_fallback_analysis()
        except Exception as e:
            # Return fallback analysis on error
            print(f"Error in analysis: {str(e)}")
            return self._create_fallback_analysis()
    
    def _create_fallback_analysis(self):
        """Create fallback analysis when AI analysis fails"""
        return {
            "improvement_suggestions": {
                "visual_clarity": "Manual review recommended for text clarity and readability improvements.",
                "image_sharpness": "Consider improving image resolution and sharpness for better visibility.",
                "overall_clarity": "Review overall visual clarity and make necessary adjustments.",
                
                "font_size": "Increase font sizes for better readability, especially for headlines.",
                "font_style": "Choose more readable fonts that align with your brand identity.",
                "font_color": "Improve font color contrast for better text visibility.",
                "text_alignment": "Ensure proper text alignment and spacing for professional appearance.",
                "text_hierarchy": "Establish clear visual hierarchy with font sizes and weights.",
                
                "background_color": "Choose background colors that enhance text readability.",
                "text_visibility": "Improve text color contrast against background for better visibility.",
                "color_harmony": "Use harmonious color palette that appeals to target audience.",
                "color_palette": "Develop consistent color palette following brand guidelines.",
                "contrast_improvements": "Increase contrast between text and background elements.",
                
                "element_placement": "Optimize element placement for better visual flow and balance.",
                "text_image_balance": "Achieve better balance between text and image elements.",
                "spacing_white_space": "Increase white space for cleaner, more professional appearance.",
                "visual_hierarchy": "Improve visual hierarchy to guide viewer's attention effectively.",
                "layout_structure": "Reorganize layout structure for better information flow.",
                
                "image_size": "Optimize image size for intended platform and use case.",
                "scaling_recommendations": "Ensure proper scaling for different device sizes and platforms.",
                "resolution_quality": "Improve image resolution for better quality and clarity.",
                "aspect_ratio": "Use appropriate aspect ratios for different marketing channels.",
                
                "cta_visibility": "Make call-to-action more prominent and visible.",
                "cta_design": "Improve CTA button design for better click-through rates.",
                "cta_effectiveness": "Enhance CTA effectiveness with better placement and design.",
                "action_text": "Use more compelling action-oriented text in CTAs.",
                
                "visual_appeal": "Enhance overall visual appeal for better engagement.",
                "engagement_factor": "Improve elements that increase user engagement.",
                "brand_consistency": "Ensure brand consistency across all visual elements.",
                "modern_design": "Update design elements to follow modern design trends."
            }
        }
    

def _generate_design_prompt_from_analysis(analysis):
    """Generate ONLY design/technical improvement instructions - no content/theme."""
    
    prompt_text = f"""You are an expert graphic design consultant.

Based on these improvement suggestions, generate a concise list of ONLY the design changes to make. Do NOT describe any image content, subject matter, theme, or topic. Do NOT invent what the poster is about.

SUGGESTIONS:
- Visual Clarity: {analysis.visual_clarity_suggestion}
- Font Size: {analysis.font_size_suggestion}
- Font Style: {analysis.font_style_suggestion}
- Font Color: {analysis.font_color_suggestion}
- Text Alignment: {analysis.text_alignment_suggestion}
- Background Color: {analysis.background_color_suggestion}
- Text Visibility: {analysis.text_visibility_suggestion}
- Color Harmony: {analysis.color_harmony_suggestion}
- Element Placement: {analysis.element_placement_suggestion}
- Text/Image Balance: {analysis.text_image_balance_suggestion}
- Spacing: {analysis.spacing_white_space_suggestion}

STRICT RULES:
- Output ONLY technical design specs: font names, font sizes (px), hex color codes, spacing values, alignment, contrast ratios
- Do NOT describe any image subject, scene, person, object, or theme
- Do NOT write "poster about..." or "featuring..." or any content description
- Format as a clean bullet-point list of actionable design changes
- Example format:
  • Font: Montserrat Bold 36px for headlines, Open Sans 16px for body
  • Colors: Primary #2C3E50, Accent #E74C3C, Background #FFFFFF
  • Spacing: 20px between elements, 1.5x line height
  • Alignment: Center-aligned headlines, left-aligned body text
  • Contrast: Minimum 4.5:1 ratio for text readability"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You output only technical design specifications. Never describe image content, subjects, scenes, or themes. Only list fonts, colors, spacing, alignment, and contrast values."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Design prompt generation failed: {str(e)}")
        return ""
    
import base64
import io

def _encode_image_to_base64(image_field):
    """Encode Django ImageField to base64 string."""
    try:
        # Get the full file path
        file_path = image_field.path
        print(f"DEBUG: Encoding image from path: {file_path}")
        
        # Read and encode
        with open(file_path, 'rb') as img_file:
            img_data = img_file.read()
            
        # Resize if too large (Groq has limits ~4MB for base64)
        if len(img_data) > 3 * 1024 * 1024:
            print(f"DEBUG: Image too large ({len(img_data)} bytes), resizing...")
            img = PILImage.open(io.BytesIO(img_data))
            img.thumbnail((1024, 1024))
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            img_data = buffer.getvalue()
            print(f"DEBUG: Resized to {len(img_data)} bytes")
        
        base64_string = base64.b64encode(img_data).decode('utf-8')
        print(f"DEBUG: Base64 encoded successfully: {len(base64_string)} chars")
        return base64_string
    except Exception as e:
        print(f"Error encoding image to base64: {str(e)}")
        return ""




def upload_edited_image(request, image_id):
    """
    Upload a user-edited version of an already-analyzed image.
    Links the edited version to the original and performs AI analysis.
    """

    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    # Get the original image
    try:
        original = MarketingImage.objects.get(id=image_id)
    except MarketingImage.DoesNotExist:
        messages.error(request, 'Original image not found.')
        return redirect('home')

    if request.method == 'POST':
        # Validate file upload
        if 'edited_image' not in request.FILES:
            messages.error(request, 'Please select an edited image to upload.')
            return redirect('upload_edited_image', image_id=image_id)

        uploaded_file = request.FILES['edited_image']
        
        # File validation
        if not _is_valid_image_file(uploaded_file):
            messages.error(request, 'Please upload a valid image file (JPG, PNG, GIF, BMP, or WebP).')
            return redirect('upload_edited_image', image_id=image_id)
        
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size must be less than 10MB.')
            return redirect('upload_edited_image', image_id=image_id)

        # Get image dimensions
        try:
            width, height = _get_image_dimensions(uploaded_file)
        except Exception as e:
            messages.error(request, f'Invalid image file: {str(e)}')
            return redirect('upload_edited_image', image_id=image_id)

        # Create edited version linked to original
        edited_image = _create_edited_image(original, uploaded_file, width, height, request.POST)
        edited_image.save()

        # Perform AI analysis
        _analyze_edited_image(edited_image)

        # Redirect to comparison
        messages.success(request, 'Edited image uploaded and analyzed successfully!')
        return redirect('compare_images', original_id=image_id, edited_id=edited_image.id)

    # GET request - show upload form
    return render(request, 'graphic_designer/upload_edited.html', {
        'user':user,
        'name':name,
        'company':company,
        'original': original,
        })


def _is_valid_image_file(file):
    """Check if file has valid image extension."""
    return file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))


def _get_image_dimensions(file):
    """Extract image dimensions from uploaded file."""
    pil_image = PILImage.open(file)
    width, height = pil_image.size
    file.seek(0)  # Reset pointer for Django to save correctly
    return width, height



def _create_edited_image(original, uploaded_file, width, height, post_data):
    """Create edited version of the original image."""
    return MarketingImage(
        title=post_data.get('title', f"{original.title} (Edited)"),
        image=uploaded_file,
        original_filename=uploaded_file.name,
        file_size=uploaded_file.size,
        width=width,
        height=height,
        target_audience=post_data.get('target_audience', original.target_audience),
        campaign_type=post_data.get('campaign_type', original.campaign_type),
        industry=post_data.get('industry', original.industry),
        call_to_action=post_data.get('call_to_action', original.call_to_action),
        edited_version_of=original,
    )


def _analyze_edited_image(edited_image):
    """Perform AI analysis on the edited image."""
    try:
        # Check if this is an edited version
        original = edited_image.edited_version_of
        is_edited = original is not None
        
        if is_edited:
            # Get original analysis for comparison
            try:
                original_analysis = ImageAnalysis.objects.get(marketing_image=original)
            except ImageAnalysis.DoesNotExist:
                original_analysis = None
            
            # Use comparative analysis for edited images
            analysis_result = _analyze_image_comparatively(edited_image, original_analysis)
        else:
            # Use regular analysis for new images
            analysis_service = MarketingAnalysisService()
            analysis_result = analysis_service.analyze_image(edited_image)
        
        # Create analysis record with new dedicated fields
        suggestions = analysis_result['improvement_suggestions']
        
        analysis_data = {
            'marketing_image': edited_image,
            'visual_clarity_score': 75,
            'color_usage_score': 75,
            'layout_score': 75,
            'balance_score': 75,
            'visual_overall_score': 75,
            'brand_consistency_score': 75,
            'message_clarity_score': 75,
            'visual_hierarchy_score': 75,
            'emotional_impact_score': 75,
            'conversion_optimization_score': 75,
            'audience_relevance_score': 75,
            'marketing_overall_score': 75,
            'overall_score': 75,
            
            # NEW: Store suggestions in dedicated fields
            'visual_clarity_suggestion': suggestions['visual_clarity'],
            'font_size_suggestion': suggestions['font_size'],
            'font_style_suggestion': suggestions['font_style'],
            'font_color_suggestion': suggestions['font_color'],
            'text_alignment_suggestion': suggestions['text_alignment'],
            'background_color_suggestion': suggestions['background_color'],
            'text_visibility_suggestion': suggestions['text_visibility'],
            'color_harmony_suggestion': suggestions['color_harmony'],
            'element_placement_suggestion': suggestions['element_placement'],
            'text_image_balance_suggestion': suggestions['text_image_balance'],
            'spacing_white_space_suggestion': suggestions['spacing_white_space'],
            
            # Keep original fields for backward compatibility
            'marketing_strategy_insights': suggestions['visual_clarity'],
            'competitive_positioning': suggestions['font_size'],
            'psychological_triggers': suggestions['font_style'],
            'cultural_considerations': suggestions['font_color'],
            'platform_optimization': suggestions['text_alignment'],
            'visual_improvements': suggestions['background_color'],
            'marketing_improvements': suggestions['text_visibility'],
            'strategic_recommendations': suggestions['color_harmony'],
            'accessibility_compliance': suggestions['element_placement'],
            'legal_considerations': suggestions['text_image_balance'],
            'platform_guidelines': suggestions['spacing_white_space'],
            'analysis_duration': analysis_result['analysis_duration'],
            'llm_tokens_used': analysis_result['llm_tokens_used'],
        }
        
        # Add comparison status if this is an edited image
        if is_edited and 'comparison_status' in analysis_result:
            comparison_status = analysis_result['comparison_status']
            analysis_data.update({
                'visual_clarity_improved': comparison_status.get('visual_clarity', 'not_analyzed'),
                'font_size_improved': comparison_status.get('font_size', 'not_analyzed'),
                'font_style_improved': comparison_status.get('font_style', 'not_analyzed'),
                'font_color_improved': comparison_status.get('font_color', 'not_analyzed'),
                'text_alignment_improved': comparison_status.get('text_alignment', 'not_analyzed'),
                'background_color_improved': comparison_status.get('background_color', 'not_analyzed'),
                'text_visibility_improved': comparison_status.get('text_visibility', 'not_analyzed'),
                'color_harmony_improved': comparison_status.get('color_harmony', 'not_analyzed'),
                'element_placement_improved': comparison_status.get('element_placement', 'not_analyzed'),
                'text_image_balance_improved': comparison_status.get('text_image_balance', 'not_analyzed'),
                'spacing_white_space_improved': comparison_status.get('spacing_white_space', 'not_analyzed'),
            })
        
        created_analysis = ImageAnalysis.objects.create(**analysis_data)
        
        # Generate design-only improvement prompt
        design_prompt = _generate_design_prompt_from_analysis(created_analysis)
        
        # Store design prompt in analysis
        created_analysis.design_improvement_prompt = design_prompt
        created_analysis.save()
        
        # Update analyzed timestamp
        edited_image.analyzed_at = timezone.now()
        edited_image.save()
        
    except Exception as e:
        # Log error but don't fail the upload
        edited_image.analyzed_at = None
        edited_image.save()
        print(f"Analysis failed for edited image {edited_image.id}: {str(e)}")
        raise e
    


def _analyze_image_comparatively(edited_image, original_analysis):
    """Analyze edited image with comparison to original suggestions."""
    start_time = time.time()
    
    try:
        # Build comparative prompt
        original_suggestions = ""
        if original_analysis:
            original_suggestions = f"""
Original Image Suggestions:
- Visual Clarity: {original_analysis.visual_clarity_suggestion or 'No suggestion'}
- Font Size: {original_analysis.font_size_suggestion or 'No suggestion'}
- Font Style: {original_analysis.font_style_suggestion or 'No suggestion'}
- Font Color: {original_analysis.font_color_suggestion or 'No suggestion'}
- Text Alignment: {original_analysis.text_alignment_suggestion or 'No suggestion'}
- Background Color: {original_analysis.background_color_suggestion or 'No suggestion'}
- Text Visibility: {original_analysis.text_visibility_suggestion or 'No suggestion'}
- Color Harmony: {original_analysis.color_harmony_suggestion or 'No suggestion'}
- Element Placement: {original_analysis.element_placement_suggestion or 'No suggestion'}
- Text/Image Balance: {original_analysis.text_image_balance_suggestion or 'No suggestion'}
- Spacing: {original_analysis.spacing_white_space_suggestion or 'No suggestion'}
"""
        
        comparative_prompt = f"""Analyze this EDITED marketing image and compare it with the original suggestions.

{original_suggestions}

Edited Image Information:
- Title: {edited_image.title}
- Campaign Type: {edited_image.campaign_type}
- Industry: {edited_image.industry}
- Call to Action: {edited_image.call_to_action}

IMPORTANT: Be generous in detecting improvements. If the edited image addresses even part of a suggestion, mark it as "yes".

Please respond with a JSON object in this exact format:

{{
  "improvement_suggestions": {{
    "visual_clarity": "specific suggestion for the edited image",
    "font_size": "specific suggestion for the edited image",
    "font_style": "specific suggestion for the edited image",
    "font_color": "specific suggestion for the edited image",
    "text_alignment": "specific suggestion for the edited image",
    "background_color": "specific suggestion for the edited image",
    "text_visibility": "specific suggestion for the edited image",
    "color_harmony": "specific suggestion for the edited image",
    "element_placement": "specific suggestion for the edited image",
    "text_image_balance": "specific suggestion for the edited image",
    "spacing_white_space": "specific suggestion for the edited image"
  }},
  "comparison_status": {{
    "visual_clarity": "yes/no/partial",
    "font_size": "yes/no/partial",
    "font_style": "yes/no/partial",
    "font_color": "yes/no/partial",
    "text_alignment": "yes/no/partial",
    "background_color": "yes/no/partial",
    "text_visibility": "yes/no/partial",
    "color_harmony": "yes/no/partial",
    "element_placement": "yes/no/partial",
    "text_image_balance": "yes/no/partial",
    "spacing_white_space": "yes/no/partial"
  }}
}}

For comparison_status:
- "yes" = The edited image addresses the original suggestion (even partially)
- "no" = The edited image does not address the original suggestion at all
- "partial" = The edited image partially addresses the original suggestion

BE GENEROUS: If there's any evidence the user tried to address a suggestion, mark it as "yes" or "partial". Only use "no" if the suggestion is completely ignored.

Focus on detecting genuine improvements and efforts made by the user."""

        # Make API call to Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert marketing analyst comparing edited images with original suggestions."},
                {"role": "user", "content": comparative_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Extract JSON from response
        json_start = analysis_text.find('{')
        json_end = analysis_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = analysis_text[json_start:json_end]
            ai_response = json.loads(json_str)
            
            # Add metadata
            ai_response['analysis_duration'] = time.time() - start_time
            ai_response['llm_tokens_used'] = len(analysis_text.split())
            
            return ai_response
        else:
            raise Exception("No JSON found in API response")
            
    except Exception as e:
        # Return fallback analysis on error
        return {
            "improvement_suggestions": {
                "visual_clarity": "Manual review recommended for visual clarity improvements.",
                "font_size": "Consider font size adjustments for better readability.",
                "font_style": "Review font style for brand consistency.",
                "font_color": "Ensure font color provides sufficient contrast.",
                "text_alignment": "Check text alignment for professional appearance.",
                "background_color": "Evaluate background color for visual impact.",
                "text_visibility": "Enhance text visibility for better readability.",
                "color_harmony": "Review color palette for harmony and brand alignment.",
                "element_placement": "Optimize element placement for visual hierarchy.",
                "text_image_balance": "Balance text and image elements for better composition.",
                "spacing_white_space": "Use spacing effectively to improve readability and visual appeal."
            },
            "comparison_status": {
                "visual_clarity": "not_analyzed",
                "font_size": "not_analyzed",
                "font_style": "not_analyzed",
                "font_color": "not_analyzed",
                "text_alignment": "not_analyzed",
                "background_color": "not_analyzed",
                "text_visibility": "not_analyzed",
                "color_harmony": "not_analyzed",
                "element_placement": "not_analyzed",
                "text_image_balance": "not_analyzed",
                "spacing_white_space": "not_analyzed"
            },
            "analysis_duration": time.time() - start_time,
            "llm_tokens_used": 0
        }



def compare_images(request, original_id, edited_id):
    """
    Side-by-side comparison of the original image and its edited version,
    including their AI analysis suggestions.
    """


    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    try:
        original = MarketingImage.objects.get(id=original_id)
        edited   = MarketingImage.objects.get(id=edited_id)
    except MarketingImage.DoesNotExist:
        messages.error(request, 'One or both images not found.')
        return redirect('image_analysis')

    # Fetch analyses (may not exist if analysis failed)
    try:
        original_analysis = ImageAnalysis.objects.get(marketing_image=original)
    except ImageAnalysis.DoesNotExist:
        original_analysis = None

    try:
        edited_analysis = ImageAnalysis.objects.get(marketing_image=edited)
    except ImageAnalysis.DoesNotExist:
        edited_analysis = None

    # NEW: Use dedicated suggestion fields for comparison
    suggestion_fields = [
        ('visual_clarity_suggestion',      'Visual clarity'),
        ('font_size_suggestion',           'Font size'),
        ('font_style_suggestion',          'Font style'),
        ('font_color_suggestion',          'Font color'),
        ('text_alignment_suggestion',      'Text alignment'),
        ('background_color_suggestion',    'Background color'),
        ('text_visibility_suggestion',     'Text visibility'),
        ('color_harmony_suggestion',       'Color harmony'),
        ('element_placement_suggestion',   'Element placement'),
        ('text_image_balance_suggestion',  'Text / image balance'),
        ('spacing_white_space_suggestion', 'Spacing & white space'),
    ]

    # Maps suggestion field to comparison status field
    status_field_map = {
        'visual_clarity_suggestion':      'visual_clarity_improved',
        'font_size_suggestion':           'font_size_improved',
        'font_style_suggestion':          'font_style_improved',
        'font_color_suggestion':          'font_color_improved',
        'text_alignment_suggestion':      'text_alignment_improved',
        'background_color_suggestion':    'background_color_improved',
        'text_visibility_suggestion':     'text_visibility_improved',
        'color_harmony_suggestion':       'color_harmony_improved',
        'element_placement_suggestion':   'element_placement_improved',
        'text_image_balance_suggestion':  'text_image_balance_improved',
        'spacing_white_space_suggestion': 'spacing_white_space_improved',
    }

    comparison_rows = []
    improved_count = 0
    for field_name, label in suggestion_fields:
        orig_val = getattr(original_analysis, field_name, '—') if original_analysis else '—'
        edited_val = getattr(edited_analysis, field_name, '—') if edited_analysis else '—'
        
        # Get comparison status from edited analysis (only available for edited images)
        status_field = status_field_map[field_name]
        comparison_status = getattr(edited_analysis, status_field, 'not_analyzed') if edited_analysis else 'not_analyzed'
        
        # DEBUG: Print comparison status
        print(f"DEBUG: {label} - Status: {comparison_status}, Original: {orig_val[:50]}..., Edited: {edited_val[:50]}...")
        
        # Determine if improved based on AI's comparison status ONLY
        is_improved = False
        
        # Only trust the AI's comparison status - no fallbacks
        if comparison_status == 'yes':
            is_improved = True
        elif comparison_status == 'partial':
            is_improved = True
        # "no" and "not_analyzed" are NOT improved - no fallbacks!
        
        print(f"DEBUG: {label} - Final improved status: {is_improved}")
        
        if is_improved:
            improved_count += 1
            
        comparison_rows.append({
            'label': label,
            'original': orig_val or '—',
            'edited': edited_val or '—',
            'improved': is_improved,
            'status': comparison_status,
        })

    context = {
        'user': user,
        'company': company,
        'name':name,
        'original':          original,
        'edited':            edited,
        'original_analysis': original_analysis,
        'edited_analysis':   edited_analysis,
        'comparison_rows':   comparison_rows,
        'improved_count':    improved_count,
        'total_fields':      len(suggestion_fields),
    }
    return render(request, 'graphic_designer/compare_images.html', context)


def image_history(request):
    """List all previously uploaded & analysed images."""

    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None


    images = MarketingImage.objects.filter(edited_version_of=None).order_by('-uploaded_at')
    context = {
        'user':user,
        'name':name,
        'company':company,
        'images': images,
    }
    return render(request, 'graphic_designer/image_history.html', context)


def poster(request):
    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    return render(request, 'graphic_designer/poster.html', {
        'user': user,
        'company': company,
        'name':name,

    })

def poster_generator(request):
    """Handle poster generation requests"""

    gdid = request.session.get('gdid')

    if not gdid:
        return redirect('login')  

    try:
        user = LogRegister_Details.objects.get(log_username=gdid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    if request.method == "POST":
        user_input = request.POST.get("request_text")
        if user_input:
            result = generate_poster_concept(user_input)
        else:
            result = None
    else:
        result = None
        user_input = ""
    
    return render(request, "graphic_designer/poster_generator.html", {
        'user': user,
        'company': company,
        'name':name,
        "result": result, 
        "user_input": user_input
        })


def generate_poster_concept(user_input):
    """
    Sends user request to Groq LLM and returns structured poster concept
    """

    prompt = f"""
You are a world-class creative director, graphic designer, and AI prompt engineer with over 15 years of experience creating award-winning poster designs for global brands.

Your task is to convert the USER REQUEST into a **complete poster design concept AND a fully detailed AI image generation prompt**.

USER REQUEST:
{user_input}

Your response must include the following sections.

------------------------------------------------------------

1. POSTER TITLE & TEXT CONTENT

Provide the EXACT TEXT that should appear on the poster.

Include:

Primary Headline  
Secondary Headline  
Supporting Message  
Tagline  
Call To Action  
Footer (website, contact, social media)

Example structure:

Primary Headline:
"SUMMER FESTIVAL 2026"

Secondary Headline:
"Music • Food • Art"

Tagline:
"Experience the Colors of Summer"

Call To Action:
"Get Your Tickets Now"

Footer:
www.summerfest.com

Also include:

Text alignment  
Text placement (top / center / bottom)  
Text hierarchy  
Spacing recommendations


------------------------------------------------------------

2. COLOR PALETTE & MOOD

Provide:

Primary colors (HEX codes)  
Secondary colors  
Accent colors  
Background colors  
Gradient suggestions

Explain:

Color psychology  
Mood and emotional impact  
Modern design trends


------------------------------------------------------------

3. VISUAL ELEMENTS & GRAPHICS

Describe the poster imagery clearly.

Include:

Main imagery  
Illustrations or photography  
Icons  
Decorative shapes  
Patterns  
Textures  
Lighting style  
Shadow and depth  
Composition details

Example:

- Dynamic illustration of a summer concert stage  
- Neon lighting accents  
- Floating confetti particles  
- Soft glow lighting  
- Layered depth with foreground and background


------------------------------------------------------------

4. TYPOGRAPHY & FONT SELECTION

Specify exact fonts.

Primary Font  
Secondary Font  
Accent Font (optional)

Example:

Primary Font:
Montserrat ExtraBold

Secondary Font:
Lato Regular

Font hierarchy:

Headline: 120pt  
Subheading: 48pt  
Body text: 24pt  
CTA Button: 32pt

Include:

Font weight  
Letter spacing  
Line height  
Font pairing reasoning  
Readability considerations


------------------------------------------------------------

5. LAYOUT & COMPOSITION

Describe how the poster should be structured.

Include:

Grid layout  
Alignment  
White space usage  
Visual flow  
Balance and symmetry  
Element placement

Example:

Top Section:
Primary headline

Center Section:
Main illustration

Bottom Section:
CTA button and event details


------------------------------------------------------------

6. CALL TO ACTION DESIGN

Explain how the CTA should appear.

Include:

CTA text  
Button color  
Button shape  
Button size  
Button placement  
Hover or glow effect suggestions


------------------------------------------------------------

7. MASTER AI IMAGE GENERATION PROMPT

Now generate **ONE COMPLETE PROMPT** for AI image generators like Midjourney or DALL-E.

This prompt must include EVERYTHING:

Poster text  
Font styles  
Font placement  
Layout structure  
Colors  
Background  
Lighting  
Visual elements  
Composition  
Mood  
Typography hierarchy

Example format:

"A vibrant promotional poster featuring the headline 'SUMMER FESTIVAL 2026' in large Montserrat ExtraBold typography at the top center, with a colorful festival stage illustration in the middle, glowing neon lights and confetti particles, bright orange and yellow gradient background..."

Include style modifiers such as:

Art style  
Rendering quality  
Lighting style  
Color grading  
Texture details


------------------------------------------------------------

8. MULTIPLE PROMPT VARIATIONS

Provide 3-5 alternative prompts with different visual styles.

Examples:

Minimalist modern poster  
Bold graphic poster  
Vintage retro poster  
Futuristic neon poster  
Illustrated children's book style poster


------------------------------------------------------------

9. TECHNICAL SPECIFICATIONS

Include recommended settings.

Resolution:
300 DPI

Poster Size:
24x36 inches

Instagram:
1080x1080

Story:
1080x1920

Aspect ratios:

1:1  
16:9  
9:16

File formats:

PNG  
JPEG  
PDF

Quality:
Maximum quality


------------------------------------------------------------

10. NEGATIVE PROMPT

List elements to avoid:

blurry text  
distorted fonts  
low resolution  
watermarks  
cropped text  
extra limbs  
bad anatomy


------------------------------------------------------------

Make the response:

- extremely detailed  
- professional  
- actionable  
- ready for designers and AI tools  

Think like a **senior creative director presenting a concept to a Fortune 500 brand**.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a creative graphic designer and creative director with expertise in branding, marketing, and visual communication."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3500
    )

    return response.choices[0].message.content






def employee_logout(request):

    session_id = request.session.get('session_id')

    if session_id:

        try:
            session = EmployeeSession.objects.get(id=session_id)

            logout_time = timezone.now()

            session.logout_time = logout_time
            session.duration = logout_time - session.login_time
            session.save()

            attendance = session.attendance

            attendance.last_logout_time = logout_time

            total = timedelta()

            for s in EmployeeSession.objects.filter(
                attendance=attendance,
                logout_time__isnull=False
            ):
                total += s.duration

            attendance.total_working_hours = total
            attendance.save()

        except EmployeeSession.DoesNotExist:
            pass

    request.session.flush()

    return redirect('login')



def employee_attendance(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

     

    return render(request, 'admin/emp_attendance.html', {
        'user': user,
        'company': company,
     
    })


def exec_attendence(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()


        employees = EmployeeRegister_Details.objects.filter(
            company=company,
            designation__dashboard_id='Executive'
        ).order_by('-id')

        attendance_list = EmployeeAttendance.objects.filter(
            employee__company=company,
            employee__designation__dashboard_id='Executive'
        ).select_related('employee')

        # Filters
        employee_id = request.GET.get('employee')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if employee_id:
            attendance_list = attendance_list.filter(
                employee_id=employee_id
            )

        if from_date:
            attendance_list = attendance_list.filter(
                date__gte=from_date
            )

        if to_date:
            attendance_list = attendance_list.filter(
                date__lte=to_date
            )

        attendance_list = attendance_list.order_by('-date')


        approved_leave_days = EmployeeLeave.objects.filter(
            employee__company=company,
            employee__designation__dashboard_id='Executive',
            status='approved'
        ).aggregate(
            total_days=Sum('number_of_days')
        )['total_days'] or 0

    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        attendance_list = []
        approved_leave_count = 0
        approved_leave_days = 0

    return render(request, 'admin/exec_attendance.html', {
        'user': user,
        'company': company,
        'attendance_list': attendance_list,
        'employees': employees,
        'approved_leave_days': approved_leave_days,

        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
    })


def telecaller_attendence(request):
    aid = request.session.get('aid')
    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        company = BusinessRegister_Details.objects.filter(login=user).first()


        employees = EmployeeRegister_Details.objects.filter(
            company=company,
            designation__dashboard_id='Telecaller'
        ).order_by('-id')

        attendance_list = EmployeeAttendance.objects.filter(
            employee__company=company,
            employee__designation__dashboard_id='Telecaller'
        ).select_related('employee')

        # Filters
        employee_id = request.GET.get('employee')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if employee_id:
            attendance_list = attendance_list.filter(
                employee_id=employee_id
            )

        if from_date:
            attendance_list = attendance_list.filter(
                date__gte=from_date
            )

        if to_date:
            attendance_list = attendance_list.filter(
                date__lte=to_date
            )

        attendance_list = attendance_list.order_by('-date')

        approved_leave_days = EmployeeLeave.objects.filter(
            employee__company=company,
            employee__designation__dashboard_id='Telecaller',
            status='approved'
        ).aggregate(
            total_days=Sum('number_of_days')
        )['total_days'] or 0

    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        attendance_list = []

    return render(request, 'admin/telecaller_attendance.html', {
        'user': user,
        'company': company,
        'attendance_list': attendance_list,
        'employees' : employees,
        'approved_leave_days': approved_leave_days,

        'selected_employee': employee_id,
        'from_date': from_date,
        'to_date': to_date,
    })







def settings_view(request):
    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    creds, created = UserCredentials.objects.get_or_create(user=name)
    
    if request.method == 'POST':
        creds.imap_server = request.POST.get('imap_server', '')
        creds.imap_email = request.POST.get('imap_email', '')
        creds.imap_password = request.POST.get('imap_password', '')
        creds.groq_api_key = request.POST.get('groq_api_key', '')
        creds.google_credentials_json = request.POST.get('google_credentials_json', '')
        creds.spreadsheet_id = request.POST.get('spreadsheet_id', '')
        creds.save()
        return render(request, 'executive/settings.html', {
            'user': user,
            'company': company,
            'name': name,
            'creds': creds,
            'success': 'Settings updated successfully!'
              })
        
    return render(request, 'executive/settings.html', {
        'creds': creds,
        'user': user,
        'company': company,
        'name': name,
        })



def resume_extract(request):
    """Render the main frontend dashboard."""
    from django_apscheduler.models import DjangoJob

    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None
    
    # Try to get the next scheduled runtime
    job = DjangoJob.objects.filter(id="resume_pipeline_job").first()
    next_run_time = None
    if job and job.next_run_time:
        next_run_time = job.next_run_time.isoformat()
        
    return render(request, 'executive/resume_extract.html', {
        'user': user,
        'company': company,
        'name': name,
        'next_run_time': next_run_time
        })


from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .tasks import process_new_resumes


@api_view(['POST'])

def trigger_resume_processing(request):
    """
    Manually triggers the pipeline logic designed in Phase 1 for the logged in user.
    """

    aid = request.session.get('eid')

    if not aid:
        return Response(
            {"status": "error", "message": "Please login first"},
            status=403
        )
    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None
        name = None

    try:
        # In a real async setup with celery, you'd use process_new_resumes.delay(request.user.id)
        result_message = process_new_resumes(name.id)
        return Response({"status": "success", "message": result_message}, status=200)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)








def bottle_add(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    if request.method == "POST":
        bottle_name = request.POST.get('bottle_name')

        if bottle_name:
            BottleAdd.objects.create(
                name=bottle_name,
                created_by=name
            )
            messages.success(request, "Bottle added successfully.")
            return redirect('bottle_add')
        else:
            messages.error(request, "Bottle name is required.")

    return render(request, 'datamanager/bottle_add.html', {
        "user": user,
        "name": name,
    })


def bottle_view(request):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    bottles = BottleAdd.objects.filter(
        created_by__company=company
    ).order_by('-id')

    return render(request, 'datamanager/bottle_view.html', {
        "user": user,
        "name": name,
        "bottles": bottles,
    })


def bottle_edit(request, id):
    aid = request.session.get('did')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(log_username=aid)
        name = EmployeeRegister_Details.objects.filter(login=user).first()
    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    bottle = get_object_or_404(BottleAdd, id=id)

    if request.method == "POST":
        bottle.name = request.POST.get('bottle_name')
        bottle.save()

        messages.success(request, "Bottle updated successfully.")
        return redirect('bottle_view')

    return render(request, 'datamanager/bottle_add.html', {
        'user': user,
        'name': name,
        'bottle': bottle,
        'edit_mode': True,
    })


def bottle_delete(request, id):
    bottle = get_object_or_404(BottleAdd, id=id)
    bottle.delete()

    messages.success(request, "Bottle deleted successfully")
    return redirect('bottle_view')


from .forms import AudioUploadForm, FilterForm, KeywordForm
import threading
from .groq_service import classify_career_bucket, detect_keywords, transcribe_audio

logger = logging.getLogger(__name__)


def _get_active_keywords():
    kws = list(KeywordConfig.objects.filter(is_active=True).values_list('keyword', flat=True))
    if not kws:
        kws = settings.DEFAULT_KEYWORDS
    return kws

def upload_audio(request):
    username = request.session.get('tcid')
    user = LogRegister_Details.objects.get(log_username=username)
    employee = EmployeeRegister_Details.objects.get(login=user)

    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            f = request.FILES['audio_file']
            record.file_name = f.name
            record.file_size = f.size
            record.status = 'pending'

            record.caller_name = employee.name

            # Optional: clear phone number
            record.phone_number = ''

            record.save()

            threading.Thread(target=_process_record, args=(record,)).start()

            messages.success(request, f"✅ Audio '{record.file_name}' uploaded and processing started!")
            return redirect('record_detail', pk=record.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AudioUploadForm()

    return render(request, 'telecaller/upload.html', {
        'user':user,
        'name':employee,
        'form': form
        })


from difflib import get_close_matches

def _process_record(record: AudioRecord):
    try:
        record.status = 'processing'
        record.save(update_fields=['status'])

        # 1. Transcribe
        audio_path = record.audio_file.path
        stt_result = transcribe_audio(audio_path)

        if not stt_result['success']:
            record.status = 'failed'
            record.error_message = stt_result['error']
            record.save()
            return

        record.transcript = stt_result['transcript']

        # 2. Keyword Detection
        keywords = _get_active_keywords()
        record.detected_keywords = detect_keywords(record.transcript, keywords)

        # 3. Career Classification
        classification = classify_career_bucket(record.transcript)
        

        bucket_name = classification.get('bucket', '').replace('_', ' ').lower()

        all_bottles = list(BottleAdd.objects.all())

        names = [b.name.lower() for b in all_bottles]

        match = get_close_matches(bucket_name, names, n=1, cutoff=0.5)

        if match:
            bottle = next(
                b for b in all_bottles
                if b.name.lower() == match[0]
            )
        else:
            bottle = None

        record.career_bucket = bottle
        record.classification_reason = classification['reason']
        record.confidence_score = classification['confidence']

        # Auto-fill caller name from LLM if not provided on upload
        if not record.caller_name and classification.get('candidate_name'):

            raw_name = classification['candidate_name'].strip()

            raw_name = re.sub(r'[^A-Za-z ]', '', raw_name)  # remove symbols
            raw_name = raw_name.title()  # capitalize properly

            # Avoid garbage values
            if 2 <= len(raw_name) <= 50:
                record.caller_name = raw_name

        if classification['error']:
            record.error_message = classification['error']

        record.status = 'completed'
        record.processed_at = timezone.now()
        record.save()

    except Exception as e:
        logger.exception(f"Pipeline error for record #{record.pk}")
        record.status = 'failed'
        record.error_message = str(e)
        record.save()


def record_detail(request, pk):
    username = request.session.get('tcid')
    user = LogRegister_Details.objects.get(log_username=username)
    employee = EmployeeRegister_Details.objects.get(login=user)

    record = get_object_or_404(AudioRecord, pk=pk)
    return render(request, 'telecaller/record_detail.html', {
        'user':user,
        'name':employee,
        'record': record
        })


def records_list(request):
    username = request.session.get('tcid')
    user = LogRegister_Details.objects.get(log_username=username)
    employee = EmployeeRegister_Details.objects.get(login=user)

    form = FilterForm(request.GET)
    records = AudioRecord.objects.all()

    if form.is_valid():
        if form.cleaned_data.get('bucket'):
            records = records.filter(career_bucket=form.cleaned_data['bucket'])
        if form.cleaned_data.get('status'):
            records = records.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('keyword'):
            q = form.cleaned_data['keyword']
            records = records.filter(
                Q(caller_name__icontains=q) |
                Q(phone_number__icontains=q) |
                Q(file_name__icontains=q)
            )
        if form.cleaned_data.get('has_keywords'):
            records = records.exclude(detected_keywords=[])

    return render(request, 'telecaller/records_list.html', {
        'user':user,
        'name':employee,
        'records': records,
        'filter_form': form,
        'total': records.count(),
    })


@require_POST
def reprocess_record(request, pk):
    record = get_object_or_404(AudioRecord, pk=pk)
    record.status = 'pending'
    record.transcript = ''
    record.detected_keywords = []
    record.career_bucket = None
    record.classification_reason = ''
    record.error_message = ''
    record.caller_name = ''
    record.save()

    threading.Thread(target=_process_record, args=(record,)).start()

    messages.success(request, "Record reprocessed successfully.")
    return redirect('record_detail', pk=pk)

@require_POST
def delete_record(request, pk):
    record = get_object_or_404(AudioRecord, pk=pk)
    try:
        if record.audio_file and os.path.exists(record.audio_file.path):
            os.remove(record.audio_file.path)
    except Exception:
        pass
    record.delete()
    messages.success(request, "Record deleted.")
    return redirect('records_list')







from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_lead_tracker_details(request, lead_id):
    try:
        lead = get_object_or_404(
            Leads.objects.select_related(
                'collected_by',
                'lead_category__client_task__client'
            ),
            id=lead_id
        )

        # Client Details
        client = None
        if lead.lead_category and lead.lead_category.client_task:
            client = lead.lead_category.client_task.client

        # Lead Additional Fields
        lead_details = LeadDetails.objects.filter(lead=lead)

        extra_fields = []
        for item in lead_details:
            extra_fields.append({
                'field_name': item.field_name,
                'field_data': item.field_data
            })

        # Allocation Details
        allocation = LeadAssignedToTC.objects.select_related(
            'telecaller'
        ).filter(lead=lead).order_by('-id').first()

        history_track = []

        if allocation:
            history_track.append({
                'title': 'Lead Allocated',
                'date': str(allocation.assign_date),
                'time': allocation.allocate_time.strftime("%I:%M:%S %p") if allocation.allocate_time else "-",
                'allocated_to': allocation.telecaller.name if allocation.telecaller else '-',
                'status': 'Allocated'
            })

        collected_by = None

        if lead.collected_by:
            collected_by = {
                'employee': lead.collected_by.name,
                'date': str(lead.added_date),
                'time': lead.added_time.strftime("%I:%M:%S %p") if lead.added_time else "-"
            }

        data = {
            'lead': {
                'name': lead.name,
                'email': lead.email,
                'contact': lead.contact,
                'source': lead.source,
                'added_date': str(lead.added_date),
                'added_time': lead.added_time.strftime("%I:%M:%S %p") if lead.added_time else "-"
            },

            'client': {
                'name': client.client_name if client else '-',
                'category': lead.lead_category.collection_for if lead.lead_category else '-'
            },

            'extra_details': extra_fields,

            'allocation': {
                'allocated_on': str(allocation.assign_date) if allocation else '-',
                'allocated_time': allocation.allocate_time.strftime("%I:%M:%S %p") if allocation and allocation.allocate_time else "-",
                'allocated_to': allocation.telecaller.name if allocation and allocation.telecaller else '-'
            },

            'collected_by': collected_by,

            'history_track': history_track
        }

        return JsonResponse(data)
    except Exception as e:
        print("ERROR IN LEAD TRACKER")
        print(str(e))
        traceback.print_exc()

        return JsonResponse({
            'error': str(e)
        }, status=500)




def tl_work_details_ajax(request, task_id):

    works = TaskDetails.objects.filter(task_assign_id=task_id)

    data = []

    for work in works:
        data.append({
            "id": work.id,
            "date": work.collect_date.strftime("%d-%m-%Y"),
            "title": work.title,
            "description": work.description,
            "file": work.file.url if work.file else "",
            "target": work.task_assign.target,
            "achieved": work.achieved_target,
            "verified": work.verified_target,
            "status": work.status,
        })

    return JsonResponse(data, safe=False)




def verify_task_detail_tl(request, detail_id):

    if request.method == "POST":

        data = json.loads(request.body)

        verified_target = int(
            data.get("verified_target", 0)
        )

        detail = TaskDetails.objects.get(id=detail_id)

        detail.verified_target = verified_target
        detail.status = 1
        detail.save()

        task_assign = detail.task_assign

        # total verified target of this task
        total_verified = TaskDetails.objects.filter(
            task_assign=task_assign
        ).aggregate(
            total=Sum('verified_target')
        )['total'] or 0

        task_assign.target_achieved = total_verified

        if task_assign.target > 0:
            progress = round(
                (total_verified / task_assign.target) * 100
            )
        else:
            progress = 0

        if progress > 100:
            progress = 100

        task_assign.progress = progress
        task_assign.save()

        # WorkAssign update
        work_assign = task_assign.work_assign

        total_work_verified = TaskAssign.objects.filter(
            work_assign=work_assign
        ).aggregate(
            total=Sum('target_achieved')
        )['total'] or 0

        work_assign.target_achieved = total_work_verified

        if work_assign.target > 0:
            work_progress = round(
                (total_work_verified / work_assign.target) * 100
            )
        else:
            work_progress = 0

        if work_progress > 100:
            work_progress = 100

        work_assign.progress = work_progress
        work_assign.save()

        return JsonResponse({
            'status':'success'
        })

    return JsonResponse({
        'status':'error'
    })




def wastelead_confirmation(request):
    user = LogRegister_Details.objects.get(log_username=request.session.get('hid'))
    employee = EmployeeRegister_Details.objects.filter(login=user).first()
    company = employee.company if employee else None
    company_id = company.id


    wasteleads = WasteLead.objects.filter(lead__collected_by__company=company,confirmation=0).select_related(
        'lead', 'lead__collected_by', 'lead__lead_category', 'lead__work__client', 
    )

    client_id = request.GET.get('client_id')
    category_id = request.GET.get('category_id')
    employee_id = request.GET.get('employee_id')
    telecaller_id = request.GET.get('telecaller_id')

    lead_from = request.GET.get('lead_from')
    lead_to = request.GET.get('lead_to')

    waste_from = request.GET.get('waste_from')
    waste_to = request.GET.get('waste_to')


    if client_id:
        wasteleads = wasteleads.filter(
            lead__lead_category__client_task__client_id=client_id
        )

    if category_id:
        wasteleads = wasteleads.filter(
            lead__lead_category_id=category_id
        )

    if employee_id:
        wasteleads = wasteleads.filter(
            lead__collected_by_id=employee_id
        )

    if telecaller_id:
        wasteleads = wasteleads.filter(
            telecaller_id=telecaller_id
        )

    if lead_from:
        wasteleads = wasteleads.filter(
            lead__added_date__gte=lead_from
        )

    if lead_to:
        wasteleads = wasteleads.filter(
            lead__added_date__lte=lead_to
        )

    if waste_from:
        wasteleads = wasteleads.filter(
            waste_marked_date__gte=waste_from
        )

    if waste_to:
        wasteleads = wasteleads.filter(
            waste_marked_date__lte=waste_to
        )



    clients = ClientRegister.objects.filter(company_id=company_id) if company_id else ClientRegister.objects.none()



    telecallers = EmployeeRegister_Details.objects.filter(designation__dashboard_id='Telecaller',company=company)
    employees = EmployeeRegister_Details.objects.filter(designation__dashboard_id__in=['Team_Lead','Executive','Data_Manager'],company=company)


    return render(request, 'dmhead/wastelead_confirmation.html', {
        "name":employee,
        "wasteleads":wasteleads,
        "clients": clients,
        "employees": employees,
        "telecallers": telecallers,
    })




@csrf_exempt
def update_waste_lead(request):

    if request.method == "POST":

        data = json.loads(request.body)

        lead_id = data.get("lead_id")
        decision = data.get("decision")
        head_reason = data.get("head_reason")

        waste = WasteLead.objects.filter(
            lead_id=lead_id
        ).first()

        if not waste:
            return JsonResponse({
                "status": "error",
                "message": "Waste lead not found"
            })

        if decision == "reject":

            waste.delete()

            return JsonResponse({
                "status": "success",
                "message": "Waste lead rejected and removed"
            })

        elif decision == "confirm":

            waste.confirmation = 1
            waste.head_reason = head_reason
            waste.save()

            return JsonResponse({
                "status": "success",
                "message": "Waste lead confirmed successfully"
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request"
    })
    
def download_lead_template(request, category_id):

    category = LeadCategory_Register.objects.get(id=category_id)

    fields = LeadField_Register.objects.filter(
        lead_category=category,
        status=0
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Lead Template"

    headers = [
        "Sl No",
        "Name",
        "Email",
        "Contact",
        "Course"
    ]

    for field in fields:
        headers.append(field.name)

    ws.append(headers)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        f'attachment; filename={category.collection_for}_template.xlsx'
    )

    wb.save(response)

    return response









from io import BytesIO
def download_lead_template_tl(request, team_alloc_id):
    category_alloc = LeadCateogry_TeamAllocate.objects.filter(id=team_alloc_id).first()

    if not category_alloc:
        return HttpResponse("Invalid Team Allocation")

    lead_category = category_alloc.lead_category

    static_columns = [
        'Name',
        'Email',
        'Contact Number',
        'Course'
    ]

    dynamic_columns = list(
        LeadField_Register.objects.filter(
            lead_category=lead_category
        ).values_list('name', flat=True)
    )

    columns = static_columns + dynamic_columns

    df = pd.DataFrame(columns=columns)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lead Template')

        worksheet = writer.sheets['Lead Template']

        for column in worksheet.columns:
            worksheet.column_dimensions[column[0].column_letter].width = 25

    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        f'attachment; filename=Lead_Template_{lead_category.collection_for}.xlsx'
    )

    return response











import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build




from datetime import datetime
from .models import GoogleFormApplication



from .google_form_sync import import_google_form_data
def google_form_leads_exec(request):

    aid = request.session.get('eid')

    if not aid:
        return redirect('login')

    try:
        user = LogRegister_Details.objects.get(
            log_username=aid
        )

        employee = EmployeeRegister_Details.objects.filter(
            login=user
        ).first()

        company = employee.company if employee else None

    except LogRegister_Details.DoesNotExist:
        return redirect('login')

    if request.method == "POST":

        credentials_file = request.FILES.get('credentials_file')
        sheet_name = request.POST.get('sheet_name')

        ExecutiveGoogleForm.objects.update_or_create(
            employee=employee,
            defaults={
                'credentials_file': credentials_file,
                'sheet_name': sheet_name
            }
        )

      
        import_google_form_data(employee)

        messages.success(
            request,
            "Google Form configuration saved successfully."
        )

        return redirect('google_form_leads_exec')

   
    config = ExecutiveGoogleForm.objects.filter(
        employee=employee
    ).first()

    if config:
        import_google_form_data(employee)

    leads = GoogleFormApplication.objects.filter(
        employee=employee
    ).order_by('-created_at')

    return render(request, 'executive/google_form_leads.html',{
            'user': user,
            'company': company,
            'name': employee,
            'leads': leads,
        }
    )


def google_form_leads_dmhead(request):
    hid = request.session.get('hid')

    if not hid:
        return redirect('login')  # or appropriate login URL

    try:
        user = LogRegister_Details.objects.get(log_username=hid)
        name=EmployeeRegister_Details.objects.filter(login=user).first()
        company = name.company if name else None 

        
    
    except LogRegister_Details.DoesNotExist:
        user = None
        company = None

    

    
    leads = GoogleFormApplication.objects.none()

    if company:
        company_emails = EmployeeRegister_Details.objects.filter(
            company=company
        ).values_list('email', flat=True)

        leads = GoogleFormApplication.objects.filter(
            google_form_owner_email__in=company_emails,transferred_status=0
        ).order_by('-created_at')

    for lead in leads:
        lead.collected_by = EmployeeRegister_Details.objects.filter(
            email=lead.google_form_owner_email
        ).first()
    
    lead_categories = LeadCategory_Register.objects.filter(
            client_task__client__company=company
        ).order_by('collection_for')

    return render(request, 'dmhead/google_form_leads_dmhead.html', {
        'user': user,
        'company': company,
        'name':name,
        'leads':leads,
        'lead_categories': lead_categories,


    })


@require_POST
def transfer_google_form_leads(request):

    selected_leads = request.POST.get('selected_leads')
    lead_category_id = request.POST.get('lead_category')

    if not selected_leads or not lead_category_id:
        messages.error(request, 'Please select leads and lead category.')
        return redirect('google_form_leads_dmhead')

    try:
        lead_ids = json.loads(selected_leads)
    except:
        messages.error(request, 'Invalid lead selection.')
        return redirect('google_form_leads_dmhead')

    lead_category = LeadCategory_Register.objects.filter(
        id=lead_category_id
    ).first()

    if not lead_category:
        messages.error(request, 'Lead category not found.')
        return redirect('google_form_leads_dmhead')

    google_leads = GoogleFormApplication.objects.filter(
        id__in=lead_ids,
        transferred_status=0
    )

    transferred_count = 0

    for g_lead in google_leads:

        # Employee who collected the lead
        collected_by = EmployeeRegister_Details.objects.filter(
            email=g_lead.google_form_owner_email
        ).first()

        # Create Lead
        lead = Leads.objects.create(
            collected_by=collected_by,
            lead_category=lead_category,
            name=g_lead.name,
            email=g_lead.email,
            contact=g_lead.phone,
            source=g_lead.source,
       
        )

        # Lead Details
        lead_details = [
            ("Qualification", g_lead.qualification),
            ("Year Of Passout", g_lead.year_of_passout),
            ("Location", g_lead.location),
            ("Applied For", g_lead.applied_for),
            ("Done Any Internship", g_lead.done_any_internship),
            ("Internship Start Date", g_lead.internship_startdate),
            ("Internship End Date", g_lead.internship_enddate),
            ("Experience", g_lead.experience),
        ]

        for field_name, field_value in lead_details:

            if field_value not in [None, ""]:

                LeadDetails.objects.create(
                    lead=lead,
                    field_name=field_name,
                    field_data=str(field_value)
                )

        transferred_count += 1

        g_lead.transferred_status = 1
        g_lead.save()

    messages.success(
        request,
        f'{transferred_count} lead(s) transferred successfully.'
    )

    return redirect('google_form_leads_dmhead')




def update_profile_image(request):

    if request.method == "POST":

        login_id = (
            request.session.get('eid') or
            request.session.get('hid') or
            request.session.get('tid') or
            request.session.get('did') or
            request.session.get('tcid') or
            request.session.get('hrid') or
            request.session.get('gdid')
        )

        

        if not login_id:
            messages.error(request, "Session expired.")
            return redirect('login')

        try:
            login_user = LogRegister_Details.objects.get(
                log_username=login_id
            )

            

            employee = EmployeeRegister_Details.objects.filter(
                login=login_user
            ).first()

           

            if not employee:
                messages.error(request, "Employee not found.")
                return redirect(request.META.get('HTTP_REFERER'))

            if 'profile_picture' in request.FILES:

                employee.profile_picture = request.FILES['profile_picture']
                employee.save()

            else:
                messages.error(
                    request,
                    "Please select an image."
                )

        except LogRegister_Details.DoesNotExist:
            messages.error(request, "Login account not found.")

        except Exception as e:
            print("Profile Update Error:", e)
            messages.error(
                request,
                "Unable to update profile image."
            )

    return redirect(request.META.get('HTTP_REFERER', '/'))





def logout(request):
    request.session.flush()
    return redirect('home')
    
def confirm_excel_duplicates(request):

    if request.method != "POST":
        return redirect("individual_work_main")

    login_user = LogRegister_Details.objects.get(
        log_username=request.session.get("tid")
    )

    employee_user = EmployeeRegister_Details.objects.get(login=login_user)

    team_alloc_id = request.POST.get("team_alloc_id")

    category_alloc = LeadCateogry_TeamAllocate.objects.get(id=team_alloc_id)

    lead_category = category_alloc.lead_category

    work_fk = LeadField_Register.objects.filter(
        lead_category=lead_category
    ).first().work

    rows = request.session.get("pending_rows", [])

    for row in rows:

        lead = Leads.objects.create(
            name=row["name"],
            email=row["email"],
            contact=row["contact"],
            source=row["source"],
            lead_category=lead_category,
            work=work_fk,
            collected_by=employee_user,
            repeated_status=1
        )

        for field_name, value in row["dynamic_fields"].items():

            LeadDetails.objects.create(
                lead=lead,
                field_name=field_name,
                field_data=value
            )

    request.session.pop("pending_rows", None)
    request.session.pop("duplicate_leads", None)

    messages.success(request, "leads saved successfully.")

    return redirect(
        "manage_leads_page",
        team_alloc_id=team_alloc_id,
        lead_category_id=lead_category.id
    )






def get_google_form_lead_details(request, lead_id):

    lead = get_object_or_404(GoogleFormApplication, id=lead_id)

    extra_fields = [
        {
            "field_name": "Source",
            "field_data": lead.source or "-"
        },
        {
            "field_name": "Qualification",
            "field_data": lead.qualification or "-"
        },
        {
            "field_name": "Year of Passout",
            "field_data": lead.year_of_passout or "-"
        },
        {
            "field_name": "Location",
            "field_data": lead.location or "-"
        },
        {
            "field_name": "Applied For",
            "field_data": lead.applied_for or "-"
        },
        {
            "field_name": "Done Any Internship",
            "field_data": lead.done_any_internship or "-"
        },
        {
            "field_name": "Internship Start Date",
            "field_data": str(lead.internship_startdate) if lead.internship_startdate else "-"
        },
        {
            "field_name": "Internship End Date",
            "field_data": str(lead.internship_enddate) if lead.internship_enddate else "-"
        },
        {
            "field_name": "Experience",
            "field_data": lead.experience or "-"
        },
    ]

    data = {
        "lead": {
            "name": lead.name,
            "email": lead.email,
            "contact": lead.phone,
            "source": "Google Form",
            "added_date": lead.created_at.strftime("%Y-%m-%d"),
            "added_time": lead.created_at.strftime("%I:%M:%S %p"),
        },

        "client": {
            "name": "-",
            "category": "Google Form"
        },

        "extra_details": extra_fields,

        "allocation": {
            "allocated_on": "-",
            "allocated_time": "-",
            "allocated_to": "-"
        },

        "collected_by": {
            "employee": lead.employee.name if lead.employee else "-",
            "date": lead.created_at.strftime("%Y-%m-%d"),
            "time": lead.created_at.strftime("%I:%M:%S %p"),
        },

        "history_track": []
    }

    return JsonResponse(data)
    
def Get_Repeated_Leads(request,id):
    Lead = Leads.objects.get(id=id)
    Lead_Email = Lead.email
    Lead_Phone = Lead.contact
    if Leads.objects.filter(~Q(id=id),email=Lead_Email).exists() or Leads.objects.filter(~Q(id=id),contact=Lead_Phone).exists():
        Leads_Exists = Leads.objects.exclude(id=id).filter(Q(email=Lead_Email) | Q(contact=Lead_Phone)).values('id','name','email','contact','added_date','collected_by__name')
        return JsonResponse({"success": True,'leads':list(Leads_Exists)})
    else:
        return JsonResponse({'status':False,'Message':"Duplicate Does Not Exists.."})
