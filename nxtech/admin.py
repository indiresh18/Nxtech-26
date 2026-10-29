import csv
import io
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages

from .models import (
    Department, User,
    HackathonTeam, HackathonMember,
    FailureAnalysisTeam, FailureAnalysisMember,
    NxTechSettings
)


def extract_problem_statement_id(statement_str):
    if not statement_str:
        return ""
    match = re.search(r'\b(NT\d{1,2})\b', str(statement_str), re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return str(statement_str).strip()


def generate_csv_response(filename, headers, rows):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response


def generate_excel_response(filename, sheet_title, headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]

    header_fill = PatternFill(start_color="4A154B", end_color="4A154B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10)
    thin_border = Border(
        left=Side(style='thin', color='D3D3D3'),
        right=Side(style='thin', color='D3D3D3'),
        top=Side(style='thin', color='D3D3D3'),
        bottom=Side(style='thin', color='D3D3D3')
    )
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border

    for r_idx, row in enumerate(rows, start=2):
        ws.append(row)
        for col_idx in range(1, len(row) + 1):
            cell = ws.cell(row=r_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx in (1, 3, 4, 5, 11, 12):
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'department', 'year_of_study', 'email', 'is_staff')
    list_filter = ('department', 'year_of_study', 'is_staff')
    search_fields = ('username', 'full_name', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Student Information', {'fields': ('full_name', 'department', 'phone', 'year_of_study')}),
    )


class ProblemStatementFilter(admin.SimpleListFilter):
    title = 'Problem Statement'
    parameter_name = 'problem_statement_code'

    def lookups(self, request, model_admin):
        from .problem_statements import HACKATHON_PROBLEM_STATEMENTS
        return [(item['ps_id'], f"[{item['ps_id']}] {item['title'][:40]}") for item in HACKATHON_PROBLEM_STATEMENTS]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(problem_statement__icontains=self.value())
        return queryset


def build_hackathon_teams_export(queryset):
    headers = [
        "S.No",
        "Team ID",
        "Team Name",
        "Leader Roll",
        "Problem Statement ID",
        "Problem Statement",
        "Problem Statement Description",
        "Leader Name",
        "Leader Dept",
        "Leader Contact",
        "Leader Email",
        "Members Count",
        "Team Members Roster",
        "Registered At"
    ]
    rows = []
    for idx, t in enumerate(queryset.prefetch_related('members'), start=1):
        ps = t.problem_statement or ""
        ps_id = extract_problem_statement_id(ps)
        members_list = ", ".join([
            f"{m.name} ({m.roll} - {m.dept})" + (" [Lead]" if m.is_leader else "")
            for m in t.members.all()
        ])
        rows.append([
            idx,
            t.id,
            t.export_team_name,
            t.leader_roll,
            ps_id,
            ps,
            t.problem_statement_detail or ps,
            t.leader_name,
            t.leader_dept,
            t.leader_contact or "",
            t.leader_email or "",
            t.members.count(),
            members_list,
            t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else ""
        ])
    return headers, rows


class HackathonMemberInline(admin.TabularInline):
    model = HackathonMember
    extra = 0
    fields = ('name', 'roll', 'dept', 'is_leader', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(HackathonTeam)
class HackathonTeamAdmin(admin.ModelAdmin):
    change_list_template = "admin/nxtech/hackathonteam/change_list.html"
    list_display = (
        'display_team_name', 'display_problem_statement', 'leader_name', 'leader_roll',
        'leader_dept', 'leader_contact', 'team_size', 'created_at'
    )
    search_fields = ('team_name', 'leader_name', 'leader_roll', 'leader_dept', 'problem_statement')
    list_filter = (ProblemStatementFilter, 'leader_dept', 'created_at')
    inlines = [HackathonMemberInline]
    actions = ['export_teams_csv', 'export_teams_excel']

    def display_team_name(self, obj):
        return format_html(
            f"<strong>{obj.team_name}</strong> <span style='color: #64748B; font-size: 11px; font-family: monospace;'>({obj.leader_roll})</span>"
        )
    display_team_name.short_description = "Team Name (Leader Roll)"

    def display_problem_statement(self, obj):
        ps = obj.problem_statement or "-"
        ps_id = extract_problem_statement_id(ps)
        if ps_id:
            return format_html(
                '<span style="padding: 2px 7px; background: #7C1A7E; color: white; border-radius: 5px; font-weight: bold; font-size: 11px; margin-right: 5px;">{}</span>'
                '<span style="font-size: 12px; color: #1E293B; font-weight: 500;">{}</span>',
                ps_id,
                ps[:55] + ("..." if len(ps) > 55 else "")
            )
        return ps
    display_problem_statement.short_description = "Problem Statement"

    def team_size(self, obj):
        count = obj.members.count()
        return format_html(f"<strong>{count}</strong> members")
    team_size.short_description = "Squad Size"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download/all-teams-excel/', self.admin_site.admin_view(self.view_download_all_teams_excel), name='hackathon_all_teams_excel'),
            path('download/all-teams-csv/', self.admin_site.admin_view(self.view_download_all_teams_csv), name='hackathon_all_teams_csv'),
        ]
        return custom_urls + urls

    def view_download_all_teams_excel(self, request):
        queryset = HackathonTeam.objects.all().order_by('-created_at')
        headers, rows = build_hackathon_teams_export(queryset)
        filename = f"NxTech26_Hackathon_Teams_With_Statements_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return generate_excel_response(filename, "Hackathon Teams", headers, rows)

    def view_download_all_teams_csv(self, request):
        queryset = HackathonTeam.objects.all().order_by('-created_at')
        headers, rows = build_hackathon_teams_export(queryset)
        filename = f"NxTech26_Hackathon_Teams_With_Statements_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        return generate_csv_response(filename, headers, rows)

    @admin.action(description="⬇ Export Selected Teams with Problem Statements to CSV")
    def export_teams_csv(self, request, queryset):
        headers, rows = build_hackathon_teams_export(queryset)
        return generate_csv_response(f"nxtech_hackathon_teams_{timezone.now().strftime('%Y%m%d_%H%M')}.csv", headers, rows)

    @admin.action(description="⬇ Export Selected Teams with Problem Statements to Excel (.xlsx)")
    def export_teams_excel(self, request, queryset):
        headers, rows = build_hackathon_teams_export(queryset)
        return generate_excel_response(f"nxtech_hackathon_teams_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx", "Hackathon Teams", headers, rows)


@admin.register(HackathonMember)
class HackathonMemberAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'roll', 'dept', 'role_badge', 'team_link',
        'problem_track', 'leader_contact_info', 'created_at'
    )
    list_filter = ('is_leader', 'dept', 'created_at')
    search_fields = ('name', 'roll', 'dept', 'team__team_name', 'team__leader_name', 'team__leader_roll')
    actions = ['export_students_csv', 'export_students_excel']

    def role_badge(self, obj):
        if obj.is_leader:
            return format_html('<span style="padding: 3px 8px; background: #7C1A7E; color: white; border-radius: 6px; font-size: 11px; font-weight: bold;">Team Leader</span>')
        return format_html('<span style="padding: 3px 8px; background: #E2E8F0; color: #334155; border-radius: 6px; font-size: 11px;">Member</span>')
    role_badge.short_description = "Role"

    def team_link(self, obj):
        return obj.team.export_team_name
    team_link.short_description = "Team Name"

    def problem_track(self, obj):
        track = obj.team.problem_statement or ""
        return track[:35] + "..." if len(track) > 35 else track
    problem_track.short_description = "Problem Statement"

    def leader_contact_info(self, obj):
        return obj.team.leader_contact or "-"
    leader_contact_info.short_description = "Leader Phone"

    @admin.action(description="⬇ Export Selected Students to CSV")
    def export_students_csv(self, request, queryset):
        headers = ["S.No", "Student Name", "Roll Number", "Department", "Role", "Team Name", "Problem Statement ID", "Problem Statement", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        rows = [
            [idx, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.export_team_name, extract_problem_statement_id(m.team.problem_statement), m.team.problem_statement, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(queryset, start=1)
        ]
        return generate_csv_response(f"nxtech_hackathon_students_{timezone.now().strftime('%Y%m%d_%H%M')}.csv", headers, rows)

    @admin.action(description="⬇ Export Selected Students to Excel (.xlsx)")
    def export_students_excel(self, request, queryset):
        headers = ["S.No", "Student Name", "Roll Number", "Department", "Role", "Team Name", "Problem Statement ID", "Problem Statement", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        rows = [
            [idx, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.export_team_name, extract_problem_statement_id(m.team.problem_statement), m.team.problem_statement, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(queryset, start=1)
        ]
        return generate_excel_response(f"nxtech_hackathon_students_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx", "Hackathon Students", headers, rows)


class FailureAnalysisMemberInline(admin.TabularInline):
    model = FailureAnalysisMember
    extra = 0
    fields = ('name', 'roll', 'dept', 'is_leader', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(FailureAnalysisTeam)
class FailureAnalysisTeamAdmin(admin.ModelAdmin):
    list_display = (
        'display_team_name', 'leader_name', 'leader_roll', 'leader_dept',
        'leader_contact', 'team_size', 'created_at'
    )
    search_fields = ('team_name', 'leader_name', 'leader_roll', 'leader_dept')
    list_filter = ('leader_dept', 'created_at')
    inlines = [FailureAnalysisMemberInline]
    actions = ['export_teams_csv', 'export_teams_excel']

    def display_team_name(self, obj):
        return format_html(
            f"<strong>{obj.team_name}</strong> <span style='color: #64748B; font-size: 11px; font-family: monospace;'>({obj.leader_roll})</span>"
        )
    display_team_name.short_description = "Team Name (Leader Roll)"

    def team_size(self, obj):
        count = obj.members.count()
        return format_html(f"<strong>{count}</strong> members")
    team_size.short_description = "Squad Size"

    @admin.action(description="⬇ Export Selected Teams to CSV")
    def export_teams_csv(self, request, queryset):
        headers = ["Team ID", "Team Name", "Leader Name", "Leader Roll", "Leader Dept", "Leader Contact", "Leader Email", "Members Count", "Registered At"]
        rows = [
            [t.id, t.export_team_name, t.leader_name, t.leader_roll, t.leader_dept, t.leader_contact or "", t.leader_email or "", t.members.count(), t.created_at.strftime("%Y-%m-%d %H:%M")]
            for t in queryset
        ]
        return generate_csv_response(f"nxtech_fa_teams_{timezone.now().strftime('%Y%m%d_%H%M')}.csv", headers, rows)

    @admin.action(description="⬇ Export Selected Teams to Excel (.xlsx)")
    def export_teams_excel(self, request, queryset):
        headers = ["Team ID", "Team Name", "Leader Name", "Leader Roll", "Leader Dept", "Leader Contact", "Leader Email", "Members Count", "Registered At"]
        rows = [
            [t.id, t.export_team_name, t.leader_name, t.leader_roll, t.leader_dept, t.leader_contact or "", t.leader_email or "", t.members.count(), t.created_at.strftime("%Y-%m-%d %H:%M")]
            for t in queryset
        ]
        return generate_excel_response(f"nxtech_fa_teams_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx", "Failure Analysis Teams", headers, rows)


@admin.register(FailureAnalysisMember)
class FailureAnalysisMemberAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'roll', 'dept', 'role_badge', 'team_link',
        'leader_contact_info', 'created_at'
    )
    list_filter = ('is_leader', 'dept', 'created_at')
    search_fields = ('name', 'roll', 'dept', 'team__team_name', 'team__leader_name', 'team__leader_roll')
    actions = ['export_students_csv', 'export_students_excel']

    def role_badge(self, obj):
        if obj.is_leader:
            return format_html('<span style="padding: 3px 8px; background: #0F172A; color: white; border-radius: 6px; font-size: 11px; font-weight: bold;">Team Leader</span>')
        return format_html('<span style="padding: 3px 8px; background: #E2E8F0; color: #334155; border-radius: 6px; font-size: 11px;">Member</span>')
    role_badge.short_description = "Role"

    def team_link(self, obj):
        return obj.team.export_team_name
    team_link.short_description = "Team Name"

    def leader_contact_info(self, obj):
        return obj.team.leader_contact or "-"
    leader_contact_info.short_description = "Leader Phone"

    @admin.action(description="⬇ Export Selected Students to CSV")
    def export_students_csv(self, request, queryset):
        headers = ["S.No", "Student Name", "Roll Number", "Department", "Role", "Team Name", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        rows = [
            [idx, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.export_team_name, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(queryset, start=1)
        ]
        return generate_csv_response(f"nxtech_fa_students_{timezone.now().strftime('%Y%m%d_%H%M')}.csv", headers, rows)

    @admin.action(description="⬇ Export Selected Students to Excel (.xlsx)")
    def export_students_excel(self, request, queryset):
        headers = ["S.No", "Student Name", "Roll Number", "Department", "Role", "Team Name", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        rows = [
            [idx, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.export_team_name, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(queryset, start=1)
        ]
        return generate_excel_response(f"nxtech_fa_students_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx", "FA Students", headers, rows)


@admin.register(NxTechSettings)
class NxTechSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'control_title',
        'hackathon_badge', 'fa_badge',
        'hackathon_capacity_badge', 'download_hub_actions'
    )
    fieldsets = (
        ("Hackathon Registration Status & Limit", {
            "fields": (
                "hackathon_registration_open",
                "max_hackathon_teams",
                "max_teams_per_problem_statement",
                "hackathon_closed_message"
            ),
            "description": "Control whether Hackathon registrations are open. Auto-locks once reaching 120 teams. Problem statements lock individually once reaching 15 teams."
        }),
        ("Failure Analysis Registration Status & Limit", {
            "fields": (
                "failure_analysis_registration_open",
                "max_fa_teams",
                "failure_analysis_closed_message"
            ),
            "description": "Control whether Failure Analysis registrations are open. Auto-locks once reaching 120 teams."
        }),
    )
    actions = [
        'action_open_both',
        'action_close_both',
        'action_open_hackathon',
        'action_close_hackathon',
        'action_open_fa',
        'action_close_fa'
    ]

    def control_title(self, obj):
        return "NxTech'26 Master Controls"
    control_title.short_description = "System Panel"

    def hackathon_badge(self, obj):
        hack_count = HackathonTeam.objects.count()
        if not obj.hackathon_registration_open:
            return format_html('<span style="padding: 4px 10px; background: #EF4444; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">🔒 CLOSED (Admin)</span>')
        elif hack_count >= obj.max_hackathon_teams:
            return format_html('<span style="padding: 4px 10px; background: #DC2626; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">🔒 FULL (120 Reached)</span>')
        return format_html('<span style="padding: 4px 10px; background: #10B981; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">✓ OPEN</span>')
    hackathon_badge.short_description = "Hackathon Status"

    def fa_badge(self, obj):
        fa_count = FailureAnalysisTeam.objects.count()
        if not obj.failure_analysis_registration_open:
            return format_html('<span style="padding: 4px 10px; background: #EF4444; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">🔒 CLOSED (Admin)</span>')
        elif fa_count >= obj.max_fa_teams:
            return format_html('<span style="padding: 4px 10px; background: #DC2626; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">🔒 FULL (120 Reached)</span>')
        return format_html('<span style="padding: 4px 10px; background: #10B981; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;">✓ OPEN</span>')
    fa_badge.short_description = "Failure Analysis Status"

    def hackathon_capacity_badge(self, obj):
        count = HackathonTeam.objects.count()
        member_count = HackathonMember.objects.count()
        limit = obj.max_hackathon_teams
        pct = round((count / limit * 100), 1) if limit else 0
        color = "#10B981" if count < (limit * 0.8) else ("#F59E0B" if count < limit else "#EF4444")
        return format_html(
            f'<div style="font-size: 12px; font-weight: 700; color: {color};">'
            f'{count} / {limit} Teams ({member_count} Students) [{pct}%]</div>'
        )
    hackathon_capacity_badge.short_description = "Hackathon Capacity"

    def download_hub_actions(self, obj):
        return format_html(
            '<div style="display: flex; flex-direction: column; gap: 6px;">'
            '  <div>'
            '    <a href="/admin/nxtech/hackathonteam/download/all-teams-excel/" style="padding: 4px 10px; background: #7C1A7E; color: white; border-radius: 6px; font-size: 11px; text-decoration: none; font-weight: bold; margin-right: 5px;">🚀 Hackathon Teams & Problem Statements (.xlsx)</a>'
            '    <a href="/admin/nxtech/hackathonteam/download/all-teams-csv/" style="padding: 4px 10px; background: #581C87; color: white; border-radius: 6px; font-size: 11px; text-decoration: none; font-weight: bold;">📄 Teams (.csv)</a>'
            '  </div>'
            '  <div>'
            '    <a href="/admin/nxtech/nxtechsettings/download/all-students-excel/" style="padding: 3px 8px; background: #16A34A; color: white; border-radius: 5px; font-size: 11px; text-decoration: none; font-weight: bold; margin-right: 5px;">📊 All Students (Excel)</a> '
            '    <a href="/admin/nxtech/nxtechsettings/download/all-students-csv/" style="padding: 3px 8px; background: #0284C7; color: white; border-radius: 5px; font-size: 11px; text-decoration: none; font-weight: bold;">📄 All Students (CSV)</a>'
            '  </div>'
            '  <div style="font-size: 10px; color: #64748B;">'
            '    <a href="/admin/nxtech/nxtechsettings/download/hackathon-excel/" style="padding: 2px 6px; background: #6B21A8; color: white; border-radius: 4px; text-decoration: none; margin-right: 4px;">Hackathon Students (.xlsx)</a> '
            '    <a href="/admin/nxtech/nxtechsettings/download/fa-excel/" style="padding: 2px 6px; background: #334155; color: white; border-radius: 4px; text-decoration: none;">Failure Analysis Students (.xlsx)</a>'
            '  </div>'
            '</div>'
        )
    download_hub_actions.short_description = "Instant Master Downloads"

    @admin.action(description="🔓 OPEN Registration for BOTH Competitions")
    def action_open_both(self, request, queryset):
        for s in queryset:
            s.hackathon_registration_open = True
            s.failure_analysis_registration_open = True
            s.save()
        messages.success(request, "Registration has been OPENED for both Hackathon and Failure Analysis.")

    @admin.action(description="🔒 CLOSE Registration for BOTH Competitions")
    def action_close_both(self, request, queryset):
        for s in queryset:
            s.hackathon_registration_open = False
            s.failure_analysis_registration_open = False
            s.save()
        messages.warning(request, "Registration has been CLOSED for both Hackathon and Failure Analysis.")

    @admin.action(description="🔓 OPEN Hackathon Registration")
    def action_open_hackathon(self, request, queryset):
        for s in queryset:
            s.hackathon_registration_open = True
            s.save()
        messages.success(request, "Hackathon registration has been OPENED.")

    @admin.action(description="🔒 CLOSE Hackathon Registration")
    def action_close_hackathon(self, request, queryset):
        for s in queryset:
            s.hackathon_registration_open = False
            s.save()
        messages.warning(request, "Hackathon registration has been CLOSED.")

    @admin.action(description="🔓 OPEN Failure Analysis Registration")
    def action_open_fa(self, request, queryset):
        for s in queryset:
            s.failure_analysis_registration_open = True
            s.save()
        messages.success(request, "Failure Analysis registration has been OPENED.")

    @admin.action(description="🔒 CLOSE Failure Analysis Registration")
    def action_close_fa(self, request, queryset):
        for s in queryset:
            s.failure_analysis_registration_open = False
            s.save()
        messages.warning(request, "Failure Analysis registration has been CLOSED.")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download/hackathon-teams-excel/', self.admin_site.admin_view(self.view_download_hackathon_teams_excel), name='nxtech_download_hackathon_teams_excel'),
            path('download/hackathon-teams-csv/', self.admin_site.admin_view(self.view_download_hackathon_teams_csv), name='nxtech_download_hackathon_teams_csv'),
            path('download/all-students-excel/', self.admin_site.admin_view(self.view_download_all_students_excel), name='nxtech_download_all_excel'),
            path('download/all-students-csv/', self.admin_site.admin_view(self.view_download_all_students_csv), name='nxtech_download_all_csv'),
            path('download/hackathon-excel/', self.admin_site.admin_view(self.view_download_hackathon_excel), name='nxtech_download_hackathon_excel'),
            path('download/hackathon-csv/', self.admin_site.admin_view(self.view_download_hackathon_csv), name='nxtech_download_hackathon_csv'),
            path('download/fa-excel/', self.admin_site.admin_view(self.view_download_fa_excel), name='nxtech_download_fa_excel'),
            path('download/fa-csv/', self.admin_site.admin_view(self.view_download_fa_csv), name='nxtech_download_fa_csv'),
        ]
        return custom_urls + urls

    def view_download_hackathon_teams_excel(self, request):
        queryset = HackathonTeam.objects.all().order_by('-created_at')
        headers, rows = build_hackathon_teams_export(queryset)
        filename = f"NxTech26_Hackathon_Teams_With_Statements_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return generate_excel_response(filename, "Hackathon Teams", headers, rows)

    def view_download_hackathon_teams_csv(self, request):
        queryset = HackathonTeam.objects.all().order_by('-created_at')
        headers, rows = build_hackathon_teams_export(queryset)
        filename = f"NxTech26_Hackathon_Teams_With_Statements_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        return generate_csv_response(filename, headers, rows)

    def _get_all_students_data(self):
        headers = [
            "S.No", "Competition Event", "Team Name", "Student Name", "Roll Number",
            "Department", "Role", "Problem Statement ID", "Problem Statement", "Team Leader Name",
            "Leader Contact", "Leader Email", "Registered Date"
        ]
        rows = []
        counter = 1

        hack_members = HackathonMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        for m in hack_members:
            ps = m.team.problem_statement or ""
            ps_id = extract_problem_statement_id(ps)
            rows.append([
                counter,
                "NxTech Hackathon",
                m.team.export_team_name,
                m.name,
                m.roll,
                m.dept,
                "Team Leader" if m.is_leader else "Member",
                ps_id,
                ps,
                m.team.leader_name,
                m.team.leader_contact or "",
                m.team.leader_email or "",
                m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""
            ])
            counter += 1

        fa_members = FailureAnalysisMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        for m in fa_members:
            rows.append([
                counter,
                "Failure Analysis",
                m.team.export_team_name,
                m.name,
                m.roll,
                m.dept,
                "Team Leader" if m.is_leader else "Member",
                "-",
                m.team.topic or "Forensic Case Defense",
                m.team.leader_name,
                m.team.leader_contact or "",
                m.team.leader_email or "",
                m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""
            ])
            counter += 1

        return headers, rows

    def view_download_all_students_excel(self, request):
        headers, rows = self._get_all_students_data()
        filename = f"NxTech26_All_Registered_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return generate_excel_response(filename, "All Registered Students", headers, rows)

    def view_download_all_students_csv(self, request):
        headers, rows = self._get_all_students_data()
        filename = f"NxTech26_All_Registered_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        return generate_csv_response(filename, headers, rows)

    def view_download_hackathon_excel(self, request):
        headers = ["S.No", "Team Name", "Student Name", "Roll Number", "Department", "Role", "Problem Statement ID", "Problem Statement", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        hack_members = HackathonMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        rows = [
            [idx, m.team.export_team_name, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", extract_problem_statement_id(m.team.problem_statement), m.team.problem_statement, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(hack_members, start=1)
        ]
        filename = f"NxTech26_Hackathon_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return generate_excel_response(filename, "Hackathon Students", headers, rows)

    def view_download_hackathon_csv(self, request):
        headers = ["S.No", "Team Name", "Student Name", "Roll Number", "Department", "Role", "Problem Statement ID", "Problem Statement", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        hack_members = HackathonMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        rows = [
            [idx, m.team.export_team_name, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", extract_problem_statement_id(m.team.problem_statement), m.team.problem_statement, m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(hack_members, start=1)
        ]
        filename = f"NxTech26_Hackathon_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        return generate_csv_response(filename, headers, rows)

    def view_download_fa_excel(self, request):
        headers = ["S.No", "Team Name", "Student Name", "Roll Number", "Department", "Role", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        fa_members = FailureAnalysisMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        rows = [
            [idx, m.team.export_team_name, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(fa_members, start=1)
        ]
        filename = f"NxTech26_Failure_Analysis_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return generate_excel_response(filename, "FA Students", headers, rows)

    def view_download_fa_csv(self, request):
        headers = ["S.No", "Team Name", "Student Name", "Roll Number", "Department", "Role", "Team Leader", "Leader Contact", "Leader Email", "Registered At"]
        fa_members = FailureAnalysisMember.objects.select_related('team').order_by('team__team_name', '-is_leader')
        rows = [
            [idx, m.team.export_team_name, m.name, m.roll, m.dept, "Team Leader" if m.is_leader else "Member", m.team.leader_name, m.team.leader_contact or "", m.team.leader_email or "", m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""]
            for idx, m in enumerate(fa_members, start=1)
        ]
        filename = f"NxTech26_Failure_Analysis_Students_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        return generate_csv_response(filename, headers, rows)

