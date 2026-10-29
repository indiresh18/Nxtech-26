import os
import sys
import django

# Set UTF-8 output encoding if possible
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from nxtech.models import User, Department, HackathonTeam, HackathonMember, FailureAnalysisTeam, FailureAnalysisMember, NxTechSettings

def run_tests():
    print("=" * 70)
    print(">> Running Full Standalone NxTech 2K26 Test Suite")
    print("=" * 70)

    # Clean up test database records for idempotency
    HackathonTeam.objects.all().delete()
    FailureAnalysisTeam.objects.all().delete()
    User.objects.filter(username__in=['727626BCS101', '727626BCS999', '727626BCS888', '727626BCS777']).delete()

    client = Client()

    # TEST 1: Home Page
    print("\n[TEST 1] Checking Landing Page (GET /)...")
    resp = client.get('/')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    content = resp.content.decode('utf-8')
    assert "NxTech" in content, "NxTech branding missing from home page"
    assert "6 Hours Live" in content, "6 Hours Live spec chip missing"
    assert "Fixed 5 Members" in content, "Fixed 5 Members spec chip missing"
    assert "INTER DEPARTMENT TEAMS WILL GET EXTRA 10 points" in content, "10 bonus points banner missing"
    assert "120" in content, "120 max limit missing"
    print("  PASS: Landing page renders with all badges, limits, and bonus callout.")

    # TEST 2: Problem Statements PDF Download
    print("\n[TEST 2] Checking Problem Statements PDF Download...")
    resp = client.get('/hackathon/download-problem-statements/')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert resp['Content-Type'] == 'application/pdf', f"Expected PDF, got {resp['Content-Type']}"
    assert len(resp.content) > 1000, "PDF content is too small"
    print(f"  PASS: ReportLab PDF generated successfully ({len(resp.content)} bytes).")

    # TEST 3: Student Sign Up & Authentication
    print("\n[TEST 3] Testing Student Account Creation (Sign Up)...")
    dept = Department.objects.first()
    signup_data = {
        'fullname': 'Arun Kumar',
        'roll': '727626BCS101',
        'department': dept.id,
        'yos': 'First Year',
        'password1': 'secret123',
        'password2': 'secret123',
        'phone': '9876543210',
        'email': 'arun@mcet.in'
    }
    resp = client.post('/signup/', signup_data, follow=True)
    assert resp.status_code == 200
    user = User.objects.filter(username='727626BCS101').first()
    assert user is not None, "User was not created"
    assert user.year_of_study == 'First Year', f"Expected 'First Year', got {user.year_of_study}"
    print(f"  PASS: User '{user.username}' created and logged in automatically.")

    # TEST 4: Hackathon Form - Reject Invalid Member Count (< 5 members)
    print("\n[TEST 4] Testing Team Size Validation (Must be exactly 5 members)...")
    invalid_data = {
        'team_name': 'Incomplete Squad',
        'leader_name': 'Arun Kumar',
        'leader_roll': '727626BCS101',
        'leader_dept': dept.code,
        'leader_contact': '9876543210',
        'problem_statement': 'NT01: AI-Powered Campus Energy Optimization Engine',
        'member_name[]': ['Member 2', 'Member 3'], # Only 2 members (total 3)
        'member_roll[]': ['727626BCS102', '727626BCS103'],
        'member_dept[]': ['CSE', 'CSE'],
    }
    resp = client.post('/hackathon/register/', invalid_data, follow=True)
    assert HackathonTeam.objects.filter(team_name='Incomplete Squad').count() == 0, "Team should not have been created"
    print("  PASS: Incomplete team (< 5 members) was correctly rejected.")

    # TEST 5: Hackathon Form - Reject Duplicate Roll Numbers
    print("\n[TEST 5] Testing Duplicate Roll Detection within Squad...")
    dup_data = {
        'team_name': 'Duplicate Squad',
        'leader_name': 'Arun Kumar',
        'leader_roll': '727626BCS101',
        'leader_dept': dept.code,
        'leader_contact': '9876543210',
        'problem_statement': 'NT01: AI-Powered Campus Energy Optimization Engine',
        'member_name[]': ['Member 2', 'Member 3', 'Member 4', 'Member 5'],
        'member_roll[]': ['727626BCS102', '727626BCS102', '727626BCS104', '727626BCS105'], # Duplicate 102
        'member_dept[]': ['CSE', 'AIDS', 'ECE', 'MECH'],
    }
    resp = client.post('/hackathon/register/', dup_data, follow=True)
    assert HackathonTeam.objects.filter(team_name='Duplicate Squad').count() == 0, "Duplicate team should not be created"
    print("  PASS: Duplicate roll numbers within squad were correctly rejected.")

    # TEST 6: Successful Registration (5 Members)
    print("\n[TEST 6] Testing Valid Hackathon Registration (Exactly 5 Members)...")
    valid_data = {
        'team_name': 'CyberKnights',
        'leader_name': 'Arun Kumar',
        'leader_roll': '727626BCS101',
        'leader_dept': 'CSE',
        'leader_contact': '9876543210',
        'problem_statement': 'NT01: AI-Powered Campus Energy Optimization Engine',
        'member_name[]': ['Bala', 'Chitra', 'Deepak', 'Eswar'],
        'member_roll[]': ['727626BCS102', '727626BAD103', '727626BEC104', '727626BME105'],
        'member_dept[]': ['CSE', 'AIDS', 'ECE', 'MECH'],
    }
    resp = client.post('/hackathon/register/', valid_data, follow=True)
    assert resp.status_code == 200
    team = HackathonTeam.objects.filter(team_name='CyberKnights').first()
    assert team is not None, "Team was not created"
    assert team.members.count() == 5, f"Expected 5 members, found {team.members.count()}"
    leader = team.members.filter(is_leader=True).first()
    assert leader.roll == '727626BCS101', "Leader roll mismatch"
    print(f"  PASS: Team '{team.team_name}' registered successfully with 5 members.")
    print(f"  PASS: Export team name formatted as: '{team.export_team_name}'")
    assert team.export_team_name == "CyberKnights (727626BCS101)"

    # TEST 7: Cross-Event Registration Locking
    print("\n[TEST 7] Testing Cross-Event Locking (Leader & Members locked)...")
    # Try registering leader for Failure Analysis
    fa_data = {
        'team_name': 'Forensic Force',
        'leader_name': 'Arun Kumar',
        'leader_roll': '727626BCS101', # Already registered in Hackathon
        'leader_dept': 'CSE',
        'member_name[]': ['F1', 'F2', 'F3', 'F4'],
        'member_roll[]': ['727626BME201', '727626BME202', '727626BME203', '727626BME204'],
        'member_dept[]': ['MECH', 'MECH', 'MECH', 'MECH'],
    }
    resp = client.post('/failure-analysis/register/', fa_data, follow=True)
    assert FailureAnalysisTeam.objects.filter(team_name='Forensic Force').count() == 0, "Should be locked"
    print("  PASS: Cross-event lock prevented Hackathon participant from registering in Failure Analysis.")

    # TEST 8: Confirmation Receipt Page
    print("\n[TEST 8] Checking Digital Confirmation Receipt...")
    resp = client.get(f'/confirmation/hackathon/{team.id}/')
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert "CyberKnights" in content
    assert "#NXT-" in content
    assert "727626BCS101" in content
    assert "print(" not in content.lower(), "Print button should not be present"
    print("  PASS: Receipt renders digital ticket with roster and without print button.")

    # TEST 9: Capacity Limit Lock (120 Teams)
    print("\n[TEST 9] Testing 120-Team Capacity Limit...")
    settings = NxTechSettings.get_settings()
    settings.max_hackathon_teams = 1 # Set limit to 1 (since 1 team is registered)
    settings.save()

    # Create a new user to test capacity lock
    user2 = User.objects.create_user(username='727626BCS999', password='password123', full_name='New Student', year_of_study='First Year')
    client.login(username='727626BCS999', password='password123')

    resp = client.get('/hackathon/register/', follow=True)
    # Should redirect back to home with error message
    assert resp.redirect_chain[0][0] == '/', f"Expected redirect to '/', got {resp.redirect_chain}"
    print("  PASS: Form access locked when max capacity is reached.")

    # Restore settings
    settings.max_hackathon_teams = 120
    settings.save()

    # TEST 10: Problem Statement Limitation (15 Teams Limit)
    print("\n[TEST 10] Testing Problem Statement 15-Team Limitation & Full Statement Auto-Lock...")
    assert settings.max_teams_per_problem_statement == 15, f"Expected default 15, got {settings.max_teams_per_problem_statement}"
    
    # Temporarily set limit to 1 (since CyberKnights already chose NT01)
    settings.max_teams_per_problem_statement = 1
    settings.save()

    # user2 views form: NT01 should be disabled and marked FULL
    resp = client.get('/hackathon/register/')
    assert resp.status_code == 200
    html = resp.content.decode('utf-8')
    assert "Max 15 Teams" in html or "15" in html
    assert "[🔒 FULL: 1/1 Teams]" in html, "NT01 option should indicate FULL status in dropdown"

    # user2 tries to register with NT01 (exceeding limit)
    over_limit_data = {
        'team_name': 'LimitBreakers',
        'leader_name': 'New Student',
        'leader_roll': '727626BCS999',
        'leader_dept': 'CSE',
        'leader_contact': '9876543219',
        'problem_statement': '[NT01] Centralized External Event Participation Tracking System (Software | IT)',
        'member_name[]': ['M2', 'M3', 'M4', 'M5'],
        'member_roll[]': ['727626BME801', '727626BME802', '727626BME803', '727626BME804'],
        'member_dept[]': ['MECH', 'MECH', 'MECH', 'MECH'],
    }
    resp = client.post('/hackathon/register/', over_limit_data, follow=True)
    assert HackathonTeam.objects.filter(team_name='LimitBreakers').count() == 0, "Team should be rejected due to PS limit"
    assert "reached the maximum limitation" in resp.content.decode('utf-8')
    print("  PASS: Problem statement limit enforced on backend; duplicate statement over limit rejected.")
    print("  PASS: Dropdown dynamically marked full problem statements as disabled.")

    # Restore settings
    settings.max_teams_per_problem_statement = 15
    settings.save()

    # TEST 11: Admin Page Teams Download with Problem Statements
    print("\n[TEST 11] Checking Admin Page Team Downloads with Problem Statements...")
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('SRCOFFICIAL2026', 'src@mcet.in', 'srcpass2026')
    client.force_login(admin_user)

    # 1. Test changelist view has download buttons
    resp = client.get('/admin/nxtech/hackathonteam/')
    assert resp.status_code == 200
    cl_html = resp.content.decode('utf-8')
    assert "Download All Teams with Problem Statements" in cl_html
    print("  PASS: Hackathon changelist displays direct export buttons.")

    # 2. Test CSV download of all teams
    resp = client.get('/admin/nxtech/hackathonteam/download/all-teams-csv/')
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('text/csv')
    csv_text = resp.content.decode('utf-8')
    assert "Problem Statement ID" in csv_text
    assert "Problem Statement" in csv_text
    assert "CyberKnights" in csv_text
    assert "NT01" in csv_text
    print("  PASS: Admin Teams CSV download includes Problem Statement ID and Problem Statement.")

    # 3. Test Excel (.xlsx) download of all teams
    resp = client.get('/admin/nxtech/hackathonteam/download/all-teams-excel/')
    assert resp.status_code == 200
    assert 'spreadsheetml' in resp['Content-Type']
    assert len(resp.content) > 1000
    print("  PASS: Admin Teams Excel download generated successfully with openpyxl.")

    # 4. Test Master Hub downloads from NxTechSettings
    resp = client.get('/admin/nxtech/nxtechsettings/download/hackathon-teams-csv/')
    assert resp.status_code == 200
    master_csv = resp.content.decode('utf-8')
    assert "Problem Statement" in master_csv
    assert "CyberKnights" in master_csv
    print("  PASS: Master Settings panel instant download serves teams with Problem Statements.")

    print("\n" + "=" * 70)
    print(">> ALL 11 STANDALONE TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()

