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

