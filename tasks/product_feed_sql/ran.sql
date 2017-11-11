
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
  allume_score

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
  UPPER(SUBSTRING_INDEX(rp.attribute_5_color, ',', 1)),
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
  0 as allume_score
FROM tasks_ranproducts rp LEFT JOIN product_api_product ap ON ap.merchant_id = rp.merchant_id AND ap.product_id = rp.product_id
INNER JOIN product_api_merchant m ON m.external_merchant_id = rp.merchant_id
WHERE ap.product_id IS NULL) x;


-- Update Existing Products
UPDATE product_api_product ap
INNER JOIN tasks_ranproducts rp ON ap.merchant_id = rp.merchant_id AND ap.product_id = rp.product_id
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
  ap.color =  UPPER(SUBSTRING_INDEX(rp.attribute_5_color, ',', 1)),
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
  ap.updated_at =  NOW();



/*


  if row["merchant_id"] == 41558:
    new_row["color"] = ""
    new_row["size"] = ""
  if new_row["age"] != "ADULT" and new_row["age"] != "KIDS":
    new_row["age"] = ""

  return new_row

*/



/*
def format_data(row):
  """Takes a row of data and formats it, returning a new row of formatted data."""
  new_row = {}

  new_row["product_id"] = row["product_id"]
  new_row["merchant_id"] = row["merchant_id"]
  new_row["product_name"] = row["product_name"]
  new_row["long_product_description"] = row["long_product_description"]
  new_row["short_product_description"] = row["short_product_description"]
  new_row["product_url"] = row["product_url"]
  new_row["product_image_url"] = row["product_image_url"]
  new_row["buy_url"] = row["buy_url"]
  new_row["manufacturer_name"] = row["manufacturer_name"]
  new_row["manufacturer_part_number"] = row["manufacturer_part_number"]
  new_row["SKU"] = row["SKU"]
  new_row["product_type"] = row["attribute_2_product_type"]
  new_row["discount"] = row["discount"]
  new_row["discount_type"] = row["discount_type"]
  new_row["sale_price"] = row["sale_price"]
  new_row["retail_price"] = row["retail_price"]
  new_row["shipping_price"] = row["shippping"]
  new_row["color"] = row["attribute_5_color"]
  new_row["gender"] = row["attribute_6_gender"]
  new_row["style"] = row["attribute_7_style"]
  new_row["size"] = row["attribute_3_size"]
  new_row["material"] = row["attribute_4_material"]
  new_row["age"] = row["attribute_8_age"]
  new_row["currency"] = row["currency"]
  new_row["availability"] = row["availablity"]
  new_row["begin_date"] = row["begin_date"]
  new_row["end_date"] = row["end_date"]
  new_row["keywords"] = row["keywords"]

  if not row["availablity"]:
    new_row["availability"] = "out-of-stock"


  if row["discount_type"] != "amount" and row["discount_type"] != "percentage":
    new_row["discount"] = 0
    new_row["discount_type"] = "amount"



  if new_row["color"] is None:
    new_row["color"] = ""
  if new_row["color"].isspace():
    new_row["color"] = ""
  if new_row["color"].startswith(","):
    new_row["color"] = new_row["color"][1:]
  new_row["color"] = new_row["color"].upper()
  new_row["color"] = new_row["color"].replace(" / ", "/")
  new_row["color"] = new_row["color"].replace("/ ", "/")
  new_row["color"] = new_row["color"].replace(" /", "/")
  new_row["color"] = new_row["color"].replace("~~", "/")
  new_row["color"] = new_row["color"].replace(",", "/")
  new_row["color"] = new_row["color"].replace(" , ", "/")
  new_row["color"] = new_row["color"].replace(" & ", "/")



  if new_row["gender"] is None:
    new_row["gender"] = ""
  new_row["gender"] = new_row["gender"].upper()
  if new_row["gender"] == "MALE":
    new_row["gender"] = "MEN"
  if new_row["gender"] == "FEMALE":
    new_row["gender"] = "WOMEN"
  if new_row["gender"] == "MAN":
    new_row["gender"] = "MEN"
  if new_row["gender"] == "WOMAN":
    new_row["gender"] = "WOMEN"
  if new_row["gender"] != "MEN" and new_row["gender"] != "WOMEN":
    new_row["gender"] = ""

  if new_row["size"] is None:
    new_row["size"] = ""
  new_row["size"] = new_row["size"].upper()
  new_row["size"] = new_row["size"].replace("~~", ",")


  */
