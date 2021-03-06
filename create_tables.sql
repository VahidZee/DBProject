-- User table
drop table if exists Usr cascade;
create table if not exists Usr
(
    id         SERIAL,
    user_name  char(30) UNIQUE,
    first_name char(30) not null,
    last_name  char(40),
    biography  char(300),
    is_bot     bool     not null default true,
    PRIMARY KEY (id)
);

-- Person Table
drop table if exists Person cascade;
create table if not exists Person
(
    id        integer  not null UNIQUE,
    phone     char(30) not null unique,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

-- Bot Table
drop table if exists Bot cascade;
create table if not exists Bot
(
    id           integer not null UNIQUE,
    creator      integer not null,
    access_token char(512) UNIQUE,
    webhook_url  text UNIQUE,
    uses_poll    boolean not null default true,
    FOREIGN KEY (id) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (creator) references Person (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);


-- Chat Table
drop table if exists Chat cascade;
create table if not exists Chat
(
    id        SERIAL,
    chat_type char(1) not null, --P for private and C for Channel and G for groups
    PRIMARY KEY (id)
);

-- Group or Channel Table
drop table if exists GroupChannel cascade;
create table if not exists GroupChannel
(
    id          integer  not null unique,
    creator     integer  not null,
    title       char(60) not null,
    description text,
    is_private  bool,
    inv_link    text     not null unique,
    user_name   char(60),
    FOREIGN KEY (id) references Chat (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (creator) references Person (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

-- Administrator Table
drop table if exists Administrator cascade;
create table if not exists Administrator
(
    chat            integer not null,
    usr             integer not null,
    promoted_by     integer,
    send_messages   bool    not null default true,
    delete_messages bool    not null default true,
    ban             bool    not null default true,
    add_members     bool    not null default true,
    add_admins      bool    not null default true,
    update_info     bool    not null default true,
    FOREIGN KEY (chat) references Chat (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (usr) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (promoted_by) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (chat, usr)
);

-- File Table
drop table if exists File cascade;
create table if not exists File
(
    id          SERIAL,
    uploader    integer not null,
    file_name   char(256),
    caption     text,
    file_type   char, -- "I" for image, "A" for audio, "V" for video, "D" for document, "O" for others
    address     text    not null,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploader) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

-- Member Table
drop table if exists Member cascade;
create table if not exists Member
(
    usr               integer not null,
    chat              integer not null,
    start_date        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    added_by          integer,
    last_read_message integer,
    FOREIGN KEY (usr) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (added_by) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (chat) references Chat (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (usr, chat),
    PRIMARY KEY (usr, chat)
);

-- Message Table
drop table if exists Message cascade;
create table if not exists Message
(
    destination      integer not null,
    id               integer not null,
    forwarded_source integer,
    forwarded_id     integer,
    reply_to_chat    integer,
    reply_to_id      integer,
    from_usr         integer,
    attachment       integer,
    upload_date      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    edit_date        timestamp,
    text             text,
    seen_count       integer                  default 0,
    FOREIGN KEY (destination) references Chat (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (forwarded_source, forwarded_id) references Message (destination, id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (reply_to_chat, reply_to_id) references Message (destination, id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (from_usr) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (attachment) references File (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (destination, id),
    PRIMARY KEY (destination, id)
);

-- Pinned message Table
drop table if exists PinnedMessage cascade;
create table if not exists PinnedMessage
(
    chat         integer not null,
    usr          integer not null,
    message_chat integer not null,
    message_id   integer not null,
    pin_date     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP not null,
    is_pinned    bool    not null         default true,
    FOREIGN KEY (chat, usr) references Administrator (chat, usr)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (message_chat, message_id) references Message (destination, id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (chat, usr, message_id, pin_date),
    PRIMARY KEY (chat, usr, message_id, pin_date)
);

-- Group Channel Picture Table
drop table if exists GroupChannelPicture cascade;
create table if not exists GroupChannelPicture
(
    admin       integer                                            not null,
    chat        integer                                            not null,
    image       integer                                            not null,
    change_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP not null,
    FOREIGN KEY (chat, admin) references Administrator (chat, usr)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (image) references File (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (chat, admin, image, change_date),
    PRIMARY KEY (chat, admin, image, change_date)
);

-- Profile Picture Table
drop table if exists ProfilePicture cascade;
create table if not exists ProfilePicture
(
    usr         integer                                            not null,
    image       integer                                            not null,
    change_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP not null,
    FOREIGN KEY (usr) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (image) references File (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (usr, image, change_date),
    PRIMARY KEY (usr, image, change_date)
);

-- Banned Table
drop table if exists Banned cascade;
create table if not exists Banned
(
    admin integer not null,
    chat  integer not null,
    usr   integer not null,
    FOREIGN KEY (usr) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (chat, admin) references Administrator (chat, usr)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (chat, usr),
    PRIMARY KEY (chat, usr)
);

-- Block Table
drop table if exists Block cascade;
create table if not exists Block
(
    blocker integer not null,
    blockee integer not null,
    FOREIGN KEY (blockee) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (blocker) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (blocker, blockee),
    PRIMARY KEY (blocker, blockee)
);

