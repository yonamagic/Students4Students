from os import abort

import werkzeug
from flask import Flask, render_template, request, session, redirect, g
from Subject import Subject
# from Emailing import Emailing
from DataBaseFunctions import DataBaseFunctions
# from User import User

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/uu')
def uu():
    return render_template('typingChatRoom.html')

@app.route('/check', methods=['POST'])
def c():
    return request.form.get("uu")

@app.route('/currently_online')
def currently_online():
    if 'user' not in session:
        return redirect('/')
    usernames = DataBaseFunctions.get_all_users_online()
    usernames.remove(session['user'])
    return render_template('currently_online.html',
                            currently_online = usernames)

@app.route('/forgot_password')
def forgot_password(error_msg=''):
    return render_template('forgot_password.html', error_msg=error_msg)

@app.route('/forgot_password_done', methods=['POST'])
def forgot_password_done():
    username = request.form.get("username")
    if not DataBaseFunctions.user_exists(username):
        return forgot_password(error_msg="מממ... נראה שלא קיים משתמש שנקרא כך. בדקו אם הזנתם שם משתמש תקין.")
    DataBaseFunctions.send_pwd_reset(username=username, email=DataBaseFunctions.get_email(username))
    return render_template('mid_reload_page.html', msg="נשלחה לחשבון המייל שלך הודעה לשינוי הסיסמה לאתר Syeto. \r\n מיד תועבר/י לדף הבית.", delay="10", url="/")

@app.route('/reset_password/<secret_key>')
def reset_password(secret_key, error_msg=""):
    if not DataBaseFunctions.pwd_reset_request_is_active(secret_key):
        return render_template('mid_reload_page.html', msg="נראה שהקישור הזה לא תקין או שאינו תקף יותר. אם שכחת את הסיסמה, ניתן לאפס אותה בדף ההתחברות. אנו מפנים אותך לדף הבית...", delay="8", url="/")#Continue here with a msg
    return render_template('reset_password.html', secret_key=secret_key, error_msg=error_msg)


@app.route('/password_reset_done/<secret_key>', methods=['POST'])
def reset_password_done(secret_key):
    pwd = request.form.get("pwd")
    pwd_conf = request.form.get("pwd_conf")
    todo_bien = True

    if pwd != pwd_conf:
        todo_bien = False
        error_msg = "יש להזין סיסמות זהות, אנא נסו שוב."
    if len(pwd) < 7:
        todo_bien = False
        error_msg = "יש להזין סיסמה שאורכה גדול משבעה תווים."

    if todo_bien:
        DataBaseFunctions.reset_password(username=DataBaseFunctions.get_username_by_secret_key(secret_key),
                                         new_password=pwd)
        return render_template('mid_reload_page.html', msg="סיסמתך שונתה בהצלחה! \r\n את/ה מועבר/ת לעמוד ההתחברות.", delay="5", url="/loginPage")
        #כאן תהיה הודעה מתאימה

    else:
        return reset_password(secret_key=secret_key, error_msg=error_msg)


@app.route('/u')
def pro():
    weak_subjects = DataBaseFunctions.get_weak_subjects("nir_selickter")

    return render_template('poten.html',
                           subjects=DataBaseFunctions.specific_users_for_all_subjects(weak_subjects, 'teacher'),
                           teachers_or_students = 'teachers'
                           )

@app.route('/ip')
def ip():
    return request.remote_addr


#Just so I can determine the "Details incorrect" message
class staticVar:
    comment=""
    connected_username = ""


#Returns True if user is connected
def connected():
    return 'user' in session


# מוחק את הצעות השיעורים מטבלת הusres אם הן לא עדכניות
# עושה זאת גם אם נקבעו שיעורים אחרים בזמנים חופפים
@app.before_request
def update_lessons_offers():
    if 'user' in session:
        DataBaseFunctions.update_lessons_offers_that_have_passed(session['user'])
        DataBaseFunctions.update_lessons_offers_that_are_no_longer_relevant(session['user'])

# מעדכן את זמן ההתחברות האחרון של המשתמש
@app.before_request
def update_last_login():
    if 'user' in session:
        DataBaseFunctions.update_last_login(session['user'])

