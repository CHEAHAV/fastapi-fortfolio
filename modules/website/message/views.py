import math
import os
import re
from datetime import datetime
from typing import cast
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import website
from modules.message.models import TBL_MESSAGE
from modules.message.schemas import MessageModel, generate_id, message_response
import resend

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMAIL_IN_SENDER_PATTERN = re.compile(r"<([^>]+)>")


def _get_resend_api_key() -> str:
    return (
        os.getenv("RESEND_API_KEY", "").strip()
        or os.getenv("RESEN_API_KEY", "").strip()
    )


def _get_resend_recipients() -> list[str]:
    recipients = [
        email.strip()
        for email in os.getenv("RESEND_TO_EMAIL", "").split(",")
        if email.strip()
    ]
    invalid_recipients = [
        email for email in recipients if not EMAIL_PATTERN.fullmatch(email)
    ]

    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RESEND_TO_EMAIL is not configured",
        )
    if invalid_recipients:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid RESEND_TO_EMAIL value: {', '.join(invalid_recipients)}",
        )

    return recipients


def _sender_email(sender: str) -> str:
    match = EMAIL_IN_SENDER_PATTERN.search(sender)
    return (match.group(1) if match else sender).strip().lower()


def _get_resend_sender() -> str:
    sender = os.getenv("RESEND_FROM_EMAIL", "").strip()
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RESEND_FROM_EMAIL is not configured in .env",
        )

    sender_email = _sender_email(sender)
    if sender_email.endswith("@gmail.com"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "RESEND_FROM_EMAIL cannot use gmail.com. Set RESEND_FROM_EMAIL "
                "in .env to onboarding@resend.dev or a verified Resend domain."
            ),
        )

    return sender


def _build_email_text(
    sender_name: str,
    reply_to: str,
    subject: str,
    message_body: str,
) -> str:
    sender_email = reply_to or "Not provided"
    sent_date = datetime.now().strftime("%B %d, %Y")

    return f"""Subject: Inquiry regarding {subject} - {sender_name}

HEADER CONTACT
From: {sender_email}
Date: {sent_date}

Dear Cheahav,

I hope this email finds you well.

I am reaching out through your portfolio contact form regarding the following inquiry:

{message_body or "No message provided."}

Could you please review this message and respond when you are available?

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,

{sender_name}
User / Client Inquiry

FOOTER
Connect with us: Portfolio Website | LinkedIn Profile

This email and any files transmitted with it are confidential and intended solely
for the use of the individual or entity to whom they are addressed.
"""


def _send_message_email(message: MessageModel) -> None:
    api_key = _get_resend_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resend API key is not configured",
        )
    if message.email and not EMAIL_PATTERN.fullmatch(message.email.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Visitor email is invalid",
        )

    resend.api_key = api_key
    recipients = _get_resend_recipients()
    sender = _get_resend_sender()
    reply_to = (message.email or "").strip()
    sender_name = " ".join(
        value for value in [message.first_name, message.last_name] if value
    ).strip() or "Website visitor"
    subject = (message.subject or "New portfolio message").strip()

    email_params = cast(resend.Emails.SendParams, {
        "from": sender,
        "to": recipients,
        "subject": f"Inquiry regarding {subject} - {sender_name}",
        "text": _build_email_text(sender_name, reply_to, subject, message.message or ""),
    })
    if reply_to:
        email_params["reply_to"] = reply_to

    try:
        resend.Emails.send(email_params)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to send email with Resend: {exc}",
        ) from exc


@website.post(
    "/create_message",
    tags=["Message"],
    status_code=201,
    operation_id="website_create_message",
)
async def create_message(
    message: MessageModel = Depends(MessageModel.form),
    db     : Session      = Depends(get_db),
):
    _send_message_email(message)

    new_item = TBL_MESSAGE(
        id         = generate_id(db),
        first_name = message.first_name,
        last_name  = message.last_name,
        email      = message.email,
        subject    = message.subject,
        message    = message.message,
        active     = True,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Message",
        "message": "Data created successfully",
        "data"   : message_response(new_item),
        "error"  : {},
    }

@website.get(
    "/get_message",
    tags=["Message"],
    operation_id="get_message",
)
async def get_message(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_MESSAGE.first_name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [message_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Message',
        'message': 'Data retrieved successfully',
        'data'   : {
            'lists'    : data_list,
            'meta_data': {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            }
        },
        'error': {}
    }


@website.get(
    "/get_message/{message_id}",
    tags=["Message"],
    operation_id="get_message_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_message_by_id(
    message_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.id == message_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Message not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Message",
        "message": "Data retrieved successfully",
        "data"   : message_response(item),
        "error"  : {},
    }

