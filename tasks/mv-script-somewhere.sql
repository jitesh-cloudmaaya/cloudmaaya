# table = temporary/intermediate table
# statement = "DELETE FROM product_api_product WHERE temp_table.product_id = product_api.product_id"
# statement = "INSERT INTO"

DROP TABLE IF EXISTS product_api_product_temp;

CREATE TABLE IF NOT EXISTS product_api_product_temp (
    id integer AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    product_id bigint(20) NULL, 
    merchant_id bigint(20) NULL, 
    product_name varchar(255) NULL, 
    long_product_description varchar(2000) NULL, 
    short_product_description varchar(500) NULL, 
    product_url varchar(2000) NULL, 
    product_image_url varchar(2000) NULL, 
    buy_url varchar(2000) NULL, 
    manufacturer_name varchar(250) NULL,
    manufacturer_part_number varchar(50) NULL, 
    SKU varchar(64) NULL, 
    product_type varchar(128) NULL, 
    discount numeric(10, 2) NULL, 
    discount_type varchar(10) NULL, 
    sale_price numeric(10, 2) NULL, 
    retail_price numeric(10, 2) NULL, 
    shipping_price numeric(10, 2) NULL, 
    color varchar(128) NULL, 
    gender varchar(128) NULL, 
    style varchar(128) NULL, 
    size varchar(128) NULL, 
    material varchar(128) NULL, 
    age varchar(128) NULL, 
    currency varchar(3) NULL, 
    begin_date datetime(6) NULL,
    end_date datetime(6) NULL,
    merchant_name varchar(2000) NULL,
    created_at datetime(6) NULL, 
    updated_at datetime(6) NULL,
    allume_score integer NULL,
    brand varchar(255) NULL,
    is_best_seller tinyint(1) NULL,
    is_trending tinyint(1) NULL,
    keywords varchar(1000) NULL,
    primary_category varchar(150) NULL,
    secondary_category varchar(500) NULL,
    availability varchar(50) NULL, 
    is_deleted tinyint(1) NULL,
    current_price numeric(10, 2) NULL,
    merchant_color varchar(255) NULL,
    allume_size varchar(255) NULL,
    allume_category varchar(255) NULL
    );

# LOAD DATA for temp table would go here
-- LOAD DATA;