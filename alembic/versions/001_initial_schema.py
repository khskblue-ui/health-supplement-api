"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. competitors                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "competitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_short", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_competitors_id", "competitors", ["id"])

    # ------------------------------------------------------------------ #
    # 2. competitor_licenses                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        "competitor_licenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("license_no", sa.String(50), nullable=False),
        sa.Column("plant_name", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_competitor_licenses_id", "competitor_licenses", ["id"])
    op.create_index(
        "ix_competitor_licenses_competitor_id",
        "competitor_licenses",
        ["competitor_id"],
    )
    op.create_index(
        "ix_competitor_licenses_license_no", "competitor_licenses", ["license_no"]
    )

    # ------------------------------------------------------------------ #
    # 3. product_registrations                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "product_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("license_id", sa.Integer(), nullable=True),
        sa.Column("license_no", sa.String(50), nullable=False),
        sa.Column("report_no", sa.String(50), nullable=False),
        sa.Column("product_name", sa.String(500), nullable=False),
        sa.Column("report_date", sa.String(8), nullable=True),
        sa.Column("change_date", sa.String(8), nullable=True),
        sa.Column("functionality", sa.Text(), nullable=True),
        sa.Column("raw_material", sa.Text(), nullable=True),
        sa.Column("raw_material_detail", sa.Text(), nullable=True),
        sa.Column(
            "traceability_registered",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("traceability_reg_num", sa.String(100), nullable=True),
        sa.Column("traceability_barcode", sa.String(100), nullable=True),
        sa.Column("traceability_mod_dt", sa.String(8), nullable=True),
        sa.Column("hfood_yn", sa.String(1), nullable=True),
        sa.Column("source_api", sa.String(10), nullable=False, server_default="I0030"),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"]),
        sa.ForeignKeyConstraint(["license_id"], ["competitor_licenses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_no", "report_no", name="uq_license_report"),
    )
    op.create_index(
        "ix_product_registrations_id", "product_registrations", ["id"]
    )
    op.create_index(
        "ix_product_registrations_competitor_id",
        "product_registrations",
        ["competitor_id"],
    )
    op.create_index(
        "ix_product_registrations_license_no",
        "product_registrations",
        ["license_no"],
    )
    op.create_index(
        "ix_product_registrations_report_no",
        "product_registrations",
        ["report_no"],
    )
    op.create_index(
        "ix_product_registrations_change_date",
        "product_registrations",
        ["change_date"],
    )

    # ------------------------------------------------------------------ #
    # 4. collection_jobs                                                   #
    # ------------------------------------------------------------------ #
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
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_collection_jobs_id", "collection_jobs", ["id"])

    # ------------------------------------------------------------------ #
    # 5. production_records                                                #
    # ------------------------------------------------------------------ #
    op.create_table(
        "production_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("license_no", sa.String(50), nullable=False),
        sa.Column("product_name", sa.String(500), nullable=False),
        sa.Column("product_type", sa.String(200), nullable=True),
        sa.Column("report_year", sa.String(4), nullable=False),
        sa.Column("production_qty_kg", sa.Float(), nullable=True),
        sa.Column("production_capacity_kg", sa.Float(), nullable=True),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "license_no", "product_name", "report_year", name="uq_production_record"
        ),
    )
    op.create_index("ix_production_records_id", "production_records", ["id"])
    op.create_index(
        "ix_production_records_competitor_id",
        "production_records",
        ["competitor_id"],
    )
    op.create_index(
        "ix_production_records_license_no", "production_records", ["license_no"]
    )
    op.create_index(
        "ix_production_records_report_year", "production_records", ["report_year"]
    )

    # ------------------------------------------------------------------ #
    # 6. Materialized Views                                                #
    # ------------------------------------------------------------------ #
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_registrations AS
        SELECT
            competitor_id,
            LEFT(change_date, 6)           AS year_month,   -- YYYYMM
            COUNT(*)                        AS registration_count,
            COUNT(*) FILTER (
                WHERE traceability_registered = TRUE
            )                               AS traceability_count
        FROM product_registrations
        WHERE change_date IS NOT NULL
          AND LENGTH(change_date) = 8
        GROUP BY competitor_id, LEFT(change_date, 6)
        ORDER BY competitor_id, year_month
        WITH DATA;
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_monthly
        ON mv_monthly_registrations (competitor_id, year_month);
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_yearly_registrations AS
        SELECT
            competitor_id,
            LEFT(change_date, 4)           AS report_year,
            COUNT(*)                        AS registration_count,
            COUNT(*) FILTER (
                WHERE traceability_registered = TRUE
            )                               AS traceability_count,
            COUNT(DISTINCT license_no)      AS distinct_licenses
        FROM product_registrations
        WHERE change_date IS NOT NULL
          AND LENGTH(change_date) = 8
        GROUP BY competitor_id, LEFT(change_date, 4)
        ORDER BY competitor_id, report_year
        WITH DATA;
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_yearly
        ON mv_yearly_registrations (competitor_id, report_year);
        """
    )

    # ------------------------------------------------------------------ #
    # 7. 시드 데이터: competitors 4개사                                     #
    # ------------------------------------------------------------------ #
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

    # ------------------------------------------------------------------ #
    # 8. 시드 데이터: competitor_licenses (대표 허가번호 1개씩)            #
    # 실제 LCNS_NO는 식품안전나라 업체조회에서 확인 후 업데이트 필요       #
    # 나머지 공장 라이선스는 초기 적재 시 자동 추가되도록 구성             #
    # ------------------------------------------------------------------ #
    op.execute(
        """
        INSERT INTO competitor_licenses (competitor_id, license_no, plant_name, is_active)
        SELECT c.id,
               CASE c.name_short
                   WHEN '노바렉스'      THEN '14-경북-0001'
                   WHEN '콜마BNH'       THEN '14-충북-0002'
                   WHEN '코스맥스바이오' THEN '14-경기-0003'
                   WHEN '코스맥스NBT'   THEN '14-인천-0004'
                   ELSE '14-기타-' || LPAD(c.id::text, 4, '0')
               END,
               c.name || ' 본사공장',
               TRUE
        FROM competitors c
        ON CONFLICT DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_yearly_registrations;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_registrations;")
    op.drop_table("production_records")
    op.drop_table("collection_jobs")
    op.drop_table("product_registrations")
    op.drop_table("competitor_licenses")
    op.drop_table("competitors")
