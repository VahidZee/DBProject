-- Person View
create or replace view UserPerson as
select usr.id, usr.user_name, p.phone, usr.first_name, usr.last_name,usr.biography, p.last_seen
from usr inner join person p on usr.id = p.id
where usr.is_bot = false;


-- Bot View
create or replace view UserBot as
select usr.id, usr.user_name, usr.first_name, usr.last_name,usr.biography, b.creator as creator_id, b.access_token , b.webhook_url, b.uses_poll
from usr inner join bot b on usr.id = b.id
where usr.is_bot = true;

