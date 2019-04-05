import constant
import mysql.connector
import cmd

PROMPT_NAME = '(ece356-proj)'

class Session(cmd.Cmd):
    prompt = PROMPT_NAME
    def __init__(self):
        super().__init__()
        self.user_id = ""
        self.login_status = False
        self.connection = None

        self.welcome_str = "Welcome to the ece356 project.   Type help to list commands.\n"

        self.login_str = "\nYou have not logged in yet.\n"\
            "To list out all usernames: show_user\n"\
            "To login with your username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
            "To exit: exit\n"

        self.manual_str = "\nHere is a list of all the commands available:\n"\
            "To show all topics: show_topic\n"\
            "To create a topic: create_topic {TopicID}. Note that: TopicID will eliminate comma.\n"\
            "To initial a post REQUIRES LOGIN, init_post {Title} {TopicID},{TopicID}(at least one) {Content} \n"\
            "To show all groups, show_group\n"\
            "To create a group REQUIRES LOGIN, create_group {Name}\n"\
            "To join a groups REQUIRES LOGIN, join_group {GroupID}\n"\
            "To leave a groups REQUIRES LOGIN, leave_group {GroupID}\n"\
            "To list out all usernames: show_user\n"\
            "To follow a user REQUIRES LOGIN, follow_user {UserID}\n"\
            "To unfollow a user REQUIRES LOGIN, unfollow_user {UserID}\n"\
            "To login with another username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
            "To logout: logout\n"\
            "To exit: exit\n"

    def precmd(self, line):
        return escape_quote(line)

    def print_login(self):
        print(self.login_str)

    def print_manual(self):
        print(self.manual_str)

    def error_command(self):
        print("\nInvalid Command\n")

    def connect_to_db(self):
        self.connection = mysql.connector.connect(user=constant.USER, database=constant.DATABASE, host = constant.HOST)

    def check_record_exist(self, table, condition):
        cursor = self.connection.cursor()
        query = "select * from {} where {}".format(
            table,
            condition
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def insert_record(self, table, columns, values):
        cursor = self.connection.cursor()
        query = "insert into {} {} VALUES({})".format(
            table,
            columns,
            values
        )
        cursor.execute(query)
        self.connection.commit()
        record_id = cursor.lastrowid
        cursor.close()
        return record_id

    def remove_record(self, table, condition):
        cursor = self.connection.cursor()
        query = "delete from {} where {}".format(
            table,
            condition
        )
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def record_already_exist(self, record_type):
        print("\n{} already exists.\n".format(record_type))

    def record_create_success(self, record_type):
        print("\n{} creates successfully.\n".format(record_type))

    def record_create_success_with_id(self,record_type, record_id):
        print("\n{} created successfully with ID: {}.\n".format(record_type, record_id))

    def error_record_not_found(self, record_type):
        print("\n{} not found.\n".format(record_type))

    def error_duplicate_record_found(self):
        print("\nFound duplicated record on primary key. Something is wrong.\n")

    def error_param_num(self):
        print("\nWrong number of parameters.\n")

    def error_not_login(self):
        print("\nYou are not logged in\n")

    def do_exit(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        return True

    def do_show_user(self, arg):
        if len(arg) != 0:
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

    def do_login(self, arg):
        parameters = arg.split()
        # user_id = parameters[0]
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "UserID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Users", condition)
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

    def do_logout(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        self.user_id = ""
        self.login_status = False
        self.print_logout()
        self.print_login()

    def do_create_user(self, arg):
        parameters = arg.split()
        # user_id = parameters[0]
        # name = parameters[1]
        # birthday = parameters[2]
        if len(parameters) < 2 or len(parameters) > 3:
            self.error_param_num()
            return
        condition = "UserID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Users", condition)
        if len(result) == 0:
            if len(parameters) == 2:
                values = "\"{}\",\"{}\",NULL".format(
                    parameters[0], 
                    parameters[1]
                )
            elif len(parameters) == 3:
                values = "\"{}\",\"{}\",\"{}\"".format(
                    parameters[0], 
                    parameters[1],
                    parameters[2]
                )
            self.insert_record("Users", "", values)
            self.record_create_success("Username")
        elif len(result) == 1:
            self.record_already_exist("Username")
        else:
            self.error_duplicate_record_found()

    def do_init_post(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split(' ',2)
        # title = parameters[0]
        # topics = parameters[1]
        # content = parameters[2]
        if len(parameters) < 3:
            self.error_param_num()
            return
        topics = parameters[1].split(',')
        topic_exists = True
        for _topic in topics:
            condition = "TopicID=\"{}\"".format(
                _topic
            )
            result = self.check_record_exist("Topics", condition)
            if len(result) == 0:
                topic_exists = False
                break
        if not topic_exists:
            self.error_record_not_found("One of the topics is")
        else:
            values = "\"{}\",\"{}\",\"{}\",\"{}\"".format(
                parameters[0],
                "text",
                parameters[2],
                self.user_id
            )
            post_id = self.insert_record("Posts", "(Name,Type,Content,CreatedBy)", values)

            for _topic in topics:
                values = "\"{}\",\"{}\"".format(
                    post_id,
                    _topic
                )
                self.insert_record("PostUnderTopic", "", values)
            self.record_create_success_with_id("Post", post_id)

    def do_show_topic(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Topics"
        cursor.execute(query)
        print("\nHeader:\n('TopicID')\nData:")
        print_cursor(cursor)
        cursor.close()

    def do_create_topic(self, arg):
        parameters = arg.split()
        # Topic_id = parameters[0]
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "TopicID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Topics", condition)
        if len(result) == 0:
            values = "\'{}\'".format(
                parameters[0].replace(',','')
            )
            self.insert_record("Topics", "", values)
            self.record_create_success("Topic")
        elif len(result) == 1:
            self.record_already_exist("Topic")
        else:
            self.error_duplicate_record_found()

    def do_show_group(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from UserGroups"
        cursor.execute(query)
        print("\nHeader:\n('GroupID', 'Name', 'CreatedBy')\nData:")
        print_cursor(cursor)
        cursor.close()

    def do_create_group(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        values = "\"{}\",\"{}\"".format(
            parameters[0],
            self.user_id
        )
        group_id = self.insert_record("UserGroups", "(Name,CreatedBy)", values)
        self.record_create_success_with_id("Group", group_id)

    def join_group_success(self, group_name):
        print("\nJoin group {} successfully.\n".format(group_name))

    def error_already_in_group(self, group_name):
        print("\nYou are already in the group {}.\n".format(group_name))

    def do_join_group(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "GroupID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("UserGroups", condition)
        if len(result) == 0:
            self.error_record_not_found("Group")
        elif len(result) == 1:
            group_name = result[0][1]
            condition = "UserID=\"{}\" and GroupID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserJoinGroup", condition)
            if len(result) == 0:
                values = "\'{}\',\'{}\'".format(
                    self.user_id,
                    parameters[0]
                )
                self.insert_record("UserJoinGroup", "", values)
                self.join_group_success(group_name)
            elif len(result) == 1:
                self.error_already_in_group(group_name)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

    def error_not_in_group(self):
        print("\nYou are not currently in this group.\n")

    def leave_group_success(self, group_name):
        print("\nLeave group {} successfully.\n".format(group_name))

    def do_leave_group(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "GroupID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("UserGroups", condition)
        if len(result) == 0:
            self.error_record_not_found("Group")
        elif len(result) == 1:
            group_name = result[0][1]
            condition = "UserID=\"{}\" and GroupID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserJoinGroup", condition)
            if len(result) == 0:
                self.error_not_in_group()
            elif len(result) == 1:
                condition = "UserID=\"{}\" and GroupID=\"{}\"".format(
                    self.user_id,
                    parameters[0]
                )
                self.remove_record("UserJoinGroup", condition)
                self.leave_group_success(group_name)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

    def follow_user_success(self, user_name):
        print("\nFollow user {} successfully.\n".format(user_name))

    def error_already_followed(self, user_name):
        print("\nYou have already followed {}.\n".format(user_name))

    def do_follow_user(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "UserID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Users", condition)
        if len(result) == 0:
            self.error_record_not_found("User")
        elif len(result) == 1:
            user_name = result[0][1]
            condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsUser", condition)
            if len(result) == 0:
                values = "\'{}\',\'{}\',NULL".format(
                    self.user_id,
                    parameters[0]
                )
                self.insert_record("UserFollowsUser", "", values)
                self.follow_user_success(user_name)
            elif len(result) == 1:
                self.error_already_followed(user_name)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

    def error_not_following(self):
        print("\nYou are not currently follow this user.\n")

    def unfollow_user_success(self, user_name):
        print("\nUnfollow user {} successfully.\n".format(user_name))
    
    def do_unfollow_user(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "UserID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Users", condition)
        if len(result) == 0:
            self.error_record_not_found("User")
        elif len(result) == 1:
            user_name = result[0][1]
            condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsUser", condition)
            if len(result) == 0:
                self.error_not_following()
            elif len(result) == 1:
                condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                    self.user_id,
                    parameters[0]
                )
                self.remove_record("UserFollowsUser", condition)
                self.unfollow_user_success(user_name)
            else:
                self.error_duplicate_record_found()
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
    session.cmdloop(session.welcome_str + session.login_str)
    
if __name__=="__main__": 
    main()