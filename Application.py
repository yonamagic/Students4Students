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
subjects = [Subject('Math',[10,11]), Subject('Arabic',[10,11,12]), Subject('History',[10])]

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
        staticVar.comment = "Username or password incorrect."
        return redirect('/login', code=302)

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['user']
    staticVar.connected_username = ""
    return redirect('/')


#First registration page,
@app.route('/register', methods=['POST','GET'])
def register(username="", username_comment="", password="", password_comment=""):

    return render_template('registerr.html',
                           username=username, password=password,
                           username_comment=username_comment,
                           password_comment=password_comment,
                           subjects=DataBaseFunctions.subjects)




@app.route('/checkRegistration', methods=['POST','GET'])
def checkRegistration():
    details_dict = {
        'username' : request.form.get("username"),
        'username_comment' : "",
        'password': request.form.get("password"),
        'password_comment': "",
        'strong_subjects': [],
        'weak_subjects': []
    }

    strong_subjects = []
    for sub in DataBaseFunctions.subjects:
        if request.form.get("strong_" + str(sub)) != None:
            current_subject = Subject(sub,[])
            for i in range(10,13):
                if request.form.get("strong_" + sub + "_class_" + str(i)) != None:
                    current_subject.classes.append(i)
            strong_subjects.append(current_subject)
    details_dict['strong_subjects'] = strong_subjects


    weak_subjects = []
    for sub in DataBaseFunctions.subjects:
        if request.form.get("weak_"+str(sub)) != None:
            current_subject = Subject(sub,[])
            for i in range(10,13):
                if request.form.get("weak_" + sub + "_class_" + str(i)) != None:
                    current_subject.classes.append(i)
            weak_subjects.append(current_subject)
    details_dict['weak_subjects'] = strong_subjects




    todo_bien = True#There are no problems in registration details

    if len(details_dict['username']) < 4 or len(details_dict['username']) > 14:#username not in legal length
        details_dict['username_comment'] = "Please enter a username between 4-14 characters"
        todo_bien=False
    if DataBaseFunctions.user_exists(details_dict['username']):#username taken
        details_dict['username_comment'] = "This username is taken"
        todo_bien = False
    if len(details_dict['password']) < 8:#password is too short
        details_dict['password_comment'] = "Please choose a password with a minimal length of 8 characters"
        todo_bien = False
    if todo_bien==False:#Theres a problem
        return register(username=details_dict['username'],
                        password=details_dict['password'],
                        username_comment=details_dict['username_comment'],
                        password_comment=details_dict['password_comment'])

    #If it came here, everything is good
    registrationDone()
    session['user'] = details_dict['username']
    return redirect('/homePage')#Every thing is ok, register me!

#Creates a new user in the DataBase
def registrationDone():
    print("Done")
    print(handle_subjects_info("strong"))
    DataBaseFunctions.create_user(request.form.get("username"),
                                  request.form.get("password"),
                                  strong_subjects=handle_subjects_info("strong"),
                                  weak_subjects=handle_subjects_info("weak"))
    # return "<h1> To sum up:</h1>" + '\r\n' + string

#Turn the POST request to a list of Subjects and returns it, according to param
def handle_subjects_info(strong_or_weak):
    subjects=[]
    for s in DataBaseFunctions.subjects:
        if request.form.get(strong_or_weak + "_" + str(s)) != None:  # It is celected
            current_subject = Subject(s, [])
            for current_class in range(10, 13):
                current_id = strong_or_weak + "_" + s + "_class_" + str(current_class)
                if request.form.get(current_id) != None:  # class was chosen
                    current_subject.classes.append(current_class)
            subjects.append(current_subject)
    return subjects

@app.route('/editProfile')
def editProfile():
    return render_template('editProfile.html', subjects=DataBaseFunctions.subjects)

@app.route('/profileEditingDone', methods=['POST'])
def profileEditingDone():
    DataBaseFunctions.edit_user_strong_subjects(username=session['user'],
                                                strong_subjects=handle_subjects_info("strong"))
    DataBaseFunctions.edit_user_weak_subjects(username=session['user'],
                                                weak_subjects=handle_subjects_info("weak"))
    DataBaseFunctions.edit_subjects_in_subjects_table(username=session['user'],
                                                      subjects=handle_subjects_info("strong")+handle_subjects_info("weak"))
    return redirect('/profile')
@app.route('/homePage', methods=['POST','GET'])
def homePage():
    if connected():
        return render_template('/homePage.html')
    return redirect('/')

