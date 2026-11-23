import io
from datetime import datetime, timezone

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.database.models.profile import TestProfile
from app.database.models.test_execution import MeasurementResult, TestExecution
from app.services.test_service import (
    TestExecutionNotFoundError,
    get_execution,
    get_measurements,
)


def get_report_context(
    db: Session,
    test_id: str,
) -> tuple[TestExecution, list[MeasurementResult], TestProfile | None]:
    try:
        execution = get_execution(db, test_id)
    except TestExecutionNotFoundError as exc:
        raise exc
    measurements = get_measurements(db, test_id)
    profile = db.get(TestProfile, execution.profile_id)
    return execution, measurements, profile


def generate_csv_report(
    db: Session,
    test_id: str,
) -> tuple[str, str]:
    execution, measurements, profile = get_report_context(db, test_id)
    rows = [
        {
            "Test ID": execution.id,
            "Device ID": execution.device_id,
            "Part Number": execution.device_part_number,
            "Device Category": execution.device_category,
            "Test Profile": profile.name if profile else execution.profile_id,
            "Profile Version": execution.profile_version,
            "Measurement Name": measurement.parameter_name,
            "Measurement Value": measurement.measured_value,
            "Unit": measurement.unit,
            "Lower Limit": measurement.lower_limit,
            "Upper Limit": measurement.upper_limit,
            "Measurement Status": measurement.status,
            "Test Timestamp": measurement.measurement_timestamp.isoformat(),
            "Simulation Flag": measurement.simulation_flag,
        }
        for measurement in measurements
    ]
    dataframe = pd.DataFrame(rows)
    csv_text = dataframe.to_csv(index=False)
    filename = f"semitest-report-{test_id}.csv"
    return csv_text, filename


def generate_pdf_report(
    db: Session,
    test_id: str,
) -> tuple[bytes, str]:
    execution, measurements, profile = get_report_context(db, test_id)
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("SemiTest AI", styles["Title"]),
        Paragraph("Simulated Semiconductor Test Report", styles["Heading2"]),
        Spacer(1, 12),
    ]

    metadata = [
        ("Report number", f"SEMITEST-{execution.id}"),
        ("Test ID", execution.id),
        ("Device", execution.device_part_number),
        ("Device category", execution.device_category),
        ("Test profile", profile.name if profile else execution.profile_id),
        ("Profile version", str(execution.profile_version)),
        ("Execution timestamp", execution.execution_started_at.isoformat()),
        ("Operator", execution.operator),
        ("Overall status", execution.overall_status),
        ("Scenario", execution.scenario),
    ]
    metadata_table = Table(metadata, colWidths=[1.7 * inch, 4.8 * inch])
    metadata_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ])
    )
    elements.extend([metadata_table, Spacer(1, 14)])

    measurement_data = [["Measurement", "Value", "Unit", "Limits", "Status"]]
    for measurement in measurements:
        value = "Invalid" if measurement.measured_value is None else str(measurement.measured_value)
        lower = "—" if measurement.lower_limit is None else str(measurement.lower_limit)
        upper = "—" if measurement.upper_limit is None else str(measurement.upper_limit)
        measurement_data.append([
            measurement.parameter_name,
            value,
            measurement.unit,
            f"{lower} to {upper}",
            measurement.status,
        ])

    measurement_table = Table(
        measurement_data,
        colWidths=[2.1 * inch, 1.0 * inch, 0.7 * inch, 1.5 * inch, 0.8 * inch],
        repeatRows=1,
    )
    measurement_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    elements.extend([
        measurement_table,
        Spacer(1, 14),
        Paragraph(
            "SIMULATION DISCLAIMER: All measurements in this report are synthetic "
            "software-generated values and do not represent actual semiconductor "
            "device measurements or production test results.",
            styles["BodyText"],
        ),
        Spacer(1, 8),
        Paragraph(
            f"Report generated: {datetime.now(timezone.utc).isoformat()}",
            styles["BodyText"],
        ),
    ])
    document.build(elements)
    filename = f"semitest-report-{test_id}.pdf"
    return buffer.getvalue(), filename
