DROP TABLE IF EXISTS shopping_tool_lookmetrics_temp;

CREATE TABLE shopping_tool_lookmetrics_temp (
    id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    average_item_price numeric(10, 2) NULL,
    total_look_price numeric(10, 2) NULL,
    total_favorites integer NOT NULL,
    total_item_sales numeric(10, 2) NULL,
    store_rank numeric(10, 2) NULL,
    allume_look_id integer NOT NULL);

-- create temporary aggregation view for average_Item_price and total_look_price
CREATE OR REPLACE VIEW aggregation_metrics AS
(SELECT
    alp.allume_look_id AS look_id,
    SUM(pap.current_price) AS total_look_price,
    SUM(pap.current_price) / COUNT(allume_look_id) AS average_item_price
    FROM allume_looks al LEFT JOIN allume_look_products alp ON al.id = alp.allume_look_id
    LEFT JOIN product_api_product pap ON alp.raw_product_id = pap.id GROUP BY al.id
);

CREATE OR REPLACE VIEW look_favorites AS
(SELECT
    al.id AS look_id,
    COUNT(ulf.look_id) AS total_favorites
    FROM allume_looks al
    LEFT JOIN shopping_tool_userlookfavorite ulf
    ON al.id = ulf.look_id GROUP BY al.id
);

INSERT INTO shopping_tool_lookmetrics_temp (
    average_item_price,
    total_look_price,
    total_favorites,
    total_item_sales,
    store_rank,
    allume_look_id)
SELECT
    am.average_item_price AS average_item_price,
    am.total_look_price AS total_look_price,
    lf.total_favorites AS total_favorites,
    0 AS total_item_sales, # Blank for now
    0 AS store_rank, # Blank for now
    al.id FROM allume_looks al
    LEFT JOIN aggregation_metrics am
    ON al.id = am.look_id
    LEFT JOIN look_favorites lf
    ON al.id = lf.look_id;

CREATE INDEX shopping_tool_lookmetrics_allume_look_id_d50ba475 ON shopping_tool_lookmetrics_temp (allume_look_id);

-- also drop the views
DROP VIEW IF EXISTS aggregation_metrics;
DROP VIEW IF EXISTS look_favorites;

DROP TABLE IF EXISTS shopping_tool_lookmetrics;

RENAME TABLE shopping_tool_lookmetrics_temp TO shopping_tool_lookmetrics;
