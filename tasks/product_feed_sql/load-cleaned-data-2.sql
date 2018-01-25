ALTER TABLE product_api_product CONVERT TO CHARACTER SET utf8;
CREATE UNIQUE INDEX products ON product_api_product (product_id, merchant_id);
INSERT INTO product_api_product (
    product_id,
    merchant_id,
    product_name,
    long_product_description,
    short_product_description,
    product_url,
    raw_product_url,
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
    papt.raw_product_url,
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
FROM product_api_product_temp papt
ON DUPLICATE KEY UPDATE
    product_id = VALUES(product_id),
    merchant_id = VALUES(merchant_id),
    product_name = VALUES(product_name),
    long_product_description = VALUES(long_product_description),
    short_product_description = VALUES(short_product_description),
    product_url = VALUES(product_url),
    raw_product_url = VALUES(raw_product_url),
    product_image_url = VALUES(product_image_url),
    buy_url = VALUES(buy_url),
    manufacturer_name = VALUES(manufacturer_name),
    manufacturer_part_number = VALUES(manufacturer_part_number),
    SKU = VALUES(SKU),
    product_type = VALUES(product_type),
    discount = VALUES(discount),
    discount_type = VALUES(discount_type),
    sale_price = VALUES(sale_price),
    retail_price = VALUES(retail_price),
    shipping_price = VALUES(shipping_price),
    color = VALUES(color),
    gender = VALUES(gender),
    style = VALUES(style),
    size = VALUES(size),
    material = VALUES(material),
    age = VALUES(age),
    currency = VALUES(currency),
    begin_date = VALUES(begin_date),
    end_date = VALUES(end_date),
    merchant_name = VALUES(merchant_name),
    created_at = VALUES(created_at),
    updated_at = VALUES(updated_at),
    allume_score = VALUES(allume_score),
    brand = VALUES(brand),
    is_best_seller = VALUES(is_best_seller),
    is_trending = VALUES(is_trending),
    keywords = VALUES(keywords),
    primary_category = VALUES(primary_category),
    secondary_category = VALUES(secondary_category),
    availability = VALUES(availability),
    is_deleted = VALUES(is_deleted),
    current_price = VALUES(current_price),
    merchant_color = VALUES(merchant_color),
    allume_size = VALUES(allume_size),
    allume_category = VALUES(allume_category);

DROP INDEX products ON product_api_product;
DROP TABLE product_api_product_temp;
