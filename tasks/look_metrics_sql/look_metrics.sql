DROP TABLE IF EXISTS shopping_tool_lookmetrics_temp;

CREATE TABLE shopping_tool_lookmetrics_temp (
    id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    average_item_price numeric(10, 2) NULL,
    total_look_price numeric(10, 2) NULL,
    total_favorites integer NOT NULL,
    total_item_sales numeric(10, 2) NULL,
    store_rank numeric(10, 2) NULL,
    allume_look_id integer NOT NULL);


-- reference view
-- CREATE OR REPLACE VIEW order_list AS
-- (SELECT 
-- wwoi.order_id AS order_id,
-- ac.wp_user_id AS wp_user_id,
-- wp.post_date AS order_date,
-- count(0) AS items,
-- sum(wwoim.meta_value) AS amt 
-- FROM 
-- wp_posts wp,
-- wp_woocommerce_order_items wwoi,
-- wp_woocommerce_order_itemmeta wwoim,
-- allume_carts ac 
-- WHERE 
-- wp.ID = wwoi.order_id AND 
-- wwoi.order_item_id = wwoim.order_item_id AND 
-- wwoi.order_item_type = 'line_item' AND 
-- wwoim.meta_key = '_line_total' AND 
-- ac.id = wp.allume_cart_id AND 
-- ac.wp_user_id <> 0 
-- GROUP BY
-- wwoi.order_id,
-- wp.post_date,
-- ac.wp_user_id);

-- create temporary aggregation view for average_Item_price and total_look_price?
CREATE OR REPLACE VIEW aggregation_metrics AS
(SELECT
    alp.allume_look_id as look_id,
    SUM(pap.current_price) as total_look_price,
    SUM(pap.current_price) / COUNT(allume_look_id) as average_item_price
    FROM allume_looks al LEFT JOIN allume_look_products alp ON al.id = alp.allume_look_id
    LEFT JOIN product_api_product pap ON alp.wp_product_id = pap.product_id GROUP BY al.id # join on wp_product_id?
);

-- SUM(pap.current_price) / COUNT(allume_look_id) as average_item_price
-- FROM allume_looks al LEFT JOIN allume_look_products alp ON al.id = alp.allume_look_id
-- LEFT JOIN product_api_product pap ON alp.wp_product_id = pap.product_id GROUP BY al.id LIMIT 10;

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
    COUNT(ulf.look_id) as total_favorites,
    0 as total_item_sales, # Blank for now
    0 as store_rank, # Blank for now
    al.id FROM allume_looks al
    LEFT JOIN aggregation_metrics am
    ON al.id = am.look_id
    LEFT JOIN shopping_tool_userlookfavorite ulf
    ON al.id = ulf.look_id GROUP BY al.id;

UPDATE shopping_tool_lookmetrics_temp stlmtt
LEFT JOIN aggregation_metrics am
ON am.look_id = stlmtt.allume_look_id
SET stlmtt.average_item_price = am.average_item_price,
    stlmtt.total_look_price = am.total_look_price
WHERE am.look_id = stlmtt.allume_look_id;

 -- SELECT alp.allume_look_id, SUM(pap.current_price) FROM
 -- allume_looks al LEFT JOIN allume_look_products alp ON
 -- al.id = alp.allume_look_id LEFT JOIN product_api_product pap
 -- ON alp.wp_product_id = pap.product_id GROUP BY al.id LIMIT 10;

-- SELECT alp.allume_look_id, alp.wp_product_id, pap.current_price, pap.product_id, pap.product_name
-- from allume_look_products alp LEFT JOIN product_api_product pap ON alp.wp_product_id = pap.product_id

CREATE INDEX shopping_tool_lookmetrics_allume_look_id_d50ba475 ON shopping_tool_lookmetrics_temp (allume_look_id);

DROP TABLE IF EXISTS shopping_tool_lookmetrics;

RENAME TABLE shopping_tool_lookmetrics_temp TO shopping_tool_lookmetrics;