# מעדכן את ערכי ההודעות החדשות (כל מה שיש בInbox) ב-session
@app.before_request
def update_lessons_requests_quantity():
    if 'user' in session:
        session['new_lessons_offers'] = DataBaseFunctions.number_of_lessons_requests(session['user'])
        session['new_messages'] = DataBaseFunctions.number_of_new_messages(session['user'])
        session['new_friend_requests'] = DataBaseFunctions.number_of_friend_requests(session['user'])
        session['lessons'] = DataBaseFunctions.number_of_lessons(session['user'])

@app.route('/', methods=['GET','POST'])
def index():

    # DataBaseFunctions.update_new_lessons_requests(session)
    # return session['user']
    # print(str(session['user']))
    staticVar.comment=""
    if connected():
        return render_template('homePage.html', user=session['user'])
    return render_template("index.html")






#This is just to make the red comment disappear
@app.route('/loginPage', methods=["POST","GET"])
def loginPage():
    staticVar.comment=""
    return redirect("/login" , code=302)

# @app.route('/ttt')
# def t():
#     session['new_messages'] = "ח"
#     return render_template("registeredLayout1.html")

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
    if 'user' in session:
        del session['user']
        staticVar.connected_username = ""
        return redirect('/')

    else:
        staticVar.connected_username = ""
        return redirect('/')


#First registration page,
@app.route('/register', methods=['POST','GET'])
def register(username="", username_comment="",
             password="", password_comment="",
             confirm_password="", confirm_password_comment="",
             email="", email_comment="",
             agree_to_terms_checked="", agree_to_terms_message="",
             selected_strong_subjects=[], selected_weak_subjects=[]):
    return render_template('reg.html',
                           username=username, password=password, confirm_password=confirm_password, email=email,
                           username_comment=username_comment,
                           password_comment=password_comment,
                           confirm_password_comment=confirm_password_comment,
                           email_comment=email_comment,
                           agree_to_terms_checked=agree_to_terms_checked,
                           agree_to_terms_message = agree_to_terms_message,
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
        'agree_to_terms_message' : "",
        'agree_to_terms_checked' : True,
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

    if request.form.get("agree_to_terms") == None:
        todo_bien = False
        details_dict['agree_to_terms_message'] = "כדי ליצור משתמש, יש להסכים לתנאי השימוש באתר."

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
                        email_comment=details_dict['email_comment'],
                        agree_to_terms_checked=request.form.get("agree_to_terms"),
                        agree_to_terms_message = details_dict['agree_to_terms_message']                        
                        )
#If it came here, everything is good
    DataBaseFunctions.create_user(username=request.form.get("username"),
                                  password=request.form.get("password"),
                                  email=request.form.get("email"),
                                  platform_nickname="",
                                  strong_subjects=strong_subjects,
                                  weak_subjects=weak_subjects)
    session['user'] = details_dict['username']
    # session['new_lessons_requests'] = 0
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
        # session['new_lessons_requests'] = 0

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

    if 'user' in session:
        if not username or username==session['user']:#if there is no specified username or the specified name is sessin['user']
            username = session['user']
            # user = build_User_object(username)
            return render_template('personal_profile.html',
                                   strong_subjects=DataBaseFunctions.get_strong_subjects(username),
                                   weak_subjects=DataBaseFunctions.get_weak_subjects(username))
        elif not DataBaseFunctions.is_admin(username):#user exists and it is not session['user']
            return render_template('user_profile.html',
                                   username=username,
                                   strong_subjects = DataBaseFunctions.get_strong_subjects(username),
                                   weak_subjects = DataBaseFunctions.get_weak_subjects(username),
                                   is_friend = not DataBaseFunctions.is_friend(self_user = session['user'],
                                                                     username=username,),#It gets the opposite somewhy
                                   friend_request_sent_already = DataBaseFunctions.is_in_friend_requests(self_user=username,
                                                                                                         username=session['user']),
                                   chance_for_a_lesson=DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_strong_subjects(session['user']),
                                                                                    subs2=DataBaseFunctions.get_weak_subjects(username))
                                                        or  DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_weak_subjects(session['user']),
                                                                                        subs2=DataBaseFunctions.get_strong_subjects(username)))
        else:
            return render_template('admin_profile.html',
                                   username=username,
                                   is_friend = not DataBaseFunctions.is_friend(self_user = session['user'],
                                                                     username=username,),#It gets the opposite somewhy
                                   friend_request_sent_already = DataBaseFunctions.is_in_friend_requests(self_user=username,
                                                                                                         username=session['user']))
    return redirect('/')

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



