DROP FUNCTION get_text_by_id(recieved_id integer);

CREATE OR REPLACE FUNCTION get_text_by_id(
	recieved_id integer
)
RETURNS TABLE(
	text_id_ integer,
	text_issued_ date,
	text_title_ varchar,
	text_language_ varchar,
	text_authors_ varchar,
	text_subject_ varchar
)
	AS
$$
	BEGIN
		IF EXISTS(SELECT texts_data.text_id FROM texts_data WHERE texts_data.text_id = recieved_id)
			THEN
				RETURN QUERY
					SELECT * FROM texts_data WHERE texts_data.text_id = recieved_id;
		ELSE
			RAISE WARNING 'Text with id % does not exist!', recieved_id;
		END IF;
	END;
$$

LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;


SELECT * FROM get_text_by_id(0);

---------------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_texts(
	recieved_text_author varchar,
	recieved_text_title varchar,
	recieved_text_language varchar,
	recieved_text_subject varchar,
	recieved_l_date date,
	recieved_r_date date
)
RETURNS TABLE(
	text_id_ integer,
	text_issued_ date,
	text_title_ varchar,
	text_language_ varchar,
	text_authors_ varchar,
	text_subject_ varchar
)
	AS
$$
	BEGIN
		IF EXISTS(

			SELECT
				texts_data.text_id
			FROM
				texts_data
			WHERE
				texts_data.text_authors ~ ''
			AND
				texts_data.text_title ~ recieved_text_title
			AND
				text_data.text_language ~ recieved_text_language
			AND
				text_data.text_subject ~ ''
			AND
				text_data.text_issued BETWEEN recieved_l_date AND recieved_r_date;

		)

			THEN
				RETURN QUERY
					SELECT * FROM texts_data WHERE texts_data.text_id = recieved_id;
		ELSE
			RAISE WARNING 'Texts with such data do not exist!';
		END IF;
	END;
$$

LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;


select * from texts_data where texts_data.text_issued between '2008-01-01' AND '2010-01-01';


