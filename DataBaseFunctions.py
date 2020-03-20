import sqlite3
from Subject import Subject
import os
from Message import Message

def get_date():
    import datetime
    date = str(datetime.datetime.now()).split(' ')[0]
    date = date.split('-')
    date.reverse()
    date = '/'.join(date)
    return date

class DataBaseFunctions:

    subjects = ['Math', 'English', 'History', 'Arabic', 'Bible']


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
    def create_user(username, password, email, strong_subjects=[], weak_subjects=[]):
        conn = sqlite3.connect('database.db', timeout=2)
        # cursor = conn.execute("select * from users where username='yehonatan'")
        # for i in cursor:
        #     print("fffff"+str(i))
        conn.execute("insert into users "
                     "(username, password, email, strong_subjects, weak_subjects, inboxID, is_admin, friends_list, friend_requests, notifications_IDs, lessons_offers_IDs) "
                     "values (?,?,?,?,?,?,'no', '' ,'' ,'' ,'')",
                     (username,
                      password,
                      email,
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

        # for r in com:
        #     print (r)
        # conn.commit()


    @staticmethod#returns a list of a user's friends list
    def get_friends_list(username):
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
    #     conn = sqlite3.connect("database.db", timeout=2)
    #     conn.execute("update users set strong_subjects = ? where username = ?",
    #                  (DataBaseFunctions.subjects_list_to_string(strong_subjects),
    #                   username))
    #     conn.commit()

    # @staticmethod#Edits the column "weak_subjects" in users table
    # def edit_user_weak_subjects(username, weak_subjects):
    #     conn = sqlite3.connect("database.db", timeout=2)
    #     conn.execute("update users set weak_subjects = ? where username = ?",
    #                  (DataBaseFunctions.subjects_list_to_string(weak_subjects),
    #                   username))
    #     conn.commit()


    # @staticmethod#Adds info to subjects table accordingly
    # def edit_subjects_in_subjects_table(username, subjects):
    #     DataBaseFunctions.delete_user_from_subjects_table(username)
    #     conn = sqlite3.connect("database.db", timeout=2)
    #     for subject in subjects:
    #         conn.execute("insert into subjects (username, subject, classes) values (?,?,?)",
    #                      (username, subject.name, str(subject.classes)[1:-1].replace(' ', '')))
    #     conn.commit()

    @staticmethod#Deletes all rows in subjects table where username fits to parameter
    def delete_user_from_subjects_table(username):
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
        msgID = str(DataBaseFunctions.random_id())
        conn.execute("insert into messages (messageID, topic, sender, content, date, is_read) "
                     "values (?,?,?,?,?,?)", (msgID, topic, sender, content, get_date(), "no")
                     )
        conn.commit()
        return msgID




    @staticmethod#Send a message - adds info to the database
    def send_msg(sender, addressee, topic, content):
        conn = sqlite3.connect("database.db", timeout=2)
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

    @staticmethod#returns a Post object
    def get_post_object(post_id):
        from Post import Post
        conn = sqlite3.connect("database.db", timeout=2)
        post = conn.execute("select * from forum_posts where post_ID = ? ", (post_id,))
        for row in post:
            post = row
            print("A",post)
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
        conn = sqlite3.connect("database.db", timeout=2)
        posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?",(forum_name,))
        for row in posts_IDs:
            posts_IDs=row[0].split(',')
        return DataBaseFunctions.get_all_posts_list(posts_IDs)

    @staticmethod#returns a Comment object by comment id
    def get_comment_object(comment_id):
        from Comment import Comment
        conn = sqlite3.connect("database.db", timeout=2)
        comment = conn.execute("select * from post_comments where comment_ID = ? ", (comment_id,))
        for row in comment:
            comment = row
        print("comment is: " , comment)
        print(isinstance(comment,tuple))
        print(type(comment))
        if not isinstance(comment,tuple) :
            return None
        return Comment(id=comment[0],
                       content=comment[1],
                       narrator=comment[2],
                       date=get_date())

    @staticmethod  # returns a list of Comments objects by a list of comments IDs
    def get_all_comments_list(comments_IDs):
        comments = []
        for id in comments_IDs:
            comment_object = DataBaseFunctions.get_comment_object(id)
            if comment_object is not None:
                comments.append(DataBaseFunctions.get_comment_object(id))
        comments.reverse()
        print("comments are: ", comments)
        return comments

    @staticmethod#returns a list of comments of a certain post
    def get_post_comments(post_ID):
        conn = sqlite3.connect("database.db", timeout=2)
        comments_IDs = conn.execute("select comments_IDs from forum_posts where post_ID=?",(post_ID,))
        for row in comments_IDs:
            comments_IDs = row[0].split(',')
            print("IDs=",comments_IDs)
        return DataBaseFunctions.get_all_comments_list(["123","456"])



    # @staticmethod#recieves a post topic and returns its id
    # def get_post_id(post_topic):
    #     conn = sqlite3.connect("database.db", timeout=2)
    #     id = conn.execute("select post_ID from forum_posts where topic=?",(post_topic,))
    #     for row in id:
    #         id=row[0]
    #     return id


    @staticmethod#adds a new comment to a post (by its id - parameter)
    def add_comment(post_id, content,narrator):
        conn = sqlite3.connect("database.db", timeout=2)
        comment_id = DataBaseFunctions.random_id()
        date = get_date()
        DataBaseFunctions.create_comment(id = comment_id,
                                         content=content,
                                         narrator=narrator,
                                         date=date)
        DataBaseFunctions.attach_comment_to_post(post_id=post_id,
                                                 comment_id=comment_id)


    @staticmethod#creates comment (updates database)
    def create_comment(id, content, narrator, date):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("insert into post_comments (comment_ID, content, narrator_username, date) values (?,?,?,?)",(id,content,narrator,date))
        conn.commit()

    @staticmethod#attaches a comment to a post - update a post's "comments_IDs" value
    def attach_comment_to_post(post_id, comment_id):
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
        com = conn.execute("select forum_name from forums")
        names=[]
        for row in com:
            names.append(row[0])
        return names

    @staticmethod#adds a new post (id) to the "forums" db and returns its id
    def create_post_in_forums(forum_name, new_post_id):
        conn = sqlite3.connect("database.db", timeout=2)
        current_posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?", (forum_name,))
        for row in current_posts_IDs:
            current_posts_IDs = row[0]
        current_posts_IDs += ',' + new_post_id
        conn.execute("update forums set posts_IDs = ? where forum_name=?", (current_posts_IDs, forum_name))
        conn.commit()

    @staticmethod
    def create_post_in_forum_posts(post_id, narrator, topic, content):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("insert into forum_posts (post_ID, narrator, topic, content, date, comments_IDs)"
                     " values (?,?,?,?,?,?)", (post_id, narrator, topic, content, get_date(), ""))
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
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
        notifications = []
        notes_IDs = conn.execute("select notifications_IDs from users where username=?", (username,))
        for row in notes_IDs:
            notes_IDs=row[0]
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
        conn = sqlite3.connect("database.db", timeout=2)
        users = []
        all=conn.execute("select username from users")
        for row in all:
            users.append(row[0])
        return users

    @staticmethod#Updates users table
    def create_notification_in_users_table(note_id):
        conn = sqlite3.connect("database.db", timeout=2)
        for user in DataBaseFunctions.get_all_users():
            existing_notes = conn.execute("select notifications_IDs from users where username=?", (user,))
            for row in existing_notes:
                existing_notes = row[0]
            print (existing_notes)
            new_notes_IDs = existing_notes + ',' + note_id
            conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs,user))

        conn.commit()

    def create_notification_in_users_table_for_a_single_user(note_id, username):
        conn = sqlite3.connect("database.db", timeout=2)
        existing_notes = conn.execute("select notifications_IDs from users where username=?", (username,))
        for row in existing_notes:
            existing_notes = row[0]
        print(existing_notes)
        new_notes_IDs = existing_notes + ',' + note_id
        conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs, username))

        conn.commit()

    @staticmethod#updates notifications table
    def create_notification_in_notifications_table(note_id, topic, content):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("insert into notifications (ID, topic, content, date, is_read)"
                     " values (?,?,?,?,?)", (note_id, topic, content, get_date(), "no"))
        conn.commit()


    @staticmethod
    def get_friend_requests(username):
        conn = sqlite3.connect("database.db", timeout=2)
        friend_requests = conn.execute("select friend_requests from users where username=?", (username,))
        for row in friend_requests:
            friend_requests = row[0]
        friend_requests = friend_requests.split(',')
        return friend_requests

    @staticmethod
    def add_to_friend_requests(self_user, username):
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
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
    def get_lessons_offers_IDs(username):#returns a list of lessons_offers IDs according to a certain usrname
        conn = sqlite3.connect("database.db", timeout=2)
        IDs = conn.execute("select lessons_offers_IDs from users where username=?", (username,))
        for row in IDs:
            IDs = row[0]
        IDs = IDs.split(',')
        return IDs

    @staticmethod
    def get_lesson_offer_object(id):#returns a Lesson_offer object
        from Lesson_offer import Lesson_offer
        conn = sqlite3.connect("database.db", timeout=2)
        offer = conn.execute("select * from lessons_offers where ID=?", (id,))
        for row in offer:
            offer=row
        return Lesson_offer(ID=offer[0],
                            username=offer[1],
                            location=offer[2],
                            date=offer[3],
                            time_range=offer[4])

    @staticmethod
    def get_lessons_offers_as_list(username):
        Lessons_offers = []
        offers_IDs = DataBaseFunctions.get_lessons_offers_IDs(username)
        for id in offers_IDs:
            Lessons_offers.append(DataBaseFunctions.get_lesson_offer_object(id))
        return Lessons_offers


    @staticmethod
    def report_user(username, report_content):
        conn = sqlite3.connect("database.db", timeout=2)
        ID = DataBaseFunctions.random_id()
        date = get_date()
        conn.execute("insert into reports (ID, reported_user, content, date) values (?,?,?,?)",
                     (ID, username, report_content, date))
        conn.commit()
    @staticmethod
    def get_list_of_reported_usernames():
        conn = sqlite3.connect("database.db", timeout=2)
        usernames = []
        all = conn.execute("select username from reportings")
        for row in all:
            usernames.append(row[0])
        return usernames

    @staticmethod
    def send_msg_to_admins(sender,  topic, content):
        conn = sqlite3.connect("database.db", timeout=2)
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
        conn = sqlite3.connect("database.db", timeout=2)
        rep = conn.execute("select * from reports where ID=?", (ID,))
        for r in rep:
            rep=r
        return Report(ID=rep[0],
                      reported_user=rep[1],
                      content=rep[2],
                      date=rep[3])
    @staticmethod
    def get_user_reports_IDs(username):
        conn = sqlite3.connect("database.db", timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        IDs=[]
        for i in command:
            IDs.append(i[0])
        return IDs

    @staticmethod
    def get_reports_list(username):
        conn = sqlite3.connect("database.db", timeout=2)
        reports=[]
        IDs = DataBaseFunctions.get_user_reports_IDs(username)
        for id in IDs:
            reports.append(DataBaseFunctions.get_Report(id))
        return reports

    @staticmethod
    def get_num_of_reports(username):
        conn = sqlite3.connect("database.db", timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        return len(list(command))

    @staticmethod
    def get_all_reported_users():
        conn = sqlite3.connect("database.db", timeout=2)
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
# print(DataBaseFunctions.add_to_friend_requests("yonamagic","newone"))
# print(DataBaseFunctions.get_all_users())
# DataBaseFunctions.create_new_post("Math","Yoni","new one","just some trying outs")
# DataBaseFunctions.get_comment_object("123")
# DataBaseFunctions.get_post_comments("1234")
# import datetime
# print(str(datetime.datetime.now()).split(' '))
# DataBaseFunctions.send_msg("yonamagic", "aviv", "Try msg", "Hello aviv, this is a msg!")
# DataBaseFunctions.edit_user_strong_subjects(sqlite3.connect("database.db", timeout=2),"yoni", [Subject("Mathematics",[10,11]), Subject("Bio",[10,12])])
# DataBaseFunctions.delete_user_from_subjects_table('helloMeyyy')
# print(str([1,2,3])[1:-1].replace(' ', ''))
# DataBaseFunctions.edit_subjects_in_subjects_table('yoni',[Subject("Math",[10,11]), Subject("Arabic",[10,11,12])])
# DataBaseFunctions.edit_subjects_in_subjects_table(username='newYoni', subjects=[Subject("Math",[10,11])]+[Subject("Arabic",[10,11,12])])
# l=([Message("1","Hi","Me","sup","22.1"),Message("1","Hi","Me","sup","22.1"),Message("1","Hi","Me","sup","22.1")])
#
# print(l)
# for i in l:
#     print(i.sender)

# #מקבלת שם משתמש של הסשן ורשימה של Subjects גרועים ומחזירה רשימה של משתמשים שיכולים לעזור על פי המקצועות החזקים שלהם בפורמט הבא:
# #[[[<רשימה של שמות >] , <שם מקצוע>],...]
# def get_teachers(self_username, weak_subjects):
#     pass


    @staticmethod
    #מקבלת שם של מקצוע ומחזירה רשימה של שמות המשתמשים שמקצוע זה נכלל ברשימת המקצועות החזקים שלהם
    def get_teachers_in_general(subject):
        conn = sqlite3.connect('database.db')
        teachers=[]
        teachers_from_db = conn.execute("select username from subjects where subject=? and status='strong'", (subject,))
        for r in teachers_from_db:
            teachers.append(r[0])
        return teachers


    subjects_and_classes = [
        # [subject, [classes]]
        [ 'Math' , ['5 יחל לכיתה י','5 יחל לכיתה יא','5 יחל לכיתה יב','4 יחל לכיתה י','4 יחל לכיתה יא','4 יחל לכיתה יב','3 יחל לכיתה י','3 יחל לכיתה יא']],
        ['English',['5 יחל לכיתה י', '5 יחל לכיתה יא', '5 יחל לכיתה יב', '4 יחל לכיתה י', '4 יחל לכיתה יא', '4 יחל לכיתה יב', '3 יחל לכיתה י', '3 יחל לכיתה יא', '3 יחל לכיתה יב']]

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
    #מקבל רשימה של Subject גרועים ומחזיר רשימה של רשימות, בתוכה כל איבר מכיל רשימה שאיברה השמאלי הוא שם מקצוע והשני רשימה המכילה רשימות, כל אחת מהן מכילה באינדקס הראשון שם של משתמש ובשני רשימה של קלאסים
    def specific_teachers_for_all_subjects(subjects):
        list = []
        for subject in subjects:
            # print(subject.name)
            # print(subject.classes)
            # print(specific_teachers_for_one_subject(subject))
            list.append([subject.name, DataBaseFunctions.specific_teachers_for_one_subject(subject)])
        return list


    @staticmethod
    #מקבל מקצוע ומחזיר רשימה שכל איבר הוא רשימה המכילה שני אינדקסים: שם משתמש ורשימה נוספת של קלאסים משותפים לדרישה ולמשתמש
    def specific_teachers_for_one_subject(subject=Subject('English',['10','11'])):
        conn = sqlite3.connect('database.db')
        specific_teachers=[]#[ [username, [common_classes]],  ...  ]
        general_teachers=(DataBaseFunctions.get_teachers_in_general(subject.name))
        for user in general_teachers:
            classes = conn.execute("select classes from subjects where username=? and subject=? and status='strong'",
                                                                                                    (user,subject.name))
            for row in classes:
                classes=row[0].split(',')
            common_classes = (list(set(classes).intersection(subject.classes)))
            if common_classes:
                specific_teachers.append([user,common_classes])