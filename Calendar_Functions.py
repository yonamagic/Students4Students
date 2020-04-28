import sqlite3
from _datetime import datetime, timedelta
from DataBaseFunctions import DataBaseFunctions

#פעולות שעוסקות ביצירת שיעורים
#---------------------------------------------------------------------------------------------------------------------
def create_new_lesson(participants, location, date, time_range, subject, teacher):#Creates a new lesson in DB
    conn = sqlite3.connect('calendar.db')
    date_ID = such_date_exists(date, location)
    if not date_ID:
        date_ID = create_new_date(date=date,
                                  place=location)
    lesson_ID = DataBaseFunctions.random_id()
    create_lesson_in_dates_table(date_ID, lesson_ID)
    create_lesson_in_lessons_table(ID=lesson_ID,
                                   location=location,
                                   date=date,
                                   subject=subject,
                                   participants=participants,
                                   teacher=teacher,
                                   time_range=time_range)
    return lesson_ID

#returns False if there is no such date in table, or the date_ID if there is
def such_date_exists(date, location):
    conn = sqlite3.connect('calendar.db')
    date_ID = conn.execute("SELECT ID FROM dates WHERE date = ? and place=?;", (date,location))
    for row in date_ID:
        return row[0]
    return False

#יוצרת date חדש בטבלת הdates
def create_new_date(date, place):
    conn = sqlite3.connect('calendar.db')
    id = DataBaseFunctions.random_id()
    conn.execute("insert into dates "
                 "(ID, date, place, lessons_IDs) "
                 "values (?,?,?,'')",
                 (id, date, place))
    conn.commit()
    return id

# יוצרת שיעור חדש בטבלת השיעורים
def create_lesson_in_lessons_table(ID, location, date, subject, participants, teacher, time_range):#Responsible for lesson creation in lessons table
    conn = sqlite3.connect('calendar.db')
    conn.execute("insert into lessons (ID, place, date, subject, participants, teacher, time_range, active) values (?,?,?,?,?,?,?,'True')",
                 (ID, location, date, subject, participants, teacher, time_range))
    conn.commit()

# יוצרת שיעור חדש בטבלת dates
def create_lesson_in_dates_table(date_ID, lesson_ID):#Responsible for lesson creation in dates table
    conn = sqlite3.connect('calendar.db')
    lessons_IDs = conn.execute("select lessons_IDs from dates where ID=?", (date_ID,))
    for row in lessons_IDs:
        lessons_IDs=row[0]
    if len(lessons_IDs) > 0:
        lessons_IDs += ',' + lesson_ID
    else:
        lessons_IDs = lesson_ID

    conn.execute("update dates set lessons_IDs = ? where ID=?", (lessons_IDs,date_ID))
    conn.commit()

#---------------------------------------------------------------------------------------------------------------------

#פעולות שעוסקות בטיפוס Lesson
#---------------------------------------------------------------------------------------------------------------------
# מחזזירה רשימה של כל השיעורים של משתמש מסויים
def get_lessons_list(username):
    conn = sqlite3.connect('calendar.db')
    command = conn.execute("select ID from lessons")
    all_IDs=[]
    for row in command:
        all_IDs.append(row[0])
#________got a list of all IDs

    wanted_lessons_IDs=[]
    for ID in all_IDs:
        participants = conn.execute("select participants from lessons where ID=?", (ID,))
        for row in participants:
            participants=row[0]
        if username in participants:
            wanted_lessons_IDs.append(ID)
    #____________got a list of wanted lessons' IDs

    wanted_lessons=[]
    for lesson in wanted_lessons_IDs:
        wanted_lessons.append(get_Lesson_Object(lesson))

    #_________ got a list of those lessons as objects
    return wanted_lessons

#מחזירה עצם Lesson לפי הID
def get_Lesson_Object(ID):#Returns a Lesson object
    from Lesson import Lesson
    conn = sqlite3.connect('calendar.db')
    lesson = conn.execute("select * from lessons where ID=?", (ID,))
    for row in lesson:
        lesson=row

    return Lesson(ID=lesson[0],
                  date=lesson[1],
                  location=lesson[2],
                  participants=lesson[3],
                  time_range=lesson[4])

#---------------------------------------------------------------------------------------------------------------------


def get_lesson_id(place, date, participants, time_range):#Returns a lesson ID according to details in params
    conn = sqlite3.connect('calendar.db')
    id = conn.execute("select ID from lessons where place=? and date=? and participants=? and time_range=?",
                 (place,date,participants,time_range))
    for row in id:
        id=row[0]
    return id

def cancel_lesson(date, place, participants, time_range):#Cancels a lesson by deleting its information from DB
    conn = sqlite3.connect('calendar.db')
    lesson_ID = get_lesson_id(place, date, participants, time_range)
    conn.execute("delete from lessons where place=? and date=? and participants=? and time_range=?",
                 (place,date,participants,time_range))
    lessons_IDs = conn.execute("select lessons_IDs from dates where date=? and place=?", (date,place))
    for row in lessons_IDs:
        lessons_IDs=row[0]
    lessons_IDs = lessons_IDs.split(',')
    print(lessons_IDs)
    lessons_IDs.remove(lesson_ID)
    lessons_IDs = ','.join(lessons_IDs)
    print(lessons_IDs)
    print("hi")
    conn.execute("update dates set lessons_IDs = ? where date=? and place=?", (lessons_IDs, date, place))
    conn.commit()

#---------------------------------------------------------------------------------------------------------------------


#פעולות העוסקות בתאריכים וזמנים
#---------------------------------------------------------------------------------------------------------------------
#מקבלת תאריך מסוג datetime ומחזירה אותו כמחרוזת
def convert_datetime_to_date(datetime_date):
    date = (str(datetime_date)).split(' ')[0].split('-')
    return date[2] + '/' + date[1] + '/' + date[0][2:]


def get_upcoming_dates(num_of_days_ahead=7):#Returns a list of dates ahead of us. param@ includes today.
    dates=[]
    for i in range(num_of_days_ahead):
        dates.append(convert_datetime_to_date(datetime.now()+timedelta(days=i)))
    return dates

#returns a list of times (as strings) in a certain range, with a certain jump
def get_times_for_lessons(range='08:00-22:00', jumps_ranges=15):
    times = []
    min_hr = range.split('-')[0]
    max_hr = range.split('-')[1]
    index = min_hr

    while datetime.strptime(index, '%H:%M') < datetime.strptime(max_hr, '%H:%M') and \
            datetime.strptime(index, '%H:%M') >= datetime.strptime(min_hr, '%H:%M'):
        new_index = str(datetime.strptime(index, '%H:%M') + timedelta(minutes=jumps_ranges))
        new_index = new_index[new_index.index(' ') + 1:new_index.index(':') + 3]
        index = new_index
        times.append(index)

    return times


def is_after(time1, time2):#Returns True if time1 is after time2
    return datetime.strptime(time1, '%H:%M') > datetime.strptime(time2, '%H:%M')

#Returns True if date1 is after date2
def date_is_after(date1, date2):
    return datetime.strptime(date1, '%d/%m/%y') > datetime.strptime(date2, '%d/%m/%y')

#מחזיר את הפרש הזמנים בדקות
def time_range_length(from_time, until_time):
    difference = str(datetime.strptime(until_time, '%H:%M') - datetime.strptime(from_time, '%H:%M'))
    minutes = int(difference[difference.find(":")+1:difference.rfind(":")])
    hours = int(difference[:difference.find(":")]) * 60
    return (hours+minutes)
#---------------------------------------------------------------------------------------------------------------------
