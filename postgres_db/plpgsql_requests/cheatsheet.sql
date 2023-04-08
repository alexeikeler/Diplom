--Johann Wolfgang von Goethe

select * from texts_data
where text_authors like '%' || 'Goethe' || '%' || '' || '%'
order by text_language;

--Delete all non english | german | russian books
delete from texts_data where text_language !~ '(de|en|ru)';
delete from texts_data where text_language !~ '(de|en|ru)$';
delete from texts_data where length(text_language) > 2;

--Delete unnecessary data
ALTER TABLE texts_data
DROP COLUMN text_type;

--Delete unnecessary data
ALTER TABLE texts_data
DROP COLUMN text_bookshelves;



select * from texts_data where text_language ~ '(de|en|ru)$';

select * from texts_data where text_language LIKE 'ru';

SELECT text_language, COUNT(*) as cnt
FROM texts_data
GROUP BY text_language
ORDER BY cnt;


select MIN(text_issued), MAX(text_issued) from texts_data;



select * from texts_data where texts_data.text_subject LIKE '%' || 'War' || '%';

select * from texts_data;