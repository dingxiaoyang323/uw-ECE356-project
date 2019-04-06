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
    THUMB_DOWN,
    READ_TYPE_ALL,
    READ_TYPE_UNREAD
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
            "To read all unread posts by topic: read_topic {TopicID} {Type}(all/unread)\n"\
            "To read all unread posts by user: read_user {UserID} {Type}(all/unread)\n"\
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

    def disconnect_db(self):
        self.connection.close()

    def check_record_exist(self, table, condition):
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from {} where {}".format(
            table,
            condition
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self.disconnect_db()
        return result
    
    def insert_record(self, table, columns, values):
        self.connect_to_db()
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
        self.disconnect_db()
        return record_id
# update posts set content = 'up' where postID = 22;
    def update_record(self, table, column, value, condition):
        self.connect_to_db()
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
        self.disconnect_db()
        return record_id

    def remove_record(self, table, condition):
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "delete from {} where {}".format(
            table,
            condition
        )
        cursor.execute(query)
        self.connection.commit()
        cursor.close()
        self.disconnect_db()
 # select content from posts inner join postresppost on (posts.PostID = postresppost.ResponseID and 
                # Type = 'thumb' and postresppost.PostID = 4 and posts.createdby = 'dxy')
    def check_exist_thumb_record(self, post_id, user_id):
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select PostRespPost.ResponseID,content from posts inner join postresppost on (Posts.PostID = "\
            "PostRespPost.ResponseID and Type = '{}' and PostRespPost.PostID = {} and Posts.CreatedBy = '{}')".format(
            POST_TYPE_THUMB,
            post_id,
            user_id
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self.disconnect_db()
        return result
        # select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopic.TopicID,Users.Name from posts join postundertopic on 
        # (posts.postID = postundertopic.postid and postundertopic.topicid = 'nakadashi') join users on 
        # (posts.createdby = users.userid)where posts.postid > 12 order by posts.postid desc;

        # select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopic.TopicID,Users.Name 
        # from Posts inner join PostUnderTopic using(PostID) join Users on (Posts.CreatedBy = Users.UserID) 
        # inner join UserFollowsTopic on (UserFollowsTopic.UserID = 'dxy' and UserFollowsTopic.FollowTopicID = 'nakadashi') 
        # where PostUnderTopic.TopicID = 'nakadashi' and Posts.PostID > UserFollowsTopic.LastReadPost and Posts.PostID not in 
        # (select PostID from Posts inner join UserFollowsUser on (UserFollowsUser.UserID = 'dxy' and
        # Posts.CreatedBy = UserFollowsUser.FollowUserID) where PostID <= LastReadPost) order by Posts.PostID desc
    def query_post_by_topic(self, topic_id, last_read_post_id, read_type):
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = ""
        if read_type == READ_TYPE_UNREAD:
            query = "select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopic.TopicID,Users.Name "\
                "from Posts inner join PostUnderTopic using(PostID) inner join Users on (Posts.CreatedBy = Users.UserID) "\
                "where PostUnderTopic.TopicId = \"{}\" and Posts.PostID > {} and Posts.PostID not in "\
                "(select PostID from Posts inner join UserFollowsUser on (UserFollowsUser.UserID = \"{}\" and "\
                "UserFollowsUser.FollowUserID = Posts.CreatedBy) where PostID <= LastReadPost) order by Posts.PostID desc".format(
                topic_id,
                last_read_post_id,
                self.user_id
            )
        elif read_type == READ_TYPE_ALL:
            query = "select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopic.TopicID,Users.Name "\
                "from Posts inner join PostUnderTopic using(PostID) inner join Users on (Posts.CreatedBy = Users.UserID)"\
                "where PostUnderTopic.TopicId = \"{}\" order by Posts.PostID desc".format(
                topic_id
            )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self.disconnect_db()
        return result

    def query_post_by_user(self, user_id, last_read_post_id, read_type):
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = ""
        if read_type == READ_TYPE_UNREAD:
            query = "select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopics.TopicID,Users.Name "\
                "from Posts inner join (select PostID,GROUP_CONCAT(TopicID SEPARATOR ',') as TopicID "\
                "from PostUnderTopic group by PostID) as PostUnderTopics using(PostID) inner join Users on "\
                "(Posts.CreatedBy = Users.UserID) where Posts.CreatedBy =  \"{}\" and Posts.PostID > {} and Posts.PostID not in "\
                "(select PostID from Posts inner join PostUnderTopic using(PostID) inner join UserFollowsTopic on "\
                "(UserFollowsTopic.UserID = \"{}\" and UserFollowsTopic.FollowTopicID = PostUnderTopic.TopicID)"\
                " where PostID <= LastReadPost) order by Posts.PostID desc".format(
                user_id,
                last_read_post_id,
                self.user_id
            )
        elif read_type == READ_TYPE_ALL:
            query = "select Posts.PostID,Posts.Name as Title,Type,Content,PostUnderTopics.TopicID,Users.Name "\
                "from Posts inner join (select PostID,GROUP_CONCAT(TopicID SEPARATOR ',') as TopicID "\
                "from PostUnderTopic group by PostID) as PostUnderTopics using(PostID) inner join Users on "\
                "(Posts.CreatedBy = Users.UserID) where Posts.CreatedBy =  \"{}\" order by Posts.PostID desc".format(
                user_id
            )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        self.disconnect_db()
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
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from Users"
        cursor.execute(query)
        print("\nHeader:\n('UserID', 'Name', 'Birthday')\nData:")
        print_cursor(cursor)
        cursor.close()
        self.disconnect_db()

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
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from Topics"
        cursor.execute(query)
        print("\nHeader:\n('TopicID')\nData:")
        print_cursor(cursor)
        cursor.close()
        self.disconnect_db()

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
            values = "\"{}\"".format(
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
            condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsTopic", condition)
            if len(result) == 0:
                values = "\"{}\",\"{}\",-NULL".format(
                    self.user_id,
                    parameters[0]
                )
                self.insert_record("UserFollowsTopic", "", values)
                self.follow_success("topic", parameters[0])
            elif len(result) == 1:
                self.error_already_followed(parameters[0])
            else:
                self.error_duplicate_record_found()
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
                self.unfollow_success("topic", parameters[0])
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

    def do_show_group(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from UserGroups"
        cursor.execute(query)
        print("\nHeader:\n('GroupID', 'Name', 'CreatedBy')\nData:")
        print_cursor(cursor)
        cursor.close()
        self.disconnect_db()

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
                values = "\"{}\",\"{}\"".format(
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

    def error_follow_oneself(self):
        print("\nYou cannot follow yourself\n")

    def do_follow_user(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 1:
            self.error_param_num()
            return
        if parameters[0] == self.user_id:
            self.error_follow_oneself()
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
                values = "\"{}\",\"{}\",NULL".format(
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
                condition = "PostID=\"{}\"".format(
                    parameters[0]
                )
                result = self.check_record_exist("PostUnderTopic", condition)
                for item in result:
                    values = "\"{}\",\"{}\"".format(
                        post_id,
                        item[1]
                    )
                    self.insert_record("PostUnderTopic", "", values)
                self.record_create_success_with_id("Response post", post_id)
            elif parameters[1] == POST_TYPE_THUMB:
                if not (parameters[2] == THUMB_UP or parameters[2] == THUMB_DOWN):
                    self.error_invalid_thumb_content()
                    return
                result = self.check_exist_thumb_record(original_post_id, self.user_id)
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
                    condition = "PostID=\"{}\"".format(
                        parameters[0]
                    )
                    result = self.check_record_exist("PostUnderTopic", condition)
                    for item in result:
                        values = "\"{}\",\"{}\"".format(
                            post_id,
                            item[1]
                        )
                        self.insert_record("PostUnderTopic", "", values)
                    self.record_create_success_with_id("Response post", post_id)
                elif len(result) == 1:
                    thumb_id = result[0][0]
                    thumb_content = result[0][1]
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
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from UserFollowsUser where UserID = \"{}\"".format(
            self.user_id
        )
        cursor.execute(query)
        print("\nlist of user id you are currently following:\n")
        print_cursor(cursor, 1)
        cursor.close()
        self.disconnect_db()

    def do_show_follow_topic(self, arg):
        if len(arg) != 0:
            self.error_param_num()
            return
        if self.login_status == False:
            self.error_not_login()
            return
        self.connect_to_db()
        cursor = self.connection.cursor()
        query = "select * from UserFollowsTopic where UserID = \"{}\"".format(
            self.user_id
        )
        cursor.execute(query)
        print("\nlist of topic id you are currently following:\n")
        print_cursor(cursor, 1)
        cursor.close()
        self.disconnect_db()

    def error_invalid_read_type(self):
        print(
            "\nType of this read is not valid. It only supports '{}' or '{}'\n".format(
                READ_TYPE_UNREAD,
                READ_TYPE_ALL
            )
        )

    def already_read_all_topic(self, topic_name):
        print(
            "\nYou have already read all posts under topic id {}\n".format(
                topic_name
            )
        )

    def do_read_topic(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 2:
            self.error_param_num()
            return
        if not (parameters[1] == READ_TYPE_ALL or parameters[1] == READ_TYPE_UNREAD):
            self.error_invalid_read_type()
            return
        condition = "TopicID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Topics", condition)
        if len(result) == 0:
            self.error_record_not_found("Topic")
        elif len(result) == 1:
            condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsTopic", condition)
            if len(result) == 0:
                self.error_not_following(parameters[0])
            elif len(result) == 1:
                last_read_post_id = result[0][2]
                if last_read_post_id is None:
                    last_read_post_id = -1
                result = self.query_post_by_topic(parameters[0], last_read_post_id, parameters[1])
                if len(result) == 0:
                    self.already_read_all_topic(parameters[0])
                else:
                    print_post(result)
                    condition = "UserID=\"{}\" and FollowTopicID=\"{}\"".format(
                        self.user_id,
                        parameters[0]
                    )
                    self.update_record("UserFollowsTopic", "LastReadPost", result[0][0], condition)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()

    def already_read_all_user(self, user_id):
        print(
            "\nYou have already read all posts from user id {}\n".format(
                user_id
            )
        )

    def do_read_user(self, arg):
        if self.login_status == False:
            self.error_not_login()
            return
        parameters = arg.split()
        if len(parameters) != 2:
            self.error_param_num()
            return
        if not (parameters[1] == READ_TYPE_ALL or parameters[1] == READ_TYPE_UNREAD):
            self.error_invalid_read_type()
            return
        condition = "UserID=\"{}\"".format(
            parameters[0]
        )
        result = self.check_record_exist("Users", condition)
        if len(result) == 0:
            self.error_record_not_found("User")
        elif len(result) == 1:
            condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                self.user_id,
                parameters[0]
            )
            result = self.check_record_exist("UserFollowsUser", condition)
            if len(result) == 0:
                self.error_not_following(parameters[0])
            elif len(result) == 1:
                last_read_post_id = result[0][2]
                if last_read_post_id is None:
                    last_read_post_id = -1
                result = self.query_post_by_user(parameters[0], last_read_post_id, parameters[1])
                if len(result) == 0:
                    self.already_read_all_user(parameters[0])
                else:
                    print_post(result)
                    condition = "UserID=\"{}\" and FollowUserID=\"{}\"".format(
                        self.user_id,
                        parameters[0]
                    )
                    self.update_record("UserFollowsUser", "LastReadPost", result[0][0], condition)
            else:
                self.error_duplicate_record_found()
        else:
            self.error_duplicate_record_found()


def print_cursor(cursor, index=None):
    row = cursor.fetchone()
    while row is not None:
        if index is None:
            print(row)
        else:
            print(row[index])
        row = cursor.fetchone()
    print("\n")

# +--------+---------+----------+------------------+-----------+--------+
# | PostID | Title   | Type     | Content          | topicid   | Name   |
# +--------+---------+----------+------------------+-----------+--------+
# |     27 | ti      | thumb    | down             | test_topic | edward |
# |     26 | ti      | response | this             | test_topic | edward |
# |     25 | titleee | response | this is a reply? | test_topic | edward |
# |     23 | titleee | initial  | haha             | test_topic | edward |
# |     18 | title   | initial  | content          | test_topic | edward |
# +--------+---------+----------+------------------+-----------+--------+
# (23, 'titleee', 'initial', 'haha', 'test_topic', 'edward')
def print_post(result):
    for post in result:
        if post[2] == POST_TYPE_INITIAL:
            print(
                "\n{} created a new post under topic: {}\nTitle: {}\nContent: {}\n".format(
                    post[5],
                    post[4],
                    post[1],
                    post[3]
                )
            )
        elif post[2] == POST_TYPE_RESPONSE:
            print(
                "\n{} responsed to post \"{}\" under topic: {}\nResponse: {}\n".format(
                    post[5],
                    post[1],
                    post[4],
                    post[3]
                )
            )
        elif post[2] == POST_TYPE_THUMB:
            print(
                "\n{} voted a thumb {} to post \"{}\" under topic: {}\n".format(
                    post[5],
                    post[3],
                    post[1],
                    post[4]
                )
            )
        # else:
        #     print("---------------------------------")
        #     print(post[0])

def escape_quote(string):
    return string.replace('"','\\"')

def main():
    session = Session()
    session.cmdloop(session.welcome_str + session.login_str)
    
if __name__=="__main__": 
    main()