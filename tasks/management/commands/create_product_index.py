from django.core.management.base import BaseCommand
from shopping_tool.models import LookProduct
from catalogue_service.settings_local import PRODUCT_INDEX, CLIENT
from django.db import connection



from elasticsearch import Elasticsearch






class Command(BaseCommand):
    help = 'Used to do the initial setup of the product index'

    def handle(self, *args, **options):

        es = CLIENT

        if es.indices.exists(PRODUCT_INDEX):
            print("index '%s' exists, skipping..." % (PRODUCT_INDEX))

        else:
            request_body = {
                              "settings": {
                                "analysis": {
                                  "filter": {
                                    "my_synonym_filter": {
                                      "type": "synonym",
                                      "synonyms": [
                                        "pants, trousers, slacks, pant, bottom, britches, bottoms, jeans, denim",
                                        "sheeth, sheath",
                                        "pump, pumps",
                                        "tops, top, shirt, blouse",
                                        "jackets, outerwear, blazers, coats, blazers",
                                        "skirts, skirt",
                                        "dresses, dress",
                                        "shoes, footwear, shoe",
                                        "bag, bags, purse, handbag, satchel, clutch",
                                        "wide leg, flare, flared, wide-leg, wide-legged",
                                        "high waist, high waisted, high rise, high waiste"
                                      ]
                                    }
                                  },
                                  "analyzer": {
                                    "my_synonyms": {
                                      "tokenizer": "standard",
                                      "filter": [
                                        "lowercase",
                                        "my_synonym_filter"
                                      ]
                                    }
                                  }
                                }
                              },
                              "mappings": {
                                "product": {
                                  "properties": {
                                    "@timestamp": {
                                      "type": "date"
                                    },
                                    "@version": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "age": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "allume_category": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "allume_score": {
                                      "type": "long"
                                    },
                                    "availability": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "brand": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "buy_url": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "color": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "currency": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "current_price": {
                                      "type": "float"
                                    },
                                    "discount": {
                                      "type": "long"
                                    },
                                    "discount_type": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "gender": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "id": {
                                      "type": "long"
                                    },
                                    "is_best_seller": {
                                      "type": "boolean"
                                    },
                                    "is_deleted": {
                                      "type": "boolean"
                                    },
                                    "is_trending": {
                                      "type": "boolean"
                                    },
                                    "keywords": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "long_product_description": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "manufacturer_name": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "manufacturer_part_number": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "material": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "merchant_color": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "merchant_id": {
                                      "type": "long"
                                    },
                                    "merchant_name": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "primary_category": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "product_id": {
                                      "type": "long"
                                    },
                                    "product_image_url": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "product_name": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "product_type": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "product_url": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "raw_product_url": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "retail_price": {
                                      "type": "float"
                                    },
                                    "sale_price": {
                                      "type": "float"
                                    },
                                    "secondary_category": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "shipping_price": {
                                      "type": "long"
                                    },
                                    "short_product_description": {
                                      "type": "text",
                                      "analyzer":  "my_synonyms",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "size": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "sku": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "style": {
                                      "type": "text",
                                      "fields": {
                                        "keyword": {
                                          "type": "keyword",
                                          "ignore_above": 256
                                        }
                                      }
                                    },
                                    "updated_at": {
                                      "type": "date"
                                    }
                                  }
                                }
                              }
                            }


            print("creating '%s' index..." % (PRODUCT_INDEX2))
            res = es.indices.create(index = PRODUCT_INDEX2, body = request_body)
            print(" response: '%s'" % (res))