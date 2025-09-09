"""
Application configuration and constants for EnteBus Server.

This module centralizes environment-based configuration, resource limits,
regular expressions, geometry constraints, timezones, and other constants.

Configuration values can be overridden via environment variables.
"""

from os import environ
from zoneinfo import ZoneInfo


# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
API_TITLE = "Entebus Server"
API_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# PostgreSQL configuration
# ---------------------------------------------------------------------------
PSQL_DB_DRIVER = environ.get("PSQL_DB_DRIVER", "postgresql")
PSQL_DB_USERNAME = environ.get("PSQL_DB_USERNAME", "postgres")
PSQL_DB_PORT = environ.get("PSQL_DB_PORT", "5432")
PSQL_DB_PASSWORD = environ.get("PSQL_DB_PASSWORD", "password")
PSQL_DB_HOST = environ.get("PSQL_DB_HOST", "localhost")
PSQL_DB_NAME = environ.get("PSQL_DB_NAME", "postgres")


# ---------------------------------------------------------------------------
# OpenObserve configuration
# ---------------------------------------------------------------------------
OPENOBSERVE_PROTOCOL = environ.get("OPENOBSERVE_PROTOCOL", "http")
OPENOBSERVE_HOST = environ.get("OPENOBSERVE_HOST", "localhost")
OPENOBSERVE_PORT = environ.get("OPENOBSERVE_PORT", "5080")
OPENOBSERVE_USERNAME = environ.get("OPENOBSERVE_USERNAME", "admin@entebus.com")
OPENOBSERVE_PASSWORD = environ.get("OPENOBSERVE_PASSWORD", "password")
OPENOBSERVE_ORG = environ.get("OPENOBSERVE_ORG", "nixbug")
OPENOBSERVE_STREAM = environ.get("OPENOBSERVE_STREAM", "entebus-core-server")


# ---------------------------------------------------------------------------
# Redis configuration
# ---------------------------------------------------------------------------
REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = environ.get("REDIS_PASSWORD", "password")


# ---------------------------------------------------------------------------
# MinIO configuration
# ---------------------------------------------------------------------------
MINIO_HOST = environ.get("MINIO_HOST", "localhost")
MINIO_PORT = environ.get("MINIO_PORT", "9000")
MINIO_USERNAME = environ.get("MINIO_USERNAME", "minio")
MINIO_PASSWORD = environ.get("MINIO_PASSWORD", "password")


# ---------------------------------------------------------------------------
# Resource upper limits
# ---------------------------------------------------------------------------
MAX_EXECUTIVE_TOKENS = 5  # Maximum tokens per executive
MAX_OPERATOR_TOKENS = 5  # Maximum tokens per operator
MAX_VENDOR_TOKENS = 1  # Maximum tokens per vendor
MAX_TOKEN_VALIDITY = 7 * 24 * 60 * 60  # Token validity (in seconds, 7 days)


# ---------------------------------------------------------------------------
# Geometry type constants
# ---------------------------------------------------------------------------
MAX_LANDMARK_AREA = 5 * 1000 * 1000  # 5 km² in m²
MIN_LANDMARK_AREA = 2  # 2 m²


# ---------------------------------------------------------------------------
# Route/landmarks constraints
# ---------------------------------------------------------------------------
MIN_LANDMARK_IN_ROUTE = 2  # Minimum number of landmarks per route
MAX_ROUTE_DISTANCE = 10000 * 1000  # Max route length in meters


# ---------------------------------------------------------------------------
# Service/duty constraints
# ---------------------------------------------------------------------------
SERVICE_START_LEAD_TIME_MINUTES = 60  # Minimum buffer before a service starts
SERVICE_CREATION_LEAD_TIME_DAYS = 1  # Minimum buffer before a service can be created
MAX_DUTIES_PER_SERVICE = 50  # Maximum number of duties allowed per service


# ---------------------------------------------------------------------------
# Timezone constants
# ---------------------------------------------------------------------------
TMZ_PRIMARY = ZoneInfo("UTC")
TMZ_SECONDARY = ZoneInfo("Asia/Kolkata")


# ---------------------------------------------------------------------------
# MiniRacer constants (for JS execution limits)
# ---------------------------------------------------------------------------
JSX_TIMEOUT_MS = 1000  # Timeout for script execution (in milliseconds)
JSX_MAX_MEMORY_BYTES = 10 * 1024 * 1024  # Max memory size (10 MB)


# ---------------------------------------------------------------------------
# Redis mutex lock constants
# ---------------------------------------------------------------------------
# Maximum time a lock can be held before it is automatically released (in seconds)
LOCK_TIMEOUT_SECONDS = 10
# Maximum time a client will wait to acquire a lock before giving up (in seconds)
LOCK_MAX_WAIT_SECONDS = 10


# ---------------------------------------------------------------------------
# Fare constants
# ---------------------------------------------------------------------------
DYNAMIC_FARE_VERSION = 1  # Current dynamic fare version
