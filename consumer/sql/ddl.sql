-- Table: public.webmon_polls

-- DROP TABLE IF EXISTS public.webmon_polls;

CREATE TABLE IF NOT EXISTS public.webmon_polls
(
    id integer NOT NULL DEFAULT nextval('webmon_polls_id_seq'::regclass),
    url character varying COLLATE pg_catalog."default",
    status_code integer,
    response_time interval,
    regex_match character varying COLLATE pg_catalog."default",
    CONSTRAINT pk_webmon_polls PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.webmon_polls
    OWNER to avnadmin;
