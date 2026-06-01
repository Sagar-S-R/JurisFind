"""Initial migration: create all JurisFind tables

Creates the following tables:
- users
- document_sessions
- document_chunks
- chat_sessions
- chat_messages

With all required indexes and foreign key constraints.

Revision ID: 0001_initial
Revises: (none)
Create Date: 2026-05-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── document_sessions ──────────────────────────────────────────────────────
    op.create_table(
        "document_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum("uploaded", "retrieved", name="source_type_enum"),
            nullable=False,
        ),
        sa.Column("document_name", sa.String(500), nullable=False),
        sa.Column("blob_path", sa.String(1000), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column(
            "processing_status",
            sa.Enum("pending", "processing", "completed", "failed", name="processing_status_enum"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_document_sessions_user_id", "document_sessions", ["user_id"])
    op.create_index(
        "idx_user_created", "document_sessions", ["user_id", "created_at"]
    )
    op.create_index(
        "idx_processing_status", "document_sessions", ["processing_status"]
    )

    # ── document_chunks ────────────────────────────────────────────────────────
    op.create_table(
        "document_chunks",
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_sessions.session_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_number", sa.Integer, nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("chunk_metadata", sa.JSON, nullable=True),
        sa.Column("embedding_reference", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_document_chunks_session_id", "document_chunks", ["session_id"])
    op.create_index(
        "ix_document_chunks_embedding_ref",
        "document_chunks",
        ["embedding_reference"],
        unique=True,
    )
    op.create_index(
        "idx_session_page", "document_chunks", ["session_id", "page_number"]
    )

    # ── chat_sessions ──────────────────────────────────────────────────────────
    op.create_table(
        "chat_sessions",
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_sessions.session_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_chat_sessions_session_id", "chat_sessions", ["session_id"])
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    # ── chat_messages ──────────────────────────────────────────────────────────
    op.create_table(
        "chat_messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "chat_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chat_sessions.chat_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", name="message_role_enum"),
            nullable=False,
        ),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("retrieved_chunks", sa.JSON, nullable=True),
        sa.Column("llm_response", sa.Text, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_chat_messages_chat_id", "chat_messages", ["chat_id"])
    op.create_index(
        "idx_chat_timestamp", "chat_messages", ["chat_id", "timestamp"]
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("document_chunks")
    op.drop_table("document_sessions")
    op.drop_table("users")

    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS message_role_enum")
    op.execute("DROP TYPE IF EXISTS processing_status_enum")
    op.execute("DROP TYPE IF EXISTS source_type_enum")
