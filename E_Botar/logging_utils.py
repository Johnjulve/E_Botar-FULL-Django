"""Compatibility shim for legacy imports.

This module re-exports logging utilities from E_Botar.utils.logging_utils so that
legacy imports like `from E_Botar.logging_utils import ...` continue to work.
"""

from E_Botar.utils.logging_utils import (  # noqa: F401
    log_activity,
    get_client_ip,
    log_user_login,
    log_user_logout,
    log_user_registration,
    log_vote_cast,
    log_admin_action,
    log_system_action,
    log_error,
)
