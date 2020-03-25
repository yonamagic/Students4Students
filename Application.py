from os import abort
from flask import Flask, render_template, request, session, redirect
# from flask_socketio import SocketIO
from Subject import Subject

from DataBaseFunctions import DataBaseFunctions
from User import User

app = Flask(__name__)
app.secret_key = 'secret_key'
# socketio = SocketIO(app)

#For registration page
# subjects = [Subject('Math',[10,11]), Subject('Arabic',[10,11,12]), Subject('History',[10])]

# SESSION_TYPE = 'redis'

# socketio = SocketIO(app)

# request.remote_addr   -    ip


@app.route('/ip')
def ip():
    return request.remote_addr

@app.route('/chat/<username1>/<username2>')
def chat(username1,username2):
            print(username1,username2)
    # if connected():
    #     if session['user'] == username1 or session['user'] == username2:
            return "username1="+username1+" username2="+username2 +\
                   render_template('typingChatRoom.html', username1='yoni', username2='aviv')
    # return "You cant get in"


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

# @socketio.on('my event')
# def handle_my_custom_event(json, methods=['GET', 'POST']):
#     print('received my event: ' + str(json))
#     socketio.emit('my response', json, callback=messageReceived)


#Just so I can determine the "Details incorrect" message
class staticVar:
    comment=""
    connected_username = ""


#Returns True if user is connected
def connected():
    return 'user' in session

@app.route('/', methods=['GET','POST'])
def index():
    # print(str(session['user']))
    staticVar.comment=""
    if connected():
        return render_template('homePage.html', user=session['user'])
    return render_template("index.html")

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template("about.html")


#This is just to make the red comment disappear
@app.route('/loginPage', methods=["POST","GET"])
def loginPage():
    staticVar.comment=""
    return redirect("/login" , code=302)

# @app.route('/ttt')
# def t():
#     session['new_messages'] = "ח"
#     return render_template("registeredLayout.html")

@app.route('/login', methods=["POST","GET"])
def login():
    return render_template("login.html", comment=staticVar.comment)



@app.route('/checkUserEntryDetails', methods=["POST" , "GET"])
def checkUserEntryDetails():
    username = request.form.get("username")
    password = request.form.get("password")
    correct = DataBaseFunctions.correctDetails(username,password)
    if correct == True:
        session['user'] = request.form.get("username")
        staticVar.connected_username = session['user']

        # return "Details are correct! You may login, " + username#Entry, I will write it later...
        return redirect('homePage', code=302)
    else:
        staticVar.comment = "שם המשתמש או הסיסמה שגויים, אנא נסו אחד אחר."
        return redirect('/login', code=302)

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['user']
    staticVar.connected_username = ""
    return redirect('/')


#First registration page,
@app.route('/register', methods=['POST','GET'])
def register(username="", username_comment="",
             password="", password_comment="",
             confirm_password="", confirm_password_comment="",
             email="", email_comment="",
             selected_strong_subjects=[], selected_weak_subjects=[]):

    return render_template('registerr.html',
                           username=username, password=password, confirm_password=confirm_password, email=email,
                           username_comment=username_comment,
                           password_comment=password_comment,
                           confirm_password_comment=confirm_password_comment,
                           email_comment=email_comment,
                           subjects=DataBaseFunctions.subjects_and_classes,
                           selected_strong_subjects=selected_strong_subjects,
                           selected_weak_subjects=selected_weak_subjects)




