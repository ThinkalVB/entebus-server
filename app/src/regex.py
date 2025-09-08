"""
Validation Patterns (Regex)

These constants define the regular expressions used across the system
for validating common fields such as usernames, passwords, and vehicle
registration numbers. Centralizing them ensures consistency and
reusability across the codebase.
"""

# Username must start with a letter and can include letters, numbers,
# and special characters (- . @ _)
USERNAME_PATTERN = r"^[a-zA-Z][a-zA-Z0-9-.@_]*$"

# Password can include letters, numbers, and a wide range of special characters
PASSWORD_PATTERN = r"^[a-zA-Z0-9-+,.@_$%&*#!^=/?]*$"

# Vehicle number format (e.g., KA01AB1234 or DL04C567)
# - Starts with 2 uppercase letters
# - Followed by 2 digits
# - Optional 2 letters
# - Ends with 1–4 digits
VEHICLE_NUMBER_PATTERN = r"^[A-Z]{2}[0-9]{2}[A-Z]{0,2}[0-9]{1,4}$"
