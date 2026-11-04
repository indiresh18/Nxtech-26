import os
import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.conf import settings

from .models import (
    Department,
    User,
    HackathonTeam,
    HackathonMember,
    FailureAnalysisTeam,
    FailureAnalysisMember,
    FailureAnalysisStatement,
    NxTechSettings,
)
from .problem_statements import (
    HACKATHON_PROBLEM_STATEMENTS,
    get_problem_statement_choices,
    generate_hackathon_pdf_bytes,
)
from .fa_data import (
    generate_fa_statements_pdf_bytes,
    generate_fa_sources_pdf_bytes,
    generate_fa_papers_pdf_bytes,
)

TENTATIVE_PROBLEM_STATEMENTS = get_problem_statement_choices()


OFFICIAL_DEPARTMENTS = [
    ("AIDS", "Artificial Intelligence & Data Science"),
    ("AIML", "Artificial Intelligence & Machine Learning"),
    ("CSE", "Computer Science & Engineering"),
    ("IT", "Information Technology"),
    ("CIVIL", "Civil Engineering"),
    ("MECH", "Mechanical Engineering"),
    ("EEE", "Electrical & Electronics Engineering"),
    ("ECE", "Electronics & Communication Engineering"),
    ("CYBER", "Cyber Security"),
    ("VLSI", "VLSI Design & Technology"),
    ("AU", "Automobile Engineering"),
]


def get_department_list():
    """
    Returns the official ordered list of department codes for dropdowns:
    AIDS, AIML, CSE, IT, CIVIL, MECH, EEE, ECE, CYBER, VLSI, AU
    """
    return [code for code, _ in OFFICIAL_DEPARTMENTS]


