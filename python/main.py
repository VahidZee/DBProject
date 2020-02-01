import psycopg2
import uuid
from python.config import *

# creating database connection
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
conn.rollback()
cur = conn.cursor()

# constant values
PRIVATE = 0
GROUP = 1
CHANNEL = 2
CHAT_ERROR = 3

# global variables
user_id = user_data = None
current_chat_id = None
state = 'base'
old_state = None
back_target = None
disabled_commands = set()
current_permissions = None


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
def handle_join_chat():
    pass


def get_chat_type(chat_id):
    cur.execute(f"SELECT chat_type from chat WHERE id={chat_id}")
    t = cur.fetchone()[0]
    return PRIVATE if t == 'P' else GROUP if t == 'G' else CHANNEL if t == 'C' else CHAT_ERROR


def get_user_info(uid):
    cur.execute(f"SELECT * from usr where id = {uid}")
    return cur.fetchone()


def get_user_name(uid):
    data = get_user_info(uid)
    if data[3]:
        return data[2].strip() + ' ' + data[3].strip()
    return data[2].strip()


def get_pv_member(chat_id):
    cur.execute(f"SELECT usr from member WHERE usr != {user_id} and chat = {chat_id}")
    member_id = cur.fetchone()[0]
    member_tuple = get_user_info(member_id)
    return f'{member_tuple[2]} {member_tuple[3] or ""}'


def get_group_channel_title(chat_id):
    cur.execute(f"SELECT title from groupchannel where id = {chat_id}")
    title = cur.fetchone()[0]
    return f'{title}'


def get_chat_title(chat_id, chat_type=None):
    if not chat_type:
        chat_type = get_chat_type(chat_id)
    if chat_type == PRIVATE:
        return get_pv_member(chat_id)
    return get_group_channel_title(chat_id)


def get_group_channel_info(chat_id):
    cur.execute(f"SELECT * from groupchannel where id = {chat_id}")
    des = cur.fetchone()
    return des


def handle_show_my_chats():
    global cur
    cur.execute(f"SELECT chat from member where usr = {user_id}")
    all_chats_ids = cur.fetchall()
    private_chat_id = []
    group_id = []
    channel_id = []
    for chat_id in all_chats_ids:
        chat_type = get_chat_type(chat_id[0])
        if chat_type == PRIVATE:
            private_chat_id.append(chat_id[0])
        elif chat_type == GROUP:
            group_id.append(chat_id[0])
        elif chat_type == CHANNEL:
            channel_id.append(chat_id[0])
        else:
            print("ERROR!")

    print('-\tPrivate Chats:')
    if private_chat_id:
        for id in private_chat_id:
            print('\t\033[1;34m', str(id), '\033[0m\t-\t\033[1;34m', get_pv_member(id), '\033[0m')

    print('-\tGroup Chats:')
    if group_id:
        for id in group_id:
            print('\t\033[1;34m', str(id), '\033[0m\t-\t\033[1;34m', get_chat_title(id, GROUP), '\033[0m')

    print('-\tChannel Chats:')
    if channel_id:
        for id in channel_id:
            print('\t\033[1;34m', str(id), '\033[0m\t-\t\033[1;34m', get_chat_title(id, CHANNEL), '\033[0m')


