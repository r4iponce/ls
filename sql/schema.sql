DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS link;
CREATE TABLE user
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(1024)        NOT NULL
);

CREATE TABLE link
(
    url      VARCHAR(10) PRIMARY KEY,
    real_url VARCHAR(100)                 NOT NULL,
    owner    INTEGER REFERENCES user (id) NOT NULL
);