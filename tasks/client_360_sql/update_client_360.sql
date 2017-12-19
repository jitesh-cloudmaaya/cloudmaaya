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


-- working update command?
UPDATE temp ac3
LEFT JOIN allume_wp_user_shipping_addresses sa ON t.wp_user_id = sa.wp_user_id
SET ac3.address_1 = sa.address_1
    ac3.address_2 = sa.address_2
    ac3.city = sa.city
    ac3.state = sa.state
    ac3.country = sa.country;


-- 4) update the recently populated table
-- UPDATE allume_client_360 
-- SET wp_user_id = (SELECT wu.id from wp_users wu),
--     first_name = expression,
--     last_name = expression,
--     address_1 = expression,
--     address_2 = expression,
--     city = expression,
--     state = expression,
--     country = expression,
--     birthday = expression,
--     occupation = expression,
--     wear_to_work = expression,
--     spend_free_time = expression,
--     where_live = expression,
--     time_of_day_text = expression,
--     social_media = expression,
--     instagram = expression,
--     pinterest = expression,
--     linkedin = expression,
--     photo = expression,
--     styling_count = expression,
--     last_styling_date = expression,
--     order_count = expression,
--     last_order_amt = expression,
--     last_order_date = expression,
--     avg_items = expression,
--     avg_amt = expression,
--     heart_count = expression,
--     comment_count = expression,
--     star_count = expression,
--     signup_date = expression,
--     utm_source = expression,
--     utm_campaign = expression,
--     utm_term = expression,
--     utm_medium = expression,
--     hear_about_allume = expression,
--     height = expression,
--     weight = expression,
--     bra_size = expression,
--     body_part_attention = expression,
--     body_part_conceal = expression,
--     fit_challenges = expression,
--     hair_complex_color = expression,
--     first_session_focus = expression,
--     looks_goal = expression,
--     pieces_focus = expression,
--     outfits_preference = expression,
--     other_goals = expression,
--     stores = expression,
--     brands = expression,
--     spending_tops = expression,
--     spending_bottoms = expression,
--     spending_dresses = expression,
--     spending_jackets = expression,
--     spending_shoes = expression,
--     style_celebs = expression,
--     style_looks = expression,
--     style_jeans = expression,
--     style_tops = expression,
--     style_dress = expression,
--     style_jacket = expression,
--     style_shoe = expression,
--     colors_preference = expression,
--     style_avoid = expression,
--     size_pants = expression,
--     size_jeans = expression,
--     size_tops = expression,
--     size_shoe = expression,
--     ears_pierced = expression,
--     jewelry_style = expression,
--     jewelry_type = expression
-- [WHERE condtions]


/* Example syntax
UPDATE table
SET column1 = expression1,
    column2 = expression2,
    column3 = (SELECT expression3 FROM table2 WHERE conditions)
    ...
    [WHERE conditions]


UPDATE T2
SET HomeAddress = t1.address
FROM TABLE t2
JOIN TABLE1 t1 on T!.id = t2.HomeAddressID
and t2.HomeAddress <> t1.address

*/



