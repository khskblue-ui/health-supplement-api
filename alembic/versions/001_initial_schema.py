"""initial schema (I0320 MVP)

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------- #
    # 1. competitors                                                   #
    # -------------------------------------------------------------- #
    op.create_table(
        "competitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_short", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_competitors_id", "competitors", ["id"])

    # -------------------------------------------------------------- #
    # 2. product_registrations (I0320 fields)                         #
    # -------------------------------------------------------------- #
    op.create_table(
        "product_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("prdlst_report_no", sa.String(30), nullable=False),
        sa.Column("product_name", sa.String(500), nullable=True),
        sa.Column("product_type", sa.String(100), nullable=True),
        sa.Column("food_type", sa.String(20), nullable=True),
        sa.Column("btype", sa.String(100), nullable=True),
        sa.Column("brnch_nm", sa.String(200), nullable=True),
        sa.Column("mnft_day", sa.String(8), nullable=True),
        sa.Column("crcl_prd", sa.String(8), nullable=True),
        sa.Column("mod_dt", sa.String(8), nullable=True),
        sa.Column("reg_num", sa.String(50), nullable=True),
        sa.Column("food_histrace_num", sa.String(50), nullable=True),
        sa.Column("barcode", sa.String(100), nullable=True),
        sa.Column("source_api", sa.String(10), nullable=False, server_default="I0320"),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("food_histrace_num", name="uq_histrace_num"),
    )
    op.create_index("ix_product_registrations_id", "product_registrations", ["id"])
    op.create_index("ix_product_registrations_competitor_id", "product_registrations", ["competitor_id"])
    op.create_index("ix_product_registrations_prdlst_report_no", "product_registrations", ["prdlst_report_no"])
    op.create_index("ix_product_registrations_mod_dt", "product_registrations", ["mod_dt"])
    op.create_index("ix_product_registrations_food_histrace_num", "product_registrations", ["food_histrace_num"])

    # -------------------------------------------------------------- #
    # 3. collection_jobs                                               #
    # -------------------------------------------------------------- #
    op.create_table(
        "collection_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(20), nullable=False),
        sa.Column("source_api", sa.String(10), nullable=False),
        sa.Column("target_date", sa.String(8), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("records_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_collection_jobs_id", "collection_jobs", ["id"])

    # -------------------------------------------------------------- #
    # 4. 시드 데이터: 4개 경쟁사                                       #
    # -------------------------------------------------------------- #
    op.execute(
        """
        INSERT INTO competitors (name, name_short) VALUES
            ('노바렉스',       '노바렉스'),
            ('콜마비앤에이치', '콜마BNH'),
            ('코스맥스바이오', '코스맥스바이오'),
            ('코스맥스엔비티', '코스맥스NBT')
        ON CONFLICT (name) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_table("collection_jobs")
    op.drop_table("product_registrations")
    op.drop_table("competitors")
