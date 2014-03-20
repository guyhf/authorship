DROP TABLE IF EXISTS article_data;
create TABLE article_data
(
	id int unsigned not null auto_increment,
	data text not null,
	CONSTRAINT pk_id primary key (id)
);
DROP TABLE IF EXISTS article;
create TABLE article
(
	id int unsigned not null auto_increment,
	title varchar(512),
	pub_year int,
	pub_month varchar(30),
	pubmed_id varchar(30),
	journal_id int unsigned not null,
	is_review boolean not null default false,
        data_id int unsigned not null,
	FOREIGN KEY (data_id) REFERENCES article_data(id),
	FOREIGN KEY (journal_id) REFERENCES journal_db.journal(id),
	CONSTRAINT pk_id primary key (id)
);

DROP TABLE IF EXISTS author;
create TABLE author
(
	id int unsigned not null auto_increment,
	last_name varchar(50) not null,
	first_name varchar(50) not null,
	initials varchar(10),
	first_initial char(1),
	second_initial char(1),
	PRIMARY KEY (last_name, initials),
	CONSTRAINT u_id unique (id)
);
DROP TABLE IF EXISTS authorship;
create TABLE authorship
(
	id int unsigned not null auto_increment,
	article_id int unsigned not null,
	author_id int unsigned not null,
	FOREIGN KEY (article_id) REFERENCES article(id),
	FOREIGN KEY (author_id) REFERENCES author(id),
	CONSTRAINT pk_id primary key (id)
);