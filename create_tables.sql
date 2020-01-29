
-- User table
create table if not exists Usr (
    id   SERIAL,
    user_name char(30) UNIQUE,
    first_name  char(30) not null,
    last_name char(40),
    biography   char(300),
    is_bot bool not null default true,
    PRIMARY KEY (id)
);

-- Person Table 
create table if not exists Person (
    id  integer not null UNIQUE ,
    phone_number char(30),
    last_seen   TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

-- Bot Table
create table if not exists Bot (
    id  integer not null UNIQUE,
    creator  integer not null,
    access_token char(512) UNIQUE,
    webhook_url text UNIQUE,
    uses_polling boolean not null default true,
    FOREIGN KEY (id) references Usr (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (creator) references Person (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (id)
);

