from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentUpdate(BaseModel):
    status: str

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str

    class Config:
        from_attributes = True