@app.route('/checkRegistration', methods=['POST','GET'])
def checkRegistration():
    details_dict = {
        'username' : request.form.get("username"),
        'username_comment' : "",
        'password': request.form.get("password"),
        'password_comment': "",
        'confirm_password' : request.form.get("confirm_password"),
        'confirm_password_comment': request.form.get("confirm_password_comment"),
        'email' : request.form.get("email"),
        'email_comment' : "",
        'strong_subjects': [],
        'weak_subjects': []
    }

    strong_subjects=[]
    for subject in DataBaseFunctions.subjects_and_classes:
        subject_name=subject[0]
        classes=[]
        for single_class in subject[1]:
            if request.form.get("strong_"+subject_name+"_"+single_class) == "on":
                classes.append(single_class)
        if classes:
            strong_subjects.append(Subject(subject_name, classes))

    weak_subjects=[]
    for subject in DataBaseFunctions.subjects_and_classes:
        subject_name=subject[0]
        classes=[]
        for single_class in subject[1]:
            if request.form.get("weak_"+subject_name+"_"+single_class) == "on":
                classes.append(single_class)
        if classes:
            weak_subjects.append(Subject(subject_name, classes))

    todo_bien = True#There are no problems in registration details

    if len(details_dict['username']) < 4 or len(details_dict['username']) > 14 or details_dict['username'].__contains__(' '):#username not in legal length
        details_dict['username_comment'] = "הקפידו ששם המשתמש הוא בין 4-14 תווים ואינו מכיל רווחים"
        todo_bien=False
    if details_dict['confirm_password'] != details_dict['password']:
        details_dict['confirm_password_comment'] = "מממ... הסיסמות לא תואמות ):"
        todo_bien=False
    if DataBaseFunctions.user_exists(details_dict['username']):#username taken
        details_dict['username_comment'] = "שם משתמש זה תפוס, בחרו כינוי שונה"
        todo_bien = False
    if len(details_dict['password']) < 8:#password is too short
        details_dict['password_comment'] = "בחרו סיסמה באורך מינימלי של 8 תווים"
        todo_bien = False
    if len(details_dict['email']) == 0:
        details_dict['email_comment']="אנא מלאו כתובת מייל תקנית"
        todo_bien=False
    if not details_dict['email'].__contains__('@'):
        details_dict['email_comment']="אנא מלאו כתובת מייל תקנית"
        todo_bien=False

    if details_dict['confirm_password_comment'] == None:
        details_dict['confirm_password_comment']=""

    if todo_bien==False:#Theres a problem
        return register(username=details_dict['username'],
                        password=details_dict['password'],
                        confirm_password=details_dict['confirm_password'],
                        email=details_dict['email'],
                        selected_strong_subjects=strong_subjects,
                        selected_weak_subjects=weak_subjects,
                        username_comment=details_dict['username_comment'],
                        password_comment=details_dict['password_comment'],
                        confirm_password_comment=details_dict['confirm_password_comment'],
                        email_comment=details_dict['email_comment']
                        )
#If it came here, everything is good
    DataBaseFunctions.create_user(username=request.form.get("username"),
                                  password=request.form.get("password"),
                                  email=request.form.get("email"),
                                  platform_nickname="",
                                  strong_subjects=strong_subjects,
                                  weak_subjects=weak_subjects)
    session['user'] = details_dict['username']
    # session['new_messages'] = 0
    # session['new_lesson_offers'] = 0
    return redirect('/homePage')#Every thing is ok, register me!



@app.route('/editProfile')
def editProfile():
    s=DataBaseFunctions.get_strong_subjects(session['user'])
    for i in s:
        print(i.name, i.classes)
    return render_template('editProfile.html',
                           subjects=DataBaseFunctions.subjects_and_classes,
                           selected_strong_subjects=DataBaseFunctions.get_strong_subjects(session['user']),
                           selected_weak_subjects=DataBaseFunctions.get_weak_subjects(session['user'])
                           )

@app.route('/profileEditingDone', methods=['POST'])
def profileEditingDone():
    strong_subjects = []
    for subject in DataBaseFunctions.subjects_and_classes:
        subject_name = subject[0]
        classes = []
        for single_class in subject[1]:
            if request.form.get("strong_" + subject_name + "_" + single_class) == "on":
                classes.append(single_class)
        if classes:
            strong_subjects.append(Subject(subject_name, classes))
    print("Hey!", ','.join(DataBaseFunctions.subjects_names(strong_subjects)))
    weak_subjects = []
    for subject in DataBaseFunctions.subjects_and_classes:
        subject_name = subject[0]
        classes = []
        for single_class in subject[1]:
            if request.form.get("weak_" + subject_name + "_" + single_class) == "on":
                classes.append(single_class)
        if classes:
            weak_subjects.append(Subject(subject_name, classes))

    DataBaseFunctions.edit_user_subjects(username=session['user'],
                                         strong_subjects=strong_subjects,
                                         weak_subjects=weak_subjects)
    return redirect('/profile?username='+session['user'])

