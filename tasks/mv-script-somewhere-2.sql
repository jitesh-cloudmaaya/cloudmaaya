-- update via delete/insert
-- DELETE FROM product_api_product WHERE product_id IN (SELECT product_id FROM product_api_product_temp);

-- DELETE FROM product_api_product pap
-- LEFT JOIN product_api_product_temp papt
-- ON pap.product_id = papt.product_id
-- AND pap.merchant_id = papt.merchant_id
-- WHERE pap.product_id = papt.product_id
-- AND pap.merchant_id = papt.merchant_id;


-- delete logic from allume_client_360
-- DELETE FROM allume_client_360
-- WHERE wp_user_id IN (SELECT wp_user_id from update_subset);


-- DELETE FROM product_api_product pap WHERE pap.product_id = product_api_product_temp.product_id;

-- DELETE try # 4
DELETE pap.* FROM product_api_product pap INNER JOIN product_api_product_temp papt ON pap.product_id = papt.product_id and pap.merchant_id = papt.merchant_id;

INSERT INTO product_api_product (
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
    primary_category,
    secondary_category,
    availability,
    is_deleted,
    current_price,
    merchant_color,
    allume_size,
    allume_category
)
SELECT
    papt.product_id,
    papt.merchant_id,
    papt.product_name,
    papt.long_product_description,
    papt.short_product_description,
    papt.product_url,
    papt.product_image_url,
    papt.buy_url,
    papt.manufacturer_name,
    papt.manufacturer_part_number,
    papt.SKU,
    papt.product_type,
    papt.discount,
    papt.discount_type,
    papt.sale_price,
    papt.retail_price,
    papt.shipping_price,
    papt.color,
    papt.gender,
    papt.style,
    papt.size,
    papt.material,
    papt.age,
    papt.currency,
    papt.begin_date,
    papt.end_date,
    papt.merchant_name,
    papt.created_at,
    papt.updated_at,
    papt.allume_score,
    papt.brand,
    papt.is_best_seller,
    papt.is_trending,
    papt.keywords,
    papt.primary_category,
    papt.secondary_category,
    papt.availability,
    papt.is_deleted,
    papt.current_price,
    papt.merchant_color,
    papt.allume_size,
    papt.allume_category
FROM product_api_product_temp papt;

-- update logic from update_client_360
-- DELETE FROM allume_client_360
-- WHERE wp_user_id IN (SELECT wp_user_id from update_subset);

DROP TABLE product_api_product_temp;
