DROP TABLE IF EXISTS shopping_tool_lookmetrics_temp;

CREATE TABLE shopping_tool_lookmetrics_temp (
    id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    average_item_price numeric(10, 2) NULL,
    total_look_price numeric(10, 2) NULL,
    total_favorites integer NOT NULL,
    total_item_sales numeric(10, 2) NULL,
    store_rank numeric(10, 2) NULL,
    allume_look_id integer NOT NULL);



-- LookMetrics are based off the Look they are foreign key'd to
-- Using the allume_looks table, I should construct some of these fields here

INSERT INTO shopping_tool_lookmetrics_temp (
    average_item_price,
    total_look_price,
    total_favorites,
    total_item_sales,
    store_rank,
    allume_look_id)
SELECT
    0 as average_item_price,
    0 as total_look_price,
    0 as total_favorites,
    0 as stotal_item_sales,
    0 as store_rank,
    al.id FROM allume_looks al;


CREATE INDEX shopping_tool_lookmetrics_allume_look_id_d50ba475 ON shopping_tool_lookmetrics_temp (allume_look_id);

DROP TABLE IF EXISTS shopping_tool_lookmetrics;

RENAME TABLE shopping_tool_lookmetrics_temp TO shopping_tool_lookmetrics;
