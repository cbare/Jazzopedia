.read ../scripts/drop_tables.sql
.read ../scripts/create_tables.sql

select * from Session s
         join Part p on s.id=p.session_id
         join Person_Part pp on pp.part_id=p.id
         join Track t on t.part_id=p.id
where Person_Part.person_id = ?
order by s.jd_sort_key;


select *
    from Session s
    join Part p on s.id=p.session_id
    join Person_Part pp on pp.part_id=p.id
    join Track t on t.part_id=p.id
where pp.person_id=1
order by s.jd_sort_key limit 10;

DROP TABLE IF EXISTS Person_Session;
CREATE TABLE IF NOT EXISTS Person_Session(
  person_id         INTEGER,
  session_id        INTEGER                                       
);

DROP TABLE IF EXISTS Person_Session;
CREATE TABLE Person_Session as
select distinct Person.id as person_id, s.id as session_id
from Session s
join Part p on s.id=p.session_id
join Person_Part pp on p.id=pp.part_id
join Person on person.id=pp.person_id
order by person.id;

select distinct Person.id as person_id, s.id as session_id
from Session s
join Part p on s.id=p.session_id
join Person_Part pp on p.id=pp.part_id
join Person on person.id=pp.person_id
order by person.id
limit 10;


select s.*, p.*
from Session s
join Person_Session ps on s.id=ps.session_id
where ps.person_id=?
order by s.jd_sort_key;