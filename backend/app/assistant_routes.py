from fastapi import (
    APIRouter,
    HTTPException
)

from pydantic import BaseModel

from app.assistant_service import (
    interpret_assistant_command
)


router = APIRouter(
    prefix="/api/assistant",
    tags=["AI Assistant"]
)


class AssistantRequest(BaseModel):

    command: str

    current_complaint: dict = {}


@router.post("/command")
def assistant_command(
    request: AssistantRequest
):

    try:

        result = interpret_assistant_command(

            command=request.command,

            current_complaint=
                request.current_complaint

        )


        return {

            "message":
                "Assistant command processed successfully",

            "result":
                result

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )