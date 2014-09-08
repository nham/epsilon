create table objects (
    hash text primary key,
    data text not null
);

create table pages (
    id integer primary key autoincrement,
);

create table page_revisions (
    pageid integer,
    rev integer not null,
    hash text not null,
    FOREIGN KEY(pageid) REFERENCES pages(id),
);
