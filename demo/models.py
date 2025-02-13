from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_choices_field.fields import TextChoicesField

from strawberry_django_plus.descriptors import model_property

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

User = get_user_model()


class Project(models.Model):
    milestones: "RelatedManager[Milestone]"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.BigAutoField(  # noqa: A003
        verbose_name="ID",
        primary_key=True,
    )
    status = TextChoicesField(
        help_text=_("This project's status"),
        choices_enum=Status,
        default=Status.ACTIVE,
    )
    name = models.CharField(
        help_text="The name of the project",
        max_length=255,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        default=None,
    )
    cost = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
    )


class Milestone(models.Model):
    issues: "RelatedManager[Issue]"

    id = models.BigAutoField(  # noqa: A003
        verbose_name="ID",
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        default=None,
    )
    project_id: int
    project = models.ForeignKey[Project](
        Project,
        on_delete=models.CASCADE,
        related_name="milestones",
        related_query_name="milestone",
    )


class Issue(models.Model):
    comments: "RelatedManager[Issue]"
    issue_assignees: "RelatedManager[Assignee]"

    class Kind(models.TextChoices):
        BUG = "b", "Bug"
        FEATURE = "f", "Feature"

    id = models.BigAutoField(  # noqa: A003
        verbose_name="ID",
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
    )
    kind = models.CharField(
        verbose_name="kind",
        help_text="the kind of the issue",
        choices=Kind.choices,
        max_length=max(len(k.value) for k in Kind),
        default=None,
        blank=True,
        null=True,
    )
    priority = models.IntegerField(
        default=0,
    )
    milestone_id: Optional[int]
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.SET_NULL,
        related_name="issues",
        related_query_name="issue",
        null=True,
        blank=True,
        default=None,
    )
    tags = models.ManyToManyField["Tag", Any](
        "Tag",
        related_name="issues",
        related_query_name="issue",
    )
    assignees = models.ManyToManyField["User", "Assignee"](
        User,
        through="Assignee",
        related_name="+",
    )

    @property
    def name_with_kind(self) -> str:
        return f"{self.kind}: {self.name}"

    @model_property(only=["kind", "priority"])
    def name_with_priority(self) -> str:
        """Field doc."""
        return f"{self.kind}: {self.priority}"


class Assignee(models.Model):
    issues: "RelatedManager[Issue]"

    id = models.BigAutoField(  # noqa: A003
        verbose_name="ID",
        primary_key=True,
    )
    issue_id: int
    issue = models.ForeignKey[Issue](
        Issue,
        on_delete=models.CASCADE,
        related_name="issue_assignees",
        related_query_name="issue_assignee",
    )
    user_id: int
    user = models.ForeignKey[User](
        User,
        on_delete=models.CASCADE,
        related_name="issue_assignees",
        related_query_name="issue_assignee",
    )
    owner = models.BooleanField(
        default=False,
    )


class Tag(models.Model):
    issues: "RelatedManager[Issue]"

    id = models.BigAutoField(  # noqa: A003
        verbose_name="ID",
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
    )
