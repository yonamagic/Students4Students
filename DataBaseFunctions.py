from _datetime import datetime, timedelta
from Emailing import Emailing
import sqlite3
from Subject import Subject
import os
from Message import Message

class DataBaseFunctions:


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
    ]

    @staticmethod # מחזיר מחרוזת המכילה את התאריך הנוכחי
    def get_date():
        import datetime
        date = str(datetime.datetime.now()).split(' ')[0]
        date = date.split('-')
        date.reverse()
        date = '/'.join(date)
        return date

    @staticmethod # מחזירה מחרוזת המכילה את השעה הנוכחית
    def get_time():
        import datetime
        date = str(datetime.datetime.now()).split(' ')[1]
        date=date.split(':')
        return (date[0]+':'+date[1])


    @staticmethod # מחזירה אמת אם שם המשתמש שקיבלה קיים במערכת
    def user_exists(username):
        conn = sqlite3.connect('database.db')
        com = conn.execute("select username from users where username==? ", (username,))
        for row in com:
            return True
        return False

    @staticmethod # מחזירה אמת אם המשתמש מנהל מערכת
    def is_admin(username):
        conn = sqlite3.connect('database.db', timeout=2)
        admin = conn.execute("select is_admin from users where username=?", (username,))
        for row in admin:
            admin = row[0]
        if admin == "yes":
            return True
        return False

    @staticmethod # יוצרת משתמש בבסיס הנתונים
    def create_user(username, password, email, strong_subjects=[], weak_subjects=[]):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into users "
                     "(username, password, email, home_page_notes_IDs, strong_subjects, weak_subjects, inboxID, is_admin, friends_list, friend_requests, notifications_IDs, lessons_offers_IDs, last_login) "
                     "values (?,?,?,'',?,?,?,'no', '' ,'' ,'' ,'',?)",
                     (username,
                      password,
                      email,
                      ','.join(DataBaseFunctions.subjects_names(strong_subjects)),
                      ','.join(DataBaseFunctions.subjects_names(weak_subjects)),
                      str(os.urandom(24)),
                     DataBaseFunctions.get_current_time_for_login()))

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
        conn.commit()
        DataBaseFunctions.send_msg("הנהלת Syeto", username, "ברוכים הבאים לסייטו!", "בהצלחה!"
                                                                                    "אנחנו כאן לכל שאלה ובעיה - שלחו הודעה למנהלי המערכת.")

        Emailing.send_email(addressee=email,
                            subject="ברוכים הבאים למשפחת Syeto!",
                            html=Emailing.welcome(username=username))



    @staticmethod # #returns a list of a user's friends list
    def get_friends_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (username,))
        for row in friends:
            friends=row[0]
        friends = friends.split(',')
        return friends

    @staticmethod # מחזירה אמת אם המשתמשים חברים
    def is_friend(self_user, username):
        return username in DataBaseFunctions.get_friends_list(self_user)

    @staticmethod # מוסיפה את username לרשימת החברים של self_user
    def add_to_friends_list(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (self_user,))
        for row in friends:
            friends = row[0]
        if friends:
            total_friends = friends + ',' + username
        else:
            total_friends = username
        conn.execute("update users "
                     "set friends_list = ? "
                     "where username = ?", (total_friends,self_user))
        conn.commit()

    @staticmethod # מסירה את username מרשימת החברים של self_user
    def remove_from_friends_list(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friends = conn.execute("select friends_list from users where username=?", (self_user,))
        for row in friends:
            friends = row[0]
        friends = friends.split(',')
        friends.remove(username)
        total_friends = ','.join(friends)
        conn.execute("update users "
                     "set friends_list = ? "
                     "where username = ?", (total_friends, self_user))
        conn.commit()



    @staticmethod # #Deletes all rows in subjects table where username fits to parameter
    def delete_user_from_subjects_table(username):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("delete from subjects where username=?", (username,))
        conn.commit()

    @staticmethod     # recieves a list of Subjects and returns a list of their names
    def subjects_names(subjects):
        subjects_names = []
        for sub in subjects:
            subjects_names.append(sub.name)
        return subjects_names

    @staticmethod # #Takes care of creating information in table: subjects, strong/weak according to the paramater
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

    @staticmethod #  #Returns True if username and password match database info
    def correctDetails(username, password):
        conn = sqlite3.connect('database.db')
        com = conn.execute("select username from users where username==? and password==?" , (username,password))

        for row in com:
            return True
        return False

    @staticmethod #returns a list of messages using user's msgs IDs
    def messages_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = conn.execute("select inboxID from users where username=?", (username,))
        ############## makes it the actual value
        for i in inboxID:
            inboxID = i
        inboxID=inboxID[0]
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
            sender = conn.execute("select sender from messages where messageID=?", (msg_id,))
            for row in sender:
                sender = row[0]
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
        return msgs_list

    @staticmethod # #returns a list of admin messages
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
        return msgs_list


    @staticmethod # Generates a random id for msg, notification e.t.c
    def random_id():
        import random
        import string
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


    @staticmethod # מקבלת ID של הודעה מבסיס הנתונים ומחזירה אותה כטיפוס
    def get_message(msg_id):
        conn = sqlite3.connect('database.db', timeout=2)
        msg = conn.execute("select * from messages where messageID = ?", (msg_id,))
        for row in msg:
            msg = row
        msg_atts = list(msg)

        msg_to_return = Message(id=msg_atts[0],
                                topic=msg_atts[1],
                                sender=msg_atts[2],
                                content=msg_atts[3],
                                date=msg_atts[4],
                                is_read=msg_atts[5]
        )
        return msg_to_return

    @staticmethod # משנה את ערך הis_read של ההודעה בבסיס הנתונים ל"yes"
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

    @staticmethod # יוצרת הודעה בבסיס הנתונים
    def create_msg(sender, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        msgID = str(DataBaseFunctions.random_id())
        conn.execute("insert into messages (messageID, topic, sender, content, date, is_read) "
                     "values (?,?,?,?,?,?)", (msgID, topic, sender, content, DataBaseFunctions.get_date(), "no")
                     )
        conn.commit()
        return msgID




    @staticmethod # #Send a message - adds info to the database
    def send_msg(sender, addressee, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = conn.execute("select inboxID from users where username=?", (addressee,))
        for row in inboxID:
            inboxID = row[0]
        current_msgs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        for row in current_msgs:
            current_msgs = row[0]

        new_msg_id = DataBaseFunctions.create_msg(sender=sender, topic=topic, content=content)

        if str(current_msgs):
            new_msgs_IDs = str(current_msgs) + ',' + str(new_msg_id)
        else:
            new_msgs_IDs = str(new_msg_id)

        conn.execute("UPDATE inboxes "
                     "SET messagesIDs = ? "
                     "WHERE inboxID = ?", (new_msgs_IDs, inboxID))

        conn.commit()
        DataBaseFunctions.send_home_page_note(addressee=addressee, topic='קיבלת הודעה חדשה מ'+sender, link='/messages')


    @staticmethod # מחזירה את שם המשתמש של המשתמש שההודעה בעלת הID שהתקבל כפרמטר נמצאת בתיבתו
    def whos_msg_is_this(msg_id):
        conn = sqlite3.connect('database.db')
        inboxes_IDs = conn.execute("select messagesIDs from inboxes")
        for one_inbox_IDs in inboxes_IDs:
            if msg_id in one_inbox_IDs[0].split(','):
                 return DataBaseFunctions.whos_inbox_is_this(inbox_ID=DataBaseFunctions.whos_messages_is_this(one_inbox_IDs[0]))

    @staticmethod # מחזירה את הID של הInbox שהID של ההודעות שלו תואמות את אלן שהתקבלו כפרמטר
    def whos_messages_is_this(inbox_msgs_IDs):
        conn = sqlite3.connect('database.db')
        inbox_ID = conn.execute("select inboxID from inboxes where messagesIDs =?", (inbox_msgs_IDs,))
        for row in inbox_ID:
            return row[0]

    @staticmethod # מחזירה את שם המשתמש שלו שייך Inbox זה
    def whos_inbox_is_this(inbox_ID):
        conn = sqlite3.connect('database.db')
        user = conn.execute("select username from users where inboxID=?", (inbox_ID,))
        for row in user:
            return row[0]


    @staticmethod # #returns a Post object
    def get_post_object(post_id):
        from Post import Post
        conn = sqlite3.connect('database.db', timeout=2)
        post = conn.execute("select * from forum_posts where post_ID = ? ", (post_id,))
        for row in post:
            post = row
        if len(post[5]) == 0:
            comments=[]
        else:
            comments = DataBaseFunctions.get_all_comments_list(post[5].split(','))
        return Post(post_ID = post[0],
                    narrator = post[1],
                    topic = post[2],
                    content = post[3],
                    date = post[4],
                    comments = comments)

    @staticmethod # #returns a list of Post objects by a list of posts IDs
    def get_all_posts_list(posts_IDs):
        posts = []
        for id in posts_IDs:
            posts.append(DataBaseFunctions.get_post_object(id))
        posts.reverse()
        return posts

    @staticmethod # #returns a list of Post objects by forum name
    def get_forum_posts(forum_name):
        conn = sqlite3.connect('database.db', timeout=2)
        posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?",(forum_name,))
        for row in posts_IDs:
            posts_IDs=row[0].split(',')
        return DataBaseFunctions.get_all_posts_list(posts_IDs)

    @staticmethod # #returns a Comment object by comment id
    def get_comment_object(comment_id):
        from Comment import Comment
        conn = sqlite3.connect('database.db', timeout=2)
        comment = conn.execute("select * from post_comments where comment_ID = ? ", (comment_id,))
        for row in comment:
            comment = row
        if not isinstance(comment,tuple) :
            return None
        return Comment(id=comment[0],
                       content=comment[1],
                       narrator=comment[2],
                       date=DataBaseFunctions.get_date(),
                       of_admin=DataBaseFunctions.is_admin(comment[2]))

    @staticmethod #   # returns a list of Comments objects by a list of comments IDs
    def get_all_comments_list(comments_IDs):
        comments = []
        for id in comments_IDs:
            comment_object = DataBaseFunctions.get_comment_object(id)
            if comment_object is not None:
                comments.append(DataBaseFunctions.get_comment_object(id))
        return comments

    @staticmethod # #adds a new comment to a post (by its id - parameter)
    def add_comment(post_id, content,narrator):
        comment_id = DataBaseFunctions.random_id()
        date = DataBaseFunctions.get_date()
        DataBaseFunctions.create_comment(id = comment_id,
                                         content=content,
                                         narrator=narrator,
                                         date=date)
        DataBaseFunctions.attach_comment_to_post(post_id=post_id,
                                                 comment_id=comment_id)


    @staticmethod # #creates comment (updates database)
    def create_comment(id, content, narrator, date):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into post_comments (comment_ID, content, narrator_username, date) values (?,?,?,?)",
                     (id, content, narrator, date))
        conn.commit()

    @staticmethod # #attaches a comment to a post - update a post's "comments_IDs" value
    def attach_comment_to_post(post_id, comment_id):
        conn = sqlite3.connect('database.db', timeout=2)
        current_IDs = conn.execute("select comments_IDs from forum_posts where post_ID=?",(post_id,))
        for row in current_IDs:
            current_IDs=row[0]
        if current_IDs:
            new_IDs = current_IDs + ',' + comment_id
        else:
            new_IDs = comment_id
        conn.execute("update forum_posts set comments_IDs = ? where post_ID=? ", (new_IDs,post_id))
        conn.commit()


    @staticmethod # מחזירה מרחוזרת של שמות כל הפורומים
    def get_forum_names():
        conn = sqlite3.connect('database.db', timeout=2)
        com = conn.execute("select forum_name from forums")
        names=[]
        for row in com:
            names.append(row[0])
        return names

    @staticmethod # מחזירה האם הפורום ששמו התקבל כפרמטר קיים
    def forum_exists(forum_name):
        return forum_name in DataBaseFunctions.get_forum_names()

    @staticmethod # #adds a new post (id) to the "forums" db and returns its id
    def create_post_in_forums(forum_name, new_post_id):
        conn = sqlite3.connect('database.db', timeout=2)
        current_posts_IDs = conn.execute("select posts_IDs from forums where forum_name=?", (forum_name,))
        for row in current_posts_IDs:
            current_posts_IDs = row[0]
        current_posts_IDs += ',' + new_post_id
        conn.execute("update forums set posts_IDs = ? where forum_name=?", (current_posts_IDs, forum_name))
        conn.commit()

    @staticmethod # מזינה את פרטי הפוסט בבסיס הנתונים, בטבלת forum_posts
    def create_post_in_forum_posts(post_id, narrator, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into forum_posts (post_ID, narrator, topic, content, date, comments_IDs)"
                     " values (?,?,?,?,?,?)", (post_id, narrator, topic, content, DataBaseFunctions.get_date(), ""))
        conn.commit()

    @staticmethod # קוראת לפעולות שאחראיות על יצירת פוסט חדש
    def create_new_post(forum_name, narrator, topic, content):
        post_id = DataBaseFunctions.random_id()
        DataBaseFunctions.create_post_in_forums(forum_name=forum_name,
                                                new_post_id=post_id)
        DataBaseFunctions.create_post_in_forum_posts(post_id=post_id,
                                                     narrator=narrator,
                                                     topic=topic,
                                                     content=content)


    @staticmethod # מחזירה עצם Notification שID שלו התקבל כפרמטר
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

    @staticmethod # מחזירה רשימה של עצמי Notification ששייכים למשתמש מסוים
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


    @staticmethod # #sends a notification to all users
    def send_notification_to_all_users(topic, content):
        id = DataBaseFunctions.random_id()
        DataBaseFunctions.create_notification_in_users_table(note_id=id)
        DataBaseFunctions.create_notification_in_notifications_table(note_id=id,
                                                                    topic=topic,
                                                                    content=content)
        for user in DataBaseFunctions.get_all_users():
            DataBaseFunctions.send_home_page_note(addressee=user, topic='קיבלת התראה חדשה ממנהלי המערכת', link='/notifications')





    @staticmethod # #Returns a list of all usernames
    def get_all_users():
        conn = sqlite3.connect('database.db', timeout=2)
        users = []
        all=conn.execute("select username from users")
        for row in all:
            users.append(row[0])
        return users

    @staticmethod # #Updates users table
    def create_notification_in_users_table(note_id):
        conn = sqlite3.connect('database.db', timeout=2)
        for user in DataBaseFunctions.get_all_users():
            existing_notes = conn.execute("select notifications_IDs from users where username=?", (user,))
            for row in existing_notes:
                existing_notes = row[0]
            if existing_notes != '':
                new_notes_IDs = existing_notes + ',' + note_id
            else:
                new_notes_IDs = note_id
            conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs,user))

        conn.commit()

    @staticmethod # מוסיפה את הID של נוטפיקציה מסוימת למאגר הIDs של הנוטיפיקציות של משתמש מסוים
    def create_notification_in_users_table_for_a_single_user(note_id, username):
        conn = sqlite3.connect('database.db', timeout=2)
        existing_notes = conn.execute("select notifications_IDs from users where username=?", (username,))
        for row in existing_notes:
            existing_notes = row[0]
        new_notes_IDs = existing_notes + ',' + note_id
        conn.execute("update users set notifications_IDs=? where username=?", (new_notes_IDs, username))

        conn.commit()

    @staticmethod # #updates notifications table
    def create_notification_in_notifications_table(note_id, topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        conn.execute("insert into notifications (ID, topic, content, date, is_read)"
                     " values (?,?,?,?,?)", (note_id, topic, content, DataBaseFunctions.get_date(), "no"))
        conn.commit()


    @staticmethod # מחזירה רשימה של כל המשתמשים שהציעו חברםי למשתמש ששמו התקבל בפרמטר
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

    @staticmethod # מוסיפה את username לרשימת החברים של self_user בבסיס הנתונים
    def add_to_friend_requests(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        requests = conn.execute("select friend_requests from users where username=?", (self_user,))
        for row in requests:
            requests = row[0]
        if requests:
            total_requests = requests + ',' + username
        else:
            total_requests = username
        conn.execute("update users "
                     "set friend_requests = ? "
                     "where username = ?", (total_requests, self_user))
        conn.commit()

    @staticmethod # מסירה את username מרשימת החברים של self_user בבסיס הנתונים
    def remove_from_friend_requests(self_user, username):
        conn = sqlite3.connect('database.db', timeout=2)
        friend_requests = DataBaseFunctions.get_friend_requests(self_user)
        friend_requests.remove(username)
        friend_requests = ','.join(friend_requests)
        conn.execute("update users set friend_requests=? where username=?", (friend_requests, self_user))
        conn.commit()

    @staticmethod # מחזירה האם username נמצא ברשימת החברים של self_user
    def is_in_friend_requests(self_user, username):
        friend_requests = DataBaseFunctions.get_friend_requests(self_user)
        return username in friend_requests

    @staticmethod # מעדכנת את בסיס הנתונים ומוסיפה את שם המשתמש המדווח ותוכן הדיוול לטבלה המתאימה
    def report_user(username, report_content):
        conn = sqlite3.connect('database.db', timeout=2)
        ID = DataBaseFunctions.random_id()
        date = DataBaseFunctions.get_date()
        conn.execute("insert into reports (ID, reported_user, content, date) values (?,?,?,?)",
                     (ID, username, report_content, date))
        conn.commit()


    @staticmethod # מוסיפה לבסיס הנתונים דיווח על פוסט
    def report_post(post_id, content, forum):
        conn = sqlite3.connect('database.db')
        conn.execute("insert into post_reports (post_ID, content, forum, deleted) values (?,?,?,'no')",
                     (post_id, content, forum))
        conn.commit()

    @staticmethod # מחזירה אמת אם הפוסט מחוק (נמחק על ידי מנהלי המערכת)
    def post_is_deleted(post_id):
        conn = sqlite3.connect('database.db')
        deleted = conn.execute("select deleted from post_reports where post_ID=?", (post_id,))
        for row in deleted:
            if row[0] == 'yes':
                return True
            return False

    @staticmethod # מחזירה רשימה של הIDs של הפוסטים שיש עליהם דיווח
    def get_reported_posts_IDs():
        conn = sqlite3.connect('database.db')
        IDs = conn.execute("select ID from post_reports")
        reps_IDs = []
        for row in IDs:
            reps_IDs.append(row[0])
        return reps_IDs

    @staticmethod # מחזירה רשימת מילונים של פוסטים שדווחו
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

    @staticmethod # מווחקת פוסט
    def delete_post(post_id):
        DataBaseFunctions.delete_post_from_forums_table(post_id)
        DataBaseFunctions.set_deleted_in_postReports_table(post_id)

    @staticmethod # משנה את הסטטוס של הפוסט בטבלת postReports ל"מחוק"
    def set_deleted_in_postReports_table(post_id):
        conn = sqlite3.connect('database.db')
        conn.execute("update post_reports set deleted = 'yes' where post_ID=?", (post_id,))
        conn.commit()

    @staticmethod # משנה את הסטטוס של הפוסט בטבלת forums ל"מחוק"
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
                conn.execute("update forums set posts_IDs = ? where forum_name=?", (posts_IDs,forum_name))
                conn.commit()
                break

    @staticmethod # מחזירה את שם הפורום על ידי קבלת ID של פוסט כפרמטר
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

    @staticmethod # מחזירה רשימה של שמות משתמשים שיש עליהם דיווח
    def get_list_of_reported_usernames():
        conn = sqlite3.connect('database.db', timeout=2)
        usernames = []
        all = conn.execute("select username from reportings")
        for row in all:
            usernames.append(row[0])
        return usernames

    @staticmethod # שולחת הודעה לתיבת ההודעות של מנהלי המערכת
    def send_msg_to_admins(sender,  topic, content):
        conn = sqlite3.connect('database.db', timeout=2)
        inboxID = "admins"
        current_msgs = conn.execute("select messagesIDs from inboxes where inboxID=?", (inboxID,))
        for row in current_msgs:
            current_msgs = row[0]

        new_msg_id = DataBaseFunctions.create_msg(sender=sender, topic=topic, content=content)

        if str(current_msgs):
            new_msgs_IDs = str(current_msgs) + ',' + str(new_msg_id)
        else:
            new_msgs_IDs = str(new_msg_id)

        conn.execute("UPDATE inboxes "
                     "SET messagesIDs = ? "
                     "WHERE inboxID = ?", (new_msgs_IDs, inboxID))

        conn.commit()

    @staticmethod # #returns a Report Object
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

    @staticmethod # מחזיר רשימה של הIDs של הדיווחים על משתמש מסוים
    def get_user_reports_IDs(username):
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        IDs=[]
        for i in command:
            IDs.append(i[0])
        return IDs

    @staticmethod # מחזיר רשימה של Report של משתמש מסויים
    def get_reports_list(username):
        conn = sqlite3.connect('database.db', timeout=2)
        reports=[]
        IDs = DataBaseFunctions.get_user_reports_IDs(username)
        for id in IDs:
            reports.append(DataBaseFunctions.get_Report(id))
        return reports

    @staticmethod # מחזיר את מספר הדיווחים על משתמש מסוים
    def get_num_of_reports(username):
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select ID from reports where reported_user=?", (username,))
        return len(list(command))

    @staticmethod # מחזיר רשימה של כל המשתמשים שדיווחו עליהם
    def get_all_reported_users():
        conn = sqlite3.connect('database.db', timeout=2)
        command = conn.execute("select reported_user from reports")
        users=[]
        for i in command:
            users.append(i[0])
        users = list(dict.fromkeys(users))
        return users

    @staticmethod #  מחזיר מילון של הדיווחים הקיימים
    def get_reports_dict_list():
        dicts = []
        all_reported_users = DataBaseFunctions.get_all_reported_users()
        for user in all_reported_users:
            dicts.append({
                'username' : user,
                'num_of_reports' : DataBaseFunctions.get_num_of_reports(user)
            })
        return dicts


    @staticmethod #
    #מקבל שם משתמש ומחזיר רשימה של Subject טובים
    def get_strong_subjects(username):
        conn = sqlite3.connect('database.db')
        strong_subjects=[]
        subjects = conn.execute("select * from subjects where username=? and status='strong'", (username,))
        for row in subjects:
            strong_subjects.append(Subject(row[1], row[3].split(',')))
        return strong_subjects


    @staticmethod #
    #מקבל שם משתמש ומחזיר רשימה של Subject גרועים
    def get_weak_subjects(username):
        conn = sqlite3.connect('database.db')
        weak_subjects=[]
        subjects = conn.execute("select * from subjects where username=? and status='weak'", (username,))
        for row in subjects:
            weak_subjects.append(Subject(row[1], row[3].split(',')))
        return weak_subjects


    @staticmethod #
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
            classes = conn.execute("select classes from subjects where username=? and subject=? and status=?",
                                                                                                    (user,subject.name, subject_key_word))
            for row in classes:
                classes=row[0].split(',')
            common_classes = (list(set(classes).intersection(subject.classes)))
            if common_classes:
                specific_users.append([user,common_classes])
        return specific_users

    @staticmethod # # מקבל רשימה של Subject גרועים ומחזיר רשימה של רשימות, בתוכה כל איבר מכיל רשימה שאיברה השמאלי הוא שם מקצוע והשני רשימה המכילה רשימות, כל אחת מהן מכילה באינדקס הראשון שם של משתמש ובשני רשימה של קלאסים
    def specific_users_for_all_subjects(subjects, teacher_or_student):
        list = []
        for subject in subjects:
            list.append([subject.name, DataBaseFunctions.specific_users_for_one_subject(subject, teacher_or_student)])
        return list

    @staticmethod #
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

    @staticmethod #
    # מקבלת רשימת Subjects ושם של מקצוע. במידה והמקצוע קיים ברשימה, הפעולה תחזיר את המקצוע עצמו ובמידה שלא - תחזיר False.
    def sub_name_exists(subs_list, sub_name):
        for sub in subs_list:
            if sub.name == sub_name:
                return sub
        return False

    @staticmethod #
    # מחזיר רשימה של Subjects שמכילה את הנושאים המשותפים (כולל קלאסים) מבין שתי רשימות נושאים
    def mix_subjects(subs1, subs2):
        ret_subs = []
        for sub in subs1:
            sub_if_exists = DataBaseFunctions.sub_name_exists(subs_list=subs2, sub_name=sub.name)
            if sub_if_exists != False:
                common_classes = list(set(sub.classes).intersection(sub_if_exists.classes))
                if common_classes:
                    ret_subs.append(Subject(sub.name, common_classes))
        return ret_subs

    @staticmethod # יוצרת בקשת שיעור בInbox של המשתמש הנמען
    def send_lesson_request(platform, date, from_user, to_user, teacher, subject,  time_range, free_text):
        conn = sqlite3.connect('database.db')
        lesson_offer_ID = DataBaseFunctions.random_id()
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


    @staticmethod #
    def get_lessons_offers_IDs(username):#returns a list of lessons_offers IDs according to a certain usrname
        conn = sqlite3.connect('database.db', timeout=2)
        IDs = conn.execute("select lessons_offers_IDs from users where username=?", (username,))
        for row in IDs:
            IDs = row[0]
        print("IDs=",IDs)
        try:
            return IDs.split(',')
        except:
            return []

    @staticmethod #
    def get_lesson_offer_object(id):#returns a Lesson_offer object
        from Lesson_offer import Lesson_offer
        conn = sqlite3.connect('database.db', timeout=2)
        offer = conn.execute("select * from lessons_offers where ID=?", (id,))
        for row in offer:
            offer=row
        return Lesson_offer(ID=offer[0],
                            place=offer[1],
                            date=offer[2],
                            from_user=offer[3],
                            teacher=offer[4],
                            subject=offer[5],
                            time_range=offer[6],
                            free_text=offer[7])

    @staticmethod # מחזירה רשימה של Lesson_offer לפי שם המשתמש שניתן כפרמטר
    def get_lessons_offers_as_list(username):
        Lessons_offers = []
        offers_IDs = DataBaseFunctions.get_lessons_offers_IDs(username)
        if offers_IDs != ['']:
            for id in offers_IDs:
                lesson_offer = DataBaseFunctions.get_lesson_offer_object(id)
                Lessons_offers.append(lesson_offer)
        return Lessons_offers


    @staticmethod #
    def delete_lesson_offer_from_lessonsOffers_table(id):
        conn_database = sqlite3.connect('database.db')
        conn_database.execute("delete from lessons_offers where ID=?", (id,))
        conn_database.commit()

    @staticmethod #
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


    @staticmethod #
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
        # DataBaseFunctions.activate_thread(function=Emailing.send_email,
        #                                   args=[
        #                                       DataBaseFunctions.get_email(lesson_offer.from_user),
        #                                   "שיעור חדש נקבע!",
        #                                   Emailing.lesson_reminder(lesson_offer.from_user, username, lesson_offer.subject, lesson_offer.time_range)
        #                                   ])
        # Emailing.send_email(addressee=DataBaseFunctions.get_email(lesson_offer.from_user),
        #                     subject="שיעור חדש נקבע!",
        #                     html=Emailing.lesson_reminder())
        # Emailing.send_email(addressee=DataBaseFunctions.get_email(username),
        #                     subject="שיעור חדש נקבע!",
        #                     html=Emailing.lesson_reminder(semi_content="היי! נראה שאישרת את הצעת השיעור של "+ lesson_offer.from_user + "!" +  '\r\n'))
        return lesson_ID


    @staticmethod #  #
    def deny_lesson_offer(username, id):
        # DataBaseFunctions.delete_lesson_offer_from_lessonsOffers_table(id=id)
        DataBaseFunctions.delete_lesson_offer_from_users_table(username=username, id=id)

    @staticmethod #  #
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


    @staticmethod #  # # מחזיר את משתתפי השיעור על פי הID שלו (כרשימה של משתתפים)
    def whos_lesson_is_this(ID):
        conn = sqlite3.connect('calendar.db')
        parts = conn.execute("select participants from lessons where ID=?", (ID,))
        for row in parts:
            parts=row[0]
        return parts.split(',')

    @staticmethod #  מחזיר עצם Lesson על סמך מידע מבסיס הנתונים, לפי הID שהתקבל כפרמטר
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

    @staticmethod #  # #מחזיר רשימה של טיפוסי Lesson החל מהיום (מסודרים על פי תאריך קיום השיעור)
    def get_lessons(username):
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
                lesson =  conn.execute("select * from lessons where ID=?", (id,))
                for detail in lesson:
                    lesson_is_active = detail[7]
                    if (not DataBaseFunctions.date_is_after(DataBaseFunctions.get_date()[:-2], detail[2]))\
                            and lesson_is_active=="True":

                        lessons.append(Lesson(ID=detail[0],
                                          place=detail[1],
                                          date=detail[2],
                                          subject=detail[3],
                                          participants=detail[4],
                                          teacher=detail[5],
                                          time_range=detail[6]))

        return DataBaseFunctions.sort_lessons_by_date_and_time(lessons)


    @staticmethod
    def time_is_after(time1, time2):  # Returns True if time1 is after time2
        return datetime.strptime(time1, '%H:%M') > datetime.strptime(time2, '%H:%M')

    @staticmethod #  # מחיזר אמת אם date1 אחרי date2
    def date_is_after(date1, date2):
        return datetime.strptime(date1, '%d/%m/%y') > datetime.strptime(date2, '%d/%m/%y')

    @staticmethod #  # # מחזיר את הפרש הזמנים בדקות
    def time_difference(time1="09:00", time2="08:00"):
        diff = (datetime.strptime(time1, '%H:%M') - datetime.strptime(time2, '%H:%M'))
        return abs(int(diff.seconds/60))

    @staticmethod # #מחזיר אמת אם התאריך (כstr) תואם לפורמט וההיפך
    def date_matches_time_format(date):
        try:
            date = datetime.strptime(date, '%d/%m/%y')
            return True
        except:
            return False

    @staticmethod # #מחזיר את התאריך האחרון שקיים בטבלת dates
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

    @staticmethod # #מחזיר את התאריך האחרון שקיים בטבלת dates
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
        return dates


    @staticmethod # מקבלת רשימה של שיעורים ומחזירה אותם מסודרים על פי סדר כרונולוגי
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

    @staticmethod # #מחזירה את שם המשתמש של המשתמש השני בשיעור שנקבע (שאינו self_username)
    def get_other_user_username(lesson, self_username):
        return lesson.participants.replace(',','').replace(self_username,'')


    @staticmethod # משנה את סטטוס active של השיעור בטבלת lessons לFalse
    # הפעולה כללה קריאות לפעולה נוספת שמוחקת את השיעור מטבלת השיעורים, אבל החלטתי לא לכלול אותה כדי שיהיה זכר לשיעור הזה (בין השאר לצרכים סטטיסטיים)
    def cancel_lesson(ID):
        DataBaseFunctions.set_lesson_not_active_in_lessons_table(ID)

    @staticmethod # משנה את סטטוס active של השיעור בטבלת lessons לFalse
    def set_lesson_not_active_in_lessons_table(lesson_ID):
        conn = sqlite3.connect('calendar.db')
        conn.execute("update lessons set active='False' where ID=?", (lesson_ID,))
        conn.commit()

    @staticmethod # מחזיר את הID של date המתאים לשיעור על פי הID שלו
    def get_date_ID_by_lesson_ID(lesson_ID):
        conn = sqlite3.connect('calendar.db')
        dates_IDs = conn.execute("select ID from dates")
        for ID in dates_IDs:
            ID=ID[0]
            lessons_IDs = conn.execute("select lessons_IDs from dates where ID=?", (ID,))
            for row in lessons_IDs:
                lessons_IDs=row[0]
            if lesson_ID in lessons_IDs:
                return ID

    @staticmethod # מוחק את השיעור מטבלת dates במיקום שנקבע על פי date_ID שהתקבל כפרמטר
    def delete_lesson_from_dates_table(date_ID, lesson_ID):
        conn = sqlite3.connect('calendar.db')
        lessons_IDs = conn.execute("select lessons_IDs from dates where ID =?",(date_ID,))
        for row in lessons_IDs:
            lessons_IDs=row[0]
        lessons_IDs=lessons_IDs.split(',')
        lessons_IDs.remove(lesson_ID)
        lessons_IDs=','.join(lessons_IDs)
        conn.execute("update dates set lessons_IDs=? where ID=?", (lessons_IDs, date_ID))
        conn.commit()



    @staticmethod # מוחק את המקצועות הרשומים בטבלת המקצועות ומשוייכים למשתמש מסוים
    def delete_subs_from_subjects_table(username):
        conn = sqlite3.connect('database.db')
        conn.execute("delete from subjects where username=?", (username,))
        conn.commit()

    @staticmethod # עורך את מקצועותיו של משתמש מסוים
    def edit_user_subjects(username, strong_subjects, weak_subjects):
        conn = sqlite3.connect('database.db')
        strong_subjects_names =','.join(DataBaseFunctions.subjects_names(strong_subjects))
        weak_subjects_names =','.join(DataBaseFunctions.subjects_names(weak_subjects))
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

    @staticmethod # מחכה לתאריך ולשעה של סיום השיעור ושולח הודעה הכוללת קישור למשוב על השיעור שהתבצע
    def send_lesson_feedback_msg(addressee, lesson_ending_time, lesson_ending_date, teacher):
        import time
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

    @staticmethod # מפעיל thread, מקבל פונקציה ורשימת פרמטרים
    def activate_thread(function, args=[]):
        import threading
        process_thread = threading.Thread(target=function, args=args)
        process_thread.start()

    @staticmethod # #מחזיר רשימה של כל השיעורים שנקבעו במערכת בטווח תאריכים מסויים
    def get_all_lessons(usernames, from_date, until_date):
            from Lesson import Lesson
            conn = sqlite3.connect('calendar.db')
            lessons = []
            IDs = conn.execute("select * from lessons where active='True'")
            for ID in IDs:
                if (DataBaseFunctions.date_is_after(ID[2],from_date) or ID[2]==from_date)\
                    and (DataBaseFunctions.date_is_after(until_date,ID[2]) or ID[2]==until_date)\
                        and set(usernames).intersection(set(DataBaseFunctions.whos_lesson_is_this(ID[0]))):
                        lessons.append(Lesson(ID=ID[0],
                                              place=ID[1],
                                              date=ID[2],
                                              subject=ID[3],
                                              participants=ID[4],
                                              teacher=ID[5],
                                              time_range=ID[6]))
            return DataBaseFunctions.sort_lessons_by_date_and_time(lessons)

    @staticmethod # מחזיר את מספר בקשות השיעורים שיש למשתמש מסוים (וטרם אושרו)
    def number_of_lessons_requests(username):
        conn  =sqlite3.connect('database.db')
        reqs = conn.execute("select lessons_offers_IDs from users where username=?", (username,))
        print("USERNAME = ", username)
        print("REQS=",reqs)
        for row in reqs:
            reqs = row[0]
        reqs = reqs.split(',')
        if '' in reqs:
            reqs.remove('')
        return len(reqs)

    @staticmethod # מחזיר את מספר ההודעות שנמצאות בתיבת ההודעות של משתמש מסוים וטרם נקראו
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

    @staticmethod # מחזיר את מספר בקשות החברות של משתמש מסוים
    def number_of_friend_requests(username):
        conn  =sqlite3.connect('database.db')
        reqs = conn.execute("select friend_requests from users where username=?", (username,))
        for row in reqs:
            reqs=row[0].split(',')
        if '' in reqs:
            reqs.remove('')
        return len(reqs)

    @staticmethod
    def get_current_time_for_login():
        current_date = DataBaseFunctions.get_date()
        current_time = DataBaseFunctions.get_time()
        time = current_date + ' ' + current_time
        return time

    @staticmethod # מעדכן את זמן ההתחברות של משתמש מסויים (בבסיס הנתונים) לזמן הנוכחי
    def update_last_login(username):
        conn = sqlite3.connect('database.db')
        time=DataBaseFunctions.get_current_time_for_login()
        conn.execute("update users set last_login = ? where username = ?", (time,username))
        conn.commit()


    @staticmethod # מוחק מטבלת הusers את הצעות השיערו שעבר זמנן
    def update_lessons_offers_that_have_passed(username):
        lessons_offers = DataBaseFunctions.get_lessons_offers_as_list(username)
        for lesson_offer in lessons_offers:
            if DataBaseFunctions.date_is_after(DataBaseFunctions.get_date()[:-2], lesson_offer.date) or\
                    (DataBaseFunctions.time_is_after(DataBaseFunctions.get_time(), lesson_offer.time_range.split('-')[0]) and\
                                                     DataBaseFunctions.get_date()[:-2] == lesson_offer.date):
                DataBaseFunctions.delete_lesson_offer_from_users_table(username, lesson_offer.ID)

    @staticmethod # # מוחק מטבלת הusers את הצעות השיעור שנקבעו שיעורים בזמן חופף לשלהם
    def update_lessons_offers_that_are_no_longer_relevant(username):
        lessons_offers = DataBaseFunctions.get_lessons_offers_as_list(username)
        for lesson_offer in lessons_offers:
            if DataBaseFunctions.lesson_exists_at_this_date_and_time(username=username,
                                                                     date=lesson_offer.date,
                                                                     from_time=lesson_offer.time_range.split('-')[0],
                                                                     until_time=lesson_offer.time_range.split('-')[1]):
                DataBaseFunctions.delete_lesson_offer_from_users_table(username=username,
                                                                       id=lesson_offer.ID)


    @staticmethod # מחזיר את מפסר השיעורים שנקבעו וטרם בוצעו עבור משתמש מסוים
    def number_of_lessons(username):
        return len(DataBaseFunctions.get_lessons(username))

    @staticmethod # # מחזיר אמת אם קיים שיעור חופף לפרמטרים
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

    @staticmethod # מפיק secret key עבור איפוס סיסמה
    def generate_pwd_reset_key():
        import secrets
        return secrets.token_hex(20)

    @staticmethod # מפיק לינק לשחזור הסיסמה
    def generate_pwd_reset_link(secret_key):
        return "http://syeto.pythonanywhere.com/reset_password/" + secret_key

    @staticmethod # מחזיר את שם המשתמש המתאים לkey שהתקבל כפרמטר
    def get_username_by_secret_key(secret_key):
        conn = sqlite3.connect('database.db')
        username = conn.execute("select username from password_reset_requests where secret_key=?", (secret_key,))
        for row in username:
            return row[0]

    @staticmethod # מחזיר את התאריך והשעה שבהם בוקש איפוס הסיסמה
    def get_request_time_by_secret_key(secret_key):
        conn = sqlite3.connect('database.db')
        req_time = conn.execute("select request_time form password_reset_requests where secret_key=?", (secret_key,))
        for row in req_time:
            return row[0]

    @staticmethod # מעדכן את סטטוס בקשת איפוס הסיסמה ללא רלוונטי (not active)
    def make_pwd_reset_req_not_active(secret_key):
        conn = sqlite3.connect('database.db')
        conn.execute("update password_reset_requests set active='no' where secret_key=?", (secret_key,))
        conn.commit()

    @staticmethod # יוצר בקשת איפוס סיסמה בבסיס הנתונים
    def create_pwd_rest_request_in_DB(username, secret_key, request_time):
        conn = sqlite3.connect('database.db')
        conn.execute("insert into password_reset_requests (username, secret_key, request_time, active)"
                     " values (?,?,?,'yes')", (username,secret_key,request_time))
        conn.commit()

    @staticmethod # מתחיל את הספירה לאחור - כשהיא נגמרת, בקשת איפוס הסיסמה תיהפך ללא פעילה
    def start_pwd_reset_countdown(secret_key):
        import time
        #in minutes
        countdown = 10
        time.sleep(countdown*60)
        conn = sqlite3.connect('database.db')
        DataBaseFunctions.make_pwd_reset_req_not_active(secret_key)

    @staticmethod # מחזירה האם בקשת איפוס הסיסמה עדיין פעילה (על פי הsecret key)
    def pwd_reset_request_is_active(secret_key):
        conn = sqlite3.connect('database.db')
        active = conn.execute("select active from password_reset_requests where secret_key=?", (secret_key,))
        for row in active:
            if row[0] == 'yes':
                return True
            return False


    @staticmethod # מחזירה את המייל של המשתמש
    def get_email(username):
        conn = sqlite3.connect('database.db')
        email = conn.execute("select email from users where username=?", (username,))
        for row in email:
            return row[0]

    @staticmethod # שולחת הודעת מייל לשחזור סיסמה
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


    @staticmethod # מעדכנת את הסיסמה של המשתמש לסיסמה חדשה
    def reset_password(username, new_password):
        conn = sqlite3.connect('database.db')
        conn.execute("update users set password=? where username=?", (new_password, username))
        conn.commit()

    @staticmethod #  מחזירה רשימה של כל המשתמשים שהתחברו לאחרונה (בaccepted_time_difference דקות האחרונות)
    def get_all_users_online():
        todays_date = (str(datetime.now())).split(' ')[0].split('-')
        todays_date = todays_date[2] + '/' + todays_date[1] + '/' + todays_date[0]
        current_time = str(datetime.now().hour) + ':' + str(datetime.now().minute)

        # in minutes
        accepted_time_difference = 5

        users = []
        conn = sqlite3.connect('database.db')
        command = conn.execute("select username,last_login from users")
        for row in command:
            date = row[1].split(' ')[0]
            time = row[1].split(' ')[1]
            username = row[0]
            if date == todays_date and DataBaseFunctions.time_difference(current_time, time) <= accepted_time_difference:
                users.append(username)
        return users

    @staticmethod
    def get_home_page_note(ID):
        conn = sqlite3.connect('database.db')
        note = conn.execute("SELECT * from home_page_notes where ID=?", (ID,))
        for row in note:
            return {
                'ID' : row[0],
                'topic' : row[1],
                'link' : row[2]
            }

    @staticmethod
    def get_user_home_page_notes_IDs(username):
        conn = sqlite3.connect('database.db')
        notes_IDs = conn.execute("select home_page_notes_IDs from users where username=?", (username,))
        for row in notes_IDs:
            notes_IDs = row[0]
        if len(str(notes_IDs)) == 0:
            return []
        else:
            return notes_IDs.split(',')


    @staticmethod
    def get_user_home_page_notes(username):
        notes = []
        for note_ID in DataBaseFunctions.get_user_home_page_notes_IDs(username):
            notes.append(DataBaseFunctions.get_home_page_note(note_ID))
        return notes

    @staticmethod
    def add_home_page_note_users_table(username, ID):
        conn = sqlite3.connect('database.db')
        current_IDs = conn.execute("select home_page_notes_IDs from users where username=?" ,(username,))
        for row in current_IDs:
            current_IDs=row[0]
        if len(current_IDs) == 0:
            new_IDs = ID
        else:
            new_IDs = current_IDs + ',' + ID
        conn.execute("UPDATE users set home_page_notes_IDs=? where username=?", (new_IDs, username))
        conn.commit()

    @staticmethod
    def add_home_page_note_notes_table(ID, topic, link):
        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO home_page_notes (ID, topic, link) VALUES (?,?,?)", (ID, topic, link))
        conn.commit()

    @staticmethod
    def send_home_page_note(addressee, topic, link):
        # conn = sqlite3.connect('database.db')
        note_ID = DataBaseFunctions.random_id()
        DataBaseFunctions.add_home_page_note_users_table(username=addressee, ID=note_ID)
        DataBaseFunctions.add_home_page_note_notes_table(ID=note_ID, topic=topic, link=link)

    @staticmethod
    def delete_hp_note_if_nessaccery(username, current_url):
        conn = sqlite3.connect('database.db')
        print(DataBaseFunctions.get_user_home_page_notes(username))
        for hp_note in DataBaseFunctions.get_user_home_page_notes(username):
            if str(current_url) == str(hp_note['link']):
                print("Equals")
                DataBaseFunctions.delete_hp_note(username=username, ID=hp_note['ID'])

    @staticmethod
    def delete_hp_note(username, ID):
        conn = sqlite3.connect('database.db')
        current_IDs = conn.execute("select home_page_notes_IDs from users where username=?", (username,))
        for row in current_IDs:
            current_IDs=row[0]
        current_IDs = current_IDs.split(',')
        current_IDs.remove(ID)
        current_IDs = ','.join(current_IDs)
        conn.execute("UPDATE users set home_page_notes_IDs=? where username=?", (current_IDs, username))
        conn.commit()
