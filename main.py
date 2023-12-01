from time import time
from collections import namedtuple
from random import randint
from copy import copy

# Week and time schedules
week_schedule = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
time_schedule = {
    1: "8:40-10:15",
    2: "10:35-12:10",
    3: "12:20-13:55",
}

# Namedtuples for data structures
Classroom = namedtuple("Classroom", "room is_big")
Time = namedtuple("Time", "weekday time")
Teacher = namedtuple("Teacher", "name")
Subject = namedtuple("Subject", "name")
Group = namedtuple("Group", "name")
Lesson = namedtuple("Lesson", "teacher subject group is_lecture per_week")
Schedule = namedtuple("Schedule", "lessons classrooms times")
DomainEl = namedtuple("DomainEl", "day time room")

# Custom __repr__ methods for better object representation
Classroom.__repr__ = lambda c: f"{c.room} ({'big' if c.is_big else 'small'})"
Teacher.__repr__ = lambda t: f"{t.name.split()[1]}"
Subject.__repr__ = lambda s: f"{s.name.split()[1]}"
Group.__repr__ = lambda g: f"{g.name}"
Lesson.__repr__ = (
    lambda l: f"{l.teacher} | {l.subject} | {l.group} | "
    f"{'Lecture' if l.is_lecture else 'Seminar'} {l.per_week}/week"
)

# __repr__ method for Schedule
def gen_repr(g: Schedule):
    output = ""
    for i in range(len(g.lessons)):
        output += f"{g.lessons[i]},   {g.classrooms[i]},   {g.times[i]}\n"
    return output

Schedule.__repr__ = lambda g: gen_repr(g)

# Function to print the schedule
def print_schedule(solution: Schedule):
    for day in week_schedule:
        print("\n" + "-" * 100)
        print(f"{week_schedule[day].upper()}")
        for time in time_schedule:
            print("\n\n" + time_schedule[time])
            for c in classrooms:
                print(f"\n{c}", end="\t\t")
                for i in range(len(solution.lessons)):
                    if (
                        solution.times[i].weekday == day
                        and solution.times[i].time == time
                        and solution.classrooms[i].room == c.room
                    ):
                        print(solution.lessons[i], end="")

# Function to initialize domains for each lesson
def init_domains():
    domain = {}
    buf = []
    buf_lecture = []

    for day in week_schedule.keys():
        for time_slot in time_schedule.keys():
            for room in classrooms:
                buf.append(DomainEl(day, time_slot, room))
                if room.is_big:
                    buf_lecture.append(DomainEl(day, time_slot, room))

    for i in range(len(lessons)):
        if lessons[i].is_lecture:
            domain[i] = copy(buf_lecture)
        else:
            domain[i] = copy(buf)
    return domain

# MRV heuristic for lesson selection
def mrv(domain):
    min_len = len(week_schedule) * len(classrooms) * len(time_schedule) * 2
    ind = list(domain.keys())[0]
    for key, value in domain.items():
        if len(value) < min_len:
            min_len = len(value)
            ind = key
    return ind

# Degree heuristic for lesson selection
def degree(domain):
    counts = {}
    for key in domain:
        counts[key] = 0 if lessons[key].is_lecture else 1
        for i in domain:
            if i == key:
                continue
            if lessons[key].teacher == lessons[i].teacher:
                counts[key] += 1
            counts[key] += len(set(map(str, lessons[key].group)) & set(map(str, lessons[i].group)))

    ind = list(counts.keys())[0]
    max_count = 0
    for key, value in counts.items():
        if value > max_count:
            max_count = value
            ind = key
    return ind