@app.route('/homePage', methods=['POST','GET'])
def homePage():
    if connected():
        if DataBaseFunctions.is_admin(session['user']):
            session['is_admin'] = True
        else:
            session['is_admin'] = False
        return render_template('/homePage.html')
    return redirect('/')


@app.route('/profile' , methods=['POST','GET'])
def profile():
    username = request.args.get("username")# Just for now
    print("username = ", username)
    if not DataBaseFunctions.user_exists(username):
        return render_template('homePage.html', search_user_comment="שם משתמש לא קיים, נסו להזין אחד אחר.")
    print((session['user']))
    if not username or username==session['user']:#if there is no specified username or the specified name is sessin['user']
        username = session['user']
        # user = build_User_object(username)
        return render_template('personal_profile.html',
                               strong_subjects=DataBaseFunctions.get_strong_subjects(username),
                               weak_subjects=DataBaseFunctions.get_weak_subjects(username))
    else:#user exists and it is not session['user']

        return render_template('user_profile.html',
                               username=username,
                               strong_subjects = DataBaseFunctions.get_strong_subjects(username),
                               weak_subjects = DataBaseFunctions.get_weak_subjects(username),
                               is_friend = not DataBaseFunctions.is_friend(self_user = session['user'],
                                                                 username=username,),#It gets the opposite somewhy
                               friend_request_sent_already = DataBaseFunctions.is_in_friend_requests(self_user=username,
                                                                                                     username=session['user']))


@app.route('/report_user', methods=['POST','GET'])
def report():
    return render_template('reportUser.html', username=request.args.get("username"))

@app.route('/report_done', methods=['POST', 'GET'])
def report_done():
    username = request.args.get("username")
    report_content = request.form.get("report_content")
    # print(report_content)
    # print(username)
    DataBaseFunctions.report_user(username, report_content)
    return redirect('/profile?username=' + str(username))



# @app.route('/editProfile' , methods=['POST','GET'])
# def editProfilePage():
#     return render_template('/editProfile')
#
# @app.route('/applyProfileChanges' , methods=['POST','GET'])
# def applyProfileChanges:
#     #For now, it is not possible to edit username



@app.route('/potentialTeachers' , methods=['POST','GET'])
def potential__teachers():
    weak_subjects = DataBaseFunctions.get_weak_subjects(session['user'])
    return render_template('potential_teachers.html',
                           subjects=DataBaseFunctions.specific_teachers_for_all_subjects(weak_subjects))

    # subjects = DataBaseFunctions.subjects_as_list_of_Subjects(username=session['user'],
    #                                                           subs=DataBaseFunctions.get_weak_subjects(session['user']),
    #                                                           status='weak')
    # teachers = (DataBaseFunctions.teachers_by_subjects(DataBaseFunctions.potential_teachers(weak_subjects=subjects,
    #                                                                                         username=session['user'])))
    # print("teachers=",teachers)
    # return render_template('potentialTeachers.html',
    #                        DataBaseFunctions=DataBaseFunctions,
    #                        my_weak_subjects=DataBaseFunctions.get_weak_subjects(session['user']),
    #                        teachers=teachers,
    #                        my_username=session['user'])



@app.route("/inbox")
def inbox():
    return render_template("inbox.html")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html", notifications=DataBaseFunctions.get_all_notifications_as_list(session['user']))

@app.route("/notifications/view_note/<note_id>")
def view_note(note_id):
    return render_template("view_note.html", notification=DataBaseFunctions.get_notification_object(note_id))

@app.route('/messages', methods=['POST', 'GET'])
def messages():
    if not connected():
        return redirect('/')
    messages_list = DataBaseFunctions.messages_list(session['user'])#Because there are 2 additional Messages that I do not know why theyre in there
    messages_list.reverse()
    # print("read="+messages_list[0].is_read)
    return render_template('messages.html', messages = messages_list)

