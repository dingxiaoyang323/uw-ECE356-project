# uw-ECE356-project

Make sure you have python3 installed.

Install dependencies using pip3 install -r requirements.txt

To build database, open connection to your local database and source database_setup.sql

Make sure your mysql version supports aggregation function GROUP_CONCAT()

To execute the command line interface, run python3 main.py




You can type "help" to view all available commands. All commands are also listed below.

Note that all commands are case-sensitive


Here is a list of all the commands available:

    show_user: List out all usernames

    login {UserID}: Login with a username

    create_user {UserID} {Name} {Birthday}(optional): Create a new username

    show_topic: Show all topics
    
    create_topic {TopicID}: Create a topic. Note that: {TopicID} will eliminate comma.

    show_group: Show all groups

    exit: Exit the command line interface
    

Following commands requires user to login using login {UserID}

    init_post {Title} {TopicID},{TopicID} {Content}: Initial a post. Note {TopicID} need to be at least one

    reply_post {PostID} {Type}(response/thumb) {Content}: Reply to a post. Note {Content} is any string if response; 'up'/'down' if thumb

    read_user {UserID} {Type}(all/unread): Read all unread posts by a followed user (cannot read yourself)

    read_topic {TopicID} {Type}(all/unread): Read all unread posts by followed topic

    show_follow_user: Show all users you are following
    
    follow_user {UserID}: Follow a user (cannot follow yourself)

    unfollow_user {UserID}: Unfollow a user

    show_follow_topic: Show all topics you are following

    follow_topic {TopicID}: Follow a topic

    unfollow_topic {TopicID}: Unfollow a topic

    create_group {Name}: Create a group

    join_group {GroupID}: Join a groups

    leave_group {GroupID}: Leave a group

    logout: Logout from current user