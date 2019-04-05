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
            "To login with your username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
            "To exit: exit\n"
        )

    def print_manual(self):
        print(
            "\nHere is a list of all the commands available:\n"\
            "To show all topics: show_topic\n"\
            "To create a topic: create_topic {TopicID}. Note that: TopicID will eliminate comma.\n"\
            "To initial a post REQUIRES LOGIN, init_post {Title} {TopicID},{TopicID}(at least one) {Content} \n"\
            "To show all groups, show_group\n"\
            "To create a group REQUIRES LOGIN, create_group {Name}\n"\
            "To join a groups REQUIRES LOGIN, join_group {GroupID}\n"\
            "To list out all usernames: show_user\n"\
            "To login with another username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
            "To logout: logout\n"\
            "To exit: exit\n"
        )

    def error_command(self):
        print("Invalid Command")

    def wait_command(self):
        self.command = input("Input Command: ").split(' ',1)

    def parse_command(self):
        if len(self.command) > 1:
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
        elif self.command[0] == "create_group":
            self.create_group()
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

    def record_already_exist(self, record_type):
        print("\n{} already exists.\n".format(record_type))

    def record_create_success(self, record_type):
        print("\n{} creates successfully.\n".format(record_type))

    def record_create_success_with_id(self,record_type, record_id):
        print("\n{} created successfully with ID: {}.\n".format(record_type, record_id))

    def error_record_not_found(self, record_type):
        print("\n{} not found.\n",format(record_type))

    def error_duplicate_record_found(self):
        print("\nFound duplicated record on primary key. Something is wrong.\n")

    def error_param_num(self):
        print("\nWrong number of parameters.\n")

    def error_not_login(self):
        print("\nYou are not logged in\n")

    def show_user(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Users"
        cursor.execute(query)
        print("\nHeader:\n('UserID', 'Name', 'Birthday')\nData:")
        print_cursor(cursor)
        cursor.close()

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
            self.error_record_not_found("Username")
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
            self.record_create_success("Username")
        elif len(result) == 1:
            self.record_already_exist("Username")
        else:
            self.error_duplicate_record_found()

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
            self.error_record_not_found("One of the topics is")
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
            self.record_create_success_with_id("Post", post_id)

    def show_topic(self):
        if len(self.command) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Topics"
        cursor.execute(query)
        print("\nHeader:\n('TopicID')\nData:")
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
            self.record_create_success("Topic")
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
        print("\nHeader:\n('GroupID', 'Name', 'CreatedBy')\nData:")
        print_cursor(cursor)
        cursor.close()

    def create_group(self):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = self.command[1].split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "insert into UserGroups (Name,CreatedBy) VALUES(\"{}\",\"{}\")".format(
            parameters[0],
            self.user_id
        )
        cursor.execute(query)
        self.connection.commit()
        group_id = cursor.lastrowid
        cursor.close()
        self.record_create_success_with_id("Group", group_id)

    def join_group_success(self, group_name):
        print("\nJoin group {} successfully.\n".format(group_name))

    def join_group(self):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = self.command[1].split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        result = self.check_record_exist("UserGroups", "GroupID", parameters[0])
        if len(result) == 0:
            self.error_record_not_found("Group")
        elif len(result) == 1:
            cursor = self.connection.cursor()
            query = "insert into UserJoinGroup VALUES(\'{}\',\'{}\')".format(
                self.user_id,
                parameters[0]
            )
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            self.join_group_success(result[0][1])
        else:
            self.error_duplicate_record_found()

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