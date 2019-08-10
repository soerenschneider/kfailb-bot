CREATE TABLE IF NOT EXISTS kfailbot (
    line SMALLINT PRIMARY KEY,
    subscribers INTEGER[]
);

CREATE TABLE IF NOT EXISTS silence (
    subscriber BIGINT PRIMARY KEY,
    until TIMESTAMP,
    mute BOOLEAN
);