@app.route('/potential_teachers' , methods=['POST','GET'])
def potential__teachers():
    weak_subjects = DataBaseFunctions.get_weak_subjects(session['user'])
    return render_template('potential_teachers_or_students.html',
                           subjects=DataBaseFunctions.specific_users_for_all_subjects(weak_subjects, 'teacher'),
                           teachers_or_students = 'teachers')


@app.route('/potential_students' , methods=['POST','GET'])
def potential__students():
    strong_subjects = DataBaseFunctions.get_strong_subjects(session['user'])
    return render_template('potential_teachers_or_students.html',
                           subjects=DataBaseFunctions.specific_users_for_all_subjects(strong_subjects, 'student'),
                           teachers_or_students='students')



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

@app.route('/sendMessage', methods=['GET'])
def sendMessage(addressee="", topic="", content="", addressee_comment=""):
    if 'user' in session:
        print("comment="+addressee_comment)
        if request.args.get("addressee"):
            addressee=request.args.get("addressee")
        if request.args.get("topic"):
            topic=request.args.get("topic")
        if request.args.get("content"):
            content=request.args.get("content")
        return render_template('sendMessage.html',
                               addressee_comment=addressee_comment,
                               addressee=addressee,
                               topic=topic,
                               content=content)
    else:
        return redirect('/index')


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
    msg_id = request.args.get("msg_id")
    if connected():
        if DataBaseFunctions.whos_msg_is_this(msg_id) != session['user']:
            return redirect('/messages')
        else:
            msg = DataBaseFunctions.get_message(msg_id)
            DataBaseFunctions.make_msg_read(request.args.get("msg_id"))
            return render_template('viewMessage.html',
                                   sender=msg.sender,
                                   topic=msg.topic,
                                   content=msg.content)
    else:
        return redirect('/')
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
    if DataBaseFunctions.is_in_friend_requests(session['user'], username):
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
    if not DataBaseFunctions.forum_exists(forum_name):
        return redirect('/forum_homepage')
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
    if DataBaseFunctions.post_is_deleted(post_id):
        if 'user' in session:
            # print("USERNAME is ", session['user'])
            if DataBaseFunctions.is_admin(session['user']):
                return render_template('view_post.html', post=DataBaseFunctions.get_post_object(post_id),
                                       post_id=post_id)
        return redirect('/forum_homepage')
    else:
        return render_template('view_post.html', post=DataBaseFunctions.get_post_object(post_id),
                                                   post_id=post_id)
@app.route('/report_post/<post_id>')
def report_post(post_id):
    return render_template('report_post.html', post_id=post_id)

@app.route('/post_report_done', methods=['POST','GET'])
def post_report_done():
    post_id = request.args.get("post_id")
    content = request.form.get("report_content")
    forum = DataBaseFunctions.get_forum_name_by_post_id(post_id)
    DataBaseFunctions.report_post(post_id=post_id, content=content, forum=forum)
    return redirect('/post/' + post_id)


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
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            return render_template("admin_options.html")
    return redirect('/homePage')

@app.route("/admin_options/view_reports")
def view_reports():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            return render_template("view_reports_by_usernames.html", reported_users=DataBaseFunctions.get_reports_dict_list())
    return redirect('/homePage')
    #DataBaseFunctions.get_list_of_reported_usernames())



@app.route("/view_user_reports")
def view_user_reports():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            username = request.args.get("username")
            return render_template("view_user_reports.html", reports=DataBaseFunctions.get_reports_list(username))
    return redirect('/homePage')


@app.route("/admin_options/view_post_reports")
def view_post_reports():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            return render_template("view_post_reports.html",
                                   reports=DataBaseFunctions.reported_posts_as_list_of_dictionaries())
    return redirect('/homePage')
    #DataBaseFunctions.get_list_of_reported_usernames())