#Returns a User object - existing user.
def build_User_object(username):
    subs = DataBaseFunctions.get_strong_subjects(username)
    strong_subjects = DataBaseFunctions.subjects_as_list_of_Subjects(username,subs)
    subs = DataBaseFunctions.get_weak_subjects(username)
    weak_subjects = DataBaseFunctions.subjects_as_list_of_Subjects(username, subs)

    return User(username,strong_subjects,weak_subjects)


@app.route('/profile' , methods=['POST','GET'])
def profile():
    username = request.args.get("username")# Just for now
    # print("username = " + session['user'])
    if not username or username==session['user']:#if there is no specified username or the specified name is sessin['user']
        return render_template('personal_profile.html', user=build_User_object(session['user']))
    else:
        return render_template('user_profile.html', user=build_User_object(username),
                               self_username=session['user'],
                               username2=username)






# @app.route('/editProfile' , methods=['POST','GET'])
# def editProfilePage():
#     return render_template('/editProfile')
#
# @app.route('/applyProfileChanges' , methods=['POST','GET'])
# def applyProfileChanges:
#     #For now, it is not possible to edit username



@app.route('/potentialTeachers' , methods=['POST','GET'])
def potential__teachers():
    subjects = DataBaseFunctions.subjects_as_list_of_Subjects(session['user'], DataBaseFunctions.get_weak_subjects(session['user']))
    teachers = (DataBaseFunctions.teachers_by_subjects(DataBaseFunctions.potential_teachers(subjects)))
    return render_template('potentialTeachers.html',DataBaseFunctions=DataBaseFunctions, my_weak_subjects=DataBaseFunctions.get_weak_subjects(session['user']),
                                                    teachers=teachers, my_username=session['user'])



@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if not connected():
        return redirect('/')
    messages_list = DataBaseFunctions.messages_list(session['user'])#[2:]#Because there are 2 additional Messages that I do not know why theyre in there
    messages_list.reverse()
    print(messages_list)
    # print("read="+messages_list[0].is_read)
    return render_template('inbox.html', messages = messages_list)

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
    # if DataBaseFunctions.user_exists(sender):
    #     print("user does not exist")
    #     return sendMessage(addressee=addressee,
    #                        topic=topic,
    #                        content=content,
    #                        addressee_comment="Please enter an existing username")
    print("User indeed exists")

    DataBaseFunctions.send_msg(sender=sender,
                               addressee = addressee,
                               topic=topic,
                               content=content)
    return redirect('/inbox')

@app.route('/viewMessage', methods=['POST','GET'])
def viewMessage():
    # msg_id = request.args.get("msg_id")
    msg = DataBaseFunctions.get_message(request.args.get("msg_id"))
    DataBaseFunctions.make_msg_read(request.args.get("msg_id"))
    return render_template('viewMessage.html',
                           sender=msg.sender,
                           topic=msg.topic,
                           content=msg.content)

@app.route('/replyMessage', methods=['GET'])
def replayMessage():
    return render_template('sendMessage.html',
                           addressee=request.args.get("origin_sender"),
                           topic="<Re>: " + request.args.get("topic"),
                           content="--------------------<Re:>"
                                   +'\r\n'+
                                   request.args.get("content")
                                   + '\r\n' +
                                   "--------------------<Re:>"
                           )

@app.route('/typingChatRoom')
def typingChatRoom(methods=['GET']):
    if not connected() or (connected() and request.args.get("self_username") != session['user']):#For preventing scams and hacks
        return "Error" + "\r\n" \
               + "You tried to enter a chat room you do not belong..."
    else:
        return render_template('typingChatRoom.html')


# @app.route('/inbox')
# def inbox():
#     pass



@app.route("/response" , methods=["POST" , "GET"])
def response():
    string=''
    # print("Yesssss " + request.form.get("username") , request.form.get("password"))
    for i in range(len(subjects)):
        for j in range(3):
            checked = request.form.get("currentID"+str(i)+'_'+str(j))
            if checked == None:
                string += (subjects[i] + " for classes: ")

                print ("currentID"+str(i)+'_'+str(j) + " Not selected")
            else:
                print("currentID"+str(i)+'_'+str(j) + " SELECTED")
    return " "
    # string=''
    # for i in range(3):
    #     print (request.form.get(str(i)))
    #     if request.form.get(str(i)) == None:
    #         string = string + "No "
    #     else:
    #         string = string + "Yes "
    #     print("string = " + string)
    # return string

if __name__ == '__main__':
    app.run(debug=True)