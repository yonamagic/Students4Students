import calendar
import sqlite3
import datetime


time_ranges = ['14:00-15:00','15:15-16:15','16:30-17:30','17:45-18:45','19:00-20:00','20:15-21:15']
locations = ['בית_המתנדב']

def lessons_in_this_place(place):
  conn = sqlite3.connect('database.db', timeout=2)
  command = conn.execute("select * from schedule where place=?", (place,))
  lessons_in_this_place = []
  for row in command:
    lessons_in_this_place.append(row)
  return lessons_in_this_place

# def get_datetime_type(date, time):#"dd/mm/yy" , "hh:mm"
#   return datetime.strptime(date + ' ' + time, '%d/%m/%y %H:%M')

def get_hr_datetime_type(time):#"dd/mm/yy" , "hh:mm"
  from datetime import datetime
  return datetime.strptime(time, '%H:%M')


def is_available(date, time_range):#Recieves details of a meetup and
                                                          # returns if the lesson's time range is available
  from datetime import datetime
  conn = sqlite3.connect('database.db', timeout=2)
  command = conn.execute("select * from schedule where date=?", (date,))
  lessons=[]
  for row in command:
    lessons.append(row)
  for lesson in lessons:
    if lesson[2] == time_range:
      return False

  return True


def get_available_time_ranges(date):
  avl_time_ranges = []
  for time_range in time_ranges:
    if is_available('some day', time_range):
      avl_time_ranges.append(time_range)
    return avl_time_ranges

def get_Day(place, date): #recieves place and date and returns a Day object
  from Day import Day
  day = Day(place, date)
  conn = sqlite3.connect('database.db', timeout=2)
  command = conn.execute("select * from schedule where date=?", (date,))
  for row in command:
    day.taken_time_ranges.append(row[1])
    day.available_time_ranges.remove(row[1])
  return day







# print(get_Day("today").taken_time_ranges, get_Day("today").available_time_ranges)
# def is_totally_available(place, date, time_range):#Recieves details of a meetup and
#                                                           # returns if the lesson's time range is available
#   from datetime import datetime
#   conn = sqlite3.connect('database.db', timeout=2)
#   command = conn.execute("select * from schedule where place=? and date=?", (place, date))
#   lessons=[]
#   for row in command:
#     lessons.append(row)
#
#   from_hr = get_hr_datetime_type(time_range[0:5])
#   until_hr = get_hr_datetime_type(time_range[6:])
#
#
#   for lesson in lessons:
#     hrs_range = lesson[2]
#     lesson_from_hr = get_hr_datetime_type(hrs_range[0:5])
#     lesson_until_hr = get_hr_datetime_type(hrs_range[6:])
#     # if lesson_from_hr<from_hr and from_hr<lesson_until_hr:
#     # if lesson_from_hr<until_hr and until_hr<lesson_until_hr:
#     if from_hr==lesson_from_hr and until_hr==lesson_until_hr:
#       return False
#
#   return True



