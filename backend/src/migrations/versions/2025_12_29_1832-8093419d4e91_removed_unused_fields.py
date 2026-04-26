"""initial virtualmedic schema

Revision ID: 8093419d4e91
Revises:
Create Date: 2026-03-08 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8093419d4e91"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum = postgresql.ENUM("superuser", "admin", "patient", "doctor", name="user_role", create_type=False)
    user_role_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=True),
        sa.Column("last_name", sa.String(length=120), nullable=True),
        sa.Column("role", user_role_enum, server_default="patient", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_verified_doctor", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "specializations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_specializations")),
        sa.UniqueConstraint("name", name=op.f("uq_specializations_name")),
    )
    op.create_index(op.f("ix_specializations_name"), "specializations", ["name"], unique=True)

    op.create_table(
        "doctor_specializations",
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("specialization_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["doctor_id"], ["users.id"], name=op.f("fk_doctor_specializations_doctor_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["specialization_id"],
            ["specializations.id"],
            name=op.f("fk_doctor_specializations_specialization_id_specializations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("doctor_id", "specialization_id", name=op.f("pk_doctor_specializations")),
    )

    op.create_table(
        "doctor_qualification_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("stored_file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["users.id"],
            name=op.f("fk_doctor_qualification_documents_doctor_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_doctor_qualification_documents")),
        sa.UniqueConstraint("stored_file_name", name=op.f("uq_doctor_qualification_documents_stored_file_name")),
        sa.UniqueConstraint("doctor_id", "sha256", name="uq_doctor_document_sha256"),
    )
    op.create_index(
        op.f("ix_doctor_qualification_documents_doctor_id"),
        "doctor_qualification_documents",
        ["doctor_id"],
        unique=False,
    )

    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_refresh_sessions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_sessions")),
        sa.UniqueConstraint("jti", name=op.f("uq_refresh_sessions_jti")),
    )
    op.create_index(op.f("ix_refresh_sessions_jti"), "refresh_sessions", ["jti"], unique=True)
    op.create_index(op.f("ix_refresh_sessions_user_id"), "refresh_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_refresh_sessions_expires_at"), "refresh_sessions", ["expires_at"], unique=False)
    op.create_index(
        "ix_refresh_sessions_user_revoked",
        "refresh_sessions",
        ["user_id", "revoked_at"],
        unique=False,
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name=op.f("fk_questions_author_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questions")),
    )
    op.create_index(op.f("ix_questions_author_id"), "questions", ["author_id"], unique=False)

    op.create_table(
        "question_comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.String(length=2000), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name=op.f("fk_question_comments_question_id_questions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name=op.f("fk_question_comments_author_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_comments")),
    )
    op.create_index(op.f("ix_question_comments_question_id"), "question_comments", ["question_id"], unique=False)
    op.create_index(op.f("ix_question_comments_author_id"), "question_comments", ["author_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    user_role_enum = postgresql.ENUM("superuser", "admin", "patient", "doctor", name="user_role", create_type=False)

    op.drop_index(op.f("ix_question_comments_author_id"), table_name="question_comments")
    op.drop_index(op.f("ix_question_comments_question_id"), table_name="question_comments")
    op.drop_table("question_comments")

    op.drop_index(op.f("ix_questions_author_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index("ix_refresh_sessions_user_revoked", table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_expires_at"), table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_user_id"), table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_jti"), table_name="refresh_sessions")
    op.drop_table("refresh_sessions")

    op.drop_index(op.f("ix_doctor_qualification_documents_doctor_id"), table_name="doctor_qualification_documents")
    op.drop_table("doctor_qualification_documents")

    op.drop_table("doctor_specializations")

    op.drop_index(op.f("ix_specializations_name"), table_name="specializations")
    op.drop_table("specializations")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")

    user_role_enum.drop(bind, checkfirst=True)
