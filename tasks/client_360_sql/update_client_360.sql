-- steps

-- 1) create the order list view
CREATE OR REPLACE VIEW order_list AS
(SELECT 
wwoi.order_id AS order_id,
ac.wp_user_id AS wp_user_id,
wp.post_date AS order_date,
count(0) AS items,
sum(wwoim.meta_value) AS amt 
FROM 
wp_posts wp,
wp_woocommerce_order_items wwoi,
wp_woocommerce_order_itemmeta wwoim,
allume_carts ac 
WHERE 
wp.ID = wwoi.order_id AND 
wwoi.order_item_id = wwoim.order_item_id AND 
wwoi.order_item_type = 'line_item' AND 
wwoim.meta_key = '_line_total' AND 
ac.id = wp.allume_cart_id AND 
ac.wp_user_id <> 0 
GROUP BY
wwoi.order_id,
wp.post_date,
ac.wp_user_id);

-- 2) set the session group_concat_max_len variable
SET SESSION group_concat_max_len=5000;

-- 3) update the table for any wp_user_id entries

-- REALLY CONFIRM THAT THIS STATEMENT UPDATES NEW ENTRIES on simple example
INSERT INTO allume_client_360 (wp_user_id, first_name, last_name)
SELECT wu.id, wu.first_name, wu.last_name FROM wp_users wu
WHERE wu.id NOT IN (
    SELECT wp_user_id from allume_client_360
);

-- 3a) remove no longer existing id, first/last name from allume_client_360?
-- DELETE


-- 4) update the recently populated table
-- working update command?

-- replace temp with allume_client_360
UPDATE temp ac3
LEFT JOIN allume_wp_user_shipping_addresses sa ON ac3.wp_user_id = sa.wp_user_id

LEFT JOIN (
    SELECT COUNT(*) styling_count,
    COALESCE(MAX(start_date), MAX(date_created)) last_styling_date,
    wp_initiator_id
    FROM allume_styling_sessions
    GROUP BY wp_initiator_id
) styling_sessions ON ac3.wp_user_id = styling_sessions.wp_initiator_id

LEFT JOIN allume_clients ac ON ac3.wp_user_id = ac.wp_client_id

SET ac3.address_1 = sa.address_1,
    ac3.address_2 = sa.address_2,
    ac3.city = sa.city,
    ac3.state = sa.state,
    ac3.country = sa.country,
    ac3.styling_count = styling_sessions.styling_count,
    ac3.last_styling_date = styling_sessions.last_styling_date,
    ac3.utm_source = ac.utm_source,
    ac3.utm_campaign = ac.utm_campaign,
    ac3.utm_term = ac.utm_term,
    ac3.utm_medium = ac.utm_medium;




