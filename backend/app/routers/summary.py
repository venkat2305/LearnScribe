from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_database
from app.utils.auth import get_current_user, User
from app.utils.summary import generate_summary

router = APIRouter()


class SummarySourceEnum(str, Enum):
    text = "text"
    youtube = "youtube"
    article = "article"


class SummaryLengthEnum(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class ContentSource(BaseModel):
    url: Optional[str] = None


class SummaryCreate(BaseModel):
    summarySource: SummarySourceEnum
    contentSource: Optional[ContentSource] = None
    textContent: Optional[str] = None
    prompt: Optional[str] = None
    length: SummaryLengthEnum = SummaryLengthEnum.medium

    @root_validator(pre=True)
    def check_content_source(cls, values):
        summary_source = values.get("summarySource")
        content_source = values.get("contentSource")
        text_content = values.get("textContent")

        if summary_source in {"youtube", "article"}:
            if not (content_source and content_source.get("url")):
                raise ValueError("ContentSource.url is required for youtube and article summaries.")

        if summary_source == "text" and not text_content:
            raise ValueError("textContent is required when summary source is 'text'.")

        return values


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_summary(summary_data: SummaryCreate,
                        current_user: User = Depends(get_current_user)):
    result = generate_summary(summary_data)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Prepare document for database
    summary_doc = {
        "summary_id": str(ObjectId()),
        "user_id": current_user.user_id,
        **result,
        "created_by": current_user.user_id,
        "created_at": datetime.utcnow(),
    }

    db = get_database()
    insert_result = await db.summaries.insert_one(summary_doc)
    if not insert_result.inserted_id:
        raise HTTPException(status_code=500, detail="Unable to create summary.")

    return {
        "message": "Summary created successfully",
        "summary_id": summary_doc["summary_id"],
    }


@router.get("/mysummaries", status_code=200)
async def get_all_summaries(current_user: User = Depends(get_current_user)):
    db = get_database()
    summaries = await db.summaries.find(
        {"created_by": current_user.user_id}, 
        {
            "_id": 0,
            "summary_id": 1,
            "source_type": 1,
            "title": 1,
            "created_at": 1
        }
    ).to_list(length=None)

    return {"summaries": summaries}


@router.get("/{summary_id}", status_code=200)
async def get_summary(summary_id: str, current_user: User = Depends(get_current_user)):
    """
    Retrieve a specific summary by ID.
    """
    db = get_database()
    summary = await db.summaries.find_one(
        {"summary_id": summary_id, "created_by": current_user.user_id},
        {"_id": 0}
    )

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found.")

    return summary


@router.delete("/{summary_id}", status_code=200)
async def delete_summary(summary_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a summary by ID.
    """
    db = get_database()
    result = await db.summaries.delete_one(
        {"summary_id": summary_id, "created_by": current_user.user_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Summary not found.")

    return {"message": "Summary deleted successfully"}
