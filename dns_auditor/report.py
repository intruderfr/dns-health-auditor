"""Report / Finding data classes and grading logic."""

from __future__ import annotations

import enum
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class Severity(str, enum.Enum):
    """Severity level for an individual finding."""

    INFO = "INFO"
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

    @property
    def weight(self) -> int:
        """Point penalty applied to the final score."""
        return {
            Severity.INFO: 0,
            Severity.PASS: 0,
            Severity.WARN: 5,
            Severity.FAIL: 15,
        }[self]


@dataclass
class Finding:
    """A single check result."""

    check: str
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["severity"] = self.severity.value
        return out


@dataclass
class Report:
    """Full audit report for a single domain."""

    domain: str
    findings: List[Finding] = field(default_factory=list)
    runtime_seconds: float = 0.0
    resolver: Optional[str] = None

    def add(
        self,
        check: str,
        severity: Severity,
        message: str,
        **details: Any,
    ) -> Finding:
        finding = Finding(check=check, severity=severity, message=message, details=details)
        self.findings.append(finding)
        return finding

    @property
    def score(self) -> int:
        """Return a 0-100 score. Starts at 100 and subtracts severity weights."""
        penalty = sum(f.severity.weight for f in self.findings)
        return max(0, 100 - penalty)

    @property
    def grade(self) -> str:
        """Letter grade derived from :attr:`score`."""
        s = self.score
        if s >= 97:
            return "A+"
        if s >= 93:
            return "A"
        if s >= 90:
            return "A-"
        if s >= 87:
            return "B+"
        if s >= 83:
            return "B"
        if s >= 80:
            return "B-"
        if s >= 77:
            return "C+"
        if s >= 73:
            return "C"
        if s >= 70:
            return "C-"
        if s >= 60:
            return "D"
        return "F"

    @property
    def counts(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity.value] += 1
        return counts

    @property
    def has_failures(self) -> bool:
        return any(f.severity is Severity.FAIL for f in self.findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.severity is Severity.WARN for f in self.findings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "score": self.score,
            "grade": self.grade,
            "counts": self.counts,
            "runtime_seconds": round(self.runtime_seconds, 3),
            "resolver": self.resolver,
            "findings": [f.to_dict() for f in self.findings],
        }


# --- rendering ---------------------------------------------------------------


_SEVERITY_BADGE = {
    Severity.INFO: "[INFO]",
    Severity.PASS: "[PASS]",
    Severity.WARN: "[WARN]",
    Severity.FAIL: "[FAIL]",
}


def render_text(report: Report, width: int = 76) -> str:
    """Render a report as a plain-text table."""
    counts = report.counts
    header = f"DNS Health Report — {report.domain}"
    grade_tag = f"Grade: {report.grade}"
    pad = max(1, width - len(header) - len(grade_tag))
    lines: List[str] = [
        f"{header}{' ' * pad}{grade_tag}",
        "─" * width,
    ]

    if not report.findings:
        lines.append("(no findings)")
    else:
        check_width = max(len(f.check) for f in report.findings)
        check_width = min(check_width, 9)
        for f in report.findings:
            badge = _SEVERITY_BADGE[f.severity]
            check = f.check.ljust(check_width)
            lines.append(f"{badge} {check}  {f.message}")

    lines.append("─" * width)

    summary = (
        f"Score: {report.score}/100    "
        f"{len(report.findings)} checks, "
        f"{counts['FAIL']} fails, {counts['WARN']} warns    "
        f"runtime {report.runtime_seconds:.2f}s"
    )
    lines.append(summary)
    return "\n".join(lines)
