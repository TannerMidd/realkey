import json

import pytest

from realkey.fabrication import (
    BUILTIN_PROFILES,
    GENERIC_PLA_PROFILE,
    ModelMetrics,
    PrinterProfile,
    PrintabilityReport,
    Severity,
    analyze_printability,
    get_builtin_profile,
)


def healthy_metrics() -> ModelMetrics:
    return ModelMetrics(
        size_x_mm=70,
        size_y_mm=25,
        size_z_mm=3,
        minimum_feature_mm=1.0,
        minimum_wall_mm=1.2,
    )


def test_happy_path_has_no_detected_profile_issues() -> None:
    report = analyze_printability(healthy_metrics(), GENERIC_PLA_PROFILE)

    assert report.status == "no_issues_detected"
    assert report.issues == ()
    assert not report.has_errors
    assert not report.has_warnings
    assert "verify" in report.notice.lower()


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"nozzle_diameter_mm": float("nan")}, "finite"),
        ({"nozzle_diameter_mm": 0}, "between"),
        ({"layer_height_mm": 0.5}, "must not exceed"),
        ({"build_width_mm": float("inf")}, "finite"),
        ({"minimum_wall_lines": True}, "integer"),
        ({"profile_id": "Not Valid"}, "lowercase"),
    ],
)
def test_invalid_profile_values_are_rejected(
    overrides: dict[str, object],
    message: str,
) -> None:
    values: dict[str, object] = {
        "profile_id": "test-profile",
        "name": "Test profile",
        "material": "Test material",
        "nozzle_diameter_mm": 0.4,
        "layer_height_mm": 0.2,
        "build_width_mm": 220,
        "build_depth_mm": 220,
        "build_height_mm": 250,
        "minimum_wall_lines": 2,
    }
    values.update(overrides)

    with pytest.raises(ValueError, match=message):
        PrinterProfile(**values)  # type: ignore[arg-type]


def test_oversize_model_reports_each_affected_axis_in_stable_order() -> None:
    metrics = ModelMetrics(
        size_x_mm=221,
        size_y_mm=230,
        size_z_mm=3,
        minimum_feature_mm=1.0,
        minimum_wall_mm=1.2,
    )

    report = analyze_printability(metrics, GENERIC_PLA_PROFILE)

    assert report.status == "outside_profile_limits"
    assert [issue.code for issue in report.issues] == [
        "MODEL_EXCEEDS_BUILD_X",
        "MODEL_EXCEEDS_BUILD_Y",
    ]
    assert all(issue.severity is Severity.ERROR for issue in report.issues)
    assert report.issues[0].measured_mm == 221
    assert report.issues[0].threshold_mm == 220


def test_thin_features_walls_and_z_are_reported() -> None:
    metrics = ModelMetrics(
        size_x_mm=70,
        size_y_mm=25,
        size_z_mm=0.3,
        minimum_feature_mm=0.3,
        minimum_wall_mm=0.6,
    )

    report = analyze_printability(metrics, GENERIC_PLA_PROFILE)

    assert [issue.code for issue in report.issues] == [
        "FEATURE_BELOW_NOZZLE",
        "WALL_BELOW_RECOMMENDED_LINES",
        "THIN_Z_LOW_LAYER_COUNT",
    ]
    assert [issue.severity for issue in report.issues] == [
        Severity.ERROR,
        Severity.WARNING,
        Severity.WARNING,
    ]


@pytest.mark.parametrize(
    ("minimum_feature_mm", "minimum_wall_mm"),
    [(None, None), (None, 1.2), (1.0, None)],
)
def test_unknown_detailed_geometry_emits_one_warning_and_skips_both_checks(
    minimum_feature_mm: float | None,
    minimum_wall_mm: float | None,
) -> None:
    metrics = ModelMetrics(
        size_x_mm=70,
        size_y_mm=25,
        size_z_mm=3,
        minimum_feature_mm=minimum_feature_mm,
        minimum_wall_mm=minimum_wall_mm,
    )

    report = analyze_printability(metrics, GENERIC_PLA_PROFILE)

    assert [issue.code for issue in report.issues] == [
        "DETAILED_GEOMETRY_NOT_MEASURED"
    ]
    assert report.issues[0].severity is Severity.WARNING
    assert report.metrics.to_dict()["minimum_feature_mm"] is minimum_feature_mm
    assert report.metrics.to_dict()["minimum_wall_mm"] is minimum_wall_mm


def test_profile_metrics_issue_and_report_round_trip_plain_dicts() -> None:
    report = analyze_printability(
        ModelMetrics(
            size_x_mm=210,
            size_y_mm=25,
            size_z_mm=0.3,
            minimum_feature_mm=0.45,
            minimum_wall_mm=0.5,
        ),
        GENERIC_PLA_PROFILE,
    )
    serialized = report.to_dict()
    restored = PrintabilityReport.from_dict(serialized)

    assert restored == report
    assert PrinterProfile.from_dict(report.profile.to_dict()) == report.profile
    assert ModelMetrics.from_dict(report.metrics.to_dict()) == report.metrics
    assert all(isinstance(item, dict) for item in serialized["issues"])
    assert isinstance(serialized["profile"], dict)
    assert isinstance(serialized["metrics"], dict)


def test_report_json_is_canonical_and_deterministic() -> None:
    report_a = analyze_printability(healthy_metrics(), GENERIC_PLA_PROFILE)
    report_b = analyze_printability(healthy_metrics(), GENERIC_PLA_PROFILE)

    payload = report_a.to_json()

    assert payload == report_b.to_json()
    assert payload == json.dumps(
        report_a.to_dict(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert PrintabilityReport.from_json(payload) == report_a


def test_builtin_profiles_are_stable_and_serializable() -> None:
    assert [profile.material for profile in BUILTIN_PROFILES] == [
        "PLA",
        "PETG",
        "ABS",
        "Nylon",
    ]
    assert get_builtin_profile("generic-pla-0.4") is GENERIC_PLA_PROFILE
    assert all(profile.to_dict()["profile_id"] for profile in BUILTIN_PROFILES)


def test_metric_and_dict_validation_reject_non_finite_or_unknown_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        ModelMetrics(
            size_x_mm=70,
            size_y_mm=25,
            size_z_mm=float("nan"),
            minimum_feature_mm=1,
            minimum_wall_mm=1,
        )

    data = GENERIC_PLA_PROFILE.to_dict()
    data["unknown"] = 1
    with pytest.raises(ValueError, match="unexpected"):
        PrinterProfile.from_dict(data)
