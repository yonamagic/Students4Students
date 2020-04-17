from _datetime import datetime, timedelta
from Emailing import Emailing
import sqlite3
from Subject import Subject
import os
from Message import Message

class DataBaseFunctions:

    subjects = ['Math', 'English', 'History', 'Arabic', 'Bible']

    @staticmethod
    def get_date():
        import datetime
        date = str(datetime.datetime.now()).split(' ')[0]
        date = date.split('-')
        date.reverse()
        date = '/'.join(date)
        return date

    @staticmethod
    def get_time():
        import datetime
        date = str(datetime.datetime.now()).split(' ')[1]
        date=date.split(':')
        return (date[0]+':'+date[1])


    @staticmethod
    def user_exists(username):
        conn = sqlite3.connect('database.db')
        com = conn.execute("select username from users where username==? ", (username,))
        for row in com:
            return True
        return False

    @staticmethod
    def is_admin(username):
        conn = sqlite3.connect('database.db', timeout=2)
        admin = conn.execute("select is_admin from users where username=?", (username,))
        for row in admin:
            admin = row[0]
        if admin == "yes":
            return True
        return False

    @staticmethod
    def create_user(username, password, email, platform_nickname, strong_subjects=[], weak_subjects=[]):
        conn = sqlite3.connect('database.db', timeout=2)
        # cursor = conn.execute("select * from users where username='yehonatan'")
        # for i in cursor:
        #     print("fffff"+str(i))
        conn.execute("insert into users "
                     "(username, password, email, platform_nickname, strong_subjects, weak_subjects, inboxID, is_admin, friends_list, friend_requests, notifications_IDs, lessons_offers_IDs) "
                     "values (?,?,?,?,?,?,?,'no', '' ,'' ,'' ,'')",
                     (username,
                      password,
                      email,
                      platform_nickname,
                      ','.join(DataBaseFunctions.subjects_names(strong_subjects)),
                      ','.join(DataBaseFunctions.subjects_names(weak_subjects)),
                      str(os.urandom(24))))
        # com = conn.execute("select * from users where username=?", (username,))
        # conn.commit()

        # DataBaseFunctions.create_strong_subs_in_users_table(conn,strong_subjects, username)
        DataBaseFunctions.create_subs_in_subjects_table(conn=conn,
                                                        subs=strong_subjects,
                                                        status='strong',
                                                        username=username)
        DataBaseFunctions.create_subs_in_subjects_table(conn=conn,
                                                        subs=weak_subjects,
                                                        status='weak',
                                                        username=username)
        inboxID = DataBaseFunctions.random_id()
        conn.execute("update users "
                     "set inboxID = ? "
                     "where username = ?", (inboxID,username))
        conn.execute("insert into inboxes (inboxID, messagesIDs) values (?,'')", (inboxID,))
        # DataBaseFunctions.edit_subjects_in_subjects_table(username=username, subjects=strong_subjects+weak_subjects)
        # DataBaseFunctions.create_weak_subs_in_users_table(conn,weak_subjects, username)
        conn.commit()
        DataBaseFunctions.send_msg("הנהלת Syeto", username, "ברוכים הבאים לסייטו!", "בהצלחה!"
                                                                                    "אנחנו כאן לכל שאלה ובעיה - שלחו הודעה למנהלי המערכת.")

        Emailing.send_email(addressee=email,
                            subject="ברוכים הבאים למשפחת Syeto!",
                            html=Emailing.welcome(username=username))
        # for r in com:
        #     print (r)
        # conn.commit()

    @staticmethod#returns a list of a user's friends list
    def get_friends_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (username,))
        for row in friends:
            friends=row[0]
        friends = friends.split(',')
        return friends

    @staticmethod
    def is_friend(self_user, username):
        return username in DataBaseFunctions.get_friends_list(self_user)

    @staticmethod
    def add_to_friends_list(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (self_user,))
        for row in friends:
            friends = row[0]
        print("favorites = ")
        print(friends)
        if friends:
            print(True)
            total_friends = friends + ',' + username
        else:
            total_friends = username
        print("total favs = " + total_friends)
        print(friends)
        print(total_friends)
        conn.execute("update users "
                     "set friends_list = ? "
                     "where username = ?", (total_friends,self_user))
        conn.commit()

    @staticmethod
    def remove_from_friends_list(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (self_user,))
        for row in friends:
            friends = row[0]
        print("Here we go:")
        friends = friends.split(',')
        print(friends)
        friends.remove(username)
        print(friends)
        total_friends = ','.join(friends)
        print(total_friends)
        conn.execute("update users "
                     "set friends_list = ? "
                     "where username = ?", (total_friends, self_user))
        conn.commit()


    # @staticmethod#Edits the column "strong_subjects" in users table
    # def edit_user_strong_subjects(username, strong_subjects):
    #     conn = sqlite3.connect('database.db', timeout=2)
    #     conn.execute("update users set strong_subjects = ? where username = ?",
    #                  (DataBaseFunctions.subjects_list_to_string(strong_subjects),
    #                   username))
    #     conn.commit()

    # @staticmethod#Edits the column "weak_subjects" in users table
    # def edit_user_weak_subjects(username, weak_subjects):
    #     conn = sqlite3.connect('database.db', timeout=2)
    #     conn.execute("update users set weak_subjects = ? where username = ?",
    #                  (DataBaseFunctions.subjects_list_to_string(weak_subjects),
    #                   username))
    #     conn.commit()


    # @staticmethod#Adds info to subjects table accordingly
    # def edit_subjects_in_subjects_table(username, subjects):
    #     DataBaseFunctions.delete_user_from_subjects_table(username)
    #     conn = sqlite3.connect('database.db', timeout=2)
    #     for subject in subjects:
    #         conn.execute("insert into subjects (username, subject, classes) values (?,?,?)",
    #                      (username, subject.name, str(subject.classes)[1:-1].replace(' ', '')))
    #     conn.commit()

    @staticmethod#Deletes all rows in subjects table where username fits to parameter
    def delete_user_from_subjects_table(username):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("delete from subjects where username=?", (username,))
        conn.commit()

    # @staticmethod
    # def subjects_list_to_string(subjects_list):
    #     string = ""
    #     for sub in subjects_list:
    #         string += ',' + sub.name
    #     string = string[1:]
    #     return string
    @staticmethod
    # recieves a list of Subjects and returns a list of their names
    def subjects_names(subjects):
        subjects_names = []
        for sub in subjects:
            subjects_names.append(sub.name)
        return subjects_names

    @staticmethod#Takes care of creating information in table: subjects, strong/weak according to the paramater
    def create_subs_in_subjects_table(conn, subs, status, username):

        for sub in subs:
            #turn classes into a string for the DB
            classes_as_string = ''
            for current_class in sub.classes:
                classes_as_string += "," + str(current_class)
            classes_as_string = classes_as_string[1:]
            #----------------------------------------
            conn.execute("insert into subjects (username, subject, status, classes) values (?,?,?,?)", (username,sub.name,status,classes_as_string,))
            conn.commit()

    @staticmethod #Returns True if username and password match database info
    def correctDetails(username, password):
        conn = sqlite3.connect('database.db')
        # print(username,password)
        com = conn.execute("select username from users where username==? and password==?" , (username,password))

        for row in com:
            return True
        return False



    # @staticmethod
    # def get_strong_subjects(username):
    #     conn = sqlite3.connect('database.db')
    #     att = conn.execute("select strong_subjects from users where username== ? ", (username,))
    #     for row in att:
    #         # print (row[0])#row[0] is the whole string
    #         att = row[0].split(',')
    #     return att
    #
    # @staticmethod
    # def get_weak_subjects(username):
    #     conn = sqlite3.connect('database.db')
    #     att = conn.execute("select weak_subjects from users where username== ? ", (username,))
    #     for row in att:
    #         # print (row[0])#row[0] is the whole string
    #         att = row[0].split(',')
    #     return att
    #
    # @staticmethod
    # def get_subject_classes(username,subject, status):
    #     conn = sqlite3.connect('database.db')
    #     att = conn.execute("select classes from subjects where username==? and subject==? and status=?" ,
    #                                                                                 (username,subject,status))
    #     for row in att:
    #         att = row[0].split(',')
    #         print(row[0])
    #     return att
    #
    #
    # @staticmethod#מחזיר רשימה עם שני אינדקסים: [0]מכיל משתמשים שחזקים במקצועות החלשים (ללא התאמה בין תתי נושאים)- מחולק לtuples שמכילים (טאפל של תתאי נושאים חזקים ,מקצוע, שם משתמש)
    # #[0] מכיל
    # def potential_teachers(username, weak_subjects=[]):
    #     conn = sqlite3.connect('database.db')
    #     weak_subjects_names = []
    #     for sub in weak_subjects:#Create a list made of those subjects' names
    #         weak_subjects_names.append(sub.name)
    #
    #     teachers = conn.execute("select * from users")
    #     subs_lists=[]#Each index conatins a tupple made of the username and the strong subjects of a user as a string
    #     for i in teachers:
    #         # print("username is i[0] = ", i[0])
    #         # print('*'+i[0]+'*')
    #         if username != i[0]:
    #             subs_lists.append((i[0],i[2]))
    #     # print("subs_lists=",subs_lists)
    #     teachers_by_subject = []
    #     teachers_by_classes = []
    #     # print("subs_lists=", subs_lists)
    #     for user in subs_lists:
    #         strong_subjects = user[1].split(',')
    #         for subject in strong_subjects:
    #             if subject in weak_subjects_names:
    #                 teachers_by_subject.append((user[0],subject))
    #                 common_classes = conn.execute("select classes from subjects where username==(?) and subject==(?) and status='strong'",
    #                                                                                                  (user[0],subject))
    #                 for row in common_classes:
    #                     common_classes = row
    #                 # print("common classes=", common_classes)
    #
    #                 teachers_by_classes.append((user[0],subject,common_classes))
    #     # print(teachers_by_subject)
    #     # print(teachers_by_classes)
    #
    #     return (teachers_by_classes,teachers_by_subject)
    #
    # @staticmethod#recieves potential_teachers returned value and returns :  [[<subject>, []
    # def teachers_by_subjects(teachers):
    #     teachers_by_classes = teachers[0]
    #     # teachers_by_subject = teachers[1]
    #     subjects = []
    #     for t in teachers_by_classes:
    #         if t[1] not in subjects:
    #             subjects.append([t[1],[]])
    #
    #     for subject in subjects:
    #         for t in teachers_by_classes:
    #             if t[1] == subject[0]:
    #                 subject[1].append(t[0])
    #
    #     print (subjects)#A list, each index contains a list in which the first index includes subcject name and the second one - a list of relevant usernames
    #     return subjects
    #     #Get it from here Yehonatan!
    #
    # @staticmethod
    # def matching_classes(users, subject):
    #     conn = sqlite3.connect('database.db')
    #     classes1 = conn.execute("select classes from subjects where username=? and subject=?", (users[0],subject))
    #     for row in classes1:
    #         classes1 = row
    #
    #     classes2 = conn.execute("select classes from subjects where username=? and subject=?", (users[1],subject))
    #     for row in classes2:
    #         classes2 = row
    #     # print(classes2)
    #
    #     classes1 = classes1[0].split(',')
    #     classes2 = classes2[0].split(',')
    #
    #     # print(classes1, classes2)
    #     common_classes = (list(set(classes1).intersection(classes2)))
    #     if common_classes:#if there are common classes
    #         return common_classes
    #     return None
    #
    # # Gets username a list of subjects' names and returns a list that contains those subjects as Subject type and their relevant classes
    # # it is needed in profile page
    # @staticmethod
    # def subjects_as_list_of_Subjects(username, subs, status):
    #     print("subs=" + str(subs))
    #     subjects = []
    #     for current_subject in subs:
    #         classes = DataBaseFunctions.get_subject_classes(username, current_subject, status)
    #         subjects.append(Subject(current_subject, classes))
    #         # print (subjects[i].name, str(subjects[i].classes))
    #
    #     return subjects

    @staticmethod#returns a list of messages using user's msgs IDs
    def messages_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = conn.execute("select inboxID from users where username=?", (username,))
        ###############makes it the actual value
        for i in inboxID:
            inboxID = i
        inboxID=inboxID[0]
        print (inboxID)
        ########################################
        messages_IDs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        #####################Kanal
        for i in messages_IDs :
            messages_IDs = (i[0])
            messages_IDs = messages_IDs.split(',')
        ##########################

        msgs_list = []
        for msg_id in messages_IDs:
            topic = conn.execute("select topic from messages where messageID=?", (msg_id,))
            for row in topic:
                topic = row[0]
            # print(topic)
            sender = conn.execute("select sender from messages where messageID=?", (msg_id,))
            for row in sender:
                sender = row[0]
            # print(sender)
            content = conn.execute("select content from messages where messageID=?", (msg_id,))
            for row in content:
                content = row[0]
            date = conn.execute("select date from messages where messageID=?", (msg_id,))
            for row in date:
                date = row[0]
            is_read = conn.execute("select is_read from messages where messageID=?", (msg_id,))
            for row in is_read:
                is_read = row[0]
            new_msg = Message(
                id = msg_id,
                topic = topic,
                sender = sender,
                content = content,
                date = date,
                is_read=is_read)
            msgs_list.append(new_msg)
            print(content)
            # print(new_msg.id)
        # print(msgs_list[0].id)
        return msgs_list

    @staticmethod#returns a list of admin messages
    def admins_messages_list():
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = "admins"
        messages_IDs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        #####################Kanal
        for i in messages_IDs :
            messages_IDs = (i[0])
            messages_IDs = messages_IDs.split(',')
        ##########################

        msgs_list = []
        for msg_id in messages_IDs:
            topic = conn.execute("select topic from messages where messageID=?", (msg_id,))
            for row in topic:
                topic = row[0]
            # print(topic)
            sender = conn.execute("select sender from messages where messageID=?", (msg_id,))
            for row in sender:
                sender = row[0]
            # print(sender)
            content = conn.execute("select content from messages where messageID=?", (msg_id,))
            for row in content:
                content = row[0]
            date = conn.execute("select date from messages where messageID=?", (msg_id,))
            for row in date:
                date = row[0]
            is_read = conn.execute("select is_read from messages where messageID=?", (msg_id,))
            for row in is_read:
                is_read = row[0]
            new_msg = Message(
                id = msg_id,
                topic = topic,
                sender = sender,
                content = content,
                date = date,
                is_read=is_read)
            msgs_list.append(new_msg)
            print(content)
            # print(new_msg.id)
        # print(msgs_list[0].id)
        return msgs_list


    @staticmethod
    def random_id():
        import random
        import string
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))


    @staticmethod
    def get_message(msg_id):
        conn = sqlite3.connect('database.db', timeout=2)
        msg = conn.execute("select * from messages where messageID = ?", (msg_id,))
        for row in msg:
            msg = row
            print(msg)
            # msg_atts.append(row)
            # print(row)
        msg_atts = list(msg)

        msg_to_return = Message(id=msg_atts[0],
                                topic=msg_atts[1],
                                sender=msg_atts[2],
                                content=msg_atts[3],
                                date=msg_atts[4],
                                is_read=msg_atts[5]
        )
        return msg_to_return

    @staticmethod
    def make_msg_read(id):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("UPDATE messages "
                           "SET is_read = 'yes' "
                           "WHERE messageID = ?", (id,))
        print(id)

        read=conn.execute("select is_read from messages where messageID=?", (id,))
        for row in read:
            read=row
        print(read)

        conn.commit()

    @staticmethod
    def create_msg(sender, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        msgID = str(DataBaseFunctions.random_id())
        conn.execute("insert into messages (messageID, topic, sender, content, date, is_read) "
                     "values (?,?,?,?,?,?)", (msgID, topic, sender, content, DataBaseFunctions.get_date(), "no")
                     )
        conn.commit()
        return msgID




    @staticmethod#Send a message - adds info to the database
    def send_msg(sender, addressee, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = conn.execute("select inboxID from users where username=?", (addressee,))
        for row in inboxID:
            inboxID = row[0]
            # print("ID="+inboxID)
            # print("inboxID="+str(inboxID[0]))
        current_msgs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        for row in current_msgs:
            current_msgs = row[0]
            # print(row)
        # print("current msgs = " + str(current_msgs))

        new_msg_id = DataBaseFunctions.create_msg(sender=sender, topic=topic, content=content)

        print(str(new_msg_id))

        if str(current_msgs):
            new_msgs_IDs = str(current_msgs) + ',' + str(new_msg_id)
        else:
            new_msgs_IDs = str(new_msg_id)

        print (new_msgs_IDs)

        conn.execute("UPDATE inboxes "
                     "SET messagesIDs = ? "
                     "WHERE inboxID = ?", (new_msgs_IDs, inboxID))

        conn.commit()


    @staticmethod
    def whos_msg_is_this(msg_id):
        conn = sqlite3.connect('database.db')
        inboxes_IDs = conn.execute("select messagesIDs from inboxes")
        for one_inbox_IDs in inboxes_IDs:
            if msg_id in one_inbox_IDs[0].split(','):

                 return DataBaseFunctions.whos_inbox_is_this(inbox_ID=DataBaseFunctions.whos_messages_is_this(one_inbox_IDs[0]))

    @staticmethod
    def whos_messages_is_this(inbox_msgs_IDs):
        conn = sqlite3.connect('database.db')
        inbox_ID = conn.execute("select inboxID from inboxes where messagesIDs =?", (inbox_msgs_IDs,))

        for row in inbox_ID:
            return row[0]

    @staticmethod
    def whos_inbox_is_this(inbox_ID):
        conn = sqlite3.connect('database.db')
        user = conn.execute("select username from users where inboxID=?", (inbox_ID,))
        for row in user:
            return row[0]


    @staticmethod#returns a Post object
    def get_post_object(post_id):
        from Post import Post
        conn = sqlite3.connect('database.db', timeout=2)
        post = conn.execute("select * from forum_posts where post_ID = ? ", (post_id,))
        for row in post:
            post = row
            # print("A",post)
        # print("comments: ", post[5].split(','))
        # print("Hi ",DataBaseFunctions.get_all_comments_list(post[5]))
        return Post(post_ID = post[0],
                    narrator = post[1],
                    topic = post[2],
                    content = post[3],
                    date = post[4],
                    comments = DataBaseFunctions.get_all_comments_list(post[5].split(',')))

    @staticmethod#returns a list of Post objects by a list of posts IDs
    def get_all_posts_list(posts_IDs):
        posts = []
        for id in posts_IDs:
            posts.append(DataBaseFunctions.get_post_object(id))
        posts.reverse()
        return posts

    @staticmethod#returns a list of Post objects by forum name
    def get_forum_posts(forum_name):
        conn = sqlite3.connect('database.db', timeout=2)
        posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?",(forum_name,))
        for row in posts_IDs:
            posts_IDs=row[0].split(',')
        return DataBaseFunctions.get_all_posts_list(posts_IDs)

    @staticmethod#returns a Comment object by comment id
    def get_comment_object(comment_id):
        from Comment import Comment
        conn = sqlite3.connect('database.db', timeout=2)
        comment = conn.execute("select * from post_comments where comment_ID = ? ", (comment_id,))
        for row in comment:
            comment = row
        # print("comment is: " , comment)
        # print(isinstance(comment,tuple))
        # print(type(comment))
        if not isinstance(comment,tuple) :
            return None
        return Comment(id=comment[0],
                       content=comment[1],
                       narrator=comment[2],
                       date=DataBaseFunctions.get_date())

    @staticmethod  # returns a list of Comments objects by a list of comments IDs
    def get_all_comments_list(comments_IDs):
        comments = []
        for id in comments_IDs:
            comment_object = DataBaseFunctions.get_comment_object(id)
            if comment_object is not None:
                comments.append(DataBaseFunctions.get_comment_object(id))
        comments.reverse()
        # print("comments are: ", comments)
        return comments

    @staticmethod#returns a list of comments of a certain post
    def get_post_comments(post_ID):
        conn = sqlite3.connect('database.db', timeout=2)
        comments_IDs = conn.execute("select comments_IDs from forum_posts where post_ID=?",(post_ID,))
        for row in comments_IDs:
            comments_IDs = row[0].split(',')
            print("IDs=",comments_IDs)
        return DataBaseFunctions.get_all_comments_list(["123","456"])



    # @staticmethod#recieves a post topic and returns its id
    # def get_post_id(post_topic):
    #     conn = sqlite3.connect('database.db', timeout=2)
    #     id = conn.execute("select post_ID from forum_posts where topic=?",(post_topic,))
    #     for row in id:
    #         id=row[0]
    #     return id


    @staticmethod#adds a new comment to a post (by its id - parameter)
    def add_comment(post_id, content,narrator):
        conn = sqlite3.connect('database.db', timeout=2)
        comment_id = DataBaseFunctions.random_id()
        date = DataBaseFunctions.get_date()
        DataBaseFunctions.create_comment(id = comment_id,
                                         content=content,
                                         narrator=narrator,
                                         date=date)
        DataBaseFunctions.attach_comment_to_post(post_id=post_id,
                                                 comment_id=comment_id)


    @staticmethod#creates comment (updates database)
    def create_comment(id, content, narrator, date):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into post_comments (comment_ID, content, narrator_username, date) values (?,?,?,?)",(id,content,narrator,date))
        conn.commit()

    @staticmethod#attaches a comment to a post - update a post's "comments_IDs" value
    def attach_comment_to_post(post_id, comment_id):
        conn = sqlite3.connect('database.db', timeout=2)
        current_IDs = conn.execute("select comments_IDs from forum_posts where post_ID=?",(post_id,))
        for row in current_IDs:
            current_IDs=row[0]
        # print("Current = " + current_IDs)
        if current_IDs:
            new_IDs = current_IDs + ',' + comment_id
        else:
            new_IDs = comment_id
        conn.execute("update forum_posts set comments_IDs = ? where post_ID=? ", (new_IDs,post_id))
        conn.commit()


    @staticmethod
    def get_forum_names():
        conn = sqlite3.connect('database.db', timeout=2)
        com = conn.execute("select forum_name from forums")
        names=[]
        for row in com:
            names.append(row[0])
        return names

    @staticmethod#adds a new post (id) to the "forums" db and returns its id
    def create_post_in_forums(forum_name, new_post_id):
        conn = sqlite3.connect('database.db', timeout=2)
        current_posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?", (forum_name,))
        for row in current_posts_IDs:
            current_posts_IDs = row[0]
        current_posts_IDs += ',' + new_post_id
        conn.execute("update forums set posts_IDs = ? where forum_name=?", (current_posts_IDs, forum_name))
        conn.commit()

    @staticmethod
    def create_post_in_forum_posts(post_id, narrator, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into forum_posts (post_ID, narrator, topic, content, date, comments_IDs)"
                     " values (?,?,?,?,?,?)", (post_id, narrator, topic, content, DataBaseFunctions.get_date(), ""))
        conn.commit()

    @staticmethod
    def create_new_post(forum_name, narrator, topic, content):
        post_id = DataBaseFunctions.random_id()
        DataBaseFunctions.create_post_in_forums(forum_name=forum_name,
                                                new_post_id=post_id)
        DataBaseFunctions.create_post_in_forum_posts(post_id=post_id,
                                                     narrator=narrator,
                                                     topic=topic,
                                                     content=content)


    @staticmethod
    def get_notification_object(id):
        from Notification import Notification
        conn = sqlite3.connect('database.db', timeout=2)
        note = conn.execute("select * from notifications where ID=?", (id,))
        for row in note:
            note = row
        return Notification(ID=note[0],
                            topic=note[1],
                            content=note[2],
                            date=note[3],
                            is_read=note[4])

    @staticmethod
    def get_all_notifications_as_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        notifications = []
        notes_IDs = conn.execute("select notifications_IDs from users where username=?", (username,))
        for row in notes_IDs:
            notes_IDs=row[0]
        if not notes_IDs:
            return []
        notes_IDs=notes_IDs.split(',')
        for note in notes_IDs:
            notifications.append(DataBaseFunctions.get_notification_object(note))
        notifications.reverse()
        return notifications


    @staticmethod#sends a notification to all users
    def send_notification_to_all_users(topic, content):
        id = DataBaseFunctions.random_id()
        DataBaseFunctions.create_notification_in_users_table(note_id=id)
        DataBaseFunctions.create_notification_in_notifications_table(note_id=id,
                                                                    topic=topic,
                                                                    content=content)



    @staticmethod#sends a notification toa single user
    def send_notification_to_a_single_user(topic, content):
        id = DataBaseFunctions.random_id()
        DataBaseFunctions.create_notification_in_users_table_for_a_single_user(note_id=id)
        DataBaseFunctions.create_notification_in_notifications_table(note_id=id,
                                                                    topic=topic,
                                                                    content=content)

    @staticmethod#Returns a list of all usernames
    def get_all_users():
        conn = sqlite3.connect('database.db', timeout=2)
        users = []
        all=conn.execute("select username from users")
        for row in all:
            users.append(row[0])
        return users

    @staticmethod#Updates users table
    def create_notification_in_users_table(note_id):
        conn = sqlite3.connect('database.db', timeout=2)
        for user in DataBaseFunctions.get_all_users():
            existing_notes = conn.execute("select notifications_IDs from users where username=?", (user,))
            for row in existing_notes:
                existing_notes = row[0]
            print (existing_notes)
            if existing_notes != '':
                new_notes_IDs = existing_notes + ',' + note_id
            else:
                new_notes_IDs = note_id
            conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs,user))

        conn.commit()

    def create_notification_in_users_table_for_a_single_user(note_id, username):
        conn = sqlite3.connect('database.db', timeout=2)
        existing_notes = conn.execute("select notifications_IDs from users where username=?", (username,))
        for row in existing_notes:
            existing_notes = row[0]
        print(existing_notes)
        new_notes_IDs = existing_notes + ',' + note_id
        conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs, username))

        conn.commit()

    @staticmethod#updates notifications table
    def create_notification_in_notifications_table(note_id, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into notifications (ID, topic, content, date, is_read)"
                     " values (?,?,?,?,?)", (note_id, topic, content, DataBaseFunctions.get_date(), "no"))
        conn.commit()


    @staticmethod
    def get_friend_requests(username):
        conn = sqlite3.connect('database.db', timeout=2)
        friend_requests = conn.execute("select friend_requests from users where username=?", (username,))
        for row in friend_requests:
            friend_requests = row[0]
        friend_requests = friend_requests.split(',')
        try:
            friend_requests.remove('')
        except:
            pass
        return friend_requests

    @staticmethod
    def add_to_friend_requests(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        requests = conn.execute("select friend_requests from users where username=?", (self_user,))
        for row in requests:
            requests = row[0]
        if requests:
            print(True)
            total_requests = requests + ',' + username
        else:
            total_requests = username
        conn.execute("update users "
                     "set friend_requests = ? "
                     "where username = ?", (total_requests, self_user))
        conn.commit()

    @staticmethod
    def remove_from_friend_requests(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friend_requests = DataBaseFunctions.get_friend_requests(self_user)
        friend_requests.remove(username)
        friend_requests = ','.join(friend_requests)
        conn.execute("update users set friend_requests=? where username=?", (friend_requests, self_user))
        conn.commit()

    @staticmethod
    def is_in_friend_requests(self_user, username):
        friend_requests = DataBaseFunctions.get_friend_requests(self_user)
        return username in friend_requests



    @staticmethod
    def report_user(username, report_content):
        conn = sqlite3.connect('database.db', timeout=2)
        ID = DataBaseFunctions.random_id()
        date = DataBaseFunctions.get_date()
        conn.execute("insert into reports (ID, reported_user, content, date) values (?,?,?,?)",
                     (ID, username, report_content, date))
        conn.commit()


    @staticmethod
    def report_post(post_id, content, forum):
        conn = sqlite3.connect('database.db')
        conn.execute("insert into post_reports (post_ID, content, forum, deleted) values (?,?,?,'no')",
                     (post_id, content, forum))
        conn.commit()

    @staticmethod
    def post_is_deleted(post_id):
        conn = sqlite3.connect('database.db')
        deleted = conn.execute("select deleted from post_reports where post_ID=?", (post_id,))
        for row in deleted:
            if row[0] == 'yes':
                return True
            return False

    @staticmethod
    def get_reported_posts_IDs():
        conn = sqlite3.connect('database.db')
        IDs = conn.execute("select ID from post_reports")
        reps_IDs = []
        for row in IDs:
            reps_IDs.append(row[0])
        return reps_IDs

    @staticmethod
    def reported_posts_as_list_of_dictionaries():
        conn = sqlite3.connect('database.db')
        dicts_list = []
        posts = conn.execute("select * from post_reports")
        for row in posts:
            dicts_list.append({
                'post_ID' : row[0],
                'content' : row[1],
                'forum' : row[2],
                'deleted' : row[3]
            })
        return dicts_list

    @staticmethod
    def delete_post(post_id):
        DataBaseFunctions.delete_post_from_forums_table(post_id)
        # DataBaseFunctions.delete_post_from_posts_table(post_id)
        DataBaseFunctions.set_deleted_in_postReports_table(post_id)

    @staticmethod
    def set_deleted_in_postReports_table(post_id):
        conn = sqlite3.connect('database.db')
        conn.execute("update post_reports set deleted = 'yes' where post_ID=?", (post_id,))
        conn.commit()

    @staticmethod
    def delete_post_from_forums_table(post_id):
        conn = sqlite3.connect('database.db')
        forums = conn.execute("select * from forums")
        for row in forums:
            forum_name = row[0]
            posts_IDs = row[1]
            if post_id in posts_IDs:
                posts_IDs = posts_IDs.split(',')
                posts_IDs.remove(post_id)
                posts_IDs = ','.join(posts_IDs)
                print("posts_IDs = " , posts_IDs)
                conn.execute("update forums set posts_IDs = ? where forum_name=?", (posts_IDs,forum_name))
                conn.commit()
                break

    @staticmethod
    def get_forum_name_by_post_id(post_id):
        conn = sqlite3.connect('database.db')
        forums = conn.execute("select forum_name from forums")
        for row in forums:
            forum_name = row[0]
            posts = DataBaseFunctions.get_forum_posts(forum_name)
            posts_IDs = []
            for i in posts:
                posts_IDs.append(i.post_ID)
            if post_id in posts_IDs:
                return forum_name

    @staticmethod
    def get_list_of_reported_usernames():
        conn = sqlite3.connect('database.db', timeout=2)
        usernames = []
        all = conn.execute("select username from reportings")
        for row in all:
            usernames.append(row[0])
        return usernames

    @staticmethod
    def send_msg_to_admins(sender,  topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = "admins"
        current_msgs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        for row in current_msgs:
            current_msgs = row[0]
            # print(row)
        # print("current msgs = " + str(current_msgs))

        new_msg_id = DataBaseFunctions.create_msg(sender=sender, topic=topic, content=content)

        print(str(new_msg_id))

        if str(current_msgs):
            new_msgs_IDs = str(current_msgs) + ',' + str(new_msg_id)
        else:
            new_msgs_IDs = str(new_msg_id)

        print(new_msgs_IDs)

        conn.execute("UPDATE inboxes "
                     "SET messagesIDs = ? "
                     "WHERE inboxID = ?", (new_msgs_IDs, inboxID))

        conn.commit()

    @staticmethod#returns a Report Object
    def get_Report(ID):
        from Report import Report
        conn = sqlite3.connect('database.db', timeout=2)
        rep = conn.execute("select * from reports where ID=?", (ID,))
        for r in rep:
            rep=r
        return Report(ID=rep[0],
                      reported_user=rep[1],
                      content=rep[2],
                      date=rep[3])
    @staticmethod
    def get_user_reports_IDs(username):
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        IDs=[]
        for i in command:
            IDs.append(i[0])
        return IDs

    @staticmethod
    def get_reports_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        reports=[]
        IDs = DataBaseFunctions.get_user_reports_IDs(username)
        for id in IDs:
            reports.append(DataBaseFunctions.get_Report(id))
        return reports

    @staticmethod
    def get_num_of_reports(username):
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        return len(list(command))

    @staticmethod
    def get_all_reported_users():
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select reported_user from reports")
        users=[]
        for i in command:
            users.append(i[0])
        users = list(dict.fromkeys(users))

        return users

    @staticmethod
    def get_reports_dict_list():
        dicts = []
        all_reported_users = DataBaseFunctions.get_all_reported_users()
        for user in all_reported_users:
            dicts.append({
                'username' : user,
                'num_of_reports' : DataBaseFunctions.get_num_of_reports(user)
            })
        return dicts





    subjects_and_classes = [
        # [subject, [classes]]
        [ 'מתמטיקה' , ['חמש יחל לכיתה י','חמש יחל לכיתה יא','חמש יחל לכיתה יב','ארבע יחל לכיתה י','ארבע יחל לכיתה יא','ארבע יחל לכיתה יב','שלוש יחל לכיתה י','שלוש יחל לכיתה יא']],
        ['אנגלית',['חמש יחל לכיתה י', 'חמש יחל לכיתה יא', 'חמש יחל לכיתה יב', 'ארבע יחל לכיתה י', 'ארבע יחל לכיתה יא', 'ארבע יחל לכיתה יב', 'שלוש יחל לכיתה י', 'שלוש יחל לכיתה יא', 'שלוש יחל לכיתה יב', 'דוברי אנכלית - כיתה ט', 'דוברי אנכלית - כיתה י', 'דוברי אנכלית - כיתה יא']],
        ['הסטוריה',['לכיתה ט', 'לכיתה י', 'לכיתה יא', 'לכיתה יב']],
        ['עברית', ['לכיתה ט', 'לכיתה י', 'לכיתה יא']],
        ['אזרחות', ['לכיתה ט', 'לכיתה י', 'לכיתה יא', 'לכיתה יב']],
        ['כימיה כמקצוע חובה (2 יחל)', ['לכיתה ט', 'לכיתה י']],
        ['כימיה כמקצוע מורחב (5 יחל)', ['לכיתה יא', 'לכיתה יב']],
        ['ביולוגיה כמקצוע חובה (2 יחל)', ['לכיתה ט', 'לכיתה י']],
        ['ביולוגיה כמקצוע מורחב (5 יחל)', ['לכיתה יא', 'לכיתה יב']],
        ['מדעי המחשב', ['Java', 'C', 'C#', 'C++', 'Assembly', 'Python', 'HTML', 'JavaScript', 'CSS']],
        ['תנ"ך כמקצוע חובה (2 יחל)', ['לכיתה ט', 'לכיתה י', 'לכיתה יא', 'לכיתה יב']],
        ['ערבית כמקצוע חובה', ['לכיתה ט', 'לכיתה י']],
        ['ערבית כמקצוע מורחב', ['לכיתה יא', 'לכיתה יב']],
        ['פיזיקה כמקצוע חובה (2 יחל)', ['לכיתה י']],
        ['פיזיקה כמקצוע מורחב (5 יחל)', ['לכיתה יא', 'לכיתה יב']],
        ['ספרות כמקצוע חובה', ['לכיתה ט', 'לכיתה י']],
        ['ספרות כמקצוע מורחב', ['לכיתה יא', 'לכיתה יב']],
        ['קולנוע', ['לכיתה י','לכיתה יא', 'לכיתה יב']]

        # ['', []],
        # ['', []],
        # ['', []],
        # ['', []]
    ]

    @staticmethod
    #מקבל שם משתמש ומחזיר רשימה של Subject טובים
    def get_strong_subjects(username):
        conn = sqlite3.connect('database.db')
        strong_subjects=[]
        subjects = conn.execute("select * from subjects where username=? and status='strong'", (username,))
        for row in subjects:
            strong_subjects.append(Subject(row[1], row[3].split(',')))
        return strong_subjects


    @staticmethod
    #מקבל שם משתמש ומחזיר רשימה של Subject גרועים
    def get_weak_subjects(username):
        conn = sqlite3.connect('database.db')
        weak_subjects=[]
        subjects = conn.execute("select * from subjects where username=? and status='weak'", (username,))
        for row in subjects:
            weak_subjects.append(Subject(row[1], row[3].split(',')))
        return weak_subjects


    @staticmethod
    #מקבל מקצוע ומחזיר רשימה שכל איבר הוא רשימה המכילה שני אינדקסים: שם משתמש ורשימה נוספת של קלאסים משותפים לדרישה ולמשתמש
    def specific_users_for_one_subject(subject, teacher_or_student):
        conn = sqlite3.connect('database.db')
        specific_users=[]#[ [username, [common_classes]],  ...  ]
        general_teachers = (DataBaseFunctions.get_users_in_general(subject.name, teacher_or_student))
        if teacher_or_student == 'teacher':
            subject_key_word='strong'
        else:
            subject_key_word='weak'
        for user in general_teachers:
            print("--------------------")
            print("user=",user)

            classes = conn.execute("select classes from subjects where username=? and subject=? and status=?",
                                                                                                    (user,subject.name, subject_key_word))
            for row in classes:
                classes=row[0].split(',')
                print("classes",classes)
            common_classes = (list(set(classes).intersection(subject.classes)))
            print("common classes=", common_classes)
            if common_classes:
                print("if common_classes = True!")
                print("specific_users before change = ",specific_users)
                specific_users.append([user,common_classes])
                print("specific_users after change = ",specific_users)
        return specific_users

    @staticmethod
    # מקבל רשימה של Subject גרועים ומחזיר רשימה של רשימות, בתוכה כל איבר מכיל רשימה שאיברה השמאלי הוא שם מקצוע והשני רשימה המכילה רשימות, כל אחת מהן מכילה באינדקס הראשון שם של משתמש ובשני רשימה של קלאסים
    def specific_users_for_all_subjects(subjects, teacher_or_student):
        list = []
        for subject in subjects:
            list.append([subject.name, DataBaseFunctions.specific_users_for_one_subject(subject, teacher_or_student)])

            # if teacher_or_student == 'teacher':
            #     list.append([subject.name, DataBaseFunctions.specific_teachers_for_one_subject(subject)])
            # else:
            #     list.append([subject.name, DataBaseFunctions.specific_students_for_one_subject(subject)])
        return list

    @staticmethod
    # מקבלת שם של מקצוע ומחזירה רשימה של שמות המשתמשים שמקצוע זה נכלל ברשימת המקצועות החזקים שלהם
    def get_users_in_general(subject, teacher_or_student):
        conn = sqlite3.connect('database.db')
        users = []
        if teacher_or_student == 'teacher':
            subject_key_word = 'strong'
        else:
            subject_key_word = 'weak'
        users_from_db = conn.execute("select username from subjects where subject=? and status=?", (subject,subject_key_word))
        for r in users_from_db:
            users.append(r[0])
        return users

    @staticmethod
    # מקבלת רשימת Subjects ושם של מקצוע. במידה והמקצוע קיים ברשימה, הפעולה תחזיר את המקצוע עצמו ובמידה שלא - תחזיר False.
    def sub_name_exists(subs_list, sub_name):
        for sub in subs_list:
            if sub.name == sub_name:
                return sub
        return False

    @staticmethod
    # מחזיר רשימה של Subjects שמכילה את הנושאים המשותפים (כולל קלאסים) מבין שתי רשימות נושאים
    def mix_subjects(subs1=[Subject('Math', ['10', '11']), Subject('Math1', ['10', '11'])],
                     subs2=[Subject('Math1v', ['11', '12'])]):
        ret_subs = []
        for sub in subs1:
            sub_if_exists = DataBaseFunctions.sub_name_exists(subs_list=subs2, sub_name=sub.name)
            if sub_if_exists != False:
                common_classes = list(set(sub.classes).intersection(sub_if_exists.classes))
                if common_classes:
                    ret_subs.append(Subject(sub.name, common_classes))
        return ret_subs
        # Subject(sub1.name, list(set(sub1.classes).intersection(sub2.classes)))

    @staticmethod
    def send_lesson_request(platform, date, from_user, to_user, teacher, subject,  time_range, free_text):
        conn = sqlite3.connect('database.db')
        lesson_offer_ID = DataBaseFunctions.random_id()
        print("from ",from_user)
        print("to ", to_user)
        lessons_requests_IDs = conn.execute("select lessons_offers_IDs from users where username=?", (to_user,))
        for row in lessons_requests_IDs:
            lessons_requests_IDs=row[0]
        if len(lessons_requests_IDs) > 0:
            lessons_requests_IDs += ',' + lesson_offer_ID
        else:
            lessons_requests_IDs = lesson_offer_ID
        conn.execute("update users set lessons_offers_IDs = ? where username=?", (lessons_requests_IDs,to_user))


        conn.execute("insert into lessons_offers "
                     "(ID, place, date, from_user, teacher, subject, time_range, free_text)"
                     " values (?,?,?,?,?,?,?,?)",
                     (lesson_offer_ID, platform, date, from_user, teacher, subject, time_range, free_text))

        conn.commit()


    @staticmethod
    def get_lessons_offers_IDs(username):#returns a list of lessons_offers IDs according to a certain usrname
        conn = sqlite3.connect('database.db', timeout=2)
        IDs = conn.execute("select lessons_offers_IDs from users where username=?", (username,))
        for row in IDs:
            IDs = row[0]
        if IDs != None:
            return IDs.split(',')
        else:
            return []

    @staticmethod
    def get_lesson_offer_object(id):#returns a Lesson_offer object
        from Lesson_offer import Lesson_offer
        conn = sqlite3.connect('database.db', timeout=2)
        offer = conn.execute("select * from lessons_offers where ID=?", (id,))
        for row in offer:
            offer=row
        print(offer)
        return Lesson_offer(ID=offer[0],
                            place=offer[1],
                            date=offer[2],
                            from_user=offer[3],
                            teacher=offer[4],
                            subject=offer[5],
                            time_range=offer[6],
                            free_text=offer[7])

    @staticmethod
    def get_lessons_offers_as_list(username):
        Lessons_offers = []
        offers_IDs = DataBaseFunctions.get_lessons_offers_IDs(username)
        print("offers_IDs = ", len(offers_IDs))

        if offers_IDs != ['']:
            for id in offers_IDs:
                lesson_offer = DataBaseFunctions.get_lesson_offer_object(id)
                # lesson_date = lesson_offer.date
                # todays_date = DataBaseFunctions.get_date()[:-2]
                # lesson_time = lesson_offer.time_range.split('-')[0]
                # current_time = DataBaseFunctions.get_time()
                # print(lesson_date, todays_date, lesson_time, current_time)
                # if ( not DataBaseFunctions.date_is_after(todays_date, lesson_date) ) :
                #         if  not DataBaseFunctions.time_is_after(current_time, lesson_time):
                Lessons_offers.append(lesson_offer)
        return Lessons_offers

    @staticmethod
    def get_platform_nickname(username):
        conn=sqlite3.connect('database.db')
        nick = conn.execute("select platform_nickname from users where username=?", (username,))
        for row in nick:
            nick = row[0]
        return nick


    @staticmethod
    def delete_lesson_offer_from_lessonsOffers_table(id):
        conn_database = sqlite3.connect('database.db')
        conn_database.execute("delete from lessons_offers where ID=?", (id,))
        conn_database.commit()

    @staticmethod
    def delete_lesson_offer_from_users_table(username, id):
        conn_database = sqlite3.connect('database.db')
        command = conn_database.execute("select lessons_offers_IDs from users where username=?", (username,))

        for row in command:
            existing_lessons_offers=row[0]
        existing_lessons_offers = existing_lessons_offers.split(',')
        # existing_lessons_offers.remove(',')
        print(existing_lessons_offers)
        existing_lessons_offers.remove(id)
        new_lessons_offers = ','.join(existing_lessons_offers)
        print(new_lessons_offers)
        conn_database.execute("update users set lessons_offers_IDs = ? where username=?" , (new_lessons_offers,username))
        conn_database.commit()


    @staticmethod
    def accept_lesson_offer(username, id):
        import Calendar_Functions
        conn_database = sqlite3.connect('database.db')
        conn_calendar = sqlite3.connect('calendar.db')
        lesson_offer = DataBaseFunctions.get_lesson_offer_object(id=id)

        lesson_ID = Calendar_Functions.create_new_lesson(participants= lesson_offer.from_user+','+username,
                                             location=lesson_offer.place,
                                             date=lesson_offer.date,
                                             time_range=lesson_offer.time_range,
                                             subject=lesson_offer.subject,
                                             teacher=lesson_offer.teacher)
        conn_calendar.commit()
        DataBaseFunctions.delete_lesson_offer_from_users_table(username=username, id=id)
        DataBaseFunctions.send_msg(sender="הנהלת Syeto", addressee=lesson_offer.from_user, topic="שיעור חדש נקבע!",
                                                             content="היי! נראה ש"+ username + " אישר את הצעת השיעור שלך!"+ '\r\n'
                                   + "ניתן לראות את כל השיעורים שקבעת באמצעות לחיצה על כפתור 'השיעורים שלי' בתפריט :)")
        DataBaseFunctions.send_msg(sender="הנהלת Syeto", addressee=username, topic="שיעור חדש נקבע!",
                                                             content="היי! נראה שאישרת את הצעת השיעור של "+ lesson_offer.from_user + "!" +  '\r\n'
                                   + "ניתן לראות את כל השיעורים שקבעת באמצעות לחיצה על כפתור 'השיעורים שלי' בתפריט :)")
        return lesson_ID

    @staticmethod
    def deny_lesson_offer(username, id):
        # DataBaseFunctions.delete_lesson_offer_from_lessonsOffers_table(id=id)
        DataBaseFunctions.delete_lesson_offer_from_users_table(username=username, id=id)

    @staticmethod
    def whos_lesson_offer_is_this(offer_id):
        conn = sqlite3.connect('database.db')
        users = conn.execute("select username from users")
        for row in users:
            user = row[0]
            lessons_offers = conn.execute("select lessons_offers_IDs from users where username=?", (user,))
            for r in lessons_offers:
                lessons_offers=r[0]
            if offer_id in lessons_offers.split(','):
                return user


    @staticmethod# מחזיר את משתתפי השיעור על פי הID שלו (כרשימה של משתתפים)
    def whos_lesson_is_this(ID):
        conn = sqlite3.connect('calendar.db')
        parts = conn.execute("select participants from lessons where ID=?", (ID,))
        for row in parts:
            parts=row[0]
        return parts.split(',')

    @staticmethod
    def get_lesson_by_ID(lesson_ID):
        from Lesson import Lesson
        conn = sqlite3.connect('calendar.db')
        lesson = conn.execute("select * from lessons where ID=?", (lesson_ID,))
        for row in lesson:
            return Lesson(ID=row[0],
                          place=row[1],
                          date=row[2],
                          subject=row[3],
                          participants=row[4],
                          teacher=row[5],
                          time_range=row[6])
    @staticmethod#מחזיר רשימה של טיפוסי Lesson החל מהיום (מסודרים על פי תאריך קיום השיעור)
    def get_lessons(username='yonamagic'):
        from Lesson import Lesson
        conn = sqlite3.connect('calendar.db')
        IDs=[]
        lessons = []
        command = conn.execute("select ID from lessons")
        for row in command:
            IDs.append(row[0])

        for id in IDs:
            participants = conn.execute("select participants from lessons where ID=?", (id,))
            for row in participants:
                participants=row[0]
            if username in participants:
                participants = participants.split(',')
                platform_nicknames = {
                    participants[0] : DataBaseFunctions.get_platform_nickname(participants[0]),
                    participants[1]: DataBaseFunctions.get_platform_nickname(participants[1])
                }
                lesson =  conn.execute("select * from lessons where ID=?", (id,))
                for detail in lesson:
                    lesson_is_active = detail[7]
                    if (not DataBaseFunctions.date_is_after(DataBaseFunctions.get_date()[:-2], detail[2]))\
                            and lesson_is_active=="True":
                        print("lesson", detail[0], detail[7])

                        lessons.append(Lesson(ID=detail[0],
                                          place=detail[1],
                                          date=detail[2],
                                          subject=detail[3],
                                          participants=detail[4],
                                          # platform_nicknames=platform_nicknames,
                                          teacher=detail[5],
                                          time_range=detail[6]))

        return DataBaseFunctions.sort_lessons_by_date_and_time(lessons)

    # @staticmethod
    # def get_all_lessons():
    #     from Lesson import Lesson
    #     conn = sqlite3.connect('calendar.db')
    #     lessons = []
    #     IDs = conn.execute("select ID from lessons")
    #     for ID in IDs:
    #         print(ID)
    #         # lessons.append(Lesson(ID=ID[0]))

    @staticmethod
    def time_is_after(time1, time2):  # Returns True if time1 is after time2
        return datetime.strptime(time1, '%H:%M') > datetime.strptime(time2, '%H:%M')

    @staticmethod
    def date_is_after(date1, date2):
        return datetime.strptime(date1, '%d/%m/%y') > datetime.strptime(date2, '%d/%m/%y')

    @staticmethod#מחזיר אמת אם התאריך (כstr) תואם לפורמט וההיפך
    def date_matches_time_format(date):
        try:
            date = datetime.strptime(date, '%d/%m/%y')
            return True
        except:
            return False

    @staticmethod#מחזיר את התאריך האחרון שקיים בטבלת dates
    def first_date_exists():
        conn = sqlite3.connect('calendar.db')
        dates = []
        comm = conn.execute("select date from dates")
        for row in comm:
            dates.append(row[0])
        for i in range(len(dates)):
            for j in range(len(dates)-1):
                if DataBaseFunctions.date_is_after(dates[j],dates[j+1]):
                    temp = dates[j]
                    dates[j] = dates[j+1]
                    dates[j+1] = temp
        return dates

    @staticmethod#מחזיר את התאריך האחרון שקיים בטבלת dates
    def dates_list():
        conn = sqlite3.connect('calendar.db')
        dates = []
        comm = conn.execute("select date from dates")
        for row in comm:
            dates.append(row[0])
        for i in range(len(dates)):
            for j in range(len(dates)-1):
                if DataBaseFunctions.date_is_after(dates[j],dates[j+1]):
                    temp = dates[j]
                    dates[j] = dates[j+1]
                    dates[j+1] = temp
        return dates#אין לי כוח לעשות פעולה יעילה face it


    @staticmethod
    def sort_lessons_by_date_and_time(lessons):
        for i in range(len(lessons)):
            for cnt in range(len(lessons)-1):
                if DataBaseFunctions.date_is_after(lessons[cnt].date, lessons[cnt+1].date):
                    temp = lessons[cnt]
                    lessons[cnt] = lessons[cnt+1]
                    lessons[cnt+1] = temp
                if lessons[cnt].date == lessons[cnt+1].date and \
                        DataBaseFunctions.time_is_after(lessons[cnt].time_range.split('-')[0], lessons[cnt].time_range.split('-')[1]):
                    temp = lessons[cnt]
                    lessons[cnt] = lessons[cnt+1]
                    lessons[cnt+1] = temp
        return lessons

    @staticmethod#מחזירה את שם המשתמש של המשתמש השני בשיעור שנקבע (שאינו self_username)
    def get_other_user_username(lesson, self_username):
        return lesson.participants.replace(',','').replace(self_username,'')


    @staticmethod#מוחק את נתוני השיעור מטבלת dates ומשנה את סטטוס active של השיעור בטבלת lessons לFalse
    def cancel_lesson(ID):
        DataBaseFunctions.set_lesson_not_active_in_lessons_table(ID)
        # DataBaseFunctions.delete_lesson_from_dates_table(date_ID=DataBaseFunctions.get_date_ID_by_lesson_ID(ID),
        #                                                  lesson_ID=ID)

    @staticmethod
    def set_lesson_not_active_in_lessons_table(lesson_ID):
        conn = sqlite3.connect('calendar.db')
        conn.execute("update lessons set active='False' where ID=?", (lesson_ID,))
        # conn.execute("delete from lessons where ID=?", (lesson_ID,))
        conn.commit()

    @staticmethod
    def get_date_ID_by_lesson_ID(lesson_ID):
        conn = sqlite3.connect('calendar.db')
        dates_IDs = conn.execute("select ID from dates")
        print(dates_IDs)
        for ID in dates_IDs:
            ID=ID[0]
            lessons_IDs = conn.execute("select lessons_IDs from dates where ID=?", (ID,))
            for row in lessons_IDs:
                lessons_IDs=row[0]
            if lesson_ID in lessons_IDs:
                print(ID)
                return ID

    @staticmethod
    def delete_lesson_from_dates_table(date_ID, lesson_ID):
        conn = sqlite3.connect('calendar.db')
        lessons_IDs = conn.execute("select lessons_IDs from dates where ID =?",(date_ID,))
        for row in lessons_IDs:
            lessons_IDs=row[0]
        print(lessons_IDs)
        lessons_IDs=lessons_IDs.split(',')
        print(lessons_IDs)

        lessons_IDs.remove(lesson_ID)
        print(lessons_IDs)
        lessons_IDs=','.join(lessons_IDs)
        print(lessons_IDs)
        conn.execute("update dates set lessons_IDs=? where ID=?", (lessons_IDs, date_ID))
        conn.commit()



    @staticmethod
    def delete_subs_from_subjects_table(username):
        conn = sqlite3.connect('database.db')
        conn.execute("delete from subjects where username=?", (username,))
        conn.commit()

    @staticmethod
    def edit_user_subjects(username, strong_subjects, weak_subjects):
        conn = sqlite3.connect('database.db')
        strong_subjects_names =','.join(DataBaseFunctions.subjects_names(strong_subjects))
        weak_subjects_names =','.join(DataBaseFunctions.subjects_names(weak_subjects))
        print("Strong and weak")
        print(strong_subjects_names, weak_subjects_names)
        conn.execute("update users "
                     "set strong_subjects=?, weak_subjects=? "
                     "where username=?",
                     (strong_subjects_names,weak_subjects_names,username))
        conn.commit()

        DataBaseFunctions.delete_subs_from_subjects_table(username)

        DataBaseFunctions.create_subs_in_subjects_table(conn=conn,
                                                        subs=strong_subjects,
                                                        status='strong',
                                                        username=username)
        DataBaseFunctions.create_subs_in_subjects_table(conn=conn,
                                                        subs=weak_subjects,
                                                        status='weak',
                                                        username=username)






    # @staticmethod
    # def get_inbox_ID(username):
    #     conn = sqlite3.connect('database.db')
    #     id = conn.execute("select inboxID from users where username=?", (username,))
    #     for row in id:
    #         id=row[0]
    #     return id
    #
    # @staticmethod
    # def number_of_msgs(username):
    #     conn = sqlite3.connect('database.db')
    #     inbox_ID = DataBaseFunctions.get_inbox_ID(username)
    #     msgs_list = conn.execute("select messagesIDs from inboxes where inboxID = ?", (inbox_ID,))
    #     for row in msgs_list:
    #         msgs_list=row[0]
    #     return len(msgs_list.split(','))

    @staticmethod
    def send_no_user_reply_for_lesson_offer_msg(addressee='yonamagic', topic='', content='', lesson_starting_time='13:21', lesson_date='03/04/20'):
        import time
        while not (datetime.now().strftime('%H:%M') == lesson_starting_time
                    and datetime.now().strftime('%d/%m/%y') == lesson_date):
            time.sleep(50)

        DataBaseFunctions.send_msg(sender="הנהלת Syeto",
                                   addressee=addressee,
                                   topic=topic,
                                   content=content)
    @staticmethod
    def send_lesson_feedback_msg(addressee="yonamagic", lesson_ending_time="14:42", lesson_ending_date='28/03/20', teacher="True"):
        import time
        print("send_lesson_feedback_msg STARTED")
        while not (datetime.now().strftime('%H:%M') == lesson_ending_time
                    and datetime.now().strftime('%d/%m/%y') == lesson_ending_date):
            time.sleep(50)

        content = "היי! מקווים שהשיעור שעברת היה מועיל... נשמח אם תוכל/י להקדיש כמה רגעים ולמלא את המשוב הקצרצר הזה :)"
        content += '\r\n'
        if teacher:
            content += "https://docs.google.com/forms/d/e/1FAIpQLSdNRTjsXWK6JttoSlss0srcvf09p4bN_IPK_wv-AjmCGA0Dgw/viewform"
        else:
            content += "https://docs.google.com/forms/d/e/1FAIpQLSdgMGdrMhqdKHg_p8nnCDkbgfq1xA_9wYj0uG3iP31btwXaew/viewform"
        DataBaseFunctions.send_msg(sender="הנהלת Syeto",
                                   addressee=addressee,
                                   topic="משוב קצר לגבי השיעור שעברת",
                                   content=content)
        # print(datetime.now().strftime('%H:%M') == lesson_ending_time)
        # while datetime.now().minute != datetime.strptime()



    @staticmethod
    def activate_thread(function, args=[]):#args=[addressee, lesson_ending_time, lesson_ending_date, teacher]
        import threading
        process_thread = threading.Thread(target=function, args=args)
        process_thread.start()
        print("start_thread DONE")

# DataBaseFunctions.activate_thread(DataBaseFunctions.send_lesson_feedback_msg, ['yonamagic', "14:43", '28/03/20', "True"])

    @staticmethod#מחזיר רשימה של כל השיעורים שנקבעו במערכת בטווח תאריכים מסויים
    def get_all_lessons(usernames, from_date, until_date):
            from Lesson import Lesson
            conn = sqlite3.connect('calendar.db')
            lessons = []
            IDs = conn.execute("select * from lessons where active='True'")
            for ID in IDs:
                print("ID = " , ID)
                # print(DataBaseFunctions.date_is_after(ID[2],from_date))
                # print("ID[2]",ID[2])
                # print()
                # print(DataBaseFunctions.date_is_after(from_date,ID[2]))

                if (DataBaseFunctions.date_is_after(ID[2],from_date) or ID[2]==from_date)\
                    and (DataBaseFunctions.date_is_after(until_date,ID[2]) or ID[2]==until_date)\
                        and set(usernames).intersection(set(DataBaseFunctions.whos_lesson_is_this(ID[0]))):
                        print(ID)
                        lessons.append(Lesson(ID=ID[0],
                                              place=ID[1],
                                              date=ID[2],
                                              subject=ID[3],
                                              participants=ID[4],
                                              teacher=ID[5],
                                              time_range=ID[6]))
            return DataBaseFunctions.sort_lessons_by_date_and_time(lessons)


    @staticmethod
    def number_of_lessons_requests(username):
        conn  =sqlite3.connect('database.db')
        reqs = conn.execute("select lessons_offers_IDs from users where username=?", (username,))
        for row in reqs:
            reqs = row[0]
        reqs = reqs.split(',')
        if '' in reqs:
            reqs.remove('')
        return len(reqs)

    @staticmethod
    def number_of_new_messages(username):
        conn  =sqlite3.connect('database.db')
        inbox_ID = conn.execute("select inboxID from users where username=?", (username,))
        for row in inbox_ID:
            inbox_ID=row[0]
        msgs_IDs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inbox_ID,))
        for row in msgs_IDs:
            msgs_IDs=row[0].split(',')
        count=0
        for msg_ID in msgs_IDs:
            msg_is_read = conn.execute("select is_read from messages where messageID=?", (msg_ID,))
            for row in msg_is_read:
                msg_is_read=row[0]
            if msg_is_read == "no":
                count+=1
        return count

    @staticmethod
    def number_of_friend_requests(username):
        conn  =sqlite3.connect('database.db')
        reqs = conn.execute("select friend_requests from users where username=?", (username,))
        for row in reqs:
            reqs=row[0].split(',')
        if '' in reqs:
            reqs.remove('')
        return len(reqs)

    # @staticmethod
    # def
    @staticmethod
    def update_last_login(username):
        current_date = DataBaseFunctions.get_date()
        current_time = DataBaseFunctions.get_time()
        time = current_date + ' ' + current_time
        conn = sqlite3.connect('database.db')
        conn.execute("update users set last_login = ? where username = ?", (time,username))
        conn.commit()
        print("Updated")


    @staticmethod
    def update_lessons_offers_that_have_passed(username):# מוחק מטבלת הusers את הצעות השיערו שעבר זמנן
        # lessons_offers_IDs = DataBaseFunctions.get_lessons_offers_IDs(username)
        lessons_offers = DataBaseFunctions.get_lessons_offers_as_list(username)
        for lesson_offer in lessons_offers:
            if DataBaseFunctions.date_is_after(DataBaseFunctions.get_date()[:-2], lesson_offer.date) or\
                    (DataBaseFunctions.time_is_after(DataBaseFunctions.get_time(), lesson_offer.time_range.split('-')[0]) and\
                                                     DataBaseFunctions.get_date()[:-2] == lesson_offer.date):
                DataBaseFunctions.delete_lesson_offer_from_users_table(username, lesson_offer.ID)

    @staticmethod# מוחק מטבלת הusers את הצעות השיעור שנקבעו שיעורים בזמן חופף לשלהם
    def update_lessons_offers_that_are_no_longer_relevant(username):
        lessons_offers = DataBaseFunctions.get_lessons_offers_as_list(username)
        for lesson_offer in lessons_offers:
            if DataBaseFunctions.lesson_exists_at_this_date_and_time(username=username,
                                                                     date=lesson_offer.date,
                                                                     from_time=lesson_offer.time_range.split('-')[0],
                                                                     until_time=lesson_offer.time_range.split('-')[1]):
                DataBaseFunctions.delete_lesson_offer_from_users_table(username=username,
                                                                       id=lesson_offer.ID)


    @staticmethod
    def number_of_lessons(username):
        return len(DataBaseFunctions.get_lessons(username))

    @staticmethod# מחזיר אמת אם קיים שיעור חופף לפרמטרים
    def lesson_exists_at_this_date_and_time(username, date, from_time, until_time):
        import Calendar_Functions
        lessons = DataBaseFunctions.get_lessons(username)
        for less in lessons:
            if date == less.date:
                less_time_range = Calendar_Functions.get_times_for_lessons(range=less.time_range, jumps_ranges=1)
                origin_time_range = Calendar_Functions.get_times_for_lessons(range=from_time+'-'+until_time, jumps_ranges=1)
                if list(set(less_time_range).intersection(set(origin_time_range))) :
                    return True
        return False

    @staticmethod
    def generate_pwd_reset_key():
        import secrets
        return secrets.token_hex(20)

    @staticmethod
    def generate_pwd_reset_link(secret_key):
        return "http://127.0.0.1:5000/reset_password/" + secret_key

    @staticmethod
    def get_username_by_secret_key(secret_key):
        conn = sqlite3.connect('database.db')
        username = conn.execute("select username from password_reset_requests where secret_key=?", (secret_key,))
        for row in username:
            return row[0]

    @staticmethod
    def get_request_time_by_secret_key(secret_key):
        conn = sqlite3.connect('database.db')
        req_time = conn.execute("select request_time form password_reset_requests where secret_key=?", (secret_key,))
        for row in req_time:
            return row[0]

    @staticmethod
    def make_pwd_reset_req_not_active(secret_key):
        conn = sqlite3.connect('database.db')
        print("Not Active anymore")
        conn.execute("update password_reset_requests set active='no' where secret_key=?", (secret_key,))
        conn.commit()

    @staticmethod
    def create_pwd_rest_request_in_DB(username, secret_key, request_time):
        conn = sqlite3.connect('database.db')
        conn.execute("insert into password_reset_requests (username, secret_key, request_time, active)"
                     " values (?,?,?,'yes')", (username,secret_key,request_time))
        conn.commit()

    @staticmethod
    def start_pwd_reset_countdown(secret_key):
        import time
        #in minutes
        countdown = 10
        time.sleep(countdown*60)
        conn = sqlite3.connect('database.db')
        DataBaseFunctions.make_pwd_reset_req_not_active(secret_key)

    @staticmethod
    def pwd_reset_request_is_active(secret_key):
        conn = sqlite3.connect('database.db')
        active = conn.execute("select active from password_reset_requests where secret_key=?", (secret_key,))
        for row in active:
            if row[0] == 'yes':
                return True
            return False


    @staticmethod
    def get_email(username):
        conn = sqlite3.connect('database.db')
        email = conn.execute("select email from users where username=?", (username,))
        for row in email:
            return row[0]

    @staticmethod
    def send_pwd_reset(username, email):
        conn = sqlite3.connect('database.db')

        secret_key = DataBaseFunctions.generate_pwd_reset_key()
        current_date = DataBaseFunctions.get_date()[:-2]
        current_time = DataBaseFunctions.get_time()

        DataBaseFunctions.create_pwd_rest_request_in_DB(username=username,
                                                        secret_key=secret_key,
                                                        request_time=current_date + ' ' + current_time)

        Emailing.send_email(addressee=email,
                            subject="שחזור סיסמה לאתר Syeto",
                            html=Emailing.forgot_password(username=username, link=DataBaseFunctions.generate_pwd_reset_link(secret_key)))

        DataBaseFunctions.activate_thread(DataBaseFunctions.start_pwd_reset_countdown, args=[secret_key])


    @staticmethod
    def reset_password(username, new_password):
        conn = sqlite3.connect('database.db')
        conn.execute("update users set password=? where username=?", (new_password, username))
        conn.commit()