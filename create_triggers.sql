-- Create Person
CREATE OR REPLACE FUNCTION create_person()
    RETURNS trigger AS
$BODY$
BEGIN

    INSERT INTO usr(id, user_name, first_name, last_name, biography, is_bot)
    VALUES (DEFAULT, NEW.user_name, NEW.first_name, NEW.last_name, NEW.biography, false);
    Insert INTO person(id, phone, last_seen) values (currval('usr_id_seq'), NEW.phone, NEW.last_seen);
    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists InsertUserPerson on userperson;
create trigger InsertUserPerson
    instead of insert
    on userperson
    for each row
execute procedure create_person();

-- Create Bot
CREATE OR REPLACE FUNCTION create_bot()
    RETURNS trigger AS
$BODY$
BEGIN

    INSERT INTO usr(id, user_name, first_name, last_name, biography, is_bot)
    VALUES (DEFAULT, NEW.user_name, NEW.first_name, NEW.last_name, NEW.biography, true);
    Insert INTO bot(id, creator, access_token, webhook_url, uses_poll)
    values (currval('usr_id_seq'), NEW.creator_id, NEW.access_token, NEW.webhook_url, NEW.uses_poll);
    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists InsertUserBot on userbot;
create trigger InsertUserBot
    instead of insert
    on userbot
    for each row
execute procedure create_bot();

-- Create Group or Channel
CREATE OR REPLACE FUNCTION create_groupchannel()
    RETURNS trigger AS
$BODY$
BEGIN

    INSERT INTO chat(id, chat_type)
    VALUES (DEFAULT, NEW.chat_type);
    Insert INTO groupchannel(id, creator, title, description, is_private, inv_link, user_name)
    values (currval('chat_id_seq'), NEW.creator, NEW.title, NEW.description, NEW.is_private, NEW.inv_link,
            NEW.user_name);
    Insert into administrator(chat, usr)
    values (currval('chat_id_seq'), NEW.creator);
    Insert into member(usr, chat)
    values (NEW.creator, currval('chat_id_seq'));
    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists InsertGroupChannelChat on groupchannelchat;
create trigger InsertGroupChannelChat
    instead of insert
    on groupchannelchat
    for each row
execute procedure create_groupchannel();

-- Admin Promotion
CREATE OR REPLACE FUNCTION promote_admin()
    RETURNS trigger AS
$BODY$
BEGIN
    If NOT EXISTS(select a.usr
                  from administrator a
                  where a.usr = new.promoted_by
                    and a.chat = new.chat
                    and a.add_admins = true)
        and new.promoted_by is not null
    then
        delete
        from administrator a
        where a.chat = new.chat
          and a.usr = new.usr;

    end if;
    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists PromoteAdmin on administrator;
create trigger PromoteAdmin
    after insert
    on administrator
    for each row
execute procedure promote_admin();


-- Banning
CREATE OR REPLACE FUNCTION ban()
    RETURNS trigger AS
$BODY$
BEGIN
    If NOT EXISTS(select a.usr
                  from administrator a
                  where a.usr = new.admin
                    and a.chat = new.chat
                    and a.ban = true)
        or NOT EXISTS(select m.usr
                      from member m
                      where new.usr = m.usr
                        and new.chat = m.chat)
        or EXISTS(select ad.usr
                  from administrator ad
                  where ad.usr = new.usr
                    and ad.chat = new.chat)
    then
        delete
        from banned b
        where b.chat = new.chat
          and b.usr = new.usr
          and b.admin = new.admin;
    end if;
    If EXISTS(select a.usr
              from administrator a
              where a.usr = new.admin
                and a.chat = new.chat
                and a.ban = true)
        and EXISTS(select m.usr
                   from member m
                   where new.usr = m.usr
                     and new.chat = m.chat)
        and NOT EXISTS(select ad.usr
                       from administrator ad
                       where ad.usr = new.usr
                         and ad.chat = new.chat)
    then
        delete
        from member m2
        where m2.chat = new.chat
          and m2.usr = new.usr;
    end if;

    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists BanMember on banned;
create trigger BanMember
    after insert
    on banned
    for each row
execute procedure ban();

-- Adding Member
CREATE OR REPLACE FUNCTION add_member()
    RETURNS trigger AS
$BODY$
BEGIN
    If NOT EXISTS(select a.usr
                  from administrator a
                  where a.usr = new.added_by
                    and a.chat = new.chat
                    and a.add_members = true)
    then
        delete
        from member m
        where m.chat = new.chat
          and m.usr = new.usr;
    end if;
    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists AddMember on member;
create trigger AddMember
    after insert
    on member
    for each row
execute procedure add_member();

-- Adding Message
CREATE OR REPLACE FUNCTION add_message()
    RETURNS trigger AS
$BODY$
BEGIN
    if (EXISTS(select *
               from chat c
               where c.id = new.destination
                 and c.chat_type = 'G')
        and EXISTS(select *
                   from banned b
                   where b.chat = new.destination
                     and b.usr = new.from_usr))
        or (EXISTS(select *
                   from chat c2
                   where c2.id = new.destination
                     and c2.chat_type = 'C')
            and (EXISTS(select *
                        from banned b2
                        where b2.chat = new.destination
                          and b2.usr = new.from_usr)
                or NOT EXISTS(select *
                              from administrator a
                              where a.chat = new.destination
                                and a.usr = new.from_usr
                                and a.send_messages = true)))
    then
        delete
        from message m
        where m.id = new.id
          and m.destination = new.destination;
    else
        update message m3
        set id = (select count(*)
                  from message m4
                  where m4.destination = new.destination)
        where new.destination = m3.destination
          and new.id = m3.id;
    end if;

    RETURN NEW;
END;
$BODY$
    LANGUAGE 'plpgsql';

drop trigger if exists AddMessage on message;
create trigger AddMessage
    after insert
    on message
    for each row
execute procedure add_message();
