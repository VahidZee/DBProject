
/* User table */
create table if not exists Usr (
    id   SERIAL,
    user_name char(30) UNIQUE,
    first_name  char(30) not null,
    last_name char(40),
    biography   char(300),
    is_bot bool not null default true,
    PRIMARY KEY (id)
);

