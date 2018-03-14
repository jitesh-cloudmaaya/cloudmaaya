# Product Feeds
Initialize a ProductFeed object:
```sh
pf = Productfeed(os.path.join(BASE_DIR, 'catalogue_service/ran_delta.yaml'))
```
If you do not have any data available, extract the files from the FTP server (if necessary):
```sh
pf.get_files_ftp()
```
With the files stored locally, you should be able to call the ProductFeed's data transformation method and subsequently update the Product table:
```sh
pf.clean_data()
pf.load_cleaned_data()
```
It is worth not3ing that the all of the possible underlying clean_data() methods will print out metrics on the result of running the process to the terminal.
```console # change this?
Processed 7925 records
Wrote 21762 records
Discovered 0 unmapped primary and secondary category pairs
Discovered 0 new merchant(s)
Dropped 1349 records due to gender
Dropped 1056 records due to inactive categories
Process takes 5.84974503517 seconds
```
The number of records processed is the number of records read in from the extracted and active data from merchants for that specific ProductFeed configured to a file. The number of written records can be greater than the number of processed records primarily because the occurrence of splitting records based on size will create numerous children records.

The discovery metrics involve reporting the number of new CategoryMap and Merchant objects that were added as a result of processing and transforming the data. These new objects default to inactivity and therefore require manual review and setting to active if their use is desired.

The number of records dropped refers to the amount of records that were read in from the data but no tranformation or writing of the data was attempted for various reasons. One such reason is gender, not processing products that correspond to men, and the other is inactivity of either the product's primary and secondary categories or the allume category that might map to.

They have a range of helper methods, with one method differing according to the network source (e.g. RAN, PepperJam, Impact Radius, CJ, etc.). Getting data from the different networks requires initializing ProductFeed objects pointing to the desired configuration files. Configuration files for a ProductFeed contain all the necessary initialization information to use the ProductFeed methods to get the product data from a network.

A ProductFeed attempts to write a cleaned flat file (such as a .csv) to the temporary file directory pd_temp/{network_name}/cleaned/. Files from the FTP server, if any, are written to the directory pd_temp/{network_name}/. Whether or not these files are removed after every run of the network's ProductFeed is governed by an option in the network's configuration file.

##### Deleted Products Inference
The products table of the database is never supposed to actually delete or remove records. This idea is encapsulated by the is_deleted field. Products deleted from a network's data are simply dropped. Therefore, their status as a deleted product needs to be inferred. This is done by checking the *updated_at* timestamp field of products that should have been updated in the most recent call to a network's data transformation method. If the *updated_at* field does not meet a certain thershold for freshness, then it is inferred to be deleted and set as such in the database.

While this process runs for RAN as well, RAN has an additional understanding for deleted products. This is because RAN data encompasses two kinds of files: full and delta files. Delta files are partial updates to a merchant's product inventory. The information encoded in a delta file for a product includes a modification attribute, which can contain information about whether a product should be set to deleted. Thus, RAN understands the deleting of products through inference as with the other networks but also through the use of delta files.

##### Overview of common transformation performed on data
One common transformation that occurs in the data feeds involves pigeonholing the 'gender' field of extracted data before checking the product gender corresponds to one that is wanted. That is, there are several terms in use in the data for indicating that the gender for a product is for men, such as the word 'male' or 'man', among others. Therefore, the extracted gender of a product goes through several replace transformations in an attempt to reduce all genders indicating that the product is for men. Then, filter based on that reduced criteria when determining whether or not to skip a record.

Another common transformation for the data involves some manipulation of the size. The first, given that the sizes contain characters of variable formatting standards, is to set all the characters of a size to uppercase. Second, the tilde ('~') character is replaced as a delimiter in lieu of the comma (',').

##### Derived Fields
Some fields of a Product are derived from the extracted data, if possible. The *raw_product_url* field is an example of a derived field. The *raw_product_url* field is typically encoded in the *product_url* field and one of the query arguments, depending on the specific network, contains the *raw_product_url*. Furhtermore, a second pass is done on this extracted url to remove additional query parameters of interest.

Another field that is derived in some of the product feeds is *current_price*. If the data contains both a *retail_price* and *shipping_price* field, then the *current_price* field as set as the *shipping_price* field is present and *retail_price* otherwise.

Mapped fields, such as *allume_size*, *allume_category*, and *allume_color* are dervied fields.

##### Discussion on Unicode Sandiwch
All the string data from a product feed is converted to unicode before working with it. Prior to writing the resulting data as a product record in the product feed's flat file, the data is converted to a plain *str* object. The reason for using this stems from some of the intricacies of Python 2's handling of *unicode* objects.

For example, mixing and matching *str* and *unicode* objects in expressions such as concatentation can cause errors. Therefore, one principle behind the transformation part of any product feed is to work with the string data as *unicode* and write it as a *str*.

##### Discussion of CSV dialects (may end up being network specific)
The data transformation process for the RAN network files involves reading in files containing data. There are at least two given CSV dialects for a given data process. The first is for reading, understanding the '|' character as a delimiter for RAN while understanding the tab (\t) character as a delimiter in Impact Radius.

