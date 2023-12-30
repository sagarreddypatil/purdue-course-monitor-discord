from .types import Term, Semester, Course, Section, Seats, SectionSeats

import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


def update_course_sections(course: Course):
    term = str(course.term)
    subject = course.subject
    number = course.number

    url = f"https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_listcrse?term_in={term}&subj_in={subject}&crse_in={number}&schd_in="
    print(url)

    r = requests.get(url, headers=req_headers)
    if r.status_code != 200:
        raise Exception("Course not found")

    soup = BeautifulSoup(r.text, "html.parser")

    if "No classes were found" in soup.text:
        raise Exception("Course not found")

    table = soup.find("table", {"class": "datadisplaytable"})
    ths = table.find_all("th", {"class": "ddlabel"})

    sections: Section = []

    for row in ths:
        # example "Systems Programming - 13335 - CS 25200 - L01"

        link = row.find("a")  # the first one is correct
        text_segments = link.text.split(" - ")

        sections.append(
            Section(id=text_segments[1], name=text_segments[3], term=course.term)
        )

    course.sections = sections


def section_seats(section: Section):
    term = str(section.term)
    section_id = section.id

    url = f"https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in={term}&crn_in={section_id}"
    r = requests.get(url, headers=req_headers)

    if "sorry" in r.text:
        raise Exception(f"Rate limited for {section['link']}")

    if "No detailed" in r.text:
        raise Exception(f"Section {section['link']} not found")

    soup = BeautifulSoup(r.text, "html.parser")

    caption = soup.find("caption", string="Registration Availability")
    if caption is None:
        print(section["link"])
        raise Exception("Could not find Registration Availability caption")

    table = caption.find_parent("table")

    # pandas wants a StringIO not a string
    table_strio = StringIO(str(table))
    df = pd.read_html(table_strio, header=0, index_col=0)[0]
    table_strio.close()

    crosslistSeats = None
    if "Cross List Seats" in df.index:
        crosslistSeats = Seats(
            capacity=df.loc["Cross List Seats"]["Capacity"],
            actual=df.loc["Cross List Seats"]["Actual"],
            remaining=df.loc["Cross List Seats"]["Remaining"],
        )

    section_seats = SectionSeats(
        section=section,
        seats=Seats(
            capacity=df.loc["Seats"]["Capacity"],
            actual=df.loc["Seats"]["Actual"],
            remaining=df.loc["Seats"]["Remaining"],
        ),
        waitlist=Seats(
            capacity=df.loc["Waitlist Seats"]["Capacity"],
            actual=df.loc["Waitlist Seats"]["Actual"],
            remaining=df.loc["Waitlist Seats"]["Remaining"],
        ),
        crosslist=crosslistSeats,
    )

    return section_seats


if __name__ == "__main__":
    test_course = Course(
        subject="STAT",
        number="41600",
        term=Term(year=2024, semester=Semester.Spring),
        sections=[],
    )
    update_course_sections(test_course)
    print(section_seats(test_course.sections[0]))
