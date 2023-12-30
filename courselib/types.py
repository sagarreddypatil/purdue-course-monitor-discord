from enum import Enum
from pydantic import BaseModel


class Semester(str, Enum):
    Fall = "FALL"
    Spring = "SPRING"
    Summer = "SUMMER"
    Winter = "WINTER"  # this is a BS semester, but it exists


# first number is year increment (Fall 2023) is 202410, 2023 + 1 + "10"
# second number is the suffix; fall is 10, spring is 20, summer is 30

semNumbers = {
    Semester.Fall: 10,
    Semester.Spring: 20,
    Semester.Summer: 30,
    Semester.Winter: 13,
}
semIncrements = {
    Semester.Fall: 1,
    Semester.Spring: 0,
    Semester.Summer: 0,
    Semester.Winter: 1,
}


class Term(BaseModel):
    year: int
    semester: Semester

    def __str__(self):
        sem = self.semester.upper()
        semEnum = Semester[sem]

        year = self.year + semIncrements[semEnum]
        return str(year) + str(semNumbers[semEnum])


class Section(BaseModel):
    id: str
    name: str


class Course(BaseModel):
    subject: str  # can't be bothered to validate this
    number: str
    term: Term
    sections: list[Section]
