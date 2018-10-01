CREATE OR REPLACE VIEW order_list AS
  (SELECT
     wwoi.order_id         AS order_id,
     ac.wp_user_id         AS wp_user_id,
     wp.post_date          AS order_date,
     count(0)              AS items,
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

SET SESSION group_concat_max_len = 5000;

DELETE FROM allume_client_360 WHERE wp_user_id IN (SELECT u0.ID FROM wp_users u0 WHERE u0.last_modified > (SELECT MAX(a0.last_updated) FROM allume_client_360 a0));


INSERT INTO allume_client_360 (
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
   VALUES
   (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
   ;