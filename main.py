import mysql.connector
import cmd
from constant import (
    HOST,
    USER,
    DATABASE,
    PROMPT_NAME,
    POST_TYPE_INITIAL,
    POST_TYPE_RESPONSE,
    POST_TYPE_THUMB,
    THUMB_UP,
    THUMB_DOWN
)

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
            "To follow a topic REQUIRES LOGIN, follow_topic {TopicID}\n"\
            "To unfollow a topic REQUIRES LOGIN, unfollow_topic {TopicID}\n"\
            "To initial a post REQUIRES LOGIN, init_post {Title} {TopicID},{TopicID}(at least one) {Content} \n"\
            "To reply to a post REQUIRES LOGIN, reply_post {PostID} {Type}(response/thumb) {Content}(string if response; 'up'/'down' if thumb)"\
            "To show all groups, show_group\n"\
            "To create a group REQUIRES LOGIN, create_group {Name}\n"\
            "To join a groups REQUIRES LOGIN, join_group {GroupID}\n"\
            "To leave a groups REQUIRES LOGIN, leave_group {GroupID}\n"\
            "To list out all usernames: show_user\n"\
            "To follow a user REQUIRES LOGIN, follow_user {UserID}\n"\
            "To unfollow a user REQUIRES LOGIN, unfollow_user {UserID}\n"\
            "To login with another username: login {UserID}\n"\
            "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
            "To show all users you are following: show_follow_user\n"\
            "To show all topics you are following: show_follow_topic\n"\
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
        self.connection = mysql.connector.connect(user=USER, database=DATABASE, host = HOST)

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
# update posts set content = 'up' where postID = 22;
    def update_record(self, table, column, value, condition):
        cursor = self.connection.cursor()
        query = "update {} set {} = \'{}\' where {}".format(
            table,
            column,
            value,
            condition
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
 # select content from posts inner join postresppost on (posts.PostID = postresppost.ResponseID and 
                # Type = 'thumb' and postresppost.PostID = 4 and posts.createdby = 'dxy')
    def check_exist_thumb_record(self, post_id, user_id):
        cursor = self.connection.cursor()
        query = "select PostRespPost.ResponseID,content from posts inner join postresppost on (Posts.PostID = PostRespPost.ResponseID and "\
            "Type = '{}' and PostRespPost.PostID = {} and Posts.CreatedBy = '{}')".format(
            POST_TYPE_THUMB,
            post_id,
            user_id
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
        print("\n{} not found.\n".format(record_type))

    def error_duplicate_record_found(self):
        print("\nFound duplicated record on primary key. Something is wrong.\n")

    def error_param_num(self):
        print("\nWrong number of parameters.\n")

    def error_not_login(self):
        print("\nYou are not logged in\n")

    def error_already_followed(self, name):
        print("\nYou have already followed {}.\n".format(name))

    def follow_success(self, record_type, record_name):
        print("\nFollow {} {} successfully.\n".format(record_type, record_name))

    def error_not_following(self, name):
        print("\nYou are not currently following {}.\n".format(name))

    def unfollow_success(self, record_type, record_name):
        print("\nUnfollow {} {} successfully.\n".format(record_type, record_name))

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
                POST_TYPE_INITIAL,
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

    def do_follow_topic(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "TopicID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Topics", condition)
        if len(result) == 0:
            self.error_record_not_found("Topic")
        elif len(result) == 1:
            topic_name = result[0][0]
            condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsTopic", condition)
            if len(result) == 0:
                values = "\'{}\',\'{}\',NULL".format(
                    self.user_id,
                    parameters[0]
                )
                self.insert_record("UserFollowsTopic", "", values)
                self.follow_success("topic", topic_name)
            elif len(result) == 1:
                self.error_already_followed(topic_name)
            else:
                self.error_duplicate_record_found()

    def do_unfollow_topic(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        condition = "TopicID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Topics", condition)
        if len(result) == 0:
            self.error_record_not_found("Topic")
        elif len(result) == 1:
            topic_name = result[0][0]
            condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsTopic", condition)
            if len(result) == 0:
                self.error_not_following(parameters[0])
            elif len(result) == 1:
                condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                    self.user_id,
                    parameters[0]
                )
                self.remove_record("UserFollowsTopic", condition)
                self.unfollow_success("topic", topic_name)
            else:
                self.error_duplicate_record_found()
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
                self.follow_success("user", user_name)
            elif len(result) == 1:
                self.error_already_followed(user_name)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

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
                self.error_not_following(parameters[0])
            elif len(result) == 1:
                condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                    self.user_id,
                    parameters[0]
                )
                self.remove_record("UserFollowsUser", condition)
                self.unfollow_success("user", user_name)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()
    
    def error_invalid_post_type(self):
        print(
            "\nType of this post is not valid. It only supports '{}' or '{}'\n".format(
                POST_TYPE_RESPONSE,
                POST_TYPE_THUMB
            )
        )

    def error_invalid_thumb_content(self):
        print(
            "\nContent of thumb is not valid. It only supports '{}' or '{}'\n".format(
                THUMB_UP,
                THUMB_DOWN
            )
        )

    def error_already_vote_thumb(self, thumb_type, post_id):
        print(
            "\nYou already vote thumb {} on post {}\n".format(
                thumb_type,
                post_id
            )
        )

    def update_thumb_success(self, thumb_type, post_id):
        print(
            "\nSuccessfully update your vote to thumb {} on post {}\n".format(
                thumb_type,
                post_id
            )
        )

    def do_reply_post(self, arg):
        # reply_post {PostID} {Type}(text/thumb) {Content}(string if text, 'up'/'down' if thumb)
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split(' ',2)
        condition = "PostID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Posts", condition)
        if len(result) == 0:
            self.error_record_not_found("Post")
        elif len(result) == 1:
            original_post_id = result[0][0]
            original_post_name = result[0][1]
            if parameters[1] == POST_TYPE_RESPONSE:
                values = "\"{}\",\"{}\",\"{}\",\"{}\"".format(
                    original_post_name,
                    POST_TYPE_RESPONSE,
                    parameters[2],
                    self.user_id
                )
                post_id = self.insert_record("Posts", "(Name,Type,Content,CreatedBy)", values)
                values = "\"{}\",\"{}\"".format(
                    original_post_id,
                    post_id
                )
                self.insert_record("PostRespPost", "", values)
                self.record_create_success_with_id("Response post", post_id)
            elif parameters[1] == POST_TYPE_THUMB:
                if not (parameters[2] == THUMB_UP or parameters[2] == THUMB_DOWN):
                    self.error_invalid_thumb_content()
                    return
                result = self.check_exist_thumb_record(original_post_id, self.user_id)
                thumb_id = result[0][0]
                thumb_content = result[0][1]
                if len(result) == 0:
                    values = "\"{}\",\"{}\",\"{}\",\"{}\"".format(
                        original_post_name,
                        POST_TYPE_THUMB,
                        parameters[2],
                        self.user_id
                    )
                    post_id = self.insert_record("Posts", "(Name,Type,Content,CreatedBy)", values)
                    values = "\"{}\",\"{}\"".format(
                        original_post_id,
                        post_id
                    )
                    self.insert_record("PostRespPost", "", values)
                    self.record_create_success_with_id("Response post", post_id)
                elif len(result) == 1:
                    if parameters[2] == thumb_content:
                        if thumb_content == THUMB_UP:
                            self.error_already_vote_thumb(THUMB_UP, original_post_id)
                        elif thumb_content == THUMB_DOWN:
                            self.error_already_vote_thumb(THUMB_DOWN, original_post_id)
                    else:
                        condition = "PostID = {}".format(
                            thumb_id
                        )
                        self.update_record("Posts", "Content", parameters[2], condition)
                        self.update_thumb_success(parameters[2], original_post_id)
                else:
                    self.error_duplicate_record_found()
            else:
                self.error_invalid_post_type()
        else:
            self.error_duplicate_record_found()

    def do_show_follow_user(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        if self.login_status == False:
            self.error_not_login()
            return
        cursor = self.connection.cursor()
        query = "select * from UserFollowsUser where UserID = \"{}\"".format(
            self.user_id
        )
        cursor.execute(query)
        print("\nlist of user id you are currently following:\n")
        print_cursor(cursor, 1)
        cursor.close()

    def do_show_follow_topic(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        if self.login_status == False:
            self.error_not_login()
            return
        cursor = self.connection.cursor()
        query = "select * from UserFollowsTopic where UserID = \"{}\"".format(
            self.user_id
        )
        cursor.execute(query)
        print("\nlist of topic id you are currently following:\n")
        print_cursor(cursor, 1)
        cursor.close()

def print_cursor(cursor, index=None):
    row = cursor.fetchone()
    while row is not None:
        if index is None:
            print(row)
        else:
            print(row[index])
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