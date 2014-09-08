drop table if exists objects;
drop table if exists pages;
drop table if exists page_revisions;

create table objects (
    hash text primary key,
    data text not null
);

create table pages (
    id integer primary key autoincrement
);

create table page_revisions (
    pageid integer,
    rev integer not null,
    hash text not null,
    FOREIGN KEY(pageid) REFERENCES pages(id)
);
