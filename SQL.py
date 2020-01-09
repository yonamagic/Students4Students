import sqlite3


def create():
    conn = sqlite3.connect('user1.db')

    conn.execute('''CREATE TABLE users
        (
        username TEXT PRIMARY KEY NOT NULL,
        password TEXT NOT NULL,
        strong_subjects TEXT NOT NULL,
        weak_subjects TEXT NOT NULL
        );''')



    conn.execute('''CREATE TABLE subjects
            (
            subject TEXT PRIMARY KEY NOT NULL,
            categories TEXT NOT NULL
            );''')

    # Inserted first user
    conn.execute("INSERT INTO users "
                 "(username,password, strong_subjects, weak_subjects)  "\
                 "VALUES ('nir' , '1234', 'Math , Bible' , 'History') ");

    conn.execute("INSERT INTO users "
                 "(username,password, strong_subjects, weak_subjects)  "
                 "VALUES ('Yehoanatan' , '12345', 'Biology, Chemistry' , 'History') ")

    conn.execute("INSERT INTO subjects "
                 "(subject , categories)  "
                 "VALUES ('Math','Trigo , Algebra') ")
    cursor = conn.execute("select username from users")
    for row in cursor:
        print (row)


def signup(username,password,strong_subjects,weak_subjects):
    conn = sqlite3.connect('user1.db')
    cl = (conn.execute("select classes from subjects where username==(?) and subject==(?)",(username,'Math')))
    for r in cl:
        print(r)
if __name__ == '__main__':
    conn = sqlite3.connect('user1.db')
    signup('yoni',"1234",1,1)
    # cursor = conn.execute("select * from users_table where name=='yoni'")
    # for row in cursor:
    #     print(row)
