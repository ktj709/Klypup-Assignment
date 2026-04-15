from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(min_length=5)


class Citation(BaseModel):
    source_type: str
    source_name: str
    reference: str


class Section(BaseModel):
    title: str
    body: str
    citations: list[Citation] = []


class ResearchResponse(BaseModel):
    title: str
    executive_summary: str
    sections: list[Section]
    tools_used: list[str]
