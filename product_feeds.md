# Product Feeds (in general?)
The ProductFeed object takes in an argument to a configuration file.
Example initialization:
```sh
pf = Productfeed(os.path.join(BASE_DIR, 'catalogue_service/ran_delta.yaml'))
```

They have a range of helper methods, with one method differing according to the network source (e.g. RAN, PepperJam, Impact Radius, CJ, etc.).
## Useful things to make note of about every network
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


##### Discussion on Unicode Sandiwch
Due to reasons I will have to remember/lookup, a lot of the string manipulation that is performed in transforming the data in records gets first. It had to do with some error'ing that would occur when manipulating (namely, concatenating strings?) strings as a bytes (aka str) and unicode objects. Probably be best to find the article again

##### Discussion of CSV dialects (may end up being network specific)
The data transformation process for the RAN network files involves reading in files containing data. There are at least two given CSV dialects for a given data process. The first is for reading, understanding the '|' character as a delimiter for RAN while understanding the tab (\t) character as a delimiter in Impact Radius.

The second dialect is for writing, which has a uniform set of options. This is because the goal of the ProductFeed processes is to transform the data in such a way that it is able to be understood and loaded into the table governing products. In all cases, the writing dialects writes to a cleaned flat file, which understands commas (,) to be the delimiting character, enclosing all fields in double quotes ("), uses a single backslash (\) as an escape character, and line terminates using the newline (\n).

#### Merchant Configuration Files
In the case of RAN, these files do not contain any column information, so the column ordering must be inferred. The documentation present for the RAN data feed notes a set of mandatory and optional fields, their ordering is not strictly enforced.

This quirk about the available data necessitates some way of tracking these idiosyncracies. The current method of doing so is tracking the derived, valid field order in a set of static YAML files. While these include a YAML file for every merchant reasoned to have a non-standard field ordering, the directory housing them also includes a default. During the process, a field ordering configuration file will be used if a corresponding file, which are named after the merchant ids, is found to exist. In its absence, the default configuration file, and consequently filed ordering, is used.


# RAN
High-level Summary of how RAN Works
- Uses the Python CSV library to 
- Uses a mapping/translation proccess to convert things like color size ('burgundy' to 'red' or 'SML' to 'S')
- Has two kinds of files: delta and full
- Has a need for merchant-specific configuration files that dictate the understood ordering of extracted data (because they differ)

# PepperJam
High-level summary of pepperjam
- Pepperjam is an API, which is unlike the other networks (which are FTP servers)
- Current key in use supports 1500 daily requests against the api
    - And a given 'run' of pepperjam is more than 1 call (roughly several hundred?)
- Another thing to note is the fields that are missing



# Impact Radius
high-level summary of impact radius
- Important to note is that the salient information from products occur in two files (the IR file and the GOOGLE file)
- Ano
-
# CJ
TBD
