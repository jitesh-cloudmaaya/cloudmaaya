DROP TABLE IF EXISTS shopping_tool_lookmetrics_temp;

CREATE TABLE shopping_tool_lookmetrics_temp (
    id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    average_item_price numeric(10, 2) NULL,
    total_look_price numeric(10, 2) NULL,
    total_favorites integer NOT NULL,
    total_item_sales numeric(10, 2) NULL,
    store_rank numeric(10, 2) NULL,
    allume_look_id integer NOT NULL);
CREATE INDEX shopping_tool_lookmetrics_allume_look_id_d50ba475 ON shopping_tool_lookmetrics_temp (allume_look_id);

DROP TABLE IF EXISTS shopping_tool_lookmetrics;

RENAME TABLE shopping_tool_lookmetrics_temp TO shopping_tool_lookmetrics;
