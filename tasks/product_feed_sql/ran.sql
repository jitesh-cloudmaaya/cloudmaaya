INSERT INTO product_api_product         |
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
	begin_date,
	end_date,
	keywords,
	primary_category,
	secondary_category,
	brand

)
SELECT 
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
	attribute_2_product_type,
	CASE WHEN discount_type <> "amount" OR discount_type <> "percentage" THEN 0 ELSE discount END AS discount,
	CASE WHEN discount_type <> "amount" OR discount_type <> "percentage" THEN "amount" ELSE discount_type END AS discount_type,
	sale_price,
	retail_price,
	shipping,
	UPPER(SUBSTRING_INDEX(attribute_5_color, ',', 1)),
	REPLACE(REPLACE(REPLACE(UPPER(attribute_6_gender), "FEMALE", "WOMEN"), "MALE", "MEN"), "MAN", "MEN");
	attribute_7_style,
	REPLACE(UPPER(attribute_3_size), '~', ','),
	attribute_4_material,
	attribute_8_age,
	currency,
	CASE WHEN availablity = '' OR NULL THEN 'out-of-stock' ELSE availablity END AS availablity,
	begin_date,
	end_date,
	keywords,
	primary_category,
	secondary_category,
	brand
FROM tasks_ranproducts

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
  if new_row["age"] is None:
    new_row["age"] = ""
  new_row["age"] = new_row["age"].upper()

  if row["merchant_id"] == 41558:
    new_row["color"] = ""
    new_row["size"] = ""
  if new_row["age"] != "ADULT" and new_row["age"] != "KIDS":
    new_row["age"] = ""

  return new_row