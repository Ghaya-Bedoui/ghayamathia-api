from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: str
    level: str
    duration_minutes: int = 60
    price_eur: int = 0
    published: bool = True


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    level: str | None = None
    duration_minutes: int | None = None
    price_eur: int | None = None
    published: bool | None = None


class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    level: str
    duration_minutes: int
    price_eur: int
    published: bool

    class Config:
        from_attributes = True
