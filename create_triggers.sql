CREATE OR REPLACE FUNCTION create_person()
  RETURNS trigger AS
$BODY$
BEGIN

       INSERT INTO usr(id, user_name, first_name,last_name, biography, is_bot)
       VALUES(DEFAULT,NEW.user_name,NEW.first_name, NEW.last_name, NEW.biography,false);

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

