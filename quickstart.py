import sqlite3
import calendar
import datetime
def get_date(todays_date=datetime.date.today() ,plus_days_amount=0):
    from datetime import datetime
    date = str(datetime.strptime(todays_date, '%y-%m-%d')
 + datetime.timedelta(days=plus_days_amount))
    date = date.split('-')
    date.reverse()
    return date[0] + '/' + date[1] + '/' + date[2]

def get_upcoming_dates(quantity):
    pass
def set_date(date):#creats a new date in dates table
    conn = sqlite3.connect('calendar.db')
    conn.execute('insert into dates (date, lessons_IDs, available_time_range) values (?,?,?)', (date,'','14:00-23:00'))
    conn.commit()


conn = sqlite3.connect('calendar.db')

def get_lesson_IDs(date):
    IDs = conn.execute("select lessons_IDs from dates where date=?", (date,))
    for row in IDs:
        IDs = row[0].split(',')
    return IDs

def get_Lesson_object(id):
    from Lesson import Lesson
    lesson = conn.execute("select * from lessons where ID=?", (id,))
    return Lesson(ID=lesson[0],
                  participant=lesson[1],
                  place=lesson[2],
                  time_range=lesson[3])

def get_Lesson_list(date):
    lessons=[]
    lessons_IDs = get_lesson_IDs(date)
    for id in lessons_IDs:
        lessons.append(get_Lesson_object(id))
    return lessons

import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'database.db')
print(my_file)