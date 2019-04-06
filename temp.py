        # self.login_str = "\nYou have not logged in yet.\n"

        # self.login_str = "\nYou have not logged in yet.\n"\
        #     "To list out all usernames: show_user\n"\
        #     "To login with your username: login {UserID}\n"\
        #     "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
        #     "To exit: exit\n"

        # self.manual_str = "\nHere is a list of all the commands available:\n"\
        #     "To show all topics: show_topic\n"\
        #     "To create a topic: create_topic {TopicID}. Note that: TopicID will eliminate comma.\n"\
        #     "To follow a topic REQUIRES LOGIN, follow_topic {TopicID}\n"\
        #     "To unfollow a topic REQUIRES LOGIN, unfollow_topic {TopicID}\n"\
        #     "To initial a post REQUIRES LOGIN, init_post {Title} {TopicID},{TopicID}(at least one) {Content} \n"\
        #     "To reply to a post REQUIRES LOGIN, reply_post {PostID} {Type}(response/thumb) {Content}(string if response; 'up'/'down' if thumb)"\
        #     "To show all groups, show_group\n"\
        #     "To create a group REQUIRES LOGIN, create_group {Name}\n"\
        #     "To join a groups REQUIRES LOGIN, join_group {GroupID}\n"\
        #     "To leave a groups REQUIRES LOGIN, leave_group {GroupID}\n"\
        #     "To list out all usernames: show_user\n"\
        #     "To follow a user REQUIRES LOGIN, follow_user {UserID}\n"\
        #     "To unfollow a user REQUIRES LOGIN, unfollow_user {UserID}\n"\
        #     "To login with another username: login {UserID}\n"\
        #     "To create a new username: create_user {UserID} {Name} {Birthday}(optional)\n"\
        #     "To show all users you are following: show_follow_user\n"\
        #     "To show all topics you are following: show_follow_topic\n"\
        #     "To read all unread posts by topic: read_topic {TopicID} {Type}(all/unread)\n"\
        #     "To read all unread posts by user: read_user {UserID} {Type}(all/unread)\n"\
        #     "To logout: logout\n"\
        #     "To exit: exit\n"

        # def print_login(self):
        #     print(self.login_str)

        # def print_manual(self):
        #     print(self.manual_str)

        # def error_command(self):
        #     print("\nInvalid Command\n")