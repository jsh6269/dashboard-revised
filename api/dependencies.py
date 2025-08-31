import os
from typing import Tuple

from fastapi import File, Form, UploadFile
from schemas import DashboardItemCreate


def parse_dashboard_form(
    title: str = Form(...),
    description: str | None = Form(None),
    image: UploadFile | str | None = File(None),
) -> Tuple[DashboardItemCreate, UploadFile | None]:
    """multipart/form-data -> (DashboardItemCreate, UploadFile|None)"""

    if image == "":
        image = None

    return DashboardItemCreate(title=title, description=description), image