@app.route('/admin_options/delete_post/<post_id>')
def delete_post(post_id):
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
             DataBaseFunctions.delete_post(post_id)
             return redirect('/admin_options/view_post_reports')
    return redirect('/homePage')

@app.route("/admin_options/send_notification", methods=['POST','GET'])
def send_notification():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            return render_template("send_notification.html")
    return redirect('/homePage')


@app.route("/admin_options/send_notification/notification_sent", methods = ['POST','GET'])
def notification_sent():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):

            topic = request.form.get("topic")
            content= request.form.get("content")
            DataBaseFunctions.send_notification_to_all_users(topic=topic, content=content)
            return redirect("/admin_options")
    return redirect('/homePage')


@app.route('/admin_options/admin_messages', methods=['GET'])
def admin_messages():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):

            messages = DataBaseFunctions.admins_messages_list()
            messages.reverse()
            return render_template('admin_messages.html', messages=messages)
    return redirect('/homePage')


@app.route('/admin_options/admin_messages/view_admin_msg/<msg_id>')
def view_admin_msg(msg_id):
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            msg = DataBaseFunctions.get_message(msg_id)
            DataBaseFunctions.make_msg_read(msg_id)
            return render_template('view_admin_msg.html',
                                   sender=msg.sender,
                                   topic=msg.topic,
                                   content=msg.content)
    return redirect('/homePage')


@app.route('/admin_options/view_all_lessons/select_date_range', methods=['POST','GET'])
def select_date_range():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            print(DataBaseFunctions.dates_list()[0])
            print("dates and stuff")
            return render_template('select_date_range_admin.html',
                                            all_usernames=','.join(DataBaseFunctions.get_all_users()),
                                           first_date_exists=DataBaseFunctions.dates_list()[0],
                                           last_date_exists=DataBaseFunctions.dates_list()[-1])
    return redirect('/homePage')


@app.route('/admin_options/view_all_lessons', methods=['POST', 'GET'])
def view_all_lessons():
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):
            from_date = str(request.args.get("from_date"))
            until_date = str(request.args.get("until_date"))
            usernames = (str(request.args.get("usernames"))).replace(' ','').split(',')
            if DataBaseFunctions.date_matches_time_format(from_date) and DataBaseFunctions.date_matches_time_format(until_date):
                if DataBaseFunctions.date_is_after(until_date, from_date) or from_date==until_date:
                    lessons = DataBaseFunctions.get_all_lessons(usernames=usernames, from_date=from_date, until_date=until_date)
                    return render_template('admin_view_all_lessons.html', lessons=lessons, from_date=from_date, until_date=until_date)
            return redirect('/admin_options/view_all_lessons/select_date_range')
    return redirect('/homePage')


@app.route('/admin_options/cancel_lesson/<lesson_ID>', methods=['GET'])
def cancel_lesson_by_admin(lesson_ID):
    if 'user' in session:
        if DataBaseFunctions.is_admin(session['user']):

            lesson = DataBaseFunctions.get_lesson_by_ID(lesson_ID)
            DataBaseFunctions.cancel_lesson(lesson_ID)
            participants = lesson.participants.split(',')
            for each in participants:
                if each == participants[0]:
                    other_participant = participants[1]
                else:
                    other_participant = participants[0]

                content = "שלום " + each + ", נראה כי מנהלי המערכת ביטלו את השיעור שקבעת עם " + other_participant +\
                          " בתאריך " + lesson.date + \
                          " בשעות " + lesson.time_range + "." +\
                          '\r\n'+\
                          "אנא התעדכנ/י בשאר השיעורים שלך על ידי לחיצה על כפתור 'השיעורים שלי' בתפריט."

                DataBaseFunctions.send_msg(sender="הנהלת Syeto", addressee=each, topic="שיעור שקבעת התבטל", content=content)
            return redirect('/admin_options/view_all_lessons?from_date=' + request.args.get('from_date') + '&until_date=' + request.args.get('until_date'))


    return redirect('/homePage')


