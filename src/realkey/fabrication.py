"""Fabrication profiles and deterministic printability checks.

This module intentionally depends only on the Python standard library so it can
be used by RealKey's Pyodide UI without importing the CAD stack.  The checks are
conservative geometry-to-profile comparisons, not physical certification.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import json
import math
import re
from typing import Any, ClassVar, Final


__all__ = [
    "ANALYSIS_VERSION",
    "BUILTIN_PROFILES",
    "GENERIC_ABS_PROFILE",
    "GENERIC_NYLON_PROFILE",
    "GENERIC_PETG_PROFILE",
    "GENERIC_PLA_PROFILE",
    "ModelMetrics",
    "PrinterProfile",
    "PrintabilityIssue",
    "PrintabilityReport",
    "Severity",
    "analyze_printability",
    "get_builtin_profile",
]


ANALYSIS_VERSION: Final = "1.0"
REPORT_NOTICE: Final = (
    "Automated profile checks only; verify dimensions, material behavior, "
    "orientation, and fit before fabrication."
)

_PROFILE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_ISSUE_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _text(value: object, field_name: str, *, maximum_length: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > maximum_length:
        raise ValueError(
            f"{field_name} must contain at most {maximum_length} characters"
        )
    return normalized


def _finite_float(
    value: object,
    field_name: str,
    *,
    minimum: float,
    maximum: float,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a finite number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"{field_name} must be finite")
    if not minimum <= normalized <= maximum:
        raise ValueError(
            f"{field_name} must be between {minimum:g} and {maximum:g}"
        )
    return normalized


def _optional_finite_float(
    value: object,
    field_name: str,
    *,
    minimum: float = 0.0,
    maximum: float = 100_000.0,
) -> float | None:
    if value is None:
        return None
    return _finite_float(
        value,
        field_name,
        minimum=minimum,
        maximum=maximum,
    )


def _strict_mapping(
    value: object,
    expected_keys: frozenset[str],
    object_name: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{object_name} must be a mapping")
    keys = set(value.keys())
    missing = expected_keys - keys
    unexpected = keys - expected_keys
    if missing:
        raise ValueError(
            f"{object_name} is missing fields: {', '.join(sorted(missing))}"
        )
    if unexpected:
        raise ValueError(
            f"{object_name} has unexpected fields: "
            f"{', '.join(sorted(str(key) for key in unexpected))}"
        )
    return value


def _format_mm(value: float) -> str:
    return f"{value:.6g} mm"


class Severity(str, Enum):
    """Severity of a profile comparison result."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class PrinterProfile:
    """Printer geometry settings used for preliminary fabrication checks."""

    profile_id: str
    name: str
    material: str
    nozzle_diameter_mm: float
    layer_height_mm: float
    build_width_mm: float
    build_depth_mm: float
    build_height_mm: float
    minimum_wall_lines: int = 3

    _DICT_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "profile_id",
            "name",
            "material",
            "nozzle_diameter_mm",
            "layer_height_mm",
            "build_width_mm",
            "build_depth_mm",
            "build_height_mm",
            "minimum_wall_lines",
        }
    )

    def __post_init__(self) -> None:
        profile_id = _text(self.profile_id, "profile_id", maximum_length=64)
        if not _PROFILE_ID_PATTERN.fullmatch(profile_id):
            raise ValueError(
                "profile_id must use lowercase letters, numbers, dots, "
                "underscores, or hyphens"
            )
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(
            self,
            "name",
            _text(self.name, "name", maximum_length=100),
        )
        object.__setattr__(
            self,
            "material",
            _text(self.material, "material", maximum_length=64),
        )

        nozzle = _finite_float(
            self.nozzle_diameter_mm,
            "nozzle_diameter_mm",
            minimum=0.1,
            maximum=5.0,
        )
        layer = _finite_float(
            self.layer_height_mm,
            "layer_height_mm",
            minimum=0.01,
            maximum=2.0,
        )
        if layer > nozzle:
            raise ValueError(
                "layer_height_mm must not exceed nozzle_diameter_mm"
            )
        object.__setattr__(self, "nozzle_diameter_mm", nozzle)
        object.__setattr__(self, "layer_height_mm", layer)

        for field_name in (
            "build_width_mm",
            "build_depth_mm",
            "build_height_mm",
        ):
            object.__setattr__(
                self,
                field_name,
                _finite_float(
                    getattr(self, field_name),
                    field_name,
                    minimum=10.0,
                    maximum=5_000.0,
                ),
            )

        if (
            isinstance(self.minimum_wall_lines, bool)
            or not isinstance(self.minimum_wall_lines, int)
            or not 1 <= self.minimum_wall_lines <= 16
        ):
            raise ValueError("minimum_wall_lines must be an integer from 1 to 16")

    @property
    def build_volume_mm(self) -> tuple[float, float, float]:
        return (
            self.build_width_mm,
            self.build_depth_mm,
            self.build_height_mm,
        )

    @property
    def recommended_wall_mm(self) -> float:
        return self.nozzle_diameter_mm * self.minimum_wall_lines

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe dictionary with a stable field order."""

        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "material": self.material,
            "nozzle_diameter_mm": self.nozzle_diameter_mm,
            "layer_height_mm": self.layer_height_mm,
            "build_width_mm": self.build_width_mm,
            "build_depth_mm": self.build_depth_mm,
            "build_height_mm": self.build_height_mm,
            "minimum_wall_lines": self.minimum_wall_lines,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> PrinterProfile:
        values = _strict_mapping(data, cls._DICT_KEYS, "PrinterProfile")
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class ModelMetrics:
    """Orientation-specific measurements of a generated model."""

    size_x_mm: float
    size_y_mm: float
    size_z_mm: float
    minimum_feature_mm: float | None
    minimum_wall_mm: float | None

    _DICT_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "size_x_mm",
            "size_y_mm",
            "size_z_mm",
            "minimum_feature_mm",
            "minimum_wall_mm",
        }
    )

    def __post_init__(self) -> None:
        for field_name in ("size_x_mm", "size_y_mm", "size_z_mm"):
            object.__setattr__(
                self,
                field_name,
                _finite_float(
                    getattr(self, field_name),
                    field_name,
                    minimum=0.001,
                    maximum=100_000.0,
                ),
            )
        for field_name in ("minimum_feature_mm", "minimum_wall_mm"):
            object.__setattr__(
                self,
                field_name,
                _optional_finite_float(
                    getattr(self, field_name),
                    field_name,
                    minimum=0.001,
                    maximum=100_000.0,
                ),
            )

    @property
    def size_mm(self) -> tuple[float, float, float]:
        return (self.size_x_mm, self.size_y_mm, self.size_z_mm)

    def to_dict(self) -> dict[str, float | None]:
        """Return a JSON-safe dictionary with a stable field order."""

        return {
            "size_x_mm": self.size_x_mm,
            "size_y_mm": self.size_y_mm,
            "size_z_mm": self.size_z_mm,
            "minimum_feature_mm": self.minimum_feature_mm,
            "minimum_wall_mm": self.minimum_wall_mm,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> ModelMetrics:
        values = _strict_mapping(data, cls._DICT_KEYS, "ModelMetrics")
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class PrintabilityIssue:
    """One actionable result from a printability profile comparison."""

    code: str
    severity: Severity
    message: str
    recommendation: str
    measured_mm: float | None = None
    threshold_mm: float | None = None

    _DICT_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "code",
            "severity",
            "message",
            "recommendation",
            "measured_mm",
            "threshold_mm",
        }
    )

    def __post_init__(self) -> None:
        code = _text(self.code, "code", maximum_length=80)
        if not _ISSUE_CODE_PATTERN.fullmatch(code):
            raise ValueError(
                "code must use uppercase letters, numbers, and underscores"
            )
        object.__setattr__(self, "code", code)
        if not isinstance(self.severity, Severity):
            raise ValueError("severity must be a Severity value")
        object.__setattr__(
            self,
            "message",
            _text(self.message, "message", maximum_length=500),
        )
        object.__setattr__(
            self,
            "recommendation",
            _text(self.recommendation, "recommendation", maximum_length=500),
        )
        object.__setattr__(
            self,
            "measured_mm",
            _optional_finite_float(self.measured_mm, "measured_mm"),
        )
        object.__setattr__(
            self,
            "threshold_mm",
            _optional_finite_float(self.threshold_mm, "threshold_mm"),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe dictionary with a stable field order."""

        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "measured_mm": self.measured_mm,
            "threshold_mm": self.threshold_mm,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> PrintabilityIssue:
        values = dict(_strict_mapping(data, cls._DICT_KEYS, "PrintabilityIssue"))
        try:
            values["severity"] = Severity(values["severity"])
        except (TypeError, ValueError) as exc:
            raise ValueError("severity must be info, warning, or error") from exc
        return cls(**values)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class PrintabilityReport:
    """Deterministic result of comparing model metrics with a profile."""

    profile: PrinterProfile
    metrics: ModelMetrics
    issues: tuple[PrintabilityIssue, ...] = ()
    analysis_version: str = ANALYSIS_VERSION

    _DICT_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "analysis_version",
            "status",
            "notice",
            "profile",
            "metrics",
            "issues",
        }
    )

    def __post_init__(self) -> None:
        if not isinstance(self.profile, PrinterProfile):
            raise ValueError("profile must be a PrinterProfile")
        if not isinstance(self.metrics, ModelMetrics):
            raise ValueError("metrics must be ModelMetrics")
        if not isinstance(self.issues, tuple):
            try:
                object.__setattr__(self, "issues", tuple(self.issues))
            except TypeError as exc:
                raise ValueError(
                    "issues must be an iterable of PrintabilityIssue"
                ) from exc
        if not all(isinstance(issue, PrintabilityIssue) for issue in self.issues):
            raise ValueError("issues must contain only PrintabilityIssue values")
        if self.analysis_version != ANALYSIS_VERSION:
            raise ValueError(
                f"analysis_version must be {ANALYSIS_VERSION!r}"
            )

    @property
    def has_errors(self) -> bool:
        return any(issue.severity is Severity.ERROR for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity is Severity.WARNING for issue in self.issues)

    @property
    def status(self) -> str:
        if self.has_errors:
            return "outside_profile_limits"
        if self.has_warnings:
            return "review_recommended"
        return "no_issues_detected"

    @property
    def notice(self) -> str:
        return REPORT_NOTICE

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe dictionary with a stable field order."""

        return {
            "analysis_version": self.analysis_version,
            "status": self.status,
            "notice": self.notice,
            "profile": self.profile.to_dict(),
            "metrics": self.metrics.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> PrintabilityReport:
        values = _strict_mapping(data, cls._DICT_KEYS, "PrintabilityReport")
        if values["analysis_version"] != ANALYSIS_VERSION:
            raise ValueError(
                f"unsupported analysis_version: {values['analysis_version']!r}"
            )
        if values["notice"] != REPORT_NOTICE:
            raise ValueError("notice does not match this analysis version")
        raw_issues = values["issues"]
        if not isinstance(raw_issues, (list, tuple)):
            raise ValueError("issues must be a list")
        report = cls(
            profile=PrinterProfile.from_dict(
                values["profile"]  # type: ignore[arg-type]
            ),
            metrics=ModelMetrics.from_dict(values["metrics"]),  # type: ignore[arg-type]
            issues=tuple(
                PrintabilityIssue.from_dict(issue)  # type: ignore[arg-type]
                for issue in raw_issues
            ),
            analysis_version=ANALYSIS_VERSION,
        )
        if values["status"] != report.status:
            raise ValueError("status is inconsistent with report issues")
        return report

    def to_json(self) -> str:
        """Return canonical compact JSON for caching or browser messaging."""

        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> PrintabilityReport:
        if not isinstance(payload, str):
            raise ValueError("payload must be a JSON string")
        try:
            data: Any = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("payload must contain valid JSON") from exc
        return cls.from_dict(data)


GENERIC_PLA_PROFILE: Final = PrinterProfile(
    profile_id="generic-pla-0.4",
    name="Generic PLA — 0.4 mm nozzle",
    material="PLA",
    nozzle_diameter_mm=0.4,
    layer_height_mm=0.08,
    build_width_mm=220.0,
    build_depth_mm=220.0,
    build_height_mm=250.0,
)

GENERIC_PETG_PROFILE: Final = PrinterProfile(
    profile_id="generic-petg-0.4",
    name="Generic PETG — 0.4 mm nozzle",
    material="PETG",
    nozzle_diameter_mm=0.4,
    layer_height_mm=0.08,
    build_width_mm=220.0,
    build_depth_mm=220.0,
    build_height_mm=250.0,
)

GENERIC_ABS_PROFILE: Final = PrinterProfile(
    profile_id="generic-abs-0.4",
    name="Generic ABS — 0.4 mm nozzle",
    material="ABS",
    nozzle_diameter_mm=0.4,
    layer_height_mm=0.08,
    build_width_mm=220.0,
    build_depth_mm=220.0,
    build_height_mm=250.0,
)

GENERIC_NYLON_PROFILE: Final = PrinterProfile(
    profile_id="generic-nylon-0.4",
    name="Generic Nylon — 0.4 mm nozzle",
    material="Nylon",
    nozzle_diameter_mm=0.4,
    layer_height_mm=0.08,
    build_width_mm=220.0,
    build_depth_mm=220.0,
    build_height_mm=250.0,
)

BUILTIN_PROFILES: Final[tuple[PrinterProfile, ...]] = (
    GENERIC_PLA_PROFILE,
    GENERIC_PETG_PROFILE,
    GENERIC_ABS_PROFILE,
    GENERIC_NYLON_PROFILE,
)


def get_builtin_profile(profile_id: str) -> PrinterProfile:
    """Return a built-in profile by ID, raising ``KeyError`` if it is unknown."""

    for profile in BUILTIN_PROFILES:
        if profile.profile_id == profile_id:
            return profile
    raise KeyError(profile_id)


def analyze_printability(
    metrics: ModelMetrics,
    profile: PrinterProfile,
) -> PrintabilityReport:
    """Compare model measurements with printer-profile geometry limits.

    Issue ordering and text are stable for identical inputs, making the report
    suitable for caching and deterministic UI snapshots.  A report with no
    issues is not a guarantee that a part will print or function as intended.
    """

    if not isinstance(metrics, ModelMetrics):
        raise ValueError("metrics must be ModelMetrics")
    if not isinstance(profile, PrinterProfile):
        raise ValueError("profile must be a PrinterProfile")

    issues: list[PrintabilityIssue] = []

    dimensions = (
        ("X", metrics.size_x_mm, profile.build_width_mm),
        ("Y", metrics.size_y_mm, profile.build_depth_mm),
        ("Z", metrics.size_z_mm, profile.build_height_mm),
    )
    for axis, measured, limit in dimensions:
        if measured > limit:
            issues.append(
                PrintabilityIssue(
                    code=f"MODEL_EXCEEDS_BUILD_{axis}",
                    severity=Severity.ERROR,
                    message=(
                        f"Model {axis} size ({_format_mm(measured)}) exceeds the "
                        f"profile's {axis} build limit ({_format_mm(limit)})."
                    ),
                    recommendation=(
                        "Choose a larger build volume or reorient and regenerate "
                        "the model."
                    ),
                    measured_mm=measured,
                    threshold_mm=limit,
                )
            )
        elif measured >= limit * 0.9:
            issues.append(
                PrintabilityIssue(
                    code=f"MODEL_NEAR_BUILD_{axis}",
                    severity=Severity.WARNING,
                    message=(
                        f"Model {axis} size ({_format_mm(measured)}) uses at least "
                        f"90% of the profile's {axis} build limit "
                        f"({_format_mm(limit)})."
                    ),
                    recommendation=(
                        "Confirm usable bed area, margins, skirt or brim space, "
                        "and the selected orientation."
                    ),
                    measured_mm=measured,
                    threshold_mm=limit,
                )
            )

    nozzle = profile.nozzle_diameter_mm
    if metrics.minimum_feature_mm is None or metrics.minimum_wall_mm is None:
        issues.append(
            PrintabilityIssue(
                code="DETAILED_GEOMETRY_NOT_MEASURED",
                severity=Severity.WARNING,
                message=(
                    "Minimum feature width and wall thickness were not both "
                    "measured, so nozzle-resolution checks were skipped."
                ),
                recommendation=(
                    "Inspect the sliced toolpath or provide measured minimum "
                    "feature and wall values before relying on those checks."
                ),
            )
        )
    else:
        if metrics.minimum_feature_mm < nozzle:
            issues.append(
                PrintabilityIssue(
                    code="FEATURE_BELOW_NOZZLE",
                    severity=Severity.ERROR,
                    message=(
                        "Minimum feature width "
                        f"({_format_mm(metrics.minimum_feature_mm)}) is below one "
                        f"nozzle diameter ({_format_mm(nozzle)})."
                    ),
                    recommendation=(
                        "Use a smaller nozzle, enlarge the feature, or validate "
                        "the slicer's feature handling with a test piece."
                    ),
                    measured_mm=metrics.minimum_feature_mm,
                    threshold_mm=nozzle,
                )
            )
        elif metrics.minimum_feature_mm < nozzle * 1.5:
            issues.append(
                PrintabilityIssue(
                    code="FEATURE_NEAR_NOZZLE",
                    severity=Severity.WARNING,
                    message=(
                        "Minimum feature width "
                        f"({_format_mm(metrics.minimum_feature_mm)}) is close to "
                        f"one nozzle diameter ({_format_mm(nozzle)})."
                    ),
                    recommendation=(
                        "Inspect the sliced toolpath and consider a small feature "
                        "calibration print."
                    ),
                    measured_mm=metrics.minimum_feature_mm,
                    threshold_mm=nozzle * 1.5,
                )
            )

        recommended_wall = profile.recommended_wall_mm
        if metrics.minimum_wall_mm < nozzle:
            issues.append(
                PrintabilityIssue(
                    code="WALL_BELOW_NOZZLE",
                    severity=Severity.ERROR,
                    message=(
                        f"Minimum wall ({_format_mm(metrics.minimum_wall_mm)}) is "
                        f"below one nozzle diameter ({_format_mm(nozzle)})."
                    ),
                    recommendation=(
                        "Use a smaller nozzle or increase the wall thickness "
                        "before fabrication."
                    ),
                    measured_mm=metrics.minimum_wall_mm,
                    threshold_mm=nozzle,
                )
            )
        elif metrics.minimum_wall_mm + 1e-9 < recommended_wall:
            issues.append(
                PrintabilityIssue(
                    code="WALL_BELOW_RECOMMENDED_LINES",
                    severity=Severity.WARNING,
                    message=(
                        f"Minimum wall ({_format_mm(metrics.minimum_wall_mm)}) is "
                        f"below the profile's {profile.minimum_wall_lines}-line "
                        f"reference ({_format_mm(recommended_wall)})."
                    ),
                    recommendation=(
                        "Inspect perimeter generation and increase wall thickness "
                        "when strength or dimensional stability matters."
                    ),
                    measured_mm=metrics.minimum_wall_mm,
                    threshold_mm=recommended_wall,
                )
            )

    layer_count = metrics.size_z_mm / profile.layer_height_mm
    if layer_count < 2.0:
        issues.append(
            PrintabilityIssue(
                code="THIN_Z_BELOW_TWO_LAYERS",
                severity=Severity.ERROR,
                message=(
                    f"Model Z size ({_format_mm(metrics.size_z_mm)}) spans fewer "
                    f"than two nominal layers at {_format_mm(profile.layer_height_mm)} "
                    "per layer."
                ),
                recommendation=(
                    "Increase Z thickness, reduce layer height, or change model "
                    "orientation."
                ),
                measured_mm=metrics.size_z_mm,
                threshold_mm=profile.layer_height_mm * 2.0,
            )
        )
    elif layer_count < 5.0:
        issues.append(
            PrintabilityIssue(
                code="THIN_Z_LOW_LAYER_COUNT",
                severity=Severity.WARNING,
                message=(
                    f"Model Z size ({_format_mm(metrics.size_z_mm)}) spans only "
                    f"{layer_count:.2f} nominal layers."
                ),
                recommendation=(
                    "Review orientation and sliced layers; consider increasing "
                    "thickness or reducing layer height."
                ),
                measured_mm=metrics.size_z_mm,
                threshold_mm=profile.layer_height_mm * 5.0,
            )
        )

    return PrintabilityReport(
        profile=profile,
        metrics=metrics,
        issues=tuple(issues),
    )
