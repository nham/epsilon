drop table if exists pages;
drop table if exists page_revisions;

create table pages (
    id integer primary key autoincrement
);

create table tags (
    id integer primary key autoincrement,
    name text not null
);

create table cards (
    id integer primary key autoincrement,
    content text not null
);

create table page_revisions (
    id integer primary key autoincrement,
    pageid integer not null,
    prev integer,
    num integer not null,
    datetime text not null,
    title text not null,
    FOREIGN KEY(pageid) REFERENCES pages(id)
    FOREIGN KEY(prev) REFERENCES page_revisions(id)
);

create table page_rev_cards (
    revid integer not null,
    cardid integer not null,
    num integer not null,
    FOREIGN KEY(revid) REFERENCES page_revisions(id),
    FOREIGN KEY(cardid) REFERENCES cards(id)
);

create table page_rev_tags (
    revid integer not null,
    tagid integer not null,
    FOREIGN KEY(revid) REFERENCES page_revisions(id),
    FOREIGN KEY(tagid) REFERENCES tags(id)
);


create table web_states (
    id integer primary key autoincrement,
    datetime text not null,
    prev integer,
    FOREIGN KEY(prev) REFERENCES web_states(id)
);

create table web_state_pages (
    stateid integer not null,
    pagerevid integer not null,
    FOREIGN KEY(stateid) REFERENCES web_states(id),
    FOREIGN KEY(pagerevid) REFERENCES page_revisions(id),
);