def extract_problem_statement_id(statement_str):
    """
    Extracts the official problem statement ID (e.g. NT01 - NT30) from any string.
    """
    if not statement_str:
        return ""
    match = re.search(r'\b(NT\d{1,2})\b', str(statement_str), re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return str(statement_str).strip()


def check_student_already_registered(roll_number):
    """
    Checks across both Hackathon and Failure Analysis whether this roll number
    is already part of any team.
    Returns (is_registered, event_name, team_name).
    """
    clean_roll = str(roll_number).strip().lower()
    if not clean_roll:
        return False, None, None

    hack_member = HackathonMember.objects.filter(roll__iexact=clean_roll).first()
    if hack_member:
        return True, "Hackathon", hack_member.team.team_name

    fa_member = FailureAnalysisMember.objects.filter(roll__iexact=clean_roll).first()
    if fa_member:
        return True, "Failure Analysis", fa_member.team.team_name

    return False, None, None


def get_user_nxtech_registration(user):
    """
    Returns user's current NxTech registration if already registered.
    """
    if not user.is_authenticated:
        return None

    clean_user = user.username.strip().lower()

    hack_member = HackathonMember.objects.filter(roll__iexact=clean_user).first()
    if hack_member:
        return {
            'type': 'Hackathon',
            'team': hack_member.team,
            'is_leader': hack_member.is_leader,
            'team_id': hack_member.team.id
        }

    fa_member = FailureAnalysisMember.objects.filter(roll__iexact=clean_user).first()
    if fa_member:
        return {
            'type': 'Failure Analysis',
            'team': fa_member.team,
            'is_leader': fa_member.is_leader,
            'team_id': fa_member.team.id
        }

    return None


def nxtech_home(request):
    """
    Main landing page for NxTech'26 showing:
    - Official Logo & Hero Header
    - Two competition cards: Hackathon & Failure Analysis
    - 4 rules/instructions below the cards for each event
    - Inter-Department bonus banner (+10 points)
    - Live team counters and capacity locks (120 teams max)
    """
    settings = NxTechSettings.get_settings()
    user_reg = get_user_nxtech_registration(request.user)

    hackathon_team_count = HackathonTeam.objects.count()
    hackathon_member_count = HackathonMember.objects.count()
    fa_team_count = FailureAnalysisTeam.objects.count()
    fa_member_count = FailureAnalysisMember.objects.count()

    hackathon_capacity_reached = (hackathon_team_count >= settings.max_hackathon_teams)
    hackathon_open = settings.hackathon_registration_open and not hackathon_capacity_reached

    fa_capacity_reached = (fa_team_count >= settings.max_fa_teams)
    fa_open = settings.failure_analysis_registration_open and not fa_capacity_reached
    fa_statements_count = FailureAnalysisStatement.objects.filter(is_active=True).count()

    context = {
        'user_registration': user_reg,
        'user_hackathon_team': user_reg['team'] if user_reg and user_reg['type'] == 'Hackathon' else None,
        'user_fa_team': user_reg['team'] if user_reg and user_reg['type'] == 'Failure Analysis' else None,
        'settings': settings,
        'hackathon_team_count': hackathon_team_count,
        'hackathon_member_count': hackathon_member_count,
        'fa_team_count': fa_team_count,
        'fa_member_count': fa_member_count,
        'fa_statements_count': fa_statements_count,
        'hackathon_capacity_reached': hackathon_capacity_reached,
        'fa_capacity_reached': fa_capacity_reached,
        'hackathon_open': hackathon_open,
        'fa_open': fa_open,
    }
    return render(request, "nxtech/home.html", context)


def signin_view(request):
    """
    Student sign in view using Roll Number and password.
    """
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/')
        return redirect(next_url)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().upper()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            return redirect(next_url)
        else:
            error = "Invalid Roll Number or Password. Please try again."

    return render(request, "nxtech/signin.html", {'error': error, 'next': request.GET.get('next', '')})


def signup_view(request):
    """
    Student account creation exclusively for First-Year MCET students.
    """
    if request.user.is_authenticated:
        return redirect('/')

    error = None
    dept_order = {code: i for i, (code, _) in enumerate(OFFICIAL_DEPARTMENTS)}
    departments = sorted(
        Department.objects.filter(code__in=dept_order.keys()),
        key=lambda d: dept_order.get(d.code, 999)
    )

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        roll = request.POST.get('roll', '').strip().upper()
        department_id = request.POST.get('department')
        yos = request.POST.get('yos', 'First Year')
        password = request.POST.get('password1', '')
        confirm_password = request.POST.get('password2', '')
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        if not fullname or not roll or not password:
            error = "All required fields must be filled."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif User.objects.filter(username__iexact=roll).exists():
            error = f"An account with Roll Number '{roll}' already exists. Please sign in."
        else:
            dept_obj = None
            if department_id:
                dept_obj = Department.objects.filter(id=department_id).first()

            user = User.objects.create_user(
                username=roll,
                password=password,
                full_name=fullname,
                first_name=fullname.split()[0] if fullname else '',
                email=email or f"{roll.lower()}@mcet.in",
                department=dept_obj,
                phone=phone,
                year_of_study="First Year"
            )
            login(request, user)
            messages.success(request, f"Welcome {fullname}! Your account has been created successfully.")
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            return redirect(next_url)

    return render(request, "nxtech/signup.html", {
        'error': error,
        'departments': departments,
        'next': request.GET.get('next', '')
    })


def signout_view(request):
    """
    Sign out user.
    """
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('nxtech_home')


@login_required(login_url='/signin/?next=/hackathon/register/')
def register_hackathon(request):
    """
    Registration form and submission handler for NxTech Hackathon.
    Exclusively for first year students, fixed team size of exactly 5 members (1 Leader + 4 Members).
    Capacity: 120 teams.
    """
    settings = NxTechSettings.get_settings()

    # 1. Admin registration open check
    if not settings.hackathon_registration_open:
        messages.error(
            request,
            settings.hackathon_closed_message or "Registrations for NxTech Hackathon have been closed by the administrator."
        )
        return redirect('nxtech_home')

    # 2. Maximum teams capacity check (120 teams)
    current_hack_count = HackathonTeam.objects.count()
    if current_hack_count >= settings.max_hackathon_teams:
        messages.error(
            request,
            f"Registrations for NxTech Hackathon are now closed. The maximum capacity of {settings.max_hackathon_teams} teams has been reached."
        )
        return redirect('nxtech_home')

    # 3. Check if user already registered for either competition (Locking)
    existing_reg = get_user_nxtech_registration(request.user)
    if existing_reg:
        messages.warning(
            request,
            f"Registration locked: You are already registered for {existing_reg['type']} under team '{existing_reg['team'].team_name}'. "
            "A student can participate in only ONE competition across NxTech'26."
        )
        return redirect('nxtech_confirmation', event_type='hackathon' if existing_reg['type'] == 'Hackathon' else 'failure-analysis', team_id=existing_reg['team_id'])

    departments = get_department_list()
    user_dept = ""
    if hasattr(request.user, 'department') and request.user.department:
        user_dept = request.user.department.code

    ps_limit = getattr(settings, 'max_teams_per_problem_statement', 15)

    # Build problem statements list with live team counts and capacity status
    problem_statements_data = []
    ps_database_dict = {}

    for item in HACKATHON_PROBLEM_STATEMENTS:
        ps_id = item['ps_id']
        count = HackathonTeam.objects.filter(problem_statement__icontains=ps_id).count()
        remaining = max(0, ps_limit - count)
        is_full = (count >= ps_limit)
        label = f"[{ps_id}] {item['title']} ({item['category']} | {item['stream']})"
        problem_statements_data.append({
            'code': ps_id,
            'label': label,
            'title': item['title'],
            'type': item['category'],
            'stream': item['stream'],
            'description': item['description'],
            'count': count,
            'limit': ps_limit,
            'remaining': remaining,
            'is_full': is_full,
        })
        ps_database_dict[ps_id] = {
            'ps_id': ps_id,
            'title': item['title'],
            'description': item['description'],
            'type': item['category'],
            'stream': item['stream'],
            'count': count,
            'limit': ps_limit,
            'remaining': remaining,
            'is_full': is_full,
        }

    ps_data_json = json.dumps(ps_database_dict)
    form_context = {
        'departments': departments,
        'problem_statements': problem_statements_data,
        'ps_limit': ps_limit,
        'user_dept': user_dept,
        'ps_data_json': ps_data_json,
    }

    if request.method == 'POST':
        # Re-verify capacity & admin open status
        if not settings.hackathon_registration_open:
            messages.error(request, "Hackathon registration has been closed by the administrator.")
            return redirect('nxtech_home')
        if HackathonTeam.objects.count() >= settings.max_hackathon_teams:
            messages.error(request, f"Registration closed: Maximum capacity of {settings.max_hackathon_teams} teams has been reached.")
            return redirect('nxtech_home')

        team_name = request.POST.get('team_name', '').strip()
        leader_name = request.POST.get('leader_name', '').strip() or request.user.full_name or request.user.username
        leader_roll = request.POST.get('leader_roll', '').strip() or request.user.username
        leader_dept = request.POST.get('leader_dept', '').strip() or user_dept
        leader_email = request.POST.get('leader_email', '').strip() or request.user.email
        leader_contact = request.POST.get('leader_contact', '').strip() or getattr(request.user, 'phone', '')
        problem_statement = request.POST.get('problem_statement', '').strip()
        problem_statement_detail = ""

        member_names = request.POST.getlist('member_name[]')
        member_rolls = request.POST.getlist('member_roll[]')
        member_depts = request.POST.getlist('member_dept[]')

        members_data = []
        for i in range(len(member_names)):
            m_name = member_names[i].strip()
            m_roll = member_rolls[i].strip()
            m_dept = member_depts[i].strip() if i < len(member_depts) else ''
            if m_name and m_roll:
                members_data.append({
                    'name': m_name,
                    'roll': m_roll.upper(),
                    'dept': m_dept or 'General'
                })

        # Basic validations
        if not team_name:
            messages.error(request, "Team Name is required.")
            return render(request, "nxtech/register_hackathon.html", form_context)

        if not problem_statement:
            messages.error(request, "Please select an official Problem Statement (NT01 to NT30).")
            return render(request, "nxtech/register_hackathon.html", form_context)

        # Check problem statement limit (e.g. 15 teams maximum per statement)
        ps_id = extract_problem_statement_id(problem_statement)
        if ps_id:
            current_ps_count = HackathonTeam.objects.filter(problem_statement__icontains=ps_id).count()
            if current_ps_count >= ps_limit:
                messages.error(
                    request,
                    f"Problem Statement [{ps_id}] has reached the maximum limitation of {ps_limit} teams. "
                    "Each problem statement can only be chosen by up to 15 teams. Please select a different problem statement."
                )
                return render(request, "nxtech/register_hackathon.html", form_context)

            matching_ps = next((item for item in HACKATHON_PROBLEM_STATEMENTS if item['ps_id'] == ps_id), None)
            if matching_ps:
                problem_statement_detail = matching_ps['description']

        # Fixed team size check: Exactly 5 members (1 Leader + 4 Members)
        if len(members_data) != 4:
            messages.error(request, f"Team must have a fixed size of exactly 5 members (1 Team Leader + 4 Members). You have provided {len(members_data)} member(s).")
            return render(request, "nxtech/register_hackathon.html", form_context)

        # Check duplicate rolls within the submitted team
        all_rolls = [leader_roll.upper()] + [m['roll'] for m in members_data]
        if len(all_rolls) != len(set(all_rolls)):
            messages.error(request, "Duplicate roll numbers detected within your team. Each member must have a unique roll number.")
            return render(request, "nxtech/register_hackathon.html", form_context)

        # Check exclusivity against database for all team members (both Hackathon & Failure Analysis)
        for roll in all_rolls:
            is_reg, ev_name, t_name = check_student_already_registered(roll)
            if is_reg:
                messages.error(
                    request,
                    f"Student with Roll No '{roll.upper()}' is already registered in {ev_name} (Team: '{t_name}'). "
                    "Per NxTech rules, a student can be part of only ONE team across both competitions."
                )
                return render(request, "nxtech/register_hackathon.html", form_context)

        # Save into database
        try:
            with transaction.atomic():
                team = HackathonTeam.objects.create(
                    team_name=team_name,
                    leader_name=leader_name,
                    leader_roll=leader_roll.upper(),
                    leader_dept=leader_dept,
                    leader_email=leader_email,
                    leader_contact=leader_contact,
                    leader_year="First Year",
                    problem_statement=problem_statement,
                    problem_statement_detail=problem_statement_detail,
                    registered_by_user=request.user.username
                )

                # Leader as member #1
                HackathonMember.objects.create(
                    team=team,
                    name=leader_name,
                    roll=leader_roll.upper(),
                    dept=leader_dept,
                    is_leader=True
                )

                # Team members
                for m in members_data:
                    HackathonMember.objects.create(
                        team=team,
                        name=m['name'],
                        roll=m['roll'].upper(),
                        dept=m['dept'],
                        is_leader=False
                    )

            messages.success(
                request,
                f"Congratulations! Team '{team_name}' has been successfully registered for the NxTech 2K26 Hackathon!"
            )
            return redirect('nxtech_confirmation', event_type='hackathon', team_id=team.id)

        except Exception as e:
            messages.error(request, f"An error occurred while saving your registration: {str(e)}")
            return render(request, "nxtech/register_hackathon.html", form_context)

    return render(request, "nxtech/register_hackathon.html", form_context)


@login_required(login_url='/signin/?next=/failure-analysis/register/')
def register_failure_analysis(request):
    """
    Registration form and submission handler for NxTech Failure Analysis.
    Exclusively for first year students, fixed team size of exactly 5 members (1 Leader + 4 Members).
    Capacity: 120 teams.
    """
    settings = NxTechSettings.get_settings()

    # 1. Admin registration open check
    if not settings.failure_analysis_registration_open:
        messages.error(
            request,
            settings.failure_analysis_closed_message or "Registrations for NxTech Failure Analysis have been closed by the administrator."
        )
        return redirect('nxtech_home')

    # 2. Maximum teams capacity check (120 teams)
    current_fa_count = FailureAnalysisTeam.objects.count()
    if current_fa_count >= settings.max_fa_teams:
        messages.error(
            request,
            f"Registrations for NxTech Failure Analysis are now closed. The maximum capacity of {settings.max_fa_teams} teams has been reached."
        )
        return redirect('nxtech_home')

    # 3. Check if user already registered for either competition (Locking)
    existing_reg = get_user_nxtech_registration(request.user)
    if existing_reg:
        messages.warning(
            request,
            f"Registration locked: You are already registered for {existing_reg['type']} under team '{existing_reg['team'].team_name}'. "
            "A student can participate in only ONE competition across NxTech'26."
        )
        return redirect('nxtech_confirmation', event_type='hackathon' if existing_reg['type'] == 'Hackathon' else 'failure-analysis', team_id=existing_reg['team_id'])

    departments = get_department_list()
    user_dept = ""
    if hasattr(request.user, 'department') and request.user.department:
        user_dept = request.user.department.code

    form_context = {
        'departments': departments,
        'user_dept': user_dept,
    }

    if request.method == 'POST':
        # Re-verify admin open status & capacity
        if not settings.failure_analysis_registration_open:
            messages.error(request, "Failure Analysis registration has been closed by the administrator.")
            return redirect('nxtech_home')
        if FailureAnalysisTeam.objects.count() >= settings.max_fa_teams:
            messages.error(request, f"Registration closed: Maximum capacity of {settings.max_fa_teams} teams has been reached.")
            return redirect('nxtech_home')

        team_name = request.POST.get('team_name', '').strip()
        leader_name = request.POST.get('leader_name', '').strip() or request.user.full_name or request.user.username
        leader_roll = request.POST.get('leader_roll', '').strip() or request.user.username
        leader_dept = request.POST.get('leader_dept', '').strip() or user_dept
        leader_email = request.POST.get('leader_email', '').strip() or request.user.email
        leader_contact = request.POST.get('leader_contact', '').strip() or getattr(request.user, 'phone', '')

        member_names = request.POST.getlist('member_name[]')
        member_rolls = request.POST.getlist('member_roll[]')
        member_depts = request.POST.getlist('member_dept[]')

        members_data = []
        for i in range(len(member_names)):
            m_name = member_names[i].strip()
            m_roll = member_rolls[i].strip()
            m_dept = member_depts[i].strip() if i < len(member_depts) else ''
            if m_name and m_roll:
                members_data.append({
                    'name': m_name,
                    'roll': m_roll.upper(),
                    'dept': m_dept or 'General'
                })

        if not team_name:
            messages.error(request, "Team Name is required.")
            return render(request, "nxtech/register_failure_analysis.html", form_context)

        # Fixed team size check: Exactly 5 members (1 Leader + 4 Members)
        if len(members_data) != 4:
            messages.error(request, f"Team must have a fixed size of exactly 5 members (1 Team Leader + 4 Members). You have provided {len(members_data)} member(s).")
            return render(request, "nxtech/register_failure_analysis.html", form_context)

        # Check duplicate rolls within the submitted team
        all_rolls = [leader_roll.upper()] + [m['roll'] for m in members_data]
        if len(all_rolls) != len(set(all_rolls)):
            messages.error(request, "Duplicate roll numbers detected within your team. Each member must have a unique roll number.")
            return render(request, "nxtech/register_failure_analysis.html", form_context)

        # Check exclusivity against database for all team members (both Hackathon & Failure Analysis)
        for roll in all_rolls:
            is_reg, ev_name, t_name = check_student_already_registered(roll)
            if is_reg:
                messages.error(
                    request,
                    f"Student with Roll No '{roll.upper()}' is already registered in {ev_name} (Team: '{t_name}'). "
                    "Per NxTech rules, a student can be part of only ONE team across both competitions."
                )
                return render(request, "nxtech/register_failure_analysis.html", form_context)

        # Save into database
        try:
            with transaction.atomic():
                team = FailureAnalysisTeam.objects.create(
                    team_name=team_name,
                    leader_name=leader_name,
                    leader_roll=leader_roll.upper(),
                    leader_dept=leader_dept,
                    leader_email=leader_email,
                    leader_contact=leader_contact,
                    leader_year="First Year",
                    registered_by_user=request.user.username
                )

                # Leader as member #1
                FailureAnalysisMember.objects.create(
                    team=team,
                    name=leader_name,
                    roll=leader_roll.upper(),
                    dept=leader_dept,
                    is_leader=True
                )

                # Team members
                for m in members_data:
                    FailureAnalysisMember.objects.create(
                        team=team,
                        name=m['name'],
                        roll=m['roll'].upper(),
                        dept=m['dept'],
                        is_leader=False
                    )

            messages.success(
                request,
                f"Congratulations! Team '{team_name}' has been successfully registered for the NxTech 2K26 Failure Analysis Challenge!"
            )
            return redirect('nxtech_confirmation', event_type='failure-analysis', team_id=team.id)

        except Exception as e:
            messages.error(request, f"An error occurred while saving your registration: {str(e)}")
            return render(request, "nxtech/register_failure_analysis.html", form_context)

    return render(request, "nxtech/register_failure_analysis.html", form_context)


@login_required
def registration_confirmation(request, event_type, team_id):
    """
    Displays the confirmation & acknowledgement receipt for registered teams.
    """
    is_hackathon = (event_type == 'hackathon')
    team = None
    members = []

    if is_hackathon:
        team = get_object_or_404(HackathonTeam, id=team_id)
        members = HackathonMember.objects.filter(team=team).order_by('-is_leader', 'id')
    else:
        team = get_object_or_404(FailureAnalysisTeam, id=team_id)
        members = FailureAnalysisMember.objects.filter(team=team).order_by('-is_leader', 'id')

    context = {
        'team': team,
        'members': members,
        'is_hackathon': is_hackathon,
        'event_title': 'NxTech 2K26 Hackathon' if is_hackathon else 'NxTech 2K26 Failure Analysis',
    }
    return render(request, "nxtech/registration_success.html", context)


def download_hackathon_problem_statements(request):
    """
    Downloads the official NxTech'26 Hackathon Problem Statements (NT01-NT30)
    as a formatted PDF document.
    """
    pdf_bytes = generate_hackathon_pdf_bytes()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="NxTech26_Hackathon_Problem_Statements.pdf"'
    return response


def download_fa_problem_statements(request):
    """
    Doc 1: Downloads the official Failure Analysis Problem Statements & Research Paper Links
    (Circuit/Electronics & Core/Auto-Mechanical).
    """
    pdf_bytes = generate_fa_statements_pdf_bytes()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="NxTech26_Failure_Analysis_Problem_Statements.pdf"'
    return response


def download_fa_case_sources(request):
    """
    Doc 2: Downloads Research Sources for 15 Startup Failure Case Studies.
    """
    pdf_bytes = generate_fa_sources_pdf_bytes()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="NxTech26_15_Startup_Case_Studies_Sources.pdf"'
    return response


def download_fa_research_papers(request):
    """
    Doc 3: Downloads Startups and Their Related Research Papers.
    """
    pdf_bytes = generate_fa_papers_pdf_bytes()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="NxTech26_Startups_and_Related_Research_Papers.pdf"'
    return response


def select_failure_analysis_statement(request):
    """
    Failure Analysis Problem Statement Selection & Materials Hub.
    Allows registered or competing teams to download the 3 official reference
    documents and officially submit their chosen case study / problem statement.
    """
    settings = NxTechSettings.get_settings()
    user_reg = get_user_nxtech_registration(request.user)

    # Active statements grouped by track
    active_statements = FailureAnalysisStatement.objects.filter(is_active=True).order_by('order', 'ps_id')
    circuit_statements = active_statements.filter(category='CIRCUIT')
    core_statements = active_statements.filter(category='CORE')
    startup_statements = active_statements.filter(category='STARTUP')

    prefill_team_name = ""
    prefill_leader_name = ""
    prefill_leader_roll = ""
    existing_team = None

    if user_reg and user_reg['type'] == 'Failure Analysis':
        existing_team = user_reg['team']
        prefill_team_name = existing_team.team_name
        prefill_leader_name = existing_team.leader_name
        prefill_leader_roll = existing_team.leader_roll
    elif request.user.is_authenticated:
        prefill_leader_name = getattr(request.user, 'full_name', '') or request.user.username
        prefill_leader_roll = request.user.username

    if request.method == 'POST':
        if not settings.fa_statement_selection_open:
            messages.error(
                request,
                settings.fa_statement_selection_closed_msg or "Statement selection for Failure Analysis is currently closed."
            )
            return redirect('select_failure_analysis_statement')

        team_name = request.POST.get('team_name', '').strip()
        leader_name = request.POST.get('leader_name', '').strip()
        leader_roll = request.POST.get('leader_roll', '').strip().upper()
        statement_id = request.POST.get('statement_id', '').strip()

        if not team_name:
            messages.error(request, "Team Name is required.")
            return redirect('select_failure_analysis_statement')
        if not statement_id:
            messages.error(request, "Please select an official Problem Statement / Case Study.")
            return redirect('select_failure_analysis_statement')

        # Find statement object (supports either ps_id like 'FA01' or integer pk)
        selected_stmt = FailureAnalysisStatement.objects.filter(ps_id=statement_id, is_active=True).first()
        if not selected_stmt and str(statement_id).isdigit():
            selected_stmt = FailureAnalysisStatement.objects.filter(id=int(statement_id), is_active=True).first()
        if not selected_stmt:
            messages.error(request, "Selected Problem Statement is invalid or has been archived.")
            return redirect('select_failure_analysis_statement')

        # Match team in database
        target_team = None
        if existing_team and existing_team.team_name.lower() == team_name.lower():
            target_team = existing_team
        else:
            target_team = FailureAnalysisTeam.objects.filter(team_name__iexact=team_name).first()
            if not target_team and leader_roll:
                target_team = FailureAnalysisTeam.objects.filter(leader_roll__iexact=leader_roll).first()

        statement_full_title = f"[{selected_stmt.ps_id}] {selected_stmt.title}"

        if target_team:
            target_team.selected_statement = selected_stmt
            target_team.selected_statement_title = statement_full_title
            target_team.topic = statement_full_title
            target_team.statement_selected_at = timezone.now()
            if leader_name and (not target_team.leader_name or target_team.leader_name == target_team.leader_roll):
                target_team.leader_name = leader_name
            target_team.save()

            messages.success(
                request,
                f"🎉 Statement locked! Team '{target_team.team_name}' has successfully selected '{statement_full_title}'."
            )
            return redirect('nxtech_confirmation', event_type='failure-analysis', team_id=target_team.id)
        else:
            # If team registered with slight variation or directly on-spot
            reg_user = request.user.username if request.user.is_authenticated else (leader_roll or team_name)
            target_team = FailureAnalysisTeam.objects.create(
                team_name=team_name,
                leader_name=leader_name or "Team Leader",
                leader_roll=leader_roll or "NXT-FA",
                leader_dept="General",
                topic=statement_full_title,
                selected_statement=selected_stmt,
                selected_statement_title=statement_full_title,
                statement_selected_at=timezone.now(),
                registered_by_user=reg_user
            )
            messages.success(
                request,
                f"🎉 Statement submitted! Team '{team_name}' has locked '{statement_full_title}'."
            )
            return redirect('nxtech_confirmation', event_type='failure-analysis', team_id=target_team.id)

    context = {
        'settings': settings,
        'active_statements': active_statements,
        'circuit_statements': circuit_statements,
        'core_statements': core_statements,
        'startup_statements': startup_statements,
        'prefill_team_name': prefill_team_name,
        'prefill_leader_name': prefill_leader_name,
        'prefill_leader_roll': prefill_leader_roll,
        'existing_team': existing_team,
        'total_statements_count': active_statements.count(),
    }
    return render(request, "nxtech/select_fa_statement.html", context)


def download_hackathon_ppt_template(request):
    """
    Downloads the official NxTech'26 Hackathon Presentation PPT Template (.pptx).
    """
    template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'NxTech26_Hackathon_Template.pptx')
    if not os.path.exists(template_path):
        fallback = r'C:\Users\indhi\.gemini\antigravity\brain\dd8e7f7d-3563-41e7-904d-2cd76d4d23ba\.user_uploaded\media_1793762494752_c7ab3d78.pptx'
        if os.path.exists(fallback):
            template_path = fallback

    if os.path.exists(template_path):
        with open(template_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response['Content-Disposition'] = 'attachment; filename="NxTech26_Hackathon_Template.pptx"'
        return response
    raise Http404("Hackathon presentation template file not found.")


def download_fa_ppt_template(request):
    """
    Downloads the official NxTech'26 Failure Analysis Presentation PPT Template (.pptx).
    """
    template_path = os.path.join(settings.BASE_DIR, 'static', 'templates', 'NxTech26_Failure_Analysis_Template.pptx')
    if not os.path.exists(template_path):
        fallback = r'C:\Users\indhi\.gemini\antigravity\brain\dd8e7f7d-3563-41e7-904d-2cd76d4d23ba\.user_uploaded\media_1793762494655_dfa708fe.pptx'
        if os.path.exists(fallback):
            template_path = fallback

    if os.path.exists(template_path):
        with open(template_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response['Content-Disposition'] = 'attachment; filename="NxTech26_Failure_Analysis_Template.pptx"'
        return response
    raise Http404("Failure Analysis presentation template file not found.")


def submit_hackathon_ppt(request):
    """
    Hackathon Presentation Submission Portal.
    Allows teams to submit their presentation PPT / PPTX / PDF file or Google Drive/Slides URL.
    """
    settings_obj = NxTechSettings.get_settings()
    user_reg = get_user_nxtech_registration(request.user)

    existing_team = None
    prefill_team_name = ""
    prefill_leader_roll = ""
    prefill_leader_name = ""

    if user_reg and user_reg['type'] == 'Hackathon':
        existing_team = user_reg['team']
        prefill_team_name = existing_team.team_name
        prefill_leader_roll = existing_team.leader_roll
        prefill_leader_name = existing_team.leader_name
    elif request.user.is_authenticated:
        prefill_leader_roll = request.user.username
        prefill_leader_name = getattr(request.user, 'full_name', '') or request.user.username

    if request.method == 'POST':
        if not settings_obj.hackathon_ppt_submission_open:
            messages.error(
                request,
                settings_obj.ppt_submission_closed_msg or "Hackathon presentation submission is currently closed."
            )
            return redirect('submit_hackathon_ppt')

        team_name = request.POST.get('team_name', '').strip()
        leader_roll = request.POST.get('leader_roll', '').strip().upper()
        leader_name = request.POST.get('leader_name', '').strip()
        ppt_link = request.POST.get('ppt_link', '').strip()
        ppt_notes = request.POST.get('ppt_notes', '').strip()
        ppt_file = request.FILES.get('ppt_file')

        if not team_name:
            messages.error(request, "Team Name is required.")
            return redirect('submit_hackathon_ppt')

        if not ppt_link and not ppt_file:
            messages.error(request, "Please provide either a Google Drive/Slides link OR upload your presentation file.")
            return redirect('submit_hackathon_ppt')

        file_bytes = None
        file_name = None
        if ppt_file:
            if ppt_file.size > 15 * 1024 * 1024:
                messages.error(request, "Uploaded file exceeds 15 MB limit. Please provide a Google Drive/Slides link instead.")
                return redirect('submit_hackathon_ppt')
            ext = os.path.splitext(ppt_file.name)[1].lower()
            if ext not in ['.pptx', '.ppt', '.pdf', '.zip']:
                messages.error(request, "Only .pptx, .ppt, .pdf, or .zip files are allowed.")
                return redirect('submit_hackathon_ppt')
            file_bytes = ppt_file.read()
            file_name = ppt_file.name

        # Lookup team
        target_team = None
        if existing_team and existing_team.team_name.lower() == team_name.lower():
            target_team = existing_team
        else:
            target_team = HackathonTeam.objects.filter(team_name__iexact=team_name).first()
            if not target_team and leader_roll:
                target_team = HackathonTeam.objects.filter(leader_roll__iexact=leader_roll).first()

        if target_team:
            if ppt_link:
                target_team.ppt_link = ppt_link
            if file_bytes:
                target_team.ppt_file_bytes = file_bytes
                target_team.ppt_filename = file_name
            if ppt_notes:
                target_team.ppt_notes = ppt_notes
            if leader_name and (not target_team.leader_name or target_team.leader_name == target_team.leader_roll):
                target_team.leader_name = leader_name
            target_team.ppt_submitted_at = timezone.now()
            target_team.save()
            messages.success(
                request,
                f"🎉 Hackathon Presentation submitted successfully for Team '{target_team.team_name}'!"
            )
            return redirect('submit_hackathon_ppt')
        else:
            # Create a submission entry so no team's work is ever rejected
            reg_user = request.user.username if request.user.is_authenticated else (leader_roll or team_name)
            target_team = HackathonTeam.objects.create(
                team_name=team_name,
                leader_name=leader_name or "Team Leader",
                leader_roll=leader_roll or "NXT-HACK",
                leader_dept="General",
                problem_statement="Hackathon Track Presentation",
                ppt_link=ppt_link,
                ppt_filename=file_name,
                ppt_file_bytes=file_bytes,
                ppt_notes=ppt_notes,
                ppt_submitted_at=timezone.now(),
                registered_by_user=reg_user
            )
            messages.success(
                request,
                f"🎉 Hackathon Presentation submitted successfully for Team '{target_team.team_name}'!"
            )
            return redirect('submit_hackathon_ppt')

    context = {
        'settings': settings_obj,
        'existing_team': existing_team,
        'prefill_team_name': prefill_team_name,
        'prefill_leader_roll': prefill_leader_roll,
        'prefill_leader_name': prefill_leader_name,
    }
    return render(request, "nxtech/submit_hackathon_ppt.html", context)


def submit_failure_analysis_ppt(request):
    """
    Failure Analysis Presentation Submission Portal.
    Allows teams to submit their presentation PPT / PPTX / PDF file or Google Drive/Slides URL.
    """
    settings_obj = NxTechSettings.get_settings()
    user_reg = get_user_nxtech_registration(request.user)

    existing_team = None
    prefill_team_name = ""
    prefill_leader_roll = ""
    prefill_leader_name = ""

    if user_reg and user_reg['type'] == 'Failure Analysis':
        existing_team = user_reg['team']
        prefill_team_name = existing_team.team_name
        prefill_leader_roll = existing_team.leader_roll
        prefill_leader_name = existing_team.leader_name
    elif request.user.is_authenticated:
        prefill_leader_roll = request.user.username
        prefill_leader_name = getattr(request.user, 'full_name', '') or request.user.username

    if request.method == 'POST':
        if not settings_obj.fa_ppt_submission_open:
            messages.error(
                request,
                settings_obj.ppt_submission_closed_msg or "Failure Analysis presentation submission is currently closed."
            )
            return redirect('submit_failure_analysis_ppt')

        team_name = request.POST.get('team_name', '').strip()
        leader_roll = request.POST.get('leader_roll', '').strip().upper()
        leader_name = request.POST.get('leader_name', '').strip()
        ppt_link = request.POST.get('ppt_link', '').strip()
        ppt_notes = request.POST.get('ppt_notes', '').strip()
        ppt_file = request.FILES.get('ppt_file')

        if not team_name:
            messages.error(request, "Team Name is required.")
            return redirect('submit_failure_analysis_ppt')

        if not ppt_link and not ppt_file:
            messages.error(request, "Please provide either a Google Drive/Slides link OR upload your presentation file.")
            return redirect('submit_failure_analysis_ppt')

        file_bytes = None
        file_name = None
        if ppt_file:
            if ppt_file.size > 15 * 1024 * 1024:
                messages.error(request, "Uploaded file exceeds 15 MB limit. Please provide a Google Drive/Slides link instead.")
                return redirect('submit_failure_analysis_ppt')
            ext = os.path.splitext(ppt_file.name)[1].lower()
            if ext not in ['.pptx', '.ppt', '.pdf', '.zip']:
                messages.error(request, "Only .pptx, .ppt, .pdf, or .zip files are allowed.")
                return redirect('submit_failure_analysis_ppt')
            file_bytes = ppt_file.read()
            file_name = ppt_file.name

        # Lookup team
        target_team = None
        if existing_team and existing_team.team_name.lower() == team_name.lower():
            target_team = existing_team
        else:
            target_team = FailureAnalysisTeam.objects.filter(team_name__iexact=team_name).first()
            if not target_team and leader_roll:
                target_team = FailureAnalysisTeam.objects.filter(leader_roll__iexact=leader_roll).first()

        if target_team:
            if ppt_link:
                target_team.ppt_link = ppt_link
            if file_bytes:
                target_team.ppt_file_bytes = file_bytes
                target_team.ppt_filename = file_name
            if ppt_notes:
                target_team.ppt_notes = ppt_notes
            if leader_name and (not target_team.leader_name or target_team.leader_name == target_team.leader_roll):
                target_team.leader_name = leader_name
            target_team.ppt_submitted_at = timezone.now()
            target_team.save()
            messages.success(
                request,
                f"🎉 Failure Analysis Presentation submitted successfully for Team '{target_team.team_name}'!"
            )
            return redirect('submit_failure_analysis_ppt')
        else:
            reg_user = request.user.username if request.user.is_authenticated else (leader_roll or team_name)
            target_team = FailureAnalysisTeam.objects.create(
                team_name=team_name,
                leader_name=leader_name or "Team Leader",
                leader_roll=leader_roll or "NXT-FA",
                leader_dept="General",
                topic="Failure Analysis Presentation",
                ppt_link=ppt_link,
                ppt_filename=file_name,
                ppt_file_bytes=file_bytes,
                ppt_notes=ppt_notes,
                ppt_submitted_at=timezone.now(),
                registered_by_user=reg_user
            )
            messages.success(
                request,
                f"🎉 Failure Analysis Presentation submitted successfully for Team '{target_team.team_name}'!"
            )
            return redirect('submit_failure_analysis_ppt')

    context = {
        'settings': settings_obj,
        'existing_team': existing_team,
        'prefill_team_name': prefill_team_name,
        'prefill_leader_roll': prefill_leader_roll,
        'prefill_leader_name': prefill_leader_name,
    }
    return render(request, "nxtech/submit_fa_ppt.html", context)


def download_hackathon_submission_file(request, team_id):
    """
    Downloads the presentation file submitted by a Hackathon team.
    """
    team = get_object_or_404(HackathonTeam, id=team_id)
    if not team.ppt_file_bytes:
        raise Http404("No uploaded file found for this team. Check if a cloud presentation link was provided.")
    filename = team.ppt_filename or f"{team.team_name}_hackathon_presentation.pptx"
    ext = os.path.splitext(filename)[1].lower()
    ct = 'application/octet-stream'
    if ext == '.pdf':
        ct = 'application/pdf'
    elif ext in ['.pptx', '.ppt']:
        ct = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    response = HttpResponse(team.ppt_file_bytes, content_type=ct)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def download_fa_submission_file(request, team_id):
    """
    Downloads the presentation file submitted by a Failure Analysis team.
    """
    team = get_object_or_404(FailureAnalysisTeam, id=team_id)
    if not team.ppt_file_bytes:
        raise Http404("No uploaded file found for this team. Check if a cloud presentation link was provided.")
    filename = team.ppt_filename or f"{team.team_name}_fa_presentation.pptx"
    ext = os.path.splitext(filename)[1].lower()
    ct = 'application/octet-stream'
    if ext == '.pdf':
        ct = 'application/pdf'
    elif ext in ['.pptx', '.ppt']:
        ct = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    response = HttpResponse(team.ppt_file_bytes, content_type=ct)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



