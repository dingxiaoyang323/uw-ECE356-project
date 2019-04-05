import constant
import mysql.connector


class Session:
    def __init__(self):
        self.user_id = ""
        self.login_status = False
        self.connection = None
        self.command = None

    def print_login(self):
        print(
            "\nYou have not logged in yet.\n"\
            "To list out all usernames: show_user\n"\
            "To login with your username: login {userID}\n"\
            "To create a new username: create_user {userID} {name} {birthday}(optional)\n"\
            "To exit: exit\n"
        )

    def print_manual(self):
        print(
            "\nHere is a list of all the commands available:\n"\
            "To show all topics: show_topic\n"\
            "To create a topic: create_topic {TopicID}. Note that: TopicID will eliminate comma.\n"\
            "To initial a post REQUIRES LOGIN, init_post {title} {TopicID},{TopicID}(at least one) {content} \n"\
            "To show all groups, show_group\n"\
            "To join a groups REQUIRES LOGIN, join_group {GroupID}\n"\
            "To list out all usernames: show_user\n"\
            "To login with another username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {name} {birthday}(optional)\n"\
            "To logout: logout\n"\
            "To exit: exit\n"
        )

    def error_command(self):
        print("Invalid Command")

    def wait_command(self):
        self.command = input("Input Command: ").split(' ',1)

    def parse_command(self):
        self.command[1] = escape_quote(self.command[1])

        if self.command[0] == "show_user":
            self.show_user()
        elif self.command[0] == "login":
            self.login()
        elif self.command[0] == "logout":
            self.logout()
        elif self.command[0] == "create_user":
            self.create_user()
        elif self.command[0] == "show_topic":
            self.show_topic()
        elif self.command[0] == "create_topic":
            self.create_topic()
        elif self.command[0] == "init_post":
            self.init_post()
        elif self.command[0] == "show_group":
            self.show_group()
        elif self.command[0] == "join_group":
            self.join_group()
        elif self.command[0] == "exit":
            exit()
        else:
            self.error_command()

    def execute(self):
        self.print_login()
        while (True):
            self.wait_command()
            self.parse_command()

    def connect_to_db(self):
        self.connection = mysql.connector.connect(user=constant.USER, database=constant.DATABASE, host = constant.HOST)

    def check_record_exist(self, table, column, value):
        cursor = self.connection.cursor()
        query = "select * from {} where {}=\"{}\"".format(
            table,
            column,
            value
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def show_user(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Users"
        cursor.execute(query)
        print("\nHeader: 'UserID', 'Name', 'Birthday'\nData:")
        print_cursor(cursor)
        cursor.close()

    def error_userid_not_found(self):
        print("\nUsername Not Found.\n")

    def error_duplicate_record_found(self):
        print("\nFound duplicated record. Something is wrong.\n")

    def error_param_num(self):
        print("\nWrong number of parameters.\n")

    def login_success(self, username):
        print("\nYou have logged in as: {}\n".format(username))

    def login(self):
        parameters = self.command[1].split()
        # user_id = parameters[0]
        if len(parameters) != 1:
            self.error_param_num()
            return
        result = self.check_record_exist("Users", "UserID", parameters[0])
        if len(result) == 0:
            self.error_userid_not_found()
        elif len(result) == 1:
            self.login_status = True
            self.user_id = result[0][0]
            self.login_success(result[0][1])
            self.print_manual()
        else:
            self.error_duplicate_record_found()

    def print_logout(self):
        print("\nLogout successfully.\n")

    def logout(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        self.user_id = ""
        self.login_status = False
        self.print_logout()
        self.print_login()

    def record_already_exist(self, record_type):
        print("\n{} already exists.\n".format(record_type))

    def create_record_success(self, record_type):
        print("\n{} creates successfully.\n".format(record_type))

    def create_user(self):
        parameters = self.command[1].split()
        # user_id = parameters[0]
        # name = parameters[1]
        # birthday = parameters[2]
        if len(parameters) < 2 or len(parameters) > 3:
            self.error_param_num()
            return
        result = self.check_record_exist("Users", "UserID", parameters[0])
        if len(result) == 0:
            cursor = self.connection.cursor()
            if len(parameters) == 2:
                query = "insert into Users VALUES(\"{}\",\"{}\",NULL)".format(
                    parameters[0], 
                    parameters[1]
                )
            elif len(parameters) == 3:
                query = "insert into Users VALUES(\"{}\",\"{}\",\"{}\")".format(
                    parameters[0], 
                    parameters[1],
                    parameters[2]
                )
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            self.create_record_success("Username")
        elif len(result) == 1:
            self.record_already_exist("Username")
        else:
            self.error_duplicate_record_found()

    def error_topic_not_exists(self):
        print("\nOne of the topics does not exist.\n")

    def error_not_login(self):
        print("\nYou are not logged in\n")

    def post_create_success(self, post_id):
        print("\nPost created successfully with PostID:{}\n".format(post_id))

    def init_post(self):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = self.command[1].split(' ',2)
        # title = parameters[0]
        # topics = parameters[1]
        # content = parameters[2]
        if len(parameters) < 3:
            self.error_param_num()
            return
        topics = parameters[1].split(',')
        topic_exists = True
        for _topic in topics:
            result = self.check_record_exist("Topics", "TopicID", _topic)
            if len(result) == 0:
                topic_exists = False
                break
        if not topic_exists:
            self.error_topic_not_exists()
        else:
            cursor = self.connection.cursor()
            query = "insert into Posts (Name,Type,Content,CreatedBy) VALUES(\"{}\",\"{}\",\"{}\",\"{}\")".format(
                parameters[0],
                "text",
                parameters[2],
                self.user_id
            )
            cursor.execute(query)
            self.connection.commit()
            post_id = cursor.lastrowid
            cursor.close()

            for _topic in topics:
                cursor = self.connection.cursor()
                query = "insert into PostUnderTopic VALUES(\"{}\",\"{}\")".format(
                    post_id,
                    _topic
                )
                cursor.execute(query)
                self.connection.commit()
                cursor.close()
            self.post_create_success(post_id)

    def show_topic(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Topics"
        cursor.execute(query)
        print("\nHeader: 'TopicID'\nData:")
        print_cursor(cursor)
        cursor.close()

    def create_topic(self):
        parameters = self.command[1].split()
        # Topic_id = parameters[0]
        if len(parameters) != 1:
            self.error_param_num()
            return
        result = self.check_record_exist("Topics", "TopicID", parameters[0])
        if len(result) == 0:
            cursor = self.connection.cursor()
            query = "insert into Topics VALUES(\'{}\')".format(
                parameters[0].replace(',','')
            )
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            self.create_record_success("Topic")
        elif len(result) == 1:
            self.record_already_exist("Topic")
        else:
            self.error_duplicate_record_found()

    def show_group(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from UserGroups"
        cursor.execute(query)
        print("\nHeader: 'GroupID', 'Name', 'CreatedBy'\nData:")
        print_cursor(cursor)
        cursor.close()

    def join_group(self):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = self.command[1].split()
        if len(parameters) != 1:
            self.error_param_num()
            return

def print_cursor(cursor):
    row = cursor.fetchone()
    while row is not None:
        print(row)
        row = cursor.fetchone()
    print("\n")

def escape_quote(string):
    return string.replace('"','\\"')

def main():
    session = Session()
    session.connect_to_db()
    session.execute()
    
if __name__=="__main__": 
    main()