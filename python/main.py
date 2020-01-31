import psycopg2

from python.config import *

# creating database connection
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
cur = conn.cursor()
cur.execute('SELECT version()')

# global variables
user_id = user_data = None
state = 'base'
old_state = None
back_target = None


# base menu commands
def db_create_user(phone, fname, lname=None, bio=None, uname=None, ):
    try:
        cur.execute(
            f"INSERT INTO userperson VALUES(DEFAULT, {uname}, '{phone}','{fname}', {lname},{bio})")

        conn.commit()
        cur.execute("SELECT max(id) FROM userperson")
        return cur.fetchone()[0]
    except Exception as error:
        print(error)


def handle_logon():
    temp = input('-\tEnter your Phone number: ')
    cur.execute(f"SELECT id from userperson WHERE phone='{temp}'")
    while cur.fetchone() or not temp:
        temp = input(
            '\t\033[0;31mPhone number Cannot be empty: \033[0m' if not temp else '\t\033[0;31mThis Phone number exists enter another number: \033[0m').strip()
        cur.execute(f"SELECT id from userperson WHERE phone='{temp}'")
    phone = temp

    temp = input('-\tWhat is your first name: ')
    while not temp:
        temp = input(
            '\t\033[0;31mFirst name cannot be empty: \033[0m').strip()
    fname = temp

    temp = input('-\tWhat is your last name (optional): ')
    lname = f"'{temp}'" if temp else 'null'

    temp = input('-\tChoose a username (optional): ')
    cur.execute(f"SELECT id from userperson WHERE user_name='{temp}'")
    while cur.fetchone() and temp:
        temp = input(
            '\t\033[0;31mThis username is already taken, choose another one or leave it empty: \033[0m').strip()
        cur.execute(f"SELECT id from userperson WHERE user_name='{temp}'")
    uname = f"'{temp}'" if temp else 'null'

    temp = input('-\tDescribe yourself in a few words (optional): ')
    bio = f"'{temp}'" if temp else 'null'

    print('Your user_id is:\033[1;34m',
          db_create_user(phone, fname, lname, bio, uname), '\033[0m')


def handle_login():
    temp = input('-\tEnter your User ID: ')
    cur.execute(f"SELECT * from userperson WHERE id={temp}")
    global user_data
    user_data = cur.fetchone()
    if not user_data or not temp:
        print(
            '\t\033[0;31mUser ID cannot be empty: \033[0m' if not temp else '\t\033[0;31mThis ID does not exist\033[0m')
        return

    global user_id
    user_id = int(temp)
    global state
    state = 'menu'
    print(f'\tWelcome \033[1;34m{user_data[3].strip()}\033[0m!')


def exit_code():
    print("Thanks for using our DataBase. :) \nGood Bye ")
    exit()


# main menu commands
def handle_logout():
    global user_id, user_data, state
    user_data = user_id = None
    state = 'base'


# profile menu commands
def handle_get_me():
    print('Your user information: ')
    print(f'-\tPhone number: \033[1;34m{user_data[2]}\033[0m')
    print(f'-\tUsername: \033[1;34m{user_data[1]}\033[0m')
    print(f'-\tFirst name: \033[1;34m{user_data[3]}\033[0m')
    print(f'-\tLast name: \033[1;34m{user_data[4]}\033[0m')
    print(f'-\tBiography: \033[1;34m{user_data[5]}\033[0m')


def handle_update_me():
    global user_data
    temp = input('-\tChange your first name: ')
    while not temp:
        temp = input(
            '\t\033[0;31mFirst name cannot be empty: \033[0m').strip()
    fname = temp

    temp = input('-\tChange your last name (optional): ')
    lname = f"'{temp}'" if temp else 'null'

    temp = input('-\tChoose a new username (optional): ')
    cur.execute(f"SELECT id from usr WHERE user_name='{temp}'")
    while cur.fetchone() and temp and temp != user_data[1]:
        temp = input(
            '\t\033[0;31mThis username is already taken, choose another one or leave it empty: \033[0m').strip()
        cur.execute(f"SELECT id from userperson WHERE user_name='{temp}'")
    uname = f"'{temp}'" if temp else 'null'

    temp = input('-\tChange your biography (optional): ')
    bio = f"'{temp}'" if temp else 'null'

    cur.execute(
        f"UPDATE usr SET user_name={uname}, first_name='{fname}', last_name={lname}, biography={bio} WHERE usr.id={user_id}")

    conn.commit()
    cur.execute(f"SELECT * from userperson WHERE id={user_id}")

    user_data = cur.fetchone()


def handle_delete_me():
    if input('-\tYou sure you want to delete your account(y/n)? ') == 'y':
        cur.execute(
            f"DELETE FROM usr  WHERE usr.id={user_id}")
        conn.commit()
        print('Your account was deleted successfully')
        handle_logout()


# chats menu commands
def handle_show_my_chats():
    pass  # todo arvin


def handle_go_to_chat():
    temp = input('-\tEnter your destination chat ID: ')
    while not temp:
        temp = input(
            '\t\033[0;31mChat ID cannot be empty: \033[0m').strip()
    cur.execute(f"SELECT chat from member WHERE chat='{temp}' and usr={user_id}")
    if not cur.fetchone():
        print('\t\033[0;31mYou are not a member of this chat ID\033[0m')


def handle_leave_chat():
    pass


# global commands
def change_menu(new_state, back=None):
    def wrapped():
        global state
        global back_target
        back_target = back if back else state
        state = new_state

    return wrapped


def handle_help():
    for key, value in available_commands[state].items():
        print(f'\t\033[1m{key.center(10, " ")}\033[0m\033[1m - \033[0m{value[1]}')


def handle_state_transitions():
    global old_state
    if old_state != state:
        print('available commands are:')
        handle_help()
        old_state = state


base_commands = {
    'logon': (handle_logon, 'create a new user'),
    'login': (handle_login, 'login to your chat account'),
    'exit': (exit_code, 'exit from program'),
    'help': (handle_help, 'print available commands'),
}

menu_commands = {
    'logout': (handle_logout, 'logout of your account'),
    'chats': (change_menu('chats_menu'), 'go to chat menu'),
    'profile': (change_menu('profile_menu'), 'see and change your profile information'),
    'help': (handle_help, 'print available commands'),
}

chats_menu_commands = {
    'show': (handle_show_my_chats, 'show a list of your chats'),
    'goto': (handle_go_to_chat, 'go to a specific chat'),
    'leave': (handle_leave_chat, 'go to chat menu'),
    'create': (change_menu('create_chat_menu'), 'create a new chat'),
    'back': (change_menu('menu'), 'back to main menu'),
    'help': (handle_help, 'print available commands'),
}

profile_menu_commands = {
    'see': (handle_get_me, 'see your profile information'),
    'update': (handle_update_me, 'change your profile information'),
    'delete': (handle_delete_me, 'delete your profile'),
    'back': (change_menu('menu'), 'go to main menu'),
    'help': (handle_help, 'print available commands'),
}

available_commands = {
    'base': base_commands,
    'menu': menu_commands,
    'profile_menu': profile_menu_commands,
    'chats_menu': chats_menu_commands,
}


def handle_command(command):
    global user_id
    try:
        available_commands[state][command][0]()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        handle_state_transitions()
        handle_command(input('$ ').strip())