@app.route('/sendMessage')
def sendMessage(addressee="", topic="", content="", addressee_comment=""):
    print("comment="+addressee_comment)
    return render_template('sendMessage.html',
                           addressee_comment=addressee_comment,
                           addressee=addressee,
                           topic=topic,
                           content=content)

@app.route('/messageSent', methods=['POST', 'GET'])
def messageSent():
    sender = session['user']
    addressee = request.form.get("addressee")
    topic = request.form.get("topic")
    content = request.form.get("content")
    if not DataBaseFunctions.user_exists(addressee):
        print("user does not exist")
        return sendMessage(addressee=addressee,
                           topic=topic,
                           content=content,
                           addressee_comment="השם הזה לא קיים במערכת, נסו אחד אחד.")
    print("User indeed exists")

    DataBaseFunctions.send_msg(sender=sender,
                               addressee = addressee,
                               topic=topic,
                               content=content)
    return redirect('/messages')

@app.route('/viewMessage', methods=['POST','GET'])
def viewMessage():
    # msg_id = request.args.get("msg_id")
    msg = DataBaseFunctions.get_message(request.args.get("msg_id"))
    DataBaseFunctions.make_msg_read(request.args.get("msg_id"))
    return render_template('viewMessage.html',
                           sender=msg.sender,
                           topic=msg.topic,
                           content=msg.content)

@app.route('/friends_list')
def friends_list():
    print((DataBaseFunctions.get_friends_list(session['user'])))
    return render_template('friends_list.html', users=DataBaseFunctions.get_friends_list(session['user']))

@app.route('/send_friend_request')
def send_friend_request():
    username = request.args.get("username")
    if not DataBaseFunctions.is_friend(self_user=session['user'],
                                       username=username):
        DataBaseFunctions.add_to_friend_requests(self_user=username,
                                                 username=session['user'])
    return redirect('/profile?username=' + username)

@app.route('/add_to_friends_list')
def add_to_friends_list():
    username = request.args.get("username")
    DataBaseFunctions.add_to_friends_list(self_user = session['user'],
                                       username = username)
    return redirect('/profile?username=' + username)

@app.route('/remove_from_friends_list')
def remove_from_friends_list():
    username = request.args.get("username")
    DataBaseFunctions.remove_from_friends_list(self_user = session['user'],
                                       username = username)
    DataBaseFunctions.remove_from_friends_list(self_user=username,
                                               username=session['user'])
    return redirect('/profile?username=' + username)

@app.route('/friend_requests')
def view_friend_requests():
    return render_template('view_friend_requests.html', users=DataBaseFunctions.get_friend_requests(session['user']))

@app.route('/accept_friend_request', methods=['GET'])
def accept_friend_request():
    username = request.args.get("username")
    DataBaseFunctions.add_to_friends_list(session['user'], username)
    DataBaseFunctions.add_to_friends_list(username, session['user'])
    DataBaseFunctions.remove_from_friend_requests(session['user'], username)
    return redirect('/friend_requests')

@app.route('/deny_friend_request', methods=['GET'])
def deny_friend_request():
    username = request.args.get("username")
    if DataBaseFunctions.is_in_friend_requests(session['user'], username):
        DataBaseFunctions.remove_from_friend_requests(session['user'], username)
    return redirect('/friend_requests')

@app.route('/cancel_friend_request', methods=['GET'])
def cancel_friend_request():
    username = request.args.get("username")
    if DataBaseFunctions.is_in_friend_requests(self_user=username,
                                                   username=session['user']):
        DataBaseFunctions.remove_from_friend_requests(username, session['user'])
    return redirect('/profile?username=' + username)

@app.route('/forum_homepage')
def forum_homepage():
    if connected():
        return render_template('forum_homepage.html', forum_names=DataBaseFunctions.get_forum_names())
    return redirect('/')

@app.route('/forum/<forum_name>')
def specific_forum(forum_name):
    return render_template('specific_forum.html', forum_name=forum_name, posts=DataBaseFunctions.get_forum_posts(forum_name))