# LCV heuristic for lesson selection
def lcv(domain):
    counts = {}
    for i in domain:
        counts[i] = 0
        for key in domain:
            if i == key:
                continue

            for d in domain[key]:
                if not (
                    d.day == domain[i][0].day
                    and d.time == domain[i][0].time
                    and d.room == domain[i][0].room
                ) and not (
                    d.day == domain[i][0].day
                    and d.time == domain[i][0].time
                    and (
                        lessons[key].teacher == lessons[i].teacher
                        or set(map(str, lessons[key].group)) & set(map(str, lessons[i].group))
                    )
                ):
                    counts[i] += 1

    ind = list(counts.keys())[0]
    max_count = 0
    for key, value in counts.items():
        if value > max_count:
            max_count = value
            ind = key
    return ind

# Forward Checking heuristic for lesson selection
def forward_checking(domain):
    return list(domain.keys())[0]

# Backtracking function for finding a solution
def backtrack(heuristic, domain, schedule):
    if not domain:
        return schedule
    ind = heuristic(domain)
    if ind == -1:
        return None
    for d in domain[ind]:
        sch_copy = copy(schedule)
        sch_copy.times.append(Time(d.day, d.time))
        sch_copy.classrooms.append(d.room)
        sch_copy.lessons.append(lessons[ind])

        dom_copy = copy(domain)
        dom_copy.pop(ind)
        dom_copy = update_domain(dom_copy, lessons[ind], d.day, d.time, d.room)

        res = backtrack(heuristic, dom_copy, sch_copy)
        if res:
            return res

    return None

# Update domains after selecting a lesson
def update_domain(domain, lesson, day, time, room):
    for key in domain:
        buf = []
        for d in domain[key]:
            if not (d.day == day and d.time == time and d.room == room) and not (
                d.day == day
                and d.time == time
                and (
                    lessons[key].teacher == lesson.teacher
                    or set(map(str, lessons[key].group)) & set(map(str, lesson.group))
                )
            ):
                buf.append(d)
        domain[key] = buf

    return domain

# Main function
def main():
    # Example data for creating a schedule
    classrooms = [
        Classroom(43, True),
        Classroom(42, True),
        Classroom(41, True),
        Classroom(228, False),
        Classroom(217, False),
        Classroom(206, False),
    ]

    schedule = [
        Time(w, n)
        for w in range(1, len(week_schedule.keys()) + 1)
        for n in range(1, len(week_schedule.keys()) + 1)
    ]

    teachers = [
        Teacher(name)
        for name in (
            "0 T1",
            "1 T2",
            "2 T3",
            "3 T4",
            "4 T5",
            "5 T6",
            "6 T7",
            "7 T8",
            "8 T9",
            "9 T10",
            "10 T11",
            "11 T12",
            "12 T13",
            "13 T14",
            "14 T15",
            "15 T16",
            "16 T17",
            "17 T18",
            "18 T19",
        )
    ]

    subjects = [
        Subject(name)
        for name in (
            "0 S1",
            "1 S2",
            "2 S3",
            "3 S4",
            "4 S5",
            "5 S6",
            "6 S7",
            "7 S8",
            "8 S9",
            "9 S10",
            "10 S11",
            "11 S12",
            "12 S13",
            "13 S14",
            "14 S15",
            "15 S16",
            "16 S17",
            "17 S18",
        )
    ]

    groups = [
        Group(name)
        for name in (
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
        )
    ]

    lessons = [
        Lesson(teachers[0], subjects[0], groups[0], False, 1),
        # ... (Other lessons)
    ]

    # Run MRV algorithm and print the schedule
    solution = run_mrv()
    print_schedule(solution)

    # Measure execution time for MRV
    start_time = time()
    run_mrv()
    print(f"\n\nMRV: {time() - start_time}")

    # Measure execution time for LCV
    start_time = time()
    run_lcv()
    print(f"LCV: {time() - start_time}")

    # Measure execution time for Degree heuristic
    start_time = time()
    run_degree()
    print(f"Degree: {time() - start_time}")

    # Measure execution time for Forward checking
    start_time = time()
    run_forward_checking()
    print(f"Forward checking: {time() - start_time}")

# Run the program
if __name__ == "__main__":
    main()
