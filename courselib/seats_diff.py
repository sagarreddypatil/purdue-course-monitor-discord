from .types import Seats, SectionSeats


def diff_seats_pretty(old: Seats, new: Seats) -> Seats:
    """Returns a pretty string of the difference between two seats objects"""

    if old.remaining != new.remaining:
        return f"Remaining changed from {old.remaining} to {new.remaining}"

    return None


def diff_section_seats_pretty(old: SectionSeats, new: SectionSeats):
    """Returns a pretty string of the difference between two section seats objects"""

    if old.crosslist is not None and new.crosslist is not None:
        # if crosslist, only compare crosslist as it's most important

        diff = diff_seats_pretty(old.crosslist, new.crosslist)
        if diff is not None:
            return diff

    # normal seats are next most important
    diff = diff_seats_pretty(old.seats, new.seats)
    if diff is not None:
        return diff

    # waitlist is least important
    diff = diff_seats_pretty(old.waitlist, new.waitlist)
    if diff is not None:
        return diff

    return None


if __name__ == "__main__":
    from .course import update_course_sections, section_seats
    from .types import Course, Term, Semester

    test_course = Course(
        subject="STAT",
        number="41600",
        term=Term(year=2024, semester=Semester.Spring),
    )

    update_course_sections(test_course)
    seats = section_seats(test_course.sections[0])

    print(diff_section_seats_pretty(seats, seats))

    new_seats = SectionSeats.model_validate_json(seats.model_dump_json())
    new_seats.seats.remaining += 1

    print(diff_section_seats_pretty(seats, new_seats))  # works