@app.route('/forum/<forum_name>/create_post')
def create_post(forum_name):
    return render_template('create_new_post.html', forum_name=forum_name)

@app.route('/forum/<forum_name>/new_post_submitted', methods=['POST'])
def new_post_submitted(forum_name):
    topic = request.form.get("topic")
    content = request.form.get("content")
    DataBaseFunctions.create_new_post(forum_name=forum_name,
                                      narrator=session['user'],
                                      topic=topic,
                                      content=content)
    return redirect('/forum/' + forum_name)


@app.route('/post/<post_id>')
def view_post(post_id):
    # print(DataBaseFunctions.get_post_object(post_id).topic)
    return render_template('view_post.html', post=DataBaseFunctions.get_post_object(post_id), post_id=post_id)

@app.route('/post/write_comment/<post_id>')
def write_comment(post_id):
    return render_template('write_comment.html', post_id=post_id)

@app.route('/post/comment_sent/<post_id>', methods=['POST'])
def comment_sent(post_id):
    content = request.form.get("content")
    DataBaseFunctions.add_comment(post_id=post_id,
                                  content=content,
                                  narrator=session['user'])
    return redirect('/post/'+post_id)

@app.route("/admin_options")
def admin_options():
    return render_template("admin_options.html")

@app.route("/admin_options/view_reports")
def view_reports():
    return render_template("view_reports_by_usernames.html", reported_users=DataBaseFunctions.get_reports_dict_list())
    #DataBaseFunctions.get_list_of_reported_usernames())

@app.route("/view_user_reports")
def view_user_reports():
    username = request.args.get("username")
    return render_template("view_user_reports.html", reports=DataBaseFunctions.get_reports_list(username))

@app.route("/admin_options/send_notification", methods=['POST','GET'])
def send_notification():
    return render_template("send_notification.html")

@app.route("/admin_options/send_notification/notification_sent", methods = ['POST','GET'])
def notification_sent():
    topic = request.form.get("topic")
    content= request.form.get("content")
    DataBaseFunctions.send_notification_to_all_users(topic=topic, content=content)
    return redirect("/admin_options")


@app.route('/admin_options/admin_messages', methods=['GET'])
def admin_messages():
    messages = DataBaseFunctions.admins_messages_list()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin_options/admin_messages/view_admin_msg/<msg_id>')
def view_admin_msg(msg_id):
    msg = DataBaseFunctions.get_message(msg_id)
    DataBaseFunctions.make_msg_read(msg_id)
    return render_template('view_admin_msg.html',
                           sender=msg.sender,
                           topic=msg.topic,
                           content=msg.content)

@app.route('/teacher_or_students_offer_lesson/<username>')
def teacher_or_students_offer_lesson(username):
    return render_template('teacher_or_student_lesson_offer.html', username=username)

#/<selected_platform>/<selected_date>/<selected_timeA>/<selected_timeB>/<error_msg>
@app.route('/offer_lesson/<username>/<teacher>', methods=['GET'])
def offer_lesson(username, teacher, selected_platform="",  selected_date="", selected_timeA="", selected_timeB="", selected_subject="", free_text="", error_msg=""):
    import Calendar_Functions
    subjects_list=[]
    if teacher == "True":
        print(teacher)
        subjects_list = DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_strong_subjects(session['user']),
                                                       subs2=DataBaseFunctions.get_weak_subjects(username))#מה שמשותף למקצועות החזקים של סשן והחלשים של יוזר
    else:
        subjects_list = DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_weak_subjects(session['user']),
                                                       subs2=DataBaseFunctions.get_strong_subjects(username))#מה שמשותף למקצועות חלשים של סשן והחזקים של יוזר
    return render_template('offer_lesson.html',
                           username=username,
                           Im_the_teacher=teacher,
                           subjects_list=subjects_list,
                           platforms=['Skype', 'Zoom'],
                           dates=Calendar_Functions.get_upcoming_dates(),
                           timesA=Calendar_Functions.get_times_for_lessons(),
                           timesB=Calendar_Functions.get_times_for_lessons(),
                           selected_platform=selected_platform,
                           selected_date=selected_date,
                           selected_timeA=selected_timeA,
                           selected_timeB=selected_timeB,
                           selected_subject=selected_subject,
                           free_text=free_text,
                           error_msg=error_msg
                           )

