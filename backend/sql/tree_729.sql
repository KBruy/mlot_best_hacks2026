-- Drzewo 729 węzłów (id 1..729), z każdego id idą 3 kolejne:
-- dzieci id k to 3k-1, 3k, 3k+1 (id1 -> 2,3,4; id2 -> 5,6,7; ...).
-- Wszystkie teksty to neutralne etykiety; właściwą treść wpisuje autor.
-- Idempotentne: ponowne uruchomienie nie duplikuje danych.

CREATE TABLE IF NOT EXISTS nodes (
    id      INTEGER PRIMARY KEY,
    content TEXT NOT NULL            -- fragment historii
);

CREATE TABLE IF NOT EXISTS choices (
    parent_id INTEGER NOT NULL REFERENCES nodes(id),
    child_id  INTEGER NOT NULL REFERENCES nodes(id),
    label     TEXT NOT NULL,         -- tekst przycisku wyboru
    legend    TEXT NOT NULL,         -- legenda dołączona do wyboru (konsekwencja)
    PRIMARY KEY (parent_id, child_id)
);

CREATE INDEX IF NOT EXISTS choices_child_idx ON choices (child_id);

INSERT INTO nodes (id, content)
SELECT n, 'Fragment historii ' || n
FROM generate_series(1, 729) AS n
ON CONFLICT (id) DO NOTHING;

INSERT INTO choices (parent_id, child_id, label, legend)
SELECT p, c, 'Wybór ' || c, 'Legenda wyboru ' || c
FROM generate_series(1, 729) AS p
CROSS JOIN LATERAL generate_series(3 * p - 1, 3 * p + 1) AS c
WHERE c <= 729
ON CONFLICT (parent_id, child_id) DO NOTHING;