The second dialect is for writing, which has a uniform set of options. This is because the goal of the ProductFeed processes is to transform the data in such a way that it is able to be understood and loaded into the table governing products. In all cases, the writing dialects writes to a cleaned flat file, which understands commas (,) to be the delimiting character, enclosing all fields in double quotes ("), uses a single backslash (\\) as an escape character, and line terminates using the newline (\n).

##### determining activity (are_categories_active, is_merchant_active)
Whether a product will be writtenis partially determined by whether the product in question is determined to be active. Activity is checked by referencing a few things in order of relevance. Initially, the *active* status of a product's merchant is checked. If a given merchant is inactive, all of their products are dropped. Next, a the *active* status of a product's categories (*primary_category*, *secondary_category*, and *allume_category*) are checked. The structure of categories for the product data supports the possibility for a *primary_category* and *secondary_category* pair be active, but have the *allume_category* be inactive. The reverse is also potentially supported. Regardless, if either the product's *primary_category* and *secondary_category* pair or *allume_category* are marked as inactive, then the product will be dropped.

##### Mapping and Translation Processes
All of the product feeds initialize *dict* objects at the beginning of the process to help with pigeonholing various attributes of interest (such as category or size). The way this works generally is that models are defined in Django having a field to map from and a field to map to. For example, there is a model ColorMap, which maps a *merchant color* 'wine' to the *allume color* 'red'.

As part of the data transformation process for the product feeds, if a field has a mapping, its mapping is referenced when determining the actual value to record for a product.

###### Size Mapping
Size mapping is a slightly different approach. There is an attempt to split the size string into its component parts.

It has three mapping objects associated with converting a *merchant_size* to an *allume_size*. It has two size mappings akin to the one used for mapping color, mapping an initial *merchant_size* to an acceptable *allume_size*. The reason for the second mapping is that there is a size mapping for shoes specifically and one for the rest of the categories. The size mapping to use for a given product depends on the product's determined *allume_category*.

An additional part of the size mapping process is the attempt to parse certain size terms present in the size data and expand or translate them to their desired meaning. For example, in a *merchant_size* of '7W', the 'W' component of the size is desired to be understood and expanded to the size term 'Wide', leading to the resulting *allume_size* of '7 Wide'.

###### Merchant, Category, and AllumeCategory Mapping
The merchant mapping is a mapping of a *merchant_id* and whether or not that merchant should be considerd *active*, which is a boolean. Whether or not a merchant is *active* determines whether product data will be updated or written for that merchant. Inactive merchants are skipped, although their data is typically still extracted from the source.

Category mapping and allume category mapping is related. Both are used in conjunction to take a product's provided *primary_category* and *secondary_category* and translate to an *allume_category*.

##### Discussion on splitting on size delimiters
Unfortunately, the data received from merchants is not standardized. One consequence of this fact, for example, is that the format of the *size* field of a product can change in ways that hugely alters the interpretation. That is, one merchant may store *size* as individual sizes and further demarcate product data on this boundary, but another might store *size* as a comma seperated list and have only one such entry for this product. This necessitates the attempted splitting of all size fields on one recognized delimiter.

Therefore, the processing of data for every product contains a final step of checking if the *size* attribute of a product can be interpreted as a delimiter seperated list. If that is the case, the size is split into its distinct parts and a child record is created for each such size. Further, while the children records retain much of the information from their parent, aside from the *product_id* and naturally the *size*, the parent has *is_deleted* set to true in order to hide the governing parent record in the search index.

##### is_deleted
One nuance of the way products are stored in the Product table is that data is only inserted or updated into the table, nothing should ever be deleted. However, it is the case the merchants might indicate that their product is, in fact, deleted. This is encoded by the *is_deleted* field of a product, a boolean. It is used primarily in the search index, where products with *is_deleted* set to True are absent.


# RAN

##### Full and Delta Files

The FTP server governing RAN files contains two kinds of files: delta and full. A given merchant from RAN will have both of these files in existence at a given time, identified by the merchant's merchant id.

Delta files are incremental updates to the products of a merchant. A given delta file intends to only update a subset of the products available to a merchant. As a result, these files tend to be relatively small in size. They contain a field 'modification' which indicate the status of a product such as 'D' for deleted. In the event of other 'modification' values, the corresponding product will be updated in the Product table.

Full files correspond to the total category of products for a merchant. These files are much larger than their delta counterparts. When initializing the product data for a new merchant, the expectation is that their full file is run first. Full files also lack the 'modification' field present in the delta files as there is no rationale to including a deleted product in such a file.

##### Merchant Configuration Files
In the case of RAN, the files from the FTP server do not contain any column information, so the column ordering must be inferred. The documentation present for the RAN data feed notes a set of mandatory and optional fields, their ordering is not strictly enforced.

This quirk about the available data necessitates some way of tracking these idiosyncracies. The current method of doing so is tracking the derived, valid field order in a set of static YAML files. While these include a YAML file for every merchant reasoned to have a non-standard field ordering, the directory housing them also includes a default. During the process, a field ordering configuration file will be used if a corresponding file, which are named after the merchant ids, is found to exist. In its absence, the default configuration file, and consequently filed ordering, is used.

# PepperJam

The information about which merchants belong to which network is typically encoded as information within the file name or as part of the header information for the file. However, the merchant information for Pepperjam is included in a different way because the data from Pepperjam is accessed as an API, rather than files on an FTP server.

##### discussion on open_w_timeout_retry
The fact that the data for Pepperjam products is accessed via a web API presents a potentially tenuous and fragile point of transfer. Because one run of the Pepperjam process actually involves in several hundred calls to the API, a possible failure on one could cripple the ability to upsert the product information for Pepperjam for the day. Therefore, accesses to the API are enclosed in a limited, exponential retry. However, if the amount of retries expires, the access will fail and interrupt the Pepperjam upsert process for that run.

##### discussion on generate_product_id_pepperjam
A key field that is missing from the data received from the Pepperjam API is the *product_id* field. The *product_id* field is used as a component of a unique key on which to perform the upsert process for a network's products. Thus, the missing *product_id* field is deterministically generated from the product's *SKU* and *merchant_id*.

##### localdev vs prod/staging
Because of the fairly strict limit on the API call, there are separate blocks of code that should be used when testing the functionality of the Pepperjam feed vs running the Pepperjam process in order to populate and update the Product table. The default running environment for the Pepperjam process is set to interpret every run as a production or staging environment run, but changing one argument in the configuration file for Pepperjam allows for easy runs of the test environment and data, which puts no strain on the API.

# Impact Radius

##### information from a merchant comes from two files
Unlike the other product feed networks, the product information for a given merchant on Impact Radius is obtained from two files. One has a filename ending in 'GOOGLE_TXT' and the other has a filename ending in 'IR'. The two files should contain an identical number of product records, but the files contain some non-overlapping information for each one.

##### missing fields from ir
Some of the expected data used to construct a product is not available in the information from the Impact Radius data. These fields include *retail_price*, *sale_price*, *discount*, *discount_type*, *style*, *currency*, *keywords*, *secondary_category*, and *merchant_id*. The way most of these missing fields are handled is to leave the value of the field blank in the product record that is written. In the case of *retail_price* and *sale_price*, they are set to the value of *current_price*, a field available in the data. Because *merchant_id* cannot be left blank for several reasons, a helper method is used to generate the *merchant_id* based on the *merchant_name* taken from the filenames.

##### sometimes maybe generate product id?
The *product_id* field occurs, if it does it all, in one of any number of optional fields in the Impact Radius data of the format custom_label_[n], where n is a number from 0 to 4 (e.g. 'custom_label_4'). When constructing the product data, all these optional fields are searched for a value that contains only numbers, with the rationale being that a value that meets these conditions is likely the *product_id*.

In the event that all the known locations for *product_id* are searched and none is found, a helper function is called to deterministically construct a *product_id*. The generated *product_id* is constructed using a combination of the product's *product_name*, *size*, and *merchant_color*.

# CJ
TBD



## Notes on kind of info to jot down
### general notes for every network
- Discussion of the data extracted (e.g. RAN has full and deltas, Pepperjam is an API call)
- Discussion of how deleted products are handled (RAN encodes partially with the modification attribute, other feeds this process is an inference)
- Some discussion of attributes that are roughly the same across all the network processes (use of mappings to aid in translation or unicode encoding/decoding or use of csv library)
- Any transformation of the data as it gets molded to a format for the products table (generally size.replace for size, more specifically things like the way price works in CJ)
- More detail about some of the more involved processes using product_feed_helpers methods
    - are_categories_active and documenting how categories are added, etc.
    - the size splitting occurrences and the creation of deleted parent records and children records
- discussion on general use of configuration fies?
- discussion on missing fields and how that gets handled
- any special rules (such as the configuration files that appear in merchants for RAN because of unenforcable orderings
- merchant discovery?
- Notes on any feed specific helpers (open w/ retry in Pepperjam)

# RAN
High-level Summary of how RAN Works
- Uses the Python CSV library to 
- Uses a mapping/translation proccess to convert things like color size ('burgundy' to 'red' or 'SML' to 'S')
- Has two kinds of files: delta and full
- Has a need for merchant-specific configuration files that dictate the understood ordering of extracted data (because they differ)

### pepperjam
High-level summary of pepperjam
- Pepperjam is an API, which is unlike the other networks (which are FTP servers)
- Current key in use supports 1500 daily requests against the api
    - And a given 'run' of pepperjam is more than 1 call (roughly several hundred?)
- Another thing to note is the fields that are missing
- Discussion on running PepperJam in local vs dev

# impact radius
high-level summary of impact radius
- Important to note is that the salient information from products occur in two files (the IR file and the GOOGLE file)
- Another thing to note is some of the missing fields and what was done about them
- Another thing to note is the special way product_id is found in Impact Radius
- Another thing to note involves handling the generation of the merchhant id


# CJ
high-level summary of CJ
