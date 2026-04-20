"""dns-health-auditor — a zero-fluff DNS health checker.

Exposes :func:`audit_domain` and the :class:`Report` / :class:`Finding`
data classes for programmatic use.
"""

from dns_auditor.auditor import audit_domain
from dns_auditor.report import Finding, Report, Severity

__all__ = ["audit_domain", "Finding", "Report", "Severity"]
__version__ = "0.1.0"
