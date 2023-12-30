from courselib import (
    Course,
    Section,
    SectionSeats,
    update_course_sections,
    section_seats,
    diff_section_seats_pretty,
)

from threading import Thread, Lock
from time import sleep
import os

from pydantic import TypeAdapter
from collections.abc import Callable

CourseList = TypeAdapter(list[Course])
SectionSeatsDict = TypeAdapter(dict[str, SectionSeats])


class CourseMonitor(Thread):
    def __init__(
        self,
        data_path: str,
        fetch_interval: float = 60,
        callback: Callable[[str], None] = lambda x: print(x),
    ):
        super().__init__()

        self.stop = False
        self.data_path = data_path
        self.fetch_interval = fetch_interval
        self.callback = callback

        # check if data_path is a folder that exists, fail otherwise
        if not os.path.isdir(data_path):
            raise ValueError(f"{data_path} is not a valid directory")

        # if data_path/subscribed_courses.json exists, load it; otherwise, create it
        subd_courses_path = os.path.join(data_path, "subscribed_courses.json")
        self.subd_courses_path = subd_courses_path
        if not os.path.exists(subd_courses_path):
            with open(subd_courses_path, "w") as f:
                f.write("[]")

        with open(subd_courses_path, "r") as f:
            self.courses = CourseList.validate_json(f.read())

        self.courses_lock = Lock()  # so others can add courses

        # same for data_path/section_seats.json
        section_seats_path = os.path.join(data_path, "section_seats.json")
        self.section_seats_path = section_seats_path
        if not os.path.exists(section_seats_path):
            with open(section_seats_path, "w") as f:
                f.write("{}")

        with open(section_seats_path, "r") as f:
            self.section_seats = SectionSeatsDict.validate_json(f.read())

        # no need to lock as it'll only be accessed by this thread

    def write_courses(self):
        with open(self.subd_courses_path, "wb") as f:
            f.write(CourseList.dump_json(self.courses))

    def add_course(self, course: Course):
        if course in self.courses:
            raise ValueError(f"{course} already being monitored")

        # populate sections
        update_course_sections(course)

        # add to courses and save to file
        with self.courses_lock:
            self.courses.append(course)
            self.write_courses()

    def remove_course(self, course: Course):
        with self.courses_lock:
            self.courses.remove(course)
            self.write_courses()

    def get_courses(self) -> list[Course]:
        with self.courses_lock:
            return self.courses.copy()

    def run(self):
        while not self.stop:
            all_sections: list[Section] = []
            section_courses: dict[str, Course] = {}

            with self.courses_lock:
                for course in self.courses:
                    if not course.sections:
                        continue

                    all_sections += course.sections
                    for section in course.sections:
                        section_courses[section.id] = course.copy()

            if len(all_sections) == 0:
                sleep(self.fetch_interval)
                continue
            dt = self.fetch_interval / len(all_sections)

            success = 0
            total = 0

            for section in all_sections:
                old_seating = self.section_seats.get(section.id, None)

                try:
                    new_seating = section_seats(section)
                except Exception as e:
                    print(e)
                    total += 1

                    sleep(dt)
                    continue

                if old_seating:
                    diff = diff_section_seats_pretty(old_seating, new_seating)
                    if diff is not None:
                        course = section_courses[section.id]
                        diff = (
                            f"{course.subject} {course.number} {section.name}: {diff}"
                        )
                        self.callback(diff)

                self.section_seats[section.id] = new_seating

                with open(self.section_seats_path, "wb") as f:
                    f.write(SectionSeatsDict.dump_json(self.section_seats))

                success += 1
                total += 1

                sleep(dt)


if __name__ == "__main__":
    from courselib.types import Term, Semester

    def callback(diff: str):
        print(diff)

    monitor = CourseMonitor("data", callback=callback, fetch_interval=1)
    monitor.start()

    while True:
        new_course = input("Enter a course to monitor: ")
        if new_course == "":
            break

        try:
            sem, year, subject, number = new_course.split(" ")
            term = Term(year=int(year), semester=Semester(sem))

            course = Course(subject=subject, number=number, term=term)
            monitor.add_course(course)
        except Exception as e:
            print("Invalid course")
            print(e)
            continue

    monitor.stop = True
    monitor.join()
