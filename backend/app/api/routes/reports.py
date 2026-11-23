from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.report_service import generate_csv_report, generate_pdf_report
from app.services.test_service import TestExecutionNotFoundError


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{test_id}/pdf")
async def download_pdf_report(test_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        content, filename = generate_pdf_report(db, test_id)
    except TestExecutionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{test_id}/csv")
async def download_csv_report(test_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    try:
        content, filename = generate_csv_report(db, test_id)
    except TestExecutionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
