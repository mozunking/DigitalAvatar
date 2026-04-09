"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-08 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "avatars",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_avatars_user_id", "avatars", ["user_id"], unique=False)

    op.create_table(
        "personas",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_personas_avatar_id", "personas", ["avatar_id"], unique=False)

    op.create_table(
        "agents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role_prompt", sa.Text(), nullable=False),
        sa.Column("permissions", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_agents_avatar_id", "agents", ["avatar_id"], unique=False)
    op.create_index("ix_agents_status", "agents", ["status"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("agent_id", sa.String(length=36), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tasks_avatar_id", "tasks", ["avatar_id"], unique=False)
    op.create_index("ix_tasks_agent_id", "tasks", ["agent_id"], unique=False)
    op.create_index("ix_tasks_trace_id", "tasks", ["trace_id"], unique=False)
    op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("ix_tasks_created_at", "tasks", ["created_at"], unique=False)

    op.create_table(
        "memories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("task_id", sa.String(length=36), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("sensitivity", sa.String(length=20), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_ref_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_memories_avatar_id", "memories", ["avatar_id"], unique=False)
    op.create_index("ix_memories_task_id", "memories", ["task_id"], unique=False)
    op.create_index("ix_memories_type", "memories", ["type"], unique=False)
    op.create_index("ix_memories_state", "memories", ["state"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("request_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("policy_hits", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("hash_prev", sa.String(length=64), nullable=True),
        sa.Column("hash_self", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_trace_id", "audit_logs", ["trace_id"], unique=False)
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_resource_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_trace_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_memories_state", table_name="memories")
    op.drop_index("ix_memories_type", table_name="memories")
    op.drop_index("ix_memories_task_id", table_name="memories")
    op.drop_index("ix_memories_avatar_id", table_name="memories")
    op.drop_table("memories")
    op.drop_index("ix_tasks_created_at", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_trace_id", table_name="tasks")
    op.drop_index("ix_tasks_agent_id", table_name="tasks")
    op.drop_index("ix_tasks_avatar_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_agents_status", table_name="agents")
    op.drop_index("ix_agents_avatar_id", table_name="agents")
    op.drop_table("agents")
    op.drop_index("ix_personas_avatar_id", table_name="personas")
    op.drop_table("personas")
    op.drop_index("ix_avatars_user_id", table_name="avatars")
    op.drop_table("avatars")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
