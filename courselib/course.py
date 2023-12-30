import requests
from bs4 import BeautifulSoup

from .misc import req_headers, base_url
from .types import Term, Semester, Course, Section


def update_course_sections(course: Course):
    term = str(course.term)
    subject = course.subject
    number = course.number

    url = f"https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_listcrse?term_in={term}&subj_in={subject}&crse_in={number}&schd_in="

    r = requests.get(url, headers=req_headers)
    if r.status_code != 200:
        raise Exception("Course not found")

    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", {"class": "datadisplaytable"})
    ths = table.find_all("th", {"class": "ddlabel"})

    sections: Section = []

    for row in ths:
        # example "Systems Programming - 13335 - CS 25200 - L01"

        link = row.find("a")  # the first one is correct
        text_segments = link.text.split(" - ")

        sections.append(Section(id=text_segments[1], name=text_segments[3]))

    course.sections = sections


test_course = Course(
    subject="CS", number="252", term=Term(year=2024, semester=Semester.Spring)
)
update_course_sections(test_course)
print(test_course)

# def section_seats(section_id: str, term: str):
#     if not validate_term(term):
#         raise Exception("Invalid term")

#     url = f"https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in={term}&crn_in={section_id}"