/* insert into temp table logic
INSERT INTO allume_client_360_temp (
wp_user_id, 
first_name, 
last_name, 
address_1, 
address_2, 
city, 
state, 
country, 
birthday, 
occupation,
wear_to_work,
spend_free_time,
where_live,
time_of_day_text,
social_media,
instagram,
pinterest,
linkedin,
photo,
styling_count, 
last_styling_date,
order_count, 
last_order_amt,
last_order_date, 
avg_items, 
avg_amt,
heart_count,
comment_count,
star_count,
signup_date, 
utm_source, 
utm_campaign, 
utm_term, 
utm_medium,
hear_about_allume,
height,
weight,
bra_size,
body_part_attention,
body_part_conceal,
fit_challenges,
hair_complex_color,
first_session_focus,
looks_goal,
pieces_focus,
outfits_preference, 
other_goals,
stores,
brands,
spending_tops,
spending_bottoms,
spending_dresses,
spending_jackets,
spending_shoes,
style_celebs,
style_looks,
style_jeans,
style_tops,
style_dress,
style_jacket,
style_shoe,
colors_preference,
style_avoid,
size_pants,
size_jeans,
size_tops,
size_shoe,
ears_pierced,
jewelry_style,
jewelry_type)
SELECT 
wu.id,
wu.first_name, 
wu.last_name, 
sa.address_1, 
sa.address_2, 
sa.city, 
sa.state, 
sa.country, 
quiz.birthday, 
quiz.occupation,
quiz.wear_to_work,
quiz.spend_free_time,
quiz.where_live,
quiz.time_of_day_text,
quiz.social_media,
quiz.instagram,
quiz.pinterest,
quiz.linkedin,
quiz.photo,
styling_sessions.styling_count, 
styling_sessions.last_styling_date,
order_summary.order_count, 
last_ord_amt.amt as last_order_amt,
order_summary.last_order_date, 
order_summary.avg_items, 
order_summary.avg_amt,
social_actions.heart_count,
social_actions.comment_count,
social_actions.star_count,
wu.user_registered as signup_date, 
ac.utm_source, 
ac.utm_campaign, 
ac.utm_term, 
ac.utm_medium,
quiz.hear_about_allume,
quiz.height,
quiz.weight,
quiz.bra_size,
quiz.body_part_attention,
quiz.body_part_conceal,
quiz.fit_challenges,
quiz.hair_complex_color,
quiz.first_session_focus,
quiz.looks_goal,
quiz.pieces_focus,
quiz.outfits_preference, 
quiz.other_goals,
quiz.stores,
quiz.brands,
quiz.spending_tops,
quiz.spending_bottoms,
quiz.spending_dresses,
quiz.spending_jackets,
quiz.spending_shoes,
quiz.style_celebs,
quiz.style_looks,
quiz.style_jeans,
quiz.style_tops,
quiz.style_dress,
quiz.style_jacket,
quiz.style_shoe,
quiz.colors_preference,
quiz.style_avoid,
quiz.size_pants,
quiz.size_jeans,
quiz.size_tops,
quiz.size_shoe,
quiz.ears_pierced,
quiz.jewelry_style,
quiz.jewelry_type
FROM 
wp_users wu 
LEFT JOIN 
allume_wp_user_shipping_addresses sa 
ON wu.ID = sa.wp_user_id
LEFT JOIN
(SELECT 
COUNT(*) styling_count, 
COALESCE(MAX(start_date), MAX(date_created)) last_styling_date,  wp_initiator_id  
FROM  
allume_styling_sessions 
GROUP BY  
wp_initiator_id
) styling_sessions
ON wu.ID = styling_sessions.wp_initiator_id
LEFT JOIN
allume_clients ac
ON wu.ID = ac.wp_client_id
LEFT JOIN 
(SELECT user_email, 
GROUP_CONCAT(if(quiz_question_answer_id = 28, label, NULL) SEPARATOR ', ') AS birthday, 
GROUP_CONCAT(if(quiz_question_answer_id = 29, label, NULL) SEPARATOR ', ') AS occupation,
GROUP_CONCAT(if(quiz_question_answer_id = 30, label, NULL) SEPARATOR ', ') AS wear_to_work,
GROUP_CONCAT(if(quiz_question_answer_id = 31, label, NULL) SEPARATOR ', ') AS spend_free_time,
GROUP_CONCAT(if(quiz_question_answer_id = 27, label, NULL) SEPARATOR ', ') AS where_live,
GROUP_CONCAT(if(quiz_question_answer_id = 48, label, NULL) SEPARATOR ', ') AS time_of_day_text, 
GROUP_CONCAT(if(quiz_question_answer_id = 32, label, NULL) SEPARATOR ', ') AS social_media, 
GROUP_CONCAT(if(quiz_question_answer_id = 33, label, NULL) SEPARATOR ', ') AS instagram,
GROUP_CONCAT(if(quiz_question_answer_id = 34, label, NULL) SEPARATOR ', ') AS pinterest,
GROUP_CONCAT(if(quiz_question_answer_id = 35, label, NULL) SEPARATOR ', ') AS linkedin,   
GROUP_CONCAT(if(quiz_question_answer_id = 36, label, NULL) SEPARATOR ', ') AS photo,
GROUP_CONCAT(if(quiz_question_answer_id = 47, label, NULL) SEPARATOR ', ') AS hear_about_allume,
GROUP_CONCAT(if(quiz_question_answer_id = 14, label, NULL) SEPARATOR ', ') AS height,
GROUP_CONCAT(if(quiz_question_answer_id = 15, label, NULL) SEPARATOR ', ') AS weight,
GROUP_CONCAT(if(quiz_question_answer_id = 16, label, NULL) SEPARATOR ', ') AS bra_size,
GROUP_CONCAT(if(quiz_question_answer_id = 20, label, NULL) SEPARATOR ', ') AS body_part_attention,
GROUP_CONCAT(if(quiz_question_answer_id = 21, label, NULL) SEPARATOR ', ') AS body_part_conceal,
GROUP_CONCAT(if(quiz_question_answer_id = 22, label, NULL) SEPARATOR ', ') AS fit_challenges,
GROUP_CONCAT(if(quiz_question_answer_id = 13, label, NULL) SEPARATOR ', ') AS hair_complex_color,
GROUP_CONCAT(if(quiz_question_answer_id = 42, label, NULL) SEPARATOR ', ') AS first_session_focus,
GROUP_CONCAT(if(quiz_question_answer_id = 43, label, NULL) SEPARATOR ', ') AS looks_goal,
GROUP_CONCAT(if(quiz_question_answer_id = 44, label, NULL) SEPARATOR ', ') AS pieces_focus,
GROUP_CONCAT(if(quiz_question_answer_id = 45, label, NULL) SEPARATOR ', ') AS outfits_preference, 
GROUP_CONCAT(if(quiz_question_answer_id = 46, label, NULL) SEPARATOR ', ') AS other_goals,
GROUP_CONCAT(if(quiz_question_answer_id = 3, label, NULL) SEPARATOR ', ') AS stores,
GROUP_CONCAT(if(quiz_question_answer_id = 5, label, NULL) SEPARATOR ', ') AS brands,
GROUP_CONCAT(if(quiz_question_answer_id = 37, label, NULL) SEPARATOR ', ') AS spending_tops,
GROUP_CONCAT(if(quiz_question_answer_id = 38, label, NULL) SEPARATOR ', ') AS spending_bottoms,
GROUP_CONCAT(if(quiz_question_answer_id = 39, label, NULL) SEPARATOR ', ') AS spending_dresses,
GROUP_CONCAT(if(quiz_question_answer_id = 40, label, NULL) SEPARATOR ', ') AS spending_jackets,
GROUP_CONCAT(if(quiz_question_answer_id = 41, label, NULL) SEPARATOR ', ') AS spending_shoes,
GROUP_CONCAT(if(quiz_question_answer_id = 1, label, NULL) SEPARATOR ', ') AS style_celebs,
GROUP_CONCAT(if(quiz_question_answer_id = 2, label, NULL) SEPARATOR ', ') AS style_looks,
GROUP_CONCAT(if(quiz_question_answer_id = 6, label, NULL) SEPARATOR ', ') AS style_jeans,
GROUP_CONCAT(if(quiz_question_answer_id = 7, label, NULL) SEPARATOR ', ') AS style_tops,
GROUP_CONCAT(if(quiz_question_answer_id = 8, label, NULL) SEPARATOR ', ') AS style_dress,
GROUP_CONCAT(if(quiz_question_answer_id = 9, label, NULL) SEPARATOR ', ') AS style_jacket,
GROUP_CONCAT(if(quiz_question_answer_id = 10, label, NULL) SEPARATOR ', ') AS style_shoe,
GROUP_CONCAT(if(quiz_question_answer_id = 11, label, NULL) SEPARATOR ', ') AS colors_preference,
GROUP_CONCAT(if(quiz_question_answer_id = 12, label, NULL) SEPARATOR ', ') AS style_avoid,
GROUP_CONCAT(if(quiz_question_answer_id = 23, label, NULL) SEPARATOR ', ') AS size_pants,
GROUP_CONCAT(if(quiz_question_answer_id = 24, label, NULL) SEPARATOR ', ') AS size_jeans,
GROUP_CONCAT(if(quiz_question_answer_id = 25, label, NULL) SEPARATOR ', ') AS size_tops,
GROUP_CONCAT(if(quiz_question_answer_id = 26, label, NULL) SEPARATOR ', ') AS size_shoe,
GROUP_CONCAT(if(quiz_question_answer_id = 17, label, NULL) SEPARATOR ', ') AS ears_pierced,
GROUP_CONCAT(if(quiz_question_answer_id = 18, label, NULL) SEPARATOR ', ') AS jewelry_style,
GROUP_CONCAT(if(quiz_question_answer_id = 19, label, NULL) SEPARATOR ', ') AS jewelry_type
FROM 
(SELECT 
qua.user_email, 
qua.quiz_question_answer_id, 
qai.label 
FROM  
allume_quiz_answer_items qai,  
allume_quiz_user_answers qua  
WHERE 
FIND_IN_SET(qai.ID, qua.quiz_answer_item_ids) AND 
qai.type <> 'free_form'  AND
qai.label <> '' 
UNION 
SELECT 
user_email, 
quiz_question_answer_id, 
quiz_free_form_answer 
FROM 
allume_quiz_user_answers 
WHERE 
quiz_free_form_answer IS NOT NULL) user_answers 
GROUP BY user_email) quiz
ON wu.user_email = quiz.user_email
LEFT JOIN
(SELECT 
COUNT(*) as order_count, 
MAX(order_date) as last_order_date, 
AVG(items) as avg_items, 
AVG(amt) as avg_amt, 
wp_user_id 
FROM 
order_list 
GROUP BY wp_user_id) order_summary
ON wu.ID = order_summary.wp_user_id
LEFT JOIN
(SELECT 
ol.wp_user_id, 
ol.amt
FROM 
order_list ol
INNER JOIN 
(SELECT wp_user_id, MAX(order_date) as last_order_date
FROM order_list
GROUP BY wp_user_id) AS lod ON 
lod.last_order_date = ol.order_date 
AND lod.wp_user_id = ol.wp_user_id) last_ord_amt
ON wu.ID = last_ord_amt.wp_user_id
LEFT JOIN
(SELECT 
user_id, 
count(case when action = 'hearted' then 1 end) heart_count, 
count(case when action = 'commented' then 1 end) comment_count,
count(case when action = 'starred' then 1 end) star_count 
FROM
allume_social_actions 
GROUP BY
user_id) social_actions
ON wu.ID = social_actions.user_id;
*/
