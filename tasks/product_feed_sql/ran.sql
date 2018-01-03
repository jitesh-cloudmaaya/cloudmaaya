
-- Delete Non Applicable Categories
DELETE p FROM tasks_ranproducts p 
LEFT JOIN product_api_merchantcategory c ON c.name = p.primary_category 
WHERE c.active = false;

-- Insert New Products
INSERT INTO product_api_product         
( 
  product_id, 
  merchant_id,
  product_name,
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
  size,
  material,
  age,
  currency,
  availablity,
  -- begin_date,
  -- end_date,
  keywords,
  primary_category,
  secondary_category,
  brand,
  updated_at,
  merchant_name,
  is_best_seller,
  is_trending,
  allume_score,
  current_price,
  is_deleted

)
SELECT * FROM (
SELECT 
  rp.product_id,
  rp.merchant_id,
  rp.product_name,
  rp.long_product_description,
  rp.short_product_description,
  rp.product_url,
  rp.product_image_url,
  rp.buy_url,
  rp.manufacturer_name,
  rp.manufacturer_part_number,
  rp.SKU,
  rp.attribute_2_product_type,
  CASE WHEN rp.discount_type <> "amount" OR rp.discount_type <> "percentage" THEN 0 ELSE rp.discount END AS discount,
  CASE WHEN rp.discount_type <> "amount" OR rp.discount_type <> "percentage" THEN "amount" ELSE rp.discount_type END AS discount_type,
  rp.sale_price,
  rp.retail_price,
  rp.shippping,
  cm.allume_color,
  REPLACE(REPLACE(REPLACE(UPPER(rp.attribute_6_gender), "FEMALE", "WOMEN"), "MALE", "MEN"), "MAN", "MEN"),
  rp.attribute_7_style,
  REPLACE(UPPER(rp.attribute_3_size), '~', ','),
  rp.attribute_4_material,
  UPPER(rp.attribute_8_age),
  rp.currency,
  CASE WHEN rp.availablity = '' OR NULL THEN 'out-of-stock' ELSE rp.availablity END AS availablity,
  -- rp.begin_date,
  -- rp.end_date,
  rp.keywords,
  rp.primary_category,
  rp.secondary_category,
  rp.brand,
  NOW() as updated_at,
  m.name,
  0 as is_best_seller,
  0 as is_trending,
  0 as allume_score,
  CASE WHEN rp.sale_price > 0  OR NOT NULL THEN rp.sale_price ELSE rp.retail_price END as current_price,
  0 as is_deleted
FROM tasks_ranproducts rp LEFT JOIN product_api_product ap ON ap.merchant_id = rp.merchant_id AND ap.product_id = rp.product_id
INNER JOIN product_api_merchant m ON rp.merchant_id = m.external_merchant_id
LEFT JOIN product_api_colormap cm ON rp.attribute_5_color = cm.external_color 
WHERE ap.current_price IS NULL
AND m.active = 1
AND ap.id IS NULL
AND rp.modification IS NULL ) x;


-- Update Existing Products
UPDATE product_api_product ap
INNER JOIN tasks_ranproducts rp ON ap.merchant_id = rp.merchant_id AND ap.product_id = rp.product_id
INNER JOIN product_api_merchant m ON rp.merchant_id = m.external_merchant_id
LEFT JOIN product_api_colormap cm ON rp.attribute_5_color = cm.external_color 
SET
  ap.product_id =  rp.product_id,
  ap.merchant_id =  rp.merchant_id,
  ap.product_name =  rp.product_name,
  ap.long_product_description =  rp.long_product_description,
  ap.short_product_description =  rp.short_product_description,
  ap.product_url =  rp.product_url,
  ap.product_image_url =  rp.product_image_url,
  ap.buy_url =  rp.buy_url,
  ap.manufacturer_name =  rp.manufacturer_name,
  ap.manufacturer_part_number =  rp.manufacturer_part_number,
  ap.SKU =  rp.SKU,
  ap.product_type =  rp.attribute_2_product_type,
  ap.discount = CASE WHEN rp.discount_type <> "amount" OR rp.discount_type <> "percentage" THEN 0 ELSE rp.discount END,
  ap.discount_type = CASE WHEN rp.discount_type <> "amount" OR rp.discount_type <> "percentage" THEN "amount" ELSE rp.discount_type END,
  ap.sale_price =  rp.sale_price,
  ap.retail_price =  rp.retail_price,
  ap.shipping_price =  rp.shippping,
  ap.color =  cm.allume_color,
  ap.gender =  REPLACE(REPLACE(REPLACE(UPPER(rp.attribute_6_gender), "FEMALE", "WOMEN"), "MALE", "MEN"), "MAN", "MEN"),
  ap.style =  rp.attribute_7_style,
  ap.size =  REPLACE(UPPER(rp.attribute_3_size), '~', ','),
  ap.material =  rp.attribute_4_material,
  ap.age =  UPPER(rp.attribute_8_age),
  ap.currency =  rp.currency,
  ap.availablity =  CASE WHEN rp.availablity = '' OR NULL THEN 'out-of-stock' ELSE rp.availablity END,
  -- ap.begin_date =  rp.begin_date,
  -- ap.end_date =  rp.end_date,
  ap.keywords =  rp.keywords,
  ap.primary_category =  rp.primary_category,
  ap.secondary_category =  rp.secondary_category,
  ap.brand =  rp.brand,
  ap.updated_at =  NOW(),
  ap.is_deleted = CASE WHEN rp.modification = 'D' THEN 1 ELSE 0 END,
  ap.current_price = CASE WHEN rp.sale_price > 0 OR NOT NULL THEN rp.sale_price ELSE rp.retail_price END;
  WHERE m.active = 1