def handle_go_to_chat():
    global disabled_commands, current_permissions, state, current_chat_id
    temp_dis = set()
    temp = input('-\tEnter your destination chat ID: ')
    while not temp:
        temp = input(
            '\t\033[0;31mChat ID cannot be empty: \033[0m').strip()
    cur.execute(f"SELECT chat from member WHERE chat='{temp}' and usr={user_id}")
    if not cur.fetchone():
        print('\t\033[0;31mYou are not a member of this chat ID\033[0m')
        return
    current_chat_id = chat_id = temp
    chat_type = get_chat_type(chat_id)
    if chat_type == PRIVATE:
        disabled_commands = set(('update_info', 'members', 'admins', 'banned_members',))
    elif chat_type == GROUP or chat_type == CHANNEL:
        cur.execute(f"SELECT * from administrator WHERE chat='{chat_id}' and usr={user_id}")
        current_permissions = permissions = cur.fetchone()
        if permissions:
            if not permissions[3] and chat_type == CHANNEL:
                temp_dis.add('send_message')
            if not permissions[4]:
                temp_dis.add('delete_message')
            if not permissions[5]:
                temp_dis.add('banned_members')
            if not permissions[6]:
                temp_dis.add('add_member')
            if not permissions[6] and chat_type == CHANNEL:
                temp_dis.add('members')
            if not permissions[7]:
                temp_dis.add('promote')
                temp_dis.add('unpromote')
                temp_dis.add('edit_admin')
            if not permissions[8]:
                temp_dis.add('update_info')
            disabled_commands = temp_dis

    state = 'inchat_menu'
    print(f'Chatting with: \033[1;34m{get_chat_title(current_chat_id)}\033[0m!')


def handle_leave_chat():
    pass


def print_message(message):
    # variables
    title_width = 20

    print(f'-\t\033[7m{"from".center(title_width, " ")}\033[0m \033[1;36m{get_user_name(message[6])}\033[0m')
    print(f'\t\033[7m{"message_id".center(title_width, " ")}\033[0m \033[1;37m{message[1]}\033[0m')
    if message[5]:
        print(f'\t\033[7m{"reply to message_id".center(title_width, " ")}\033[0m \033[1;37m{message[5]}\033[0m')
    print(f'\t\033[7m{"date".center(title_width, " ")}\033[0m \033[1;37m{message[8]}\033[0m')

    if message[2] and message[3]:
        cur.execute(f"SELECT from_usr from message WHERE destination={message[2]} and id={message[3]}")
        source_user_id = cur.fetchone()[0]
        print(
            f'\t\033[7m{"forwarded from".center(title_width, " ")}\033[0m',
            f'\033[1;35m{get_user_name(source_user_id)}\033[0m')
        src = message[2], message[3]
        edit = None
        text = ''
        while src[0] and src[1]:
            cur.execute(
                f"SELECT text, edit_date from message WHERE destination={src[0]} and id={src[1]}")
            text, edit = cur.fetchone()
            cur.execute(
                f"SELECT forwarded_source,forwarded_id from message WHERE destination={src[0]} and id={src[1]}"
            )
            src = cur.fetchone()
        if edit:
            print(f'\t\033[7m{"edit_date".center(title_width, " ")}\033[0m \033[1;37m{edit}\033[0m')
        print(f'\t\033[7m{"text".center(title_width, " ")}\033[0m \033[1;34m{text}\033[0m')
    else:
        if message[9]:
            print(f'\t\033[7m{"edit_date".center(title_width, " ")}\033[0m \033[1;37m{message[9]}\033[0m')
        print(f'\t\033[7m{"text".center(title_width, " ")}\033[0m \033[1;34m{message[10]}\033[0m')
    print()


def handle_show_messages():
    # variables
    temp = input('-\tMessage count (default=10): ')
    limit = int(temp) if temp else 10

    cur.execute(f"SELECT * from message WHERE destination={current_chat_id} ORDER BY upload_date DESC LIMIT {limit}")
    messages = cur.fetchall()
    print()
    for message in messages:
        print_message(message)


def handle_find_message():
    # variables
    temp = input('-\tMessage id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mMessage id cannot be empty: \033[0m').strip()

    cur.execute(f"SELECT * from message WHERE destination={current_chat_id} and id={temp}")
    message = cur.fetchone()
    if message:
        print_message(message)
    else:
        print("\t\033[0;31mCould not find the desired message\033[0m")


