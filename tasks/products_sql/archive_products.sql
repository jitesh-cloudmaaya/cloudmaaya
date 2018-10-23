INSERT IGNORE INTO product_api_producthistory (
  product_id,
  size,
  allume_size,
  merchant_id,
  product_name,
  primary_category,
  secondary_category,
  long_product_description,
  short_product_description,
  product_url,
  product_image_url,
  buy_url,
  manufacturer_name,
  manufacturer_part_number,
  SKU,
  product_type,
  discount,
  discount_type,
  sale_price,
  retail_price,
  shipping_price,
  color,
  gender,
  style,
  material,
  age,
  currency,
  begin_date,
  end_date,
  merchant_name,
  created_at,
  updated_at,
  allume_score,
  brand,
  is_best_seller,
  is_trending,
  keywords,
  availability,
  is_deleted,
  current_price,
  allume_category,
  merchant_color,
  raw_product_url 
)
SELECT
  hist.product_id,
  hist.size,
  hist.allume_size,
  hist.merchant_id,
  hist.product_name,
  hist.primary_category,
  hist.secondary_category,
  hist.long_product_description,
  hist.short_product_description,
  hist.product_url,
  hist.product_image_url,
  hist.buy_url,
  hist.manufacturer_name,
  hist.manufacturer_part_number,
  hist.SKU,
  hist.product_type,
  hist.discount,
  hist.discount_type,
  hist.sale_price,
  hist.retail_price,
  hist.shipping_price,
  hist.color,
  hist.gender,
  hist.style,
  hist.material,
  hist.age,
  hist.currency,
  hist.begin_date,
  hist.end_date,
  hist.merchant_name,
  NOW(),
  hist.updated_at,
  hist.allume_score,
  hist.brand,
  hist.is_best_seller,
  hist.is_trending,
  hist.keywords,
  hist.availability,
  hist.is_deleted,
  hist.current_price,
  hist.allume_category,
  hist.merchant_color,
  hist.raw_product_url 
FROM product_api_product hist
where hist.is_deleted=1 
     and hist.product_id not in (select DISTINCT product_id from allume_product_images)
     and hist.product_id not in (select DISTINCT product_id from allume_stylist_add_on_data)
     and hist.product_id not in (select DISTINCT product_id from shopping_tool_rack)
     and hist.product_id not in (select DISTINCT product_id from shopping_tool_report)
     and hist.product_id not in (select DISTINCT product_id from shopping_tool_userproductfavorite)
     and hist.product_id not in (select DISTINCT product_id from wp_woocommerce_downloadable_product_permissions) 
     and hist.product_id not in (select raw_product_id from allume_look_products where raw_product_id >0 and raw_product_id group by raw_product_id)
     and hist.product_id not in (select p.affiliate_feed_product_api_product_id
                                 from wp_woocommerce_order_itemmeta m
                                 join wp_posts p on p.ID = meta_value and meta_key = '_product_id'
                                 where p.affiliate_feed_product_api_product_id is not null
                                 GROUP BY p.affiliate_feed_product_api_product_id);

DELETE FROM product_api_product
     where is_deleted=1 
     and product_id not in (select DISTINCT product_id from allume_product_images)
     and product_id not in (select DISTINCT product_id from allume_stylist_add_on_data)
     and product_id not in (select DISTINCT product_id from shopping_tool_rack)
     and product_id not in (select DISTINCT product_id from shopping_tool_report)
     and product_id not in (select DISTINCT product_id from shopping_tool_userproductfavorite)
     and product_id not in (select DISTINCT product_id from wp_woocommerce_downloadable_product_permissions)
     and product_id not in (select raw_product_id from allume_look_products where raw_product_id >0 and raw_product_id group by raw_product_id)
     and product_id not in (select p.affiliate_feed_product_api_product_id
                                 from wp_woocommerce_order_itemmeta m
                                 join wp_posts p on p.ID = meta_value and meta_key = '_product_id'
                                 where p.affiliate_feed_product_api_product_id is not null
                                 GROUP BY p.affiliate_feed_product_api_product_id);

