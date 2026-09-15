"""
FaFaProFree scripts module.
"""

from scripts.version_resolver import (
    get_available_versions,
    validate_cdn_availability,
    clean_version_str,
    group_versions_by_major
)
from scripts.i18n import (
    _,
    t,
    set_language,
    get_language,
    get_supported_languages,
    detect_system_language
)

