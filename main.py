import constant
import mysql.connector


class Session:
    def __init__(self):
        self.user_id = ""
        self.login = False
        self.connection = None
        self.command = None

    def print_login(self):
        print(
            "\nYou have not logged in yet.\n"\
            "To login with your username: login {{userid}}\n"\
            "To create a new username: create_user {{userid}} {{name}} {{birthday}}(optional)\n".format()
        )

    def print_manual(self):
        print(
            "Here is a list of all the commands available:\n"\
            "To initial a post, init_post \{title\} \{content\}\n"
        )

    def error_command(self):
        print("Invalid Command")

    def wait_command(self):
        self.command = input("Input Command: ").split()

    def parse_command(self):
        if self.command[0] == "login":
            self.user_login()
        elif self.command[0] == "create_user":
            self.user_create()
        else:
            self.error_command()

    def execute(self):
        self.print_login()
        while (True):
            self.wait_command()
            self.parse_command()

    def connect_to_db(self):
        self.connection = mysql.connector.connect(user=constant.USER, database=constant.DATABASE, host = constant.HOST)
        # connection = mysql.connector.connect(user=constant.USER, database=constant.DATABASE, host = constant.HOST)
        # cursor = connection.cursor()

        # query = ("select * from Users;")
        # cursor.execute(query)

        # for item in cursor:
        #     print(item)

    def error_userid_not_found(self):
        print("Username Not Found.")

    def error_duplicate_userid_found(self):
        print("Found duplicated user. Something is wrong.")

    def error_param_num(self):
        print("Wrong number of parameters")

    def user_login(self):
        # user_id = self.command[1]
        if len(self.command) != 2:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Users where UserID=\"{}\"".format(
            self.command[1]
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 0:
            self.error_userid_not_found()
        elif len(result) == 1:
            self.login = True
            # self.user_id = 
            print(result)
        else:
            self.error_duplicate_userid_found()

    def user_already_exist(self):
        print("Username already exists")

    def create_user_success(self):
        print("User create successfully. You can use command to login now.\n")

    def user_create(self):
        # user_id = self.command[1]
        # name = self.command[2]
        # birthday = self.command[3]
        if len(self.command) < 3 or len(self.command) > 4:
            self.error_param_num()
            return
        cursor = self.connection.cursor()
        query = "select * from Users where UserID=\"{}\"".format(
            self.command[1]
        )
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        if len(result) == 0:
            cursor = self.connection.cursor()
            if len(self.command) == 3:
                query = "insert into Users VALUES(\'{}\',\'{}\',NULL)".format(
                    self.command[1], 
                    self.command[2]
                )
            elif len(self.command) == 4:
                query = "insert into Users VALUES(\'{}\',\'{}\',\'{}\')".format(
                    self.command[1], 
                    self.command[2],
                    self.command[3]
                )
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            self.create_user_success()
        elif len(result) == 1:
            self.user_already_exist()
        else:
            self.error_duplicate_userid_found()

def main():
    session = Session()
    session.connect_to_db()
    session.execute()
    
if __name__=="__main__": 
    main()