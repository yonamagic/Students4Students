import sqlite3

conn = sqlite3.connect('calendar.db')


def random_id():
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))


def add_lesson(place, date, time_range, participants):
    lesson_ID = random_id()
    date_ID = conn.execute("select ID from dates where date=?", (date,))
    for row in date_ID:
        date_ID=row[0]

    create_lesson_in_lessons_table(lesson_ID, place, date, participants, time_range)
    create_lesson_in_dates_table(date_ID,lesson_ID)
    create_lesson_in_places_table(place, date_ID)


def create_lesson_in_lessons_table(id, place, date, participants, time_range):
    conn.execute("insert into lessons (ID, place, date, participants, time_range) values (?,?,?,?,?)",
                                                                    (id,place,date,participants,time_range))
    conn.commit()

def create_lesson_in_dates_table(date_ID, lesson_ID):
    lessons_IDs = conn.execute("select lessons_IDs from dates where ID=?", (date_ID,))
    for row in lessons_IDs:
        lessons_IDs=row[0]
    lessons_IDs += ',' + lesson_ID
    conn.execute("update dates set lessons_IDs = ? where ID=?",
                                                                    (lessons_IDs,date_ID))
    conn.commit()

def create_lesson_in_places_table(place, date_ID):
    dates_IDs = conn.execute("select dates_IDs from places where location=?", (place,))
    for row in dates_IDs:
        dates_IDs = row[0]
    dates_IDs += ',' + date_ID
    conn.execute("update places set dates_IDs=? where location=?", (dates_IDs,place))
    conn.commit()

# add_lesson("בית המתנדב", "06/03/20", "16:00-17:00", "yonamagic,aviv")