@app.route('/process_lesson_request/<username>/<teacher>', methods=['POST','GET'])
def process_lesson_request(username, teacher):
    import Calendar_Functions
    print("username=",username)
    if teacher == "False":
        teacher = username
    else:
        teacher = session['user']
    platform = request.form.get("platforms_list")
    date = request.form.get("dates")
    from_time = request.form.get("from_time_list")
    until_time = request.form.get("until_time_list")
    selected_subject = request.form.get("subjects_list")
    print("yoooooo", selected_subject)
    free_text = request.form.get("free_text")
    if free_text is None:
        free_text = ""

    #בדיקת תקינות של הפרטים שהוכנסו
    todo_bien = True
    if not Calendar_Functions.is_after(until_time,from_time):
        error_msg = "אנא בחר טווח שעות הגיוני"
        todo_bien=False
    #---------------------------------------------------------סיום בדיקת תקינות
    if not todo_bien:
        return offer_lesson(username=username,
                            teacher=teacher,
                            selected_subject=selected_subject,
                            selected_platform=platform,
                            selected_date=date,
                            selected_timeA=from_time,
                            selected_timeB=until_time,
                            free_text=free_text,
                            error_msg=error_msg)
    # Calendar_Functions.create_new_lesson(participants=str(session['user'])+','+username,
    #                                      location=platform,
    #                                      date=date,
    #                                      time_range=from_time+'-'+until_time
    #                                      )
    DataBaseFunctions.send_lesson_request(platform=platform,
                                          date=date,
                                          from_user=session['user'],
                                          to_user=username,
                                          teacher=teacher,
                                          subject=selected_subject,
                                          time_range=from_time+'-'+until_time,
                                          free_text=free_text)
    return redirect('/profile?username='+username)

@app.route('/accept_lesson_offer/<ID>')
def accept_lesson_offer(ID):
    (DataBaseFunctions.accept_lesson_offer(username=session['user'],
                                          id = ID))
    return redirect("/view_lessons_offers")

@app.route('/deny_lesson_offer/<ID>')
def deny_lesson_offer(ID):
    (DataBaseFunctions.deny_lesson_offer(username=session['user'],
                                          id = ID))
    return redirect("/view_lessons_offers")


@app.route('/view_lessons_offers')
def lessons_offers():
    return render_template('view_lessons_offers.html',
                           lessons_offers=DataBaseFunctions.get_lessons_offers_as_list(session['user']))

@app.route('/view_lessons_offers/single_offer/<offer_id>')
def view_a_single_lesson_offer(offer_id):
    offer = DataBaseFunctions.get_lesson_offer_object(offer_id)
    return render_template('view_a_single_lesson_offer.html',
                           offer=offer,
                           platform_nickname=DataBaseFunctions.get_platform_nickname(offer.from_user))

@app.route('/my_lessons')
def my_lessons():
    return render_template('my_lessons.html', DataBaseFunctions=DataBaseFunctions,
                                               lessons=DataBaseFunctions.get_lessons(username=session['user']),
                           todays_date=DataBaseFunctions.get_date()[:-2])

@app.route('/my_lessons/<lesson_ID>')
def view_one_lesson(lesson_ID):
    lesson = DataBaseFunctions.get_lesson_by_ID(lesson_ID)
    return render_template("view_a_single_lesson.html",
                           lesson=lesson,
                           todays_date=DataBaseFunctions.get_date()[:-2],
                           platform_nickname = DataBaseFunctions.get_platform_nickname(
                               username=DataBaseFunctions.get_other_user_username(lesson=lesson,
                                                                                  self_username=session['user'])))
@app.route('/my_lessons/cancel_lesson/<lesson_ID>')
def cancel_lesson(lesson_ID):
    DataBaseFunctions.cancel_lesson(lesson_ID)
    return redirect('/my_lessons')
if __name__ == '__main__':
    app.run(debug=True)#, host='0.0.0.0')