@app.route('/teacher_or_students_offer_lesson/<username>')
def teacher_or_students_offer_lesson(username):
    # print("Can be a teacher:", not not DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_strong_subjects(session['user']),
    #                                                                             subs2=DataBaseFunctions.get_weak_subjects(username)))
    # print("can be a student:", not not DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_weak_subjects(session['user']),
    #                                                                                 subs2=DataBaseFunctions.get_strong_subjects(username)))
    return render_template('teacher_or_student_lesson_offer.html',
                           username=username,
                           show_teach_option = not not DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_strong_subjects(session['user']),
                                                                                subs2=DataBaseFunctions.get_weak_subjects(username)),
                           show_can_be_taught_option = not not DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_weak_subjects(session['user']),
                                                                                    subs2=DataBaseFunctions.get_strong_subjects(username))
                           )

#/<selected_platform>/<selected_date>/<selected_timeA>/<selected_timeB>/<error_msg>
@app.route('/offer_lesson/<username>/<teacher>', methods=['GET'])
def offer_lesson(username, teacher, selected_platform="",  selected_date="", selected_timeA="", selected_timeB="", selected_subject="", free_text="", error_msg=""):
    import Calendar_Functions
    subjects_list=[]
    if teacher == "True":
        # print(teacher)
        subjects_list = DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_strong_subjects(session['user']),
                                                       subs2=DataBaseFunctions.get_weak_subjects(username))#מה שמשותף למקצועות החזקים של סשן והחלשים של יוזר
    else:
        subjects_list = DataBaseFunctions.mix_subjects(subs1=DataBaseFunctions.get_weak_subjects(session['user']),
                                                       subs2=DataBaseFunctions.get_strong_subjects(username))#מה שמשותף למקצועות חלשים של סשן והחזקים של יוזר
    return render_template('offer_lesson.html',
                           username=username,
                           Im_the_teacher=teacher,
                           subjects_list=subjects_list,
                           platforms=['Zoom'],
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
    elif DataBaseFunctions.lesson_exists_at_this_date_and_time(session['user'], date, from_time, until_time):
        error_msg = "נראה שכבר קבעתם שיעור בתאריך ושעה חופפים/זהים... נסו להציע מועד אחר."
        todo_bien = False
    elif DataBaseFunctions.lesson_exists_at_this_date_and_time(username, date, from_time, until_time):
        error_msg = "נראה שהמשתמש הזה כבר קבע שיעור בתאריך ושעה חופפים/זהים... נסו להציע מועד אחר."
        todo_bien = False
    elif Calendar_Functions.time_range_length(from_time=from_time, until_time=until_time) < 30\
            or Calendar_Functions.time_range_length(from_time=from_time, until_time=until_time) > 60:
        error_msg = "אורך השיעור צריך להיות בין 30 דקות לשעה :)"
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

    lesson_ID = (DataBaseFunctions.accept_lesson_offer(username=session['user'],
                                          id = ID))
    print("less ID = ", lesson_ID)
    lesson = DataBaseFunctions.get_lesson_by_ID(lesson_ID=lesson_ID)
    participants = lesson.participants.split(',')
    lesson_ending_time = lesson.time_range.split('-')[1]
    print("Teacher is ", lesson.teacher)
    print("addressee",participants[0])

    # שולח שתי הדעות לאחר השיעור, אחת למורה ואחת לתלמיד
    for i in range(2):
        DataBaseFunctions.activate_thread(function=DataBaseFunctions.send_lesson_feedback_msg,
                                          args=[participants[i], lesson_ending_time, lesson.date, lesson.teacher == participants[i]])
    # ------------------------------------------------------------------------------------------------
    # DataBaseFunctions.send_lesson_feedback_msg(addressee=participants[0],
    #                                            lesson_ending_time=lesson_ending_time,
    #                                            lesson_ending_date=lesson.date,
    #                                            teacher=lesson.teacher)
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
    if DataBaseFunctions.whos_lesson_offer_is_this(offer_id=offer_id) != session['user']:
        return redirect('/view_lessons_offers')
    offer = DataBaseFunctions.get_lesson_offer_object(offer_id)
    return render_template('view_a_single_lesson_offer.html',
                           offer=offer)#,
                           # platform_nickname=DataBaseFunctions.get_platform_nickname(offer.from_user))

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