def handle_send_message():
    # variables
    cur.execute(f"SELECT id from message WHERE destination= {current_chat_id}")
    if cur.fetchone():
        cur.execute(f"SELECT max(id) from message WHERE destination={current_chat_id}")
        new_message_id = cur.fetchone()[0] + 1
    else:
        new_message_id = 1

    text = 'null'
    source_chat_id = 'null'
    source_message_id = 'null'
    # reply
    temp = input('-\tReply to message_id (optional): ')
    if temp:
        cur.execute(f"SELECT * from message WHERE id={temp} and destination= {current_chat_id}")
    while not cur.fetchone() and temp:
        temp = input(
            '\t\033[0;31mThe message you want to reply to does not exist in this chat, try another message_id (optional): \033[0m').strip()
        if not temp:
            break
        cur.execute(f"SELECT id from message WHERE id={temp} and destination= {current_chat_id}")

    reply_to_id = 'null' if not temp else temp
    reply_to_chat = 'null' if not temp else current_chat_id
    temp = input('-\tDo you want to forward an existing message (y/n)? ')
    if not temp or temp == 'n':
        temp = input('-\tMesssage text: ')
        while not temp:
            temp = input(
                '\t\033[0;31mMesssage text cannot be empty: \033[0m').strip()
        text = f"'{temp}'"
    else:
        # forwarding message
        temp = input('-\tForward source chat_id: ')
        while not temp:
            temp = input(
                '\t\033[0;31mSource chat_id cannot be empty: \033[0m').strip()
        source_chat_id = temp

        temp = input('-\tForward source message_id: ')
        while not temp:
            temp = input(
                '\t\033[0;31mSource message_id cannot be empty: \033[0m').strip()
        source_message_id = temp
        cur.execute(f"SELECT * from message WHERE id='{source_message_id}' and destination='{source_chat_id}'")
        if not cur.fetchone():
            print(
                '\t\033[0;31mSource message could not be found\033[0m')
            return
    cur.execute(
        f"INSERT INTO message VALUES ({current_chat_id}, {new_message_id}, {source_chat_id}, {source_message_id}, {'null' if reply_to_id == 'null' else current_chat_id},{reply_to_id}, {user_id}, null,DEFAULT, null,{text})")
    conn.commit()


def handle_delete_message():
    # variables
    temp = input('-\tMessage id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mMessage id cannot be empty: \033[0m').strip()
    cur.execute(f"SELECT * from message WHERE destination={current_chat_id} and id={temp}")
    message = cur.fetchone()
    if message:
        cur.execute(f"DELETE from message WHERE destination={current_chat_id} and id={temp}")
        conn.commit()
        print("\tMessage was deleted successfully")
    else:
        print("\t\033[0;31mCould not find the desired message\033[0m")


def handle_edit_message():
    # variables
    temp = input('-\tMessage id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mMessage id cannot be empty: \033[0m').strip()
    message_id = temp
    cur.execute(f"SELECT * from message WHERE destination={current_chat_id} and id={message_id}")
    message = cur.fetchone()
    if message:
        if message[6] != user_id:
            print("\t\033[0;31mYou can only edit your own messages\033[0m")
            return
        if message[2] and message[3]:
            print("\t\033[0;31mYou cannot edit forwarded messages\033[0m")
            return
        print('-\tEditing Message:')
        print_message(message)
        temp = input('-\tNew essage text: ')
        while not temp:
            temp = input(
                '\t\033[0;31mMesssage text cannot be empty: \033[0m').strip()
        text = f"'{temp}'"
        cur.execute(
            f"UPDATE message set text={text}, edit_date=CURRENT_TIMESTAMP WHERE destination={current_chat_id} and id={message_id}")
        conn.commit()
        print("\tMessage was edited successfully")
    else:
        print("\t\033[0;31mCould not find the desired message\033[0m")


def handle_leave():
    temp = input('\tAre you sure you want to leave this chat?(y/n)')
    while temp not in ['y', 'n']:
        print('\tPlease respond with y or n.')
        temp = input('\tAre you sure you want to leave this chat?(y/n)')
    temp = True if temp == 'y' else False
    if temp:
        cur.execute(f"DELETE from member WHERE usr={user_id} AND chat={current_chat_id}")
        conn.commit()


## TODO cleaning up UI
def handle_chat_info():
    chat_type = get_chat_type(current_chat_id)
    chat_title = get_chat_title(current_chat_id, chat_type)
    if chat_type == GROUP:
        info = get_group_channel_info(current_chat_id)
        bio = info[3]
        is_private = info[4]
        inv_link = info[5]
        user_name = info[6]
        print('*\tGroup\t' + chat_title)
        print('*\tGroup ID ' + str(current_chat_id))
        print('*\tGroup Creator ' + get_user_name(info[1]))
        print('*\tBio:\t' + (bio if bio else '-'))
        print('*\tPrivate:\t' + ('Yes' if is_private else 'No'))
        print('*\tInvite link:\t' + (inv_link if inv_link else '-'))
        print('*\tUsername:\t' + (user_name if user_name else '-'))

    elif chat_type == CHANNEL:
        info = get_group_channel_info(current_chat_id)
        bio = info[3]
        is_private = info[4]
        inv_link = info[5]
        user_name = info[6]
        print('*\tChannel\t' + chat_title)
        print('*\tChannel ID ' + str(current_chat_id))
        print('*\tChannel Creator ' + get_user_name(info[1]))
        print('*\tBio:\t' + (bio if bio else '-'))
        print('*\tPrivate:\t' + ('Yes' if is_private else 'No'))
        print('*\tInvite link:\t' + (inv_link if inv_link else '-'))
        print('*\tUsername:\t' + (user_name if user_name else '-'))

    elif chat_type == PRIVATE:
        info = get_user_info(user_id)
        is_bot = info[5]
        if is_bot:
            print('*\tBot\t' + chat_title)
            print('*\tBot ID ' + str(info[0]))
            print('*\tBot description:\t' + (info[4] if info[4] else '-'))
            print('*\tBot username:\t' + (info[1] if info[1] else '-'))
        else:
            print('*\tUser\t' + chat_title)
            print('*\tUser ID ' + str(info[0]))
            print('*\tUser description:\t' + (info[4] if info[4] else '-'))
            print('*\tUser username:\t' + (info[1] if info[1] else '-'))
    else:
        print('\t\033[0;31mWrong chat type\033[0m')


def handle_update_info():
    title = input("-\tPlease update the title:\t")
    while not title:
        title = input(
            '\t\033[0;31mTitle cannot be empty: \033[0m').strip()
    description = input("-\tupdate the description(optional):\t")
    is_private = input("-\tIs this chat  private (y/n):")
    user_name = input("-\tenter the chat's username (optional): ")

    is_private = False if is_private == 'n' or not is_private else True
    description = f"'{description}'" if description else 'null'
    user_name = f"'{user_name}'" if user_name else 'null'

    cur.execute(
        f"UPDATE groupchannel set title = '{title}', description = {description}, is_private = {is_private}, user_name = {user_name} where id = {current_chat_id}")
    conn.commit()


# create chat commands
def handle_creating_pv():
    temp = input('-\tFind person using phone number(p) or username(u)?\t')
    if temp == 'p':
        temp = input('-\tEnter the phone number:\t')
        cur.execute(f"SELECT * from userperson WHERE phone = '{temp}'")
        dest = cur.fetchone()
        if dest:
            cur.execute(f"INSERT into chat values(DEFAULT, 'P')")
            conn.commit()
            cur.execute("SELECT max(id) FROM chat")
            chat_id = cur.fetchone()[0]
            cur.execute(f"INSERT into member values({user_id}, {chat_id}, DEFAULT, null, null)")
            cur.execute(f"INSERT into member values({dest[0]}, {chat_id}, DEFAULT, null, null)")
            conn.commit()
        else:
            print('\t\033[0;31mUser with this phone number does not exist!\033[0m')
            return
    else:
        temp = input('-\tEnter the username:\t')
        cur.execute(f"SELECT * from usr WHERE user_name = '{temp}'")
        dest = cur.fetchone()[0]
        if dest:
            cur.execute(f"INSERT into chat values(DEFAULT, 'P')")
            conn.commit()
            cur.execute("SELECT max(id) FROM chat")
            chat_id = cur.fetchone()[0]
            cur.execute(f"INSERT into member values({user_id}, {chat_id}, DEFAULT, null, null)")
            cur.execute(f"INSERT into member values({dest}, {chat_id}, DEFAULT, null, null)")
            conn.commit()
        else:
            print('\t\033[0;31mUser with this username does not exist!\033[0m')
            return


def handle_creating_gp_ch(is_group):
    def wrapper():
        title = input(f"-\tPlease enter the title of your {'group' if is_group else 'channel'}:\t")
        while not title:
            print("\tTitle can not be empty.")
            title = input(f"-\tPlease enter the title of your {'group' if is_group else 'channel'}:\t")
        description = input(
            f"-\tPlease enter the description of your {'group' if is_group else 'channel'}(optional):\t")
        is_private = input(f"-\tShall your {'group' if is_group else 'channel'} be private?(y/n):\t")
        while not is_private or is_private not in ['y', 'n']:
            print("\tGroup has to be private or not.")
            is_private = input(f"-\tShall your {'group' if is_group else 'channel'} be private?(y/n):\t")
        user_name = input(f"-\tPlease enter the username of your {'group' if is_group else 'channel'}(optional):\t")

        gp_id = 0
        creator = user_id
        is_private = True if is_private == 'y' else False
        inv_link = 'chiz.me/' + uuid.uuid4().hex[:10]
        chat_type = 'G' if is_group else 'C'
        description = f"'{description}'" if description else 'null'
        user_name = f"'{user_name}'" if user_name else 'null'

        cur.execute(
            f"INSERT into groupchannelchat values({gp_id}, {creator}, '{title}', {description}, {is_private}, '{inv_link}', {user_name}, '{chat_type}')")
        conn.commit()

    return wrapper


# members commands
def handle_show_members():
    temp = input('-\tMember count (default=10): ')
    limit = int(temp) if temp else 10

    cur.execute(f"SELECT * from member WHERE chat={current_chat_id} limit {limit}")
    members = cur.fetchall()
    for member in members:
        mem_id = member[0]
        info = get_user_info(mem_id)
        username = info[1]
        name = get_user_name(mem_id)
        print("-\t" + name + (("\t-\t" + username) if username else ''))


def handle_add_member():
    temp = input('-\tFind person using phone number(p) or username(u)?\t')
    if temp == 'p':
        temp = input('-\tEnter the phone number:\t')
        cur.execute(f"SELECT * from userperson WHERE phone = '{temp}'")
        dest = cur.fetchone()
        if dest:
            cur.execute(f"SELECT * from member where usr = {dest[0]} and chat = {current_chat_id}")
            if not cur.fetchone():
                cur.execute(f"INSERT into member values({dest[0]}, {current_chat_id}, DEFAULT, null, null)")
                conn.commit()
            else:
                print('\t\033[0;31mUser is already in this chat!\033[0m')
        else:
            print('\t\033[0;31mUser with this phone number does not exist!\033[0m')
            return
    else:
        temp = input('-\tEnter the username:\t')
        cur.execute(f"SELECT * from usr WHERE user_name='{temp}'")
        dest = cur.fetchone()
        if dest:
            cur.execute(f"SELECT * from member where usr={dest[0]} and chat={current_chat_id}")
            if not cur.fetchone():
                cur.execute(f"INSERT into member values({dest[0]}, {current_chat_id}, DEFAULT, null, null)")
                conn.commit()
            else:
                print('\t\033[0;31mUser is already in this chat!\033[0m')
        else:
            print('\t\033[0;31mUser with this username does not exist!\033[0m')
            return


def handle_show_banned():
    temp = input('-\tBanned member count (default=10): ')
    limit = int(temp) if temp else 10

    cur.execute(f"SELECT * from banned WHERE chat={current_chat_id} limit {limit}")
    members = cur.fetchall()
    for member in members:
        admin = member[0]
        mem_id = member[2]
        info = get_user_info(mem_id)
        username = info[1]
        name = get_user_name(mem_id)
        admin_name = get_user_name(admin)
        print(f"-\t{mem_id}\t" + name + (("\t-\t" + username) if username else '') + '\tbanned by\t' + admin_name)


def handle_add_banned():
    temp = int(input('-\tPlease enter the id of the user getting banned:\t'))
    cur.execute(f"SELECT * from member WHERE usr = {temp} and chat = {current_chat_id}")
    dest = cur.fetchone()
    if dest:
        cur.execute(f"SELECT * from banned where usr = {temp} and chat = {current_chat_id}")
        if not cur.fetchone():
            cur.execute(f"INSERT into banned values({user_id}, {current_chat_id}, {temp})")
            conn.commit()
        else:
            print('\t\033[0;31mUser is already banned in this chat!\033[0m')
    else:
        print('\t\033[0;31mUser is not in this chat or does not exist at all!\033[0m')
        return


def handle_remove_banned():
    temp = int(input('-\tPlease enter the id of the user getting unbanned:\t'))
    cur.execute(f"SELECT * from banned WHERE usr = {temp} and chat = {current_chat_id}")
    dest = cur.fetchone()
    if dest:
        cur.execute(f"DELETE FROM banned WHERE usr = {temp} AND chat = {current_chat_id}")
        conn.commit()
    else:
        print('\t\033[0;31mUser is not banned in this chat!\033[0m')
        return


# admins commands
def print_admin(admin):
    admin_id = admin[1]
    info = get_user_info(admin_id)
    username = info[1]
    admin_name = get_user_name(admin_id)
    print(
        f"-\t\033[1;37m{admin_id}\033[0m - \033[1;34m{admin_name}\033[0m" + (
            ' -' if not username else f' (\033[1;34m@{username.strip()}\033[0m) -'),
        'Creator' if not admin[2] else f'Promoted by: \033[1;37m{get_user_name(admin[2])}\033[0m')
    print(('\033[1;32m\t' if admin[3] else '\033[1;31m\t') + 'send_messages\033[0m', end=', ')
    print(('\033[1;32m\t' if admin[4] else '\033[1;31m\t') + 'delete_messages\033[0m', end=', ')
    print(('\033[1;32m\t' if admin[5] else '\033[1;31m\t') + 'ban\033[0m', end=', ')
    print(('\033[1;32m\t' if admin[6] else '\033[1;31m\t') + 'add_member\033[0m', end=', ')
    print(('\033[1;32m\t' if admin[7] else '\033[1;31m\t') + 'add_admins\033[0m', end=', ')
    print(('\033[1;32m\t' if admin[8] else '\033[1;31m\t') + 'update_info\033[0m')


def handle_show_admins():
    temp = input('-\tMember count (default=10): ')
    limit = int(temp) if temp else 10

    cur.execute(f"SELECT * from administrator WHERE chat={current_chat_id} limit {limit}")
    admins = cur.fetchall()
    for admin in admins:
        print_admin(admin)
    print()


def handle_add_admin():
    temp = input('-\tUser id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mUser id cannot be empty: \033[0m').strip()
    admin_id = temp
    cur.execute(f"SELECT * from member WHERE chat={current_chat_id} and usr={admin_id}")
    admin = cur.fetchone()
    if not admin:
        print('\t\033[0;31mThis user is not a member of this chat\033[0m')
        return

    send_messages = current_permissions[3]
    delete_messages = current_permissions[4]
    ban = current_permissions[5]
    add_member = current_permissions[6]
    add_admin = current_permissions[7]
    update_info = current_permissions[8]

    if send_messages:
        temp = input('-\tCan this admin send messages (y/n): ')
        send_messages = False if not temp or temp == 'n' else True
    if delete_messages:
        temp = input('-\tCan this admin delete messages (y/n): ')
        delete_messages = False if not temp or temp == 'n' else True
    if ban:
        temp = input('-\tCan this admin ban users (y/n): ')
        ban = False if not temp or temp == 'n' else True
    if add_member:
        temp = input('-\tCan this admin add new members (y/n): ')
        add_member = False if not temp or temp == 'n' else True
    if add_admin:
        temp = input('-\tCan this admin add new admins (y/n): ')
        add_admin = False if not temp or temp == 'n' else True
    if update_info:
        temp = input("-\tCan this admin update chat's info (y/n): ")
        update_info = False if not temp or temp == 'n' else True
    send_messages = 'FALSE' if not send_messages else 'TRUE'
    delete_messages = 'FALSE' if not delete_messages else 'TRUE'
    ban = 'FALSE' if not ban else 'TRUE'
    add_member = 'FALSE' if not add_member else 'TRUE'
    add_admin = 'FALSE' if not add_admin else 'TRUE'
    update_info = 'FALSE' if not update_info else 'TRUE'

    cur.execute(
        f"INSERT INTO administrator values ({current_chat_id},{admin_id},{user_id},{send_messages},{delete_messages},{ban},{add_member},{add_admin},{update_info})")
    conn.commit()
    print('\tAdmin was added successfully')


def handle_remove_admin():
    temp = input('-\tAdmin id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mAdmin id cannot be empty: \033[0m').strip()
    admin_id = temp
    cur.execute(f"SELECT * from administrator WHERE chat={current_chat_id} and usr={admin_id}")
    admin = cur.fetchone()
    if not admin:
        print('\t\033[0;31mDesired admin could not be found\033[0m')
        return
    if admin[2] != user_id and user_id != get_group_channel_info(current_chat_id)[1]:
        print('\t\033[0;31mYou cannot remove this admins\033[0m')
        return
    if admin[1] == user_id:
        print('\t\033[0;31mYou cannot provoke your own rights\033[0m')
        return
    print('\tRemoving admin:')
    print_admin(admin)
    cur.execute(
        f"DELETE from administrator WHERE chat={current_chat_id} and usr={admin_id}")
    conn.commit()
    print('\tAdmin was removed successfully')


def handle_edit_admin():
    temp = input('-\tAdmin id: ')
    while not temp:
        temp = input(
            '\t\033[0;31mAdmin id cannot be empty: \033[0m').strip()
    admin_id = temp
    cur.execute(f"SELECT * from administrator WHERE chat={current_chat_id} and usr={admin_id}")
    admin = cur.fetchone()
    if not admin:
        print('\t\033[0;31mDesired admin could not be found\033[0m')
        return

    if admin[2] != user_id and user_id != get_group_channel_info(current_chat_id)[1]:
        print("\t\033[0;31mYou cannot edit this admin's rights\033[0m")
        return
    print('\tUpdating admin:')
    print_admin(admin)

    send_messages = current_permissions[3]
    delete_messages = current_permissions[4]
    ban = current_permissions[5]
    add_member = current_permissions[6]
    add_admin = current_permissions[7]
    update_info = current_permissions[8]

    if send_messages:
        temp = input('-\tCan this admin send messages (y/n): ')
        send_messages = False if not temp or temp == 'n' else True
    if delete_messages:
        temp = input('-\tCan this admin delete messages (y/n): ')
        delete_messages = False if not temp or temp == 'n' else True
    if ban:
        temp = input('-\tCan this admin ban users (y/n): ')
        ban = False if not temp or temp == 'n' else True
    if add_member:
        temp = input('-\tCan this admin add new members (y/n): ')
        add_member = False if not temp or temp == 'n' else True
    if add_admin:
        temp = input('-\tCan this admin add new admins (y/n): ')
        add_admin = False if not temp or temp == 'n' else True
    if update_info:
        temp = input("-\tCan this admin update chat's info (y/n): ")
        update_info = False if not temp or temp == 'n' else True
    send_messages = 'FALSE' if not send_messages else 'TRUE'
    delete_messages = 'FALSE' if not delete_messages else 'TRUE'
    ban = 'FALSE' if not ban else 'TRUE'
    add_member = 'FALSE' if not add_member else 'TRUE'
    add_admin = 'FALSE' if not add_admin else 'TRUE'
    update_info = 'FALSE' if not update_info else 'TRUE'

    cur.execute(
        f"UPDATE administrator set send_messages={send_messages}, delete_messages={delete_messages}, ban={ban}, add_members={add_member}, add_admins={add_admin}, update_info={update_info}",
        f"'WHERE chat={current_chat_id} and usr={admin_id}")
    conn.commit()
    print('\tAdmins permissions updated successfully')


# global commands
def change_menu(new_state, reset=True):
    def wrapped():
        global state, current_permissions, current_chat_id
        state = new_state
        if reset:
            current_permissions = None
            current_chat_id = None

    return wrapped


def handle_help():
    for key, value in available_commands[state].items():
        if key not in disabled_commands:
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
    'create': (change_menu('create_chat'), 'create a new chat'),
    'join': (handle_join_chat, 'join an existing chat'),
    'back': (change_menu('menu'), 'back to main menu'),
    'help': (handle_help, 'print available commands'),
}

inchat_menu_commands = {
    'messages': (handle_show_messages, 'show messages of this chat'),
    'send_message': (handle_send_message, 'send a new message to this chat'),
    'delete_message': (handle_delete_message, 'delete a message from this chat'),
    'edit_message': (handle_edit_message, 'edit one of your own messages'),
    'find_message': (handle_find_message, 'show messages of this chat'),
    'members': (change_menu('members_menu', False), 'show messages of this chat'),
    'banned_members': (change_menu('banned_menu', False), 'show messages of this chat'),
    'admins': (change_menu('admins_menu', False), 'show messages of this chat'),
    'info': (handle_chat_info, 'show information about this chat'),
    'update_info': (handle_update_info, 'edit the information about this chat'),
    'leave': (handle_leave, 'leave this chat'),
    'back': (change_menu('chats_menu'), 'go back to chats menu'),
    'help': (handle_help, 'print available commands'),
}

members_menu_commands = {
    'show': (handle_show_members, 'show members of this chat'),
    'add_member': (handle_add_member, 'add a new member to this chat'),
    'back': (change_menu('inchat_menu', False), 'go back to chat'),
    'help': (handle_help, 'print available commands'),
}

banned_menu_commands = {
    'show': (handle_show_banned, 'show banned members of this chat'),
    'ban': (handle_add_banned, 'ban a new member from this chat'),
    'unban': (handle_remove_banned, 'remove a member from the banned list'),
    'back': (change_menu('inchat_menu', False), 'go back to chats menu'),
    'help': (handle_help, 'print available commands'),
}

admins_menu_commands = {
    'show': (handle_show_admins, 'show admins of this chat'),
    'promote': (handle_add_admin, 'add a new admin to this chat'),
    'unpromote': (handle_remove_admin, 'add a new admin to this chat'),
    'edit_admin': (handle_edit_admin, "update an admin's permissions"),
    'back': (change_menu('inchat_menu', False), 'go back to chat'),
    'help': (handle_help, 'print available commands'),
}

profile_menu_commands = {
    'see': (handle_get_me, 'see your profile information'),
    'update': (handle_update_me, 'change your profile information'),
    'delete': (handle_delete_me, 'delete your profile'),
    'back': (change_menu('menu'), 'go to main menu'),
    'help': (handle_help, 'print available commands'),
}

create_chat_menu_commands = {
    'private': (handle_creating_pv, 'start a new chat with your friend'),
    'group': (handle_creating_gp_ch(True), 'make a new group'),
    'channel': (handle_creating_gp_ch(False), 'create a new channel'),
    'back': (change_menu('chats_menu'), 'go to main menu'),
    'help': (handle_help, 'print available commands'),
}

available_commands = {
    'base': base_commands,
    'menu': menu_commands,
    'profile_menu': profile_menu_commands,
    'chats_menu': chats_menu_commands,
    'inchat_menu': inchat_menu_commands,
    'members_menu': members_menu_commands,
    'banned_menu': banned_menu_commands,
    'create_chat': create_chat_menu_commands,
    'admins_menu': admins_menu_commands,
}


def handle_command(command):
    global user_id
    try:
        if command not in disabled_commands:
            available_commands[state][command][0]()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        handle_state_transitions()
        handle_command(input('$ ').strip())
        print('\n' + '-' * 40, '\n')

# TODO Join, Block, Find user, Find chat, Cleaning up UI
