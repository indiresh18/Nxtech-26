from django.db import models
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class User(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    year_of_study = models.CharField(max_length=20, default="First Year")

    def __str__(self):
        return f"{self.username} ({self.full_name or self.username})"


class HackathonTeam(models.Model):
    team_name = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100)
    leader_roll = models.CharField(max_length=30)
    leader_dept = models.CharField(max_length=50)
    leader_email = models.EmailField(blank=True, null=True)
    leader_contact = models.CharField(max_length=20, blank=True, null=True)
    leader_year = models.CharField(max_length=20, default="First Year")
    problem_statement = models.CharField(max_length=150)
    problem_statement_detail = models.TextField(blank=True, null=True)
    registered_by_user = models.CharField(max_length=150, help_text="Roll number / username who submitted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NxTech Hackathon Team"
        verbose_name_plural = "NxTech Hackathon Teams"
        ordering = ['-created_at']

    @property
    def export_team_name(self):
        roll = (self.leader_roll or "").strip().upper()
        name = (self.team_name or "").strip()
        if not roll:
            return name
        if roll in name.upper():
            return name
        return f"{name} ({roll})"

    def __str__(self):
        return f"[Hackathon] {self.team_name} (Lead: {self.leader_name} - {self.leader_roll})"


class HackathonMember(models.Model):
    team = models.ForeignKey(HackathonTeam, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=30)
    dept = models.CharField(max_length=50)
    is_leader = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NxTech Hackathon Member"
        verbose_name_plural = "NxTech Hackathon Members"

    def __str__(self):
        return f"{self.name} ({self.roll} - {self.dept})"


class FailureAnalysisTeam(models.Model):
    team_name = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100)
    leader_roll = models.CharField(max_length=30)
    leader_dept = models.CharField(max_length=50)
    leader_email = models.EmailField(blank=True, null=True)
    leader_contact = models.CharField(max_length=20, blank=True, null=True)
    leader_year = models.CharField(max_length=20, default="First Year")
    topic = models.CharField(max_length=200, blank=True, default="Forensic Engineering Case Defense")
    registered_by_user = models.CharField(max_length=150, help_text="Roll number / username who submitted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NxTech Failure Analysis Team"
        verbose_name_plural = "NxTech Failure Analysis Teams"
        ordering = ['-created_at']

    @property
    def export_team_name(self):
        roll = (self.leader_roll or "").strip().upper()
        name = (self.team_name or "").strip()
        if not roll:
            return name
        if roll in name.upper():
            return name
        return f"{name} ({roll})"

    def __str__(self):
        return f"[Failure Analysis] {self.team_name} (Lead: {self.leader_name} - {self.leader_roll})"


class FailureAnalysisMember(models.Model):
    team = models.ForeignKey(FailureAnalysisTeam, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=30)
    dept = models.CharField(max_length=50)
    is_leader = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NxTech Failure Analysis Member"
        verbose_name_plural = "NxTech Failure Analysis Members"

    def __str__(self):
        return f"{self.name} ({self.roll} - {self.dept})"


class NxTechSettings(models.Model):
    hackathon_registration_open = models.BooleanField(
        default=True,
        verbose_name="Hackathon Registration Open"
    )
    failure_analysis_registration_open = models.BooleanField(
        default=True,
        verbose_name="Failure Analysis Registration Open"
    )
    max_hackathon_teams = models.PositiveIntegerField(
        default=120,
        verbose_name="Max Hackathon Teams Limit"
    )
    max_teams_per_problem_statement = models.PositiveIntegerField(
        default=15,
        verbose_name="Max Teams Per Problem Statement"
    )
    max_fa_teams = models.PositiveIntegerField(
        default=120,
        verbose_name="Max Failure Analysis Teams Limit"
    )
    hackathon_closed_message = models.CharField(
        max_length=255,
        default="Registration for NxTech Hackathon is currently closed.",
        blank=True
    )
    failure_analysis_closed_message = models.CharField(
        max_length=255,
        default="Registration for NxTech Failure Analysis is currently closed.",
        blank=True
    )

    class Meta:
        verbose_name = "NxTech Registration Control & Limits"
        verbose_name_plural = "NxTech Registration Control & Limits"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"NxTech Master Controls [Hackathon: {'OPEN' if self.hackathon_registration_open else 'CLOSED'}, FA: {'OPEN' if self.failure_analysis_registration_open else 'CLOSED'}]"

