import sqlite3
from Subject import Subject
class DataBaseFunctions:

    subjects = ['Math', 'History', 'Arabic', 'Bible']


    @staticmethod
    def user_exists(username):
        conn = sqlite3.connect('database.db')
        com = conn.execute("select username from users where username==? ", (username,))
        for row in com:
            return True
        return False

    @staticmethod
    def create_user(username, password, strong_subjects=[], weak_subjects=[]):
        conn = sqlite3.connect('database.db', timeout=2)
        # cursor = conn.execute("select * from users where username='yehonatan'")
        # for i in cursor:
        #     print("fffff"+str(i))
        conn.execute("insert into users "
                     "(username, password, strong_subjects, weak_subjects) values (?,?,?,?)",
                     (username,
                      password,
                      DataBaseFunctions.subjects_list_to_string(strong_subjects),
                      DataBaseFunctions.subjects_list_to_string(weak_subjects)))
        # com = conn.execute("select * from users where username=?", (username,))
        # conn.commit()

        # DataBaseFunctions.create_strong_subs_in_users_table(conn,strong_subjects, username)
        DataBaseFunctions.create_subs_in_subjects_table(conn,strong_subjects, username)
        DataBaseFunctions.create_subs_in_subjects_table(conn,weak_subjects, username)

        # DataBaseFunctions.edit_subjects_in_subjects_table(username=username, subjects=strong_subjects+weak_subjects)
        # DataBaseFunctions.create_weak_subs_in_users_table(conn,weak_subjects, username)
        conn.commit()

        # for r in com:
        #     print (r)
        # conn.commit()

    @staticmethod#Edits the column "strong_subjects" in users table
    def edit_user_strong_subjects(username, strong_subjects):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("update users set strong_subjects = ? where username = ?",
                     (DataBaseFunctions.subjects_list_to_string(strong_subjects),
                      username))
        conn.commit()

    @staticmethod#Edits the column "weak_subjects" in users table
    def edit_user_weak_subjects(username, weak_subjects):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("update users set weak_subjects = ? where username = ?",
                     (DataBaseFunctions.subjects_list_to_string(weak_subjects),
                      username))
        conn.commit()


    @staticmethod#Adds info to subjects table accordingly
    def edit_subjects_in_subjects_table(username, subjects):
        DataBaseFunctions.delete_user_from_subjects_table(username)
        conn = sqlite3.connect("database.db", timeout=2)
        for subject in subjects:
            conn.execute("insert into subjects (username, subject, classes) values (?,?,?)",
                         (username, subject.name, str(subject.classes)[1:-1].replace(' ', '')))
        conn.commit()

    @staticmethod#Deleted all rows in subjects table where username fits to parameter
    def delete_user_from_subjects_table(username):
        conn = sqlite3.connect("database.db", timeout=2)
        conn.execute("delete from subjects where username=?", (username,))
        conn.commit()

    @staticmethod
    def subjects_list_to_string(subjects_list):
        string = ""
        for sub in subjects_list:
            string += ',' + sub.name
        string = string[1:]
        return string


    @staticmethod#Takes care of creating information in table: subjects, strong/weak according to the paramater
    def create_subs_in_subjects_table(conn, subs, username):

        for sub in subs:
            #turn classes into a string for the DB
            classes_as_string = ''
            for current_class in sub.classes:
                classes_as_string += "," + str(current_class)
            classes_as_string = classes_as_string[1:]
            #----------------------------------------
            conn.execute("insert into subjects (username, subject, classes) values (?,?,?)", (username,sub.name,classes_as_string,))
            conn.commit()

    @staticmethod #Returns True if username and password match database info
    def correctDetails(username, password):
        conn = sqlite3.connect('database.db')
        # print(username,password)
        com = conn.execute("select username from users where username==? and password==?" , (username,password))

        for row in com:
            return True
        return False


    @staticmethod#returns a list of subjects
    def get_user_strong_subjects(username):
        ret_subjects = []
        subs = DataBaseFunctions.get_strong_subjects(username)
        for sub in subs:
            ret_subjects.append(Subject(sub,DataBaseFunctions.get_subject_classes(username,sub)))
        return ret_subjects

    @staticmethod
    def get_strong_subjects(username):
        conn = sqlite3.connect('database.db')
        att = conn.execute("select strong_subjects from users where username== ? ", (username,))
        for row in att:
            # print (row[0])#row[0] is the whole string
            att = row[0].split(',')
        return att

    @staticmethod
    def get_weak_subjects(username):
        conn = sqlite3.connect('database.db')
        att = conn.execute("select weak_subjects from users where username== ? ", (username,))
        for row in att:
            # print (row[0])#row[0] is the whole string
            att = row[0].split(',')
        return att

    @staticmethod
    def get_subject_classes(username,subject):
        conn = sqlite3.connect('database.db')
        att = conn.execute("select classes from subjects where username==? and subject==?" , (username,subject))
        for row in att:
            att = row[0].split(',')
        return att


    @staticmethod
    def potential_teachers(weak_subjects=[]):
        conn = sqlite3.connect('database.db')
        weak_subjects_names = []
        for sub in weak_subjects:#Create a list made of those subjects' names
            weak_subjects_names.append(sub.name)

        teachers = conn.execute("select * from users")
        subs_lists=[]#Each index conatins a tupple made of the username and the strong subjects of a user as a string
        for i in teachers:
            subs_lists.append((i[0],i[2]))

        teachers_by_subject = []
        teachers_by_classes = []
        for user in subs_lists:
            strong_subjects = user[1].split(',')
            for subject in strong_subjects:
                if subject in weak_subjects_names:
                    teachers_by_subject.append((user[0],subject))
                    common_classes = conn.execute("select classes from subjects where username==(?) and subject==(?) ",
                                                                                                                (user[0],subject))
                    for row in common_classes:
                        common_classes = row
                    teachers_by_classes.append((user[0],subject,common_classes))
        # print(teachers_by_subject)
        # print(teachers_by_classes)

        return (teachers_by_classes,teachers_by_subject)

    @staticmethod
    def teachers_by_subjects(teachers):
        teachers_by_classes = teachers[0]
        # teachers_by_subject = teachers[1]
        subjects = []
        for t in teachers_by_classes:
            if t[1] not in subjects:
                subjects.append([t[1],[]])

        for subject in subjects:
            for t in teachers_by_classes:
                if t[1] == subject[0]:
                    subject[1].append(t[0])

        print (subjects)#A list, each index contains a list in which the first index includes subcject name and the second one - a list of relevant usernames
        return subjects
        #Get it from here Yehonatan!

    @staticmethod
    def matching_classes(users, subject):
        conn = sqlite3.connect('database.db')
        classes1 = conn.execute("select classes from subjects where username=? and subject=?", (users[0],subject))
        for row in classes1:
            classes1 = row

        classes2 = conn.execute("select classes from subjects where username=? and subject=?", (users[1],subject))
        for row in classes2:
            classes2 = row
        # print(classes2)

        classes1 = classes1[0].split(',')
        classes2 = classes2[0].split(',')

        # print(classes1, classes2)
        common_classes = (list(set(classes1).intersection(classes2)))
        if common_classes:#if there are common classes
            return common_classes
        return None

    # Gets username a list of subjects' names and returns a list that contains those subjects as Subject type and their relevant classes
    # it is needed in profile page
    @staticmethod
    def subjects_as_list_of_Subjects(username, subs):
        print("subs=" + str(subs))
        subjects = []
        for current_subject in subs:
            classes = DataBaseFunctions.get_subject_classes(username, current_subject)
            subjects.append(Subject(current_subject, classes))
            # print (subjects[i].name, str(subjects[i].classes))

        return subjects


# DataBaseFunctions.edit_user_strong_subjects(sqlite3.connect("database.db", timeout=2),"yoni", [Subject("Mathematics",[10,11]), Subject("Bio",[10,12])])
# DataBaseFunctions.delete_user_from_subjects_table('helloMeyyy')
# print(str([1,2,3])[1:-1].replace(' ', ''))
# DataBaseFunctions.edit_subjects_in_subjects_table('yoni',[Subject("Math",[10,11]), Subject("Arabic",[10,11,12])])
# DataBaseFunctions.edit_subjects_in_subjects_table(username='newYoni', subjects=[Subject("Math",[10,11])]+[Subject("Arabic",[10,11,12])])
