"""
Database Setup & ORM Models for Entebus Server.

This module:
- Configures the SQLAlchemy engine, session factory, and base class.
- Defines ORM models for core entities.
- Provides schema definitions to support authentication, authorization,
  and role-based access control (RBAC).

All ORM models should inherit from `ORMbase`.
"""

from secrets import token_hex
from geoalchemy2 import Geometry
from sqlalchemy import (
    ARRAY,
    TEXT,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
    Index,
    UniqueConstraint,
    create_engine,
    func,
    text,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB

from app.src.constants import (
    PSQL_DB_DRIVER,
    PSQL_DB_HOST,
    PSQL_DB_PASSWORD,
    PSQL_DB_NAME,
    PSQL_DB_PORT,
    PSQL_DB_USERNAME,
)
from app.src.enums import (
    AccountStatus,
    BankAccountType,
    GenderType,
    LandmarkType,
    PlatformType,
    BusinessStatus,
    BusinessType,
    CompanyStatus,
    CompanyType,
    BusStatus,
    TicketingMode,
    TriggeringMode,
    ServiceStatus,
    DutyStatus,
    RouteStatus,
)


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
def get_db_url() -> str:
    """Return a SQLAlchemy-compatible PostgreSQL connection URL."""
    return (
        f"{PSQL_DB_DRIVER}://{PSQL_DB_USERNAME}:{PSQL_DB_PASSWORD}"
        f"@{PSQL_DB_HOST}:{PSQL_DB_PORT}/{PSQL_DB_NAME}"
    )


dbURL = get_db_url()
engine = create_engine(url=dbURL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# ---------------------------------------------------------------------------
# General Models
# ---------------------------------------------------------------------------
class ORMbase(DeclarativeBase):
    """
    Base class for all ORM models.

    Documentation Template
    ----------------------
    Each ORM model must follow this structure to maintain consistency and clarity.
    Keep descriptions concise but meaningful, focusing on the business purpose
    and schema-level details.

    Summary
    -------
    <One-line summary of the entity. Example: Represents a registered company in the system.>

    Description
    -----------
    <Optional longer description with business context, usage scenarios, or
    relationships to other entities.>

    Notes
    -----
    - <Special behavior, caveats, or usage guidelines>
    - <If data lifecycle or retention rules apply, mention here>

    Table
    -----
    table_name

    Columns
    -------
    column_name (Type, Constraints):
        Description of the column's purpose, semantics, and usage.
        - Example: `email (String, unique, nullable=False)`:
          Stores the login email of the user.

    Indexes
    -------
    - index_name: Columns included, purpose of the index.

    Constraints
    -----------
    - constraint_name: Description of constraint, why it exists, and implications.
    """

    pass


class Landmark(ORMbase):
    __tablename__ = "landmark"

    id = Column(Integer, primary_key=True)
    is_use = Column(Boolean, nullable=False, default=True)
    name = Column(String(32), nullable=False, index=True)
    alias_names = Column(ARRAY(String(32)), nullable=True)
    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    type = Column(Integer, nullable=False, default=LandmarkType.LOCAL, index=True)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_landmark_alias_names_gin", alias_names, postgresql_using="gin"),
        Index("ix_landmark_boundary_gist", boundary, postgresql_using="gist"),
    )


class BusStop(ORMbase):
    __tablename__ = "bus_stop"

    id = Column(Integer, primary_key=True)
    name = Column(TEXT, nullable=False)
    landmark_id = Column(
        Integer,
        ForeignKey(Landmark.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(location, landmark_id),)


class Wallet(ORMbase):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True)
    name = Column(TEXT, nullable=False)
    balance = Column(Numeric(10, 2), nullable=False, server_default=text("0"))
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class BankAccount(ORMbase):
    __tablename__ = "bank_account"

    id = Column(Integer, primary_key=True)
    bank_name = Column(TEXT, nullable=False)
    branch_name = Column(TEXT)
    account_number = Column(TEXT, nullable=False)
    holder_name = Column(TEXT, nullable=False)
    ifsc = Column(TEXT, nullable=False)
    account_type = Column(Integer, nullable=False, default=BankAccountType.OTHER)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class GlobalFare(ORMbase):
    __tablename__ = "global_fare"

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    name = Column(String(32), nullable=False, unique=True)
    attributes = Column(JSONB, nullable=False)
    function = Column(TEXT, nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


# ---------------------------------------------------------------------------
# Entebus Models
# ---------------------------------------------------------------------------
class Executive(ORMbase):
    __tablename__ = "executive"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(TEXT, nullable=False)
    gender = Column(Integer, nullable=False, default=GenderType.OTHER)
    full_name = Column(TEXT)
    designation = Column(TEXT)
    status = Column(Integer, nullable=False, default=AccountStatus.ACTIVE)
    phone_number = Column(TEXT)
    email_id = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class ExecutiveRole(ORMbase):
    __tablename__ = "executive_role"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    permissions = Column(ARRAY(String), nullable=False, default=list)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_executive_role_permissions_gin", permissions, postgresql_using="gin"),
    )


class ExecutiveRoleMap(ORMbase):
    __tablename__ = "executive_role_map"

    id = Column(Integer, primary_key=True)
    role_id = Column(
        Integer,
        ForeignKey(ExecutiveRole.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executive_id = Column(
        Integer,
        ForeignKey(Executive.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(role_id, executive_id),)


class ExecutiveToken(ORMbase):
    __tablename__ = "executive_token"

    id = Column(Integer, primary_key=True)
    executive_id = Column(
        Integer,
        ForeignKey(Executive.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    access_token = Column(
        String(64),
        nullable=False,
        unique=True,
        default=lambda: token_hex(32),
    )
    expires_in = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    platform_type = Column(Integer, nullable=False, default=PlatformType.OTHER)
    client_details = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class ExecutiveImage(ORMbase):
    __tablename__ = "executive_image"

    id = Column(Integer, primary_key=True)
    executive_id = Column(
        Integer,
        ForeignKey(Executive.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Business Models
# ---------------------------------------------------------------------------
class Business(ORMbase):

    __tablename__ = "business"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    status = Column(Integer, nullable=False, default=BusinessStatus.ACTIVE)
    type = Column(Integer, nullable=False, default=BusinessType.OTHER)

    address = Column(TEXT, nullable=False)
    contact_person = Column(TEXT, nullable=False)
    phone_number = Column(TEXT, nullable=False)
    email_id = Column(TEXT, nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_business_location_gist", location, postgresql_using="gist"),
    )


class BusinessImage(ORMbase):
    __tablename__ = "business_image"

    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class BusinessWallet(ORMbase):
    __tablename__ = "business_wallet"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(
        Integer, ForeignKey(Wallet.id, ondelete="CASCADE"), nullable=False
    )
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class Vendor(ORMbase):
    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    username = Column(String(32), nullable=False)
    password = Column(TEXT, nullable=False)
    gender = Column(Integer, nullable=False, default=GenderType.OTHER)
    full_name = Column(TEXT)
    status = Column(Integer, nullable=False, default=AccountStatus.ACTIVE)
    phone_number = Column(TEXT)
    email_id = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(username, business_id),)


class VendorRole(ORMbase):
    __tablename__ = "vendor_role"

    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(32), nullable=False)
    permissions = Column(ARRAY(String), nullable=False, default=list)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(name, business_id),
        Index("ix_vendor_role_permissions_gin", permissions, postgresql_using="gin"),
    )


class VendorRoleMap(ORMbase):
    __tablename__ = "Vendor_role_map"

    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        Integer,
        ForeignKey(VendorRole.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id = Column(
        Integer,
        ForeignKey(Vendor.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(business_id, role_id, vendor_id),)


class VendorToken(ORMbase):
    __tablename__ = "vendor_token"

    id = Column(Integer, primary_key=True)
    business_id = Column(
        Integer,
        ForeignKey(Business.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id = Column(
        Integer,
        ForeignKey(Vendor.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    access_token = Column(
        String(64),
        nullable=False,
        unique=True,
        default=lambda: token_hex(32),
    )
    expires_in = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    platform_type = Column(Integer, nullable=False, default=PlatformType.OTHER)
    client_details = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class VendorImage(ORMbase):
    __tablename__ = "vendor_image"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(
        Integer,
        ForeignKey(Vendor.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Company Models
# ---------------------------------------------------------------------------
class Company(ORMbase):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    status = Column(Integer, nullable=False, default=CompanyStatus.UNDER_VERIFICATION)
    type = Column(Integer, nullable=False, default=CompanyType.OTHER)
    address = Column(TEXT, nullable=False)
    contact_person = Column(TEXT, nullable=False)
    phone_number = Column(TEXT, nullable=False)
    email_id = Column(TEXT, nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_company_location_gist", location, postgresql_using="gist"),
    )


class CompanyImage(ORMbase):
    __tablename__ = "company_image"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class CompanyWallet(ORMbase):
    __tablename__ = "company_wallet"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(
        Integer, ForeignKey(Wallet.id, ondelete="CASCADE"), nullable=False
    )
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class Operator(ORMbase):
    __tablename__ = "operator"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    username = Column(String(32), nullable=False)
    password = Column(TEXT, nullable=False)
    gender = Column(Integer, nullable=False, default=GenderType.OTHER)
    full_name = Column(TEXT)
    status = Column(Integer, nullable=False, default=AccountStatus.ACTIVE)
    phone_number = Column(TEXT)
    email_id = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(username, company_id),)


class OperatorRole(ORMbase):
    __tablename__ = "operator_role"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(32), nullable=False)
    permissions = Column(ARRAY(String), nullable=False, default=list)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(name, company_id),
        Index("ix_operator_role_permissions_gin", permissions, postgresql_using="gin"),
    )


class OperatorRoleMap(ORMbase):
    __tablename__ = "operator_role_map"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        Integer,
        ForeignKey(OperatorRole.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operator_id = Column(
        Integer,
        ForeignKey(Operator.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(company_id, role_id, operator_id),)


class OperatorToken(ORMbase):
    __tablename__ = "operator_token"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operator_id = Column(
        Integer,
        ForeignKey(Operator.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    access_token = Column(
        String(64),
        nullable=False,
        unique=True,
        default=lambda: token_hex(32),
    )
    expires_in = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    platform_type = Column(Integer, nullable=False, default=PlatformType.OTHER)
    client_details = Column(TEXT)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class OperatorImage(ORMbase):
    __tablename__ = "operator_image"

    id = Column(Integer, primary_key=True)
    operator_id = Column(
        Integer,
        ForeignKey(Operator.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class LocalFare(ORMbase):
    __tablename__ = "local_fare"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    global_fare_id = Column(
        Integer,
        ForeignKey(GlobalFare.id, ondelete="SET NULL"),
        index=True,
    )
    name = Column(String(32), nullable=False, unique=True)
    attributes = Column(JSONB, nullable=False)
    function = Column(TEXT, nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(name, company_id),)


class Route(ORMbase):
    __tablename__ = "route"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey("company.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(256), nullable=False)
    attributes = Column(JSONB, nullable=False)
    status = Column(Integer, nullable=False, default=RouteStatus.INVALID)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(name, company_id),)


class LandmarkInRoute(ORMbase):
    __tablename__ = "landmark_in_route"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    route_id = Column(
        Integer, ForeignKey(Route.id, ondelete="CASCADE"), nullable=False, index=True
    )
    landmark_id = Column(
        Integer, ForeignKey(Landmark.id, ondelete="RESTRICT"), nullable=False
    )
    distance_from_start = Column(Integer, nullable=False)
    arrival_delta = Column(Integer, nullable=False)
    departure_delta = Column(Integer, nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(route_id, distance_from_start),)


class Bus(ORMbase):
    __tablename__ = "bus"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    registration_number = Column(String(16), nullable=False, index=True)
    name = Column(String(32), nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    manufactured_on = Column(DateTime(timezone=True), nullable=False)
    insurance_upto = Column(DateTime(timezone=True))
    pollution_upto = Column(DateTime(timezone=True))
    fitness_upto = Column(DateTime(timezone=True))
    road_tax_upto = Column(DateTime(timezone=True))
    status = Column(Integer, nullable=False, default=BusStatus.ACTIVE)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint(registration_number, company_id),)


class BusImage(ORMbase):
    __tablename__ = "bus_image"

    id = Column(Integer, primary_key=True)
    bus_id = Column(
        Integer,
        ForeignKey(Bus.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(128), nullable=False)
    created_on = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Service Related Models
# ---------------------------------------------------------------------------
class Schedule(ORMbase):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, index=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticketing_mode = Column(Integer, nullable=False, default=TicketingMode.HYBRID)
    start_time = Column(Time(timezone=True), nullable=False)
    bus_id = Column(Integer, ForeignKey(Bus.id, ondelete="SET NULL"))
    route_id = Column(Integer, ForeignKey(Route.id, ondelete="SET NULL"))
    fare_id = Column(Integer, ForeignKey(LocalFare.id, ondelete="SET NULL"))
    trigger_on = Column(ARRAY(Integer))
    trigger_mode = Column(Integer, nullable=False, default=TriggeringMode.AUTO)
    trigger_at = Column(Time(timezone=True), nullable=False)
    trigger_from = Column(DateTime(timezone=True))
    trigger_till = Column(DateTime(timezone=True))
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class Service(ORMbase):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(128), nullable=False)
    route = Column(Integer, ForeignKey(Route.id, ondelete="RESTRICT"))
    fare = Column(Integer, ForeignKey(LocalFare.id, ondelete="RESTRICT"))
    bus_id = Column(Integer, ForeignKey(Bus.id, ondelete="RESTRICT"))
    ticket_mode = Column(Integer, nullable=False, default=TicketingMode.HYBRID)
    status = Column(Integer, nullable=False, default=ServiceStatus.CREATED)
    starting_at = Column(DateTime(timezone=True), nullable=False)
    ending_at = Column(DateTime(timezone=True), nullable=False)
    private_key = Column(TEXT, nullable=False)
    public_key = Column(TEXT, nullable=False)
    remark = Column(TEXT)
    started_on = Column(DateTime(timezone=True))
    finished_on = Column(DateTime(timezone=True))
    bus_snapshot = Column(JSONB, nullable=False)
    route_snapshot = Column(JSONB, nullable=False)
    fare_snapshot = Column(JSONB, nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class ServiceTrace(ORMbase):
    __tablename__ = "service_trace"

    id = Column(Integer, primary_key=True)
    service_id = Column(
        Integer,
        ForeignKey(Service.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    landmark_id = Column(
        Integer, ForeignKey(Landmark.id, ondelete="CASCADE"), nullable=False
    )
    location = Column(Geometry(geometry_type="POINT", srid=4326))
    accuracy = Column(Numeric(10, 2))
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class Duty(ORMbase):
    __tablename__ = "duty"

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operator_id = Column(
        Integer,
        ForeignKey(Operator.id, ondelete="SET NULL"),
    )
    service_id = Column(
        Integer,
        ForeignKey(Service.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    passcode = Column(String(32), nullable=False)
    status = Column(Integer, nullable=False, default=DutyStatus.ASSIGNED)
    started_on = Column(DateTime(timezone=True))
    finished_on = Column(DateTime(timezone=True))
    collection = Column(Numeric(10, 2))
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())


class PaperTicket(ORMbase):
    __tablename__ = "paper_ticket"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id = Column(
        Integer,
        ForeignKey(Service.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    duty_id = Column(
        Integer, ForeignKey(Duty.id, ondelete="RESTRICT"), nullable=False, index=True
    )
    sequence_id = Column(Integer, nullable=False)
    ticket_types = Column(JSONB, nullable=False)
    pickup_point = Column(
        Integer, ForeignKey(Landmark.id, ondelete="RESTRICT"), nullable=False
    )
    dropping_point = Column(
        Integer, ForeignKey(Landmark.id, ondelete="RESTRICT"), nullable=False
    )
    extra = Column(JSONB, nullable=False)
    distance = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("service_id", "duty_id", "sequence_id"),)


class DigitalTicket(ORMbase):
    __tablename__ = "digital_ticket"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey(Company.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id = Column(
        Integer,
        ForeignKey(Service.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_id = Column(Integer, nullable=False)
    ticket_types = Column(JSONB, nullable=False)
    pickup_point = Column(
        Integer, ForeignKey(Landmark.id, ondelete="RESTRICT"), nullable=False
    )
    dropping_point = Column(
        Integer, ForeignKey(Landmark.id, ondelete="RESTRICT"), nullable=False
    )
    extra = Column(JSONB, nullable=False)
    distance = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
