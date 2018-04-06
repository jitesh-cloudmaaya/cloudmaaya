-- temp file also for the one time migration script but in sql version
-- Exclude/flag as deleted exisitng products and set their corresponding allume category id = 10 (exclude), active/pending = 0



-- list of terms to exclude
-- kid's
-- toddler's
-- baby's
-- boys
-- girls
-- toys
-- kids
-- boy's
-- girl's
-- babies
-- toddlers
-- bed/bath
-- toys
-- food
-- goods
-- electronic
-- beverage
-- home
-- kitchen
-- entertainment
-- electronics
-- barbies
-- foods
-- beverages


-- also the space for this periodic job
-- run a job to set the allume_category_id to Other, active = 1, pending_review = 0 for category_map
-- attached to products whose name LIKE 'swimsuit', 'maternity', or 'lingerie'
SELECT product_name, primary_category, secondary_category FROM product_api_product
WHERE (product_name LIKE '%swimsuit%' AND (primary_category LIKE '%swimsuit%' OR secondary_category LIKE '%swimsuit%'))
OR (product_name LIKE '%maternity%' AND (primary_category LIKE '%maternity%' OR secondary_category LIKE '%maternity%'))
OR (product_name LIKE '%lingerie%' AND (primary_category LIKE '%lingerie%' OR secondary_category LIKE '%lingerie%'));

SELECT distinct primary_category, secondary_category FROM product_api_product
WHERE (product_name LIKE '%swimsuit%' AND (primary_category LIKE '%swimsuit%' OR secondary_category LIKE '%swimsuit%'))
OR (product_name LIKE '%maternity%' AND (primary_category LIKE '%maternity%' OR secondary_category LIKE '%maternity%'))
OR (product_name LIKE '%lingerie%' AND (primary_category LIKE '%lingerie%' OR secondary_category LIKE '%lingerie%'));

SELECT product_name, primary_category, secondary_category FROM product_api_product
WHERE product_name LIKE '%swimsuit%'
OR product_name LIKE '%maternity%'
OR product_name LIKE '%lingerie%';




# STEP 1: get the set of distinct category pairs
SELECT product_name, primary_category, secondary_category FROM product_api_product
WHERE product_name LIKE '%swimsuit%'
OR product_name LIKE '%maternity%'
OR product_name LIKE '%lingerie%';
-- OR product_name LIKE '%etc%';

