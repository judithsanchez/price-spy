BEGIN TRANSACTION;
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    date TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    last_request_at TEXT,
    is_exhausted INTEGER DEFAULT 0,
    UNIQUE(model, date)
);
INSERT INTO "api_usage" VALUES(1,'gemini-2.5-flash','2026-01-21',14,'2026-01-22T02:41:28.209494+00:00',0);
INSERT INTO "api_usage" VALUES(15,'gemini-2.5-flash','2026-01-22',12,'2026-01-22T13:41:29.693709+00:00',0);
INSERT INTO "api_usage" VALUES(27,'gemini-2.5-flash-lite','2026-01-23',40,'2026-01-24T06:39:26.823230+00:00',0);
INSERT INTO "api_usage" VALUES(67,'gemini-2.5-flash-lite','2026-01-24',9,'2026-01-24T23:20:57.234222+00:00',0);
INSERT INTO "api_usage" VALUES(76,'gemini-2.5-flash-lite','2026-01-25',11,'2026-01-25T23:00:38.839499+00:00',0);
CREATE TABLE brand_sizes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    size TEXT NOT NULL, label TEXT, profile_id INTEGER REFERENCES profiles(id), item_type TEXT,
    UNIQUE(brand, category)
);
INSERT INTO "brand_sizes" VALUES(1,'Levis','Clothing','M',NULL,1,'Overall');
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
, is_size_sensitive BOOLEAN DEFAULT 0);
INSERT INTO "categories" VALUES(1,'Dairy','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(2,'Bakery','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(3,'Beverages','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(4,'Snacks','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(5,'Frozen Foods','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(6,'Canned Goods','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(7,'Pasta & Grains','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(8,'Meat & Poultry','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(9,'Seafood','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(10,'Fruits','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(11,'Vegetables','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(12,'Condiments & Sauces','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(13,'Spices & Seasonings','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(14,'Baking Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(15,'Breakfast Foods','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(16,'Coffee & Tea','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(17,'Delicatessen','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(18,'Health Foods','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(19,'Baby Food','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(20,'Pet Food','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(21,'Cleaning Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(22,'Paper Products','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(23,'Laundry Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(24,'Dishwashing','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(25,'Personal Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(26,'Hair Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(27,'Skincare','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(28,'Oral Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(29,'Shaving & Grooming','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(30,'Cosmetics','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(31,'Feminine Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(32,'First Aid','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(33,'Over-the-Counter Medicine','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(34,'Vitamins & Minerals','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(35,'Baby Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(36,'School Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(37,'Office Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(38,'Electronics','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(39,'Computer Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(40,'Mobile Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(41,'Audio','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(42,'Photography','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(43,'Gaming','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(44,'Kitchen Appliances','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(45,'Small Home Appliances','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(46,'Tools & Hardware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(47,'Painting & Decorating','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(48,'Electrical','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(49,'Plumbing','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(50,'Gardening','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(51,'Outdoor Tools','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(52,'Home Security','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(53,'Automotive','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(54,'Sports Equipment','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(55,'Fitness','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(56,'Camping & Outdoors','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(57,'Toys','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(58,'Board Games','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(59,'Crafts & Hobbies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(60,'Party Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(61,'Gift Wrapping','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(62,'Clothing','2026-01-23 13:30:37',1);
INSERT INTO "categories" VALUES(63,'Underwear & Sleepwear','2026-01-23 13:30:37',1);
INSERT INTO "categories" VALUES(64,'Footwear','2026-01-23 13:30:37',1);
INSERT INTO "categories" VALUES(65,'Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(66,'Jewelry','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(67,'Luggage & Bags','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(68,'Bedding','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(69,'Bath Linens','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(70,'Kitchen Linens','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(71,'Curtains & Blinds','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(72,'Lighting','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(73,'Home Decor','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(74,'Storage & Organization','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(75,'Furniture','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(76,'Cookware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(77,'Dinnerware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(78,'Flatware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(79,'Kitchen Utensils','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(80,'Glassware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(81,'Barware','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(82,'Books - Fiction','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(83,'Books - Non-Fiction','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(84,'Books - Educational','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(85,'Books - Children','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(86,'Magazines & Newspapers','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(87,'Stationery','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(88,'Musical Instruments','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(89,'Professional Equipment','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(90,'Safety Equipment','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(91,'Travel Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(92,'Seasonal Decor','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(93,'Religious & Spiritual Items','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(94,'Wine','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(95,'Beer','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(96,'Spirits','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(97,'Alcohol-Free Alternatives','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(98,'Organic Foods','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(99,'Gluten-Free Products','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(100,'Vegan & Plant-Based','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(101,'International Foods - Asian','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(102,'International Foods - Mexican','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(103,'International Foods - Mediterranean','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(104,'Fresh Herbs','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(105,'Cooking Oils','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(106,'Vinegar','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(107,'Honey & Syrups','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(108,'Spreads','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(109,'Prepared Meals','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(110,'Deli Meats','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(111,'Artisanal Cheeses','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(112,'Smoked Fish','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(113,'Tofu & Meat Substitutes','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(114,'Special Diets','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(115,'Nuts & Dried Fruits','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(116,'Seeds','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(117,'Sweets & Confectionery','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(118,'Gum & Mints','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(119,'Dessert Toppings','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(120,'Water Softening Salts','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(121,'Pest Control','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(122,'Pool Maintenance','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(123,'Bicycle Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(124,'Pet Accessories','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(125,'Fish Tank Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(126,'Small Animal Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(127,'Terrarium Supplies','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(128,'Collectibles','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(129,'Antiques','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(130,'Fine Art','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(131,'Photography Equipment','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(132,'Video Projectors & Screens','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(133,'Smart Home Devices','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(134,'Wearable Tech','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(135,'Drones & RC Vehicles','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(136,'Home Office Furniture','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(137,'Space Heaters & Fans','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(138,'Air Purifiers & Humidifiers','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(139,'Water Filtration','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(140,'Fitness Large Equipment','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(141,'Yoga & Pilates','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(142,'Swimming Gear','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(143,'Team Sports','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(144,'Exercise Monitors','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(145,'Protective Gear','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(146,'Foot Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(147,'Eye Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(148,'Hearing Care','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(149,'Massage & Relaxation','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(150,'Aromatherapy & Essential Oils','2026-01-23 13:30:37',0);
INSERT INTO "categories" VALUES(151,'Health','2026-01-24 05:37:28',0);
INSERT INTO "categories" VALUES(152,'Fragrance','2026-01-24 22:24:34',0);
INSERT INTO "categories" VALUES(156,'Smart home devices','2026-01-26 15:18:32',0);
INSERT INTO "categories" VALUES(157,'Pet food','2026-01-26 15:18:32',0);
INSERT INTO "categories" VALUES(158,'Personal care','2026-01-26 15:18:32',0);
INSERT INTO "categories" VALUES(159,'Hair care','2026-01-26 15:18:32',0);
INSERT INTO "categories" VALUES(160,'Health foods','2026-01-26 15:18:32',0);
INSERT INTO "categories" VALUES(161,'Home decor','2026-01-26 15:18:32',0);
CREATE TABLE error_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    url TEXT,
    screenshot_path TEXT,
    stack_trace TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "error_log" VALUES(1,'extraction_error','Gemini API error 400: {
  "error": {
    "code": 400,
    "message": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[7].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[8].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[9].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[10].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[11].value'': Proto field is not repeating, cannot start list.",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "generation_config.response_schema.properties[7].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[7].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[8].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[8].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[9].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[9].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[1','https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290',NULL,'Traceback (most recent call last):
  File "/home/judithvsanchezc/Desktop/dev/price-spy/spy.py", line 69, in cmd_extract
    result, model_used = await extract_with_structured_output(screenshot, api_key, preferred_model=preferred_model)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 284, in extract_with_structured_output
    result = await _call_gemini_api(image_bytes, api_key, config)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 214, in _call_gemini_api
    raise Exception(f"Gemini API error {response.status}: {error_text}")
Exception: Gemini API error 400: {
  "error": {
    "code": 400,
    "message": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[7].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[8].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[9].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[10].value'': Proto field is not repeating, cannot start list.\nInvalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[11].value'': Proto field is not repeating, cannot start list.",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "generation_config.response_schema.properties[7].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[7].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[8].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[8].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[9].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[9].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[10].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[10].value'': Proto field is not repeating, cannot start list."
          },
          {
            "field": "generation_config.response_schema.properties[11].value",
            "description": "Invalid JSON payload received. Unknown name \"type\" at ''generation_config.response_schema.properties[11].value'': Proto field is not repeating, cannot start list."
          }
        ]
      }
    ]
  }
}','2026-01-24 06:30:09');
INSERT INTO "error_log" VALUES(2,'extraction_error','1 validation error for ExtractionResult
store_name
  String should have at most 500 characters [type=string_too_long, input_value="Kruidvat'', ''value_pack'':...10 stuks''.```jsonjson{ ", input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290',NULL,'Traceback (most recent call last):
  File "/home/judithvsanchezc/Desktop/dev/price-spy/spy.py", line 69, in cmd_extract
    result, model_used = await extract_with_structured_output(screenshot, api_key, preferred_model=preferred_model)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 284, in extract_with_structured_output
    result = await _call_gemini_api(image_bytes, api_key, config)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 219, in _call_gemini_api
    result = ExtractionResult.model_validate_json(text)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/venv/lib/python3.11/site-packages/pydantic/main.py", line 766, in model_validate_json
    return cls.__pydantic_validator__.validate_json(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for ExtractionResult
store_name
  String should have at most 500 characters [type=string_too_long, input_value="Kruidvat'', ''value_pack'':...10 stuks''.```jsonjson{ ", input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','2026-01-24 06:31:46');
INSERT INTO "error_log" VALUES(3,'extraction_error','1 validation error for ExtractionResult
store_name
  String should have at most 500 characters [type=string_too_long, input_value=''Kruidvat club en thuiswi...ft aan dat het product '', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290',NULL,'Traceback (most recent call last):
  File "/home/judithvsanchezc/Desktop/dev/price-spy/spy.py", line 69, in cmd_extract
    result, model_used = await extract_with_structured_output(screenshot, api_key, preferred_model=preferred_model)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 295, in extract_with_structured_output
    result = await _call_gemini_api(image_bytes, api_key, config)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 230, in _call_gemini_api
    result = ExtractionResult.model_validate_json(json_text)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/venv/lib/python3.11/site-packages/pydantic/main.py", line 766, in model_validate_json
    return cls.__pydantic_validator__.validate_json(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for ExtractionResult
store_name
  String should have at most 500 characters [type=string_too_long, input_value=''Kruidvat club en thuiswi...ft aan dat het product '', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','2026-01-24 06:33:28');
INSERT INTO "error_log" VALUES(4,'extraction_error','1 validation error for ExtractionResult
store_name
  String should have at most 1000 characters [type=string_too_long, input_value="Kruidvat, thuiswinkel wa...Actie'' label. Er staat ", input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290',NULL,'Traceback (most recent call last):
  File "/home/judithvsanchezc/Desktop/dev/price-spy/spy.py", line 69, in cmd_extract
    result, model_used = await extract_with_structured_output(screenshot, api_key, preferred_model=preferred_model)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 295, in extract_with_structured_output
    result = await _call_gemini_api(image_bytes, api_key, config)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/app/core/vision.py", line 230, in _call_gemini_api
    result = ExtractionResult.model_validate_json(json_text)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/judithvsanchezc/Desktop/dev/price-spy/venv/lib/python3.11/site-packages/pydantic/main.py", line 766, in model_validate_json
    return cls.__pydantic_validator__.validate_json(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for ExtractionResult
store_name
  String should have at most 1000 characters [type=string_too_long, input_value="Kruidvat, thuiswinkel wa...Actie'' label. Er staat ", input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_too_long','2026-01-24 06:34:27');
CREATE TABLE extraction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracked_item_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('success', 'error')) NOT NULL,
    model_used TEXT,
    price REAL,
    currency TEXT,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);
INSERT INTO "extraction_logs" VALUES(1,1,'success','gemini-2.5-flash',11.29,'EUR',NULL,10821,'2026-01-21 13:08:09');
INSERT INTO "extraction_logs" VALUES(2,2,'success','gemini-2.5-flash',70.99,'EUR',NULL,8865,'2026-01-21 13:19:11');
INSERT INTO "extraction_logs" VALUES(3,3,'success','gemini-2.5-flash',14.99,'EUR',NULL,11285,'2026-01-21 13:26:31');
INSERT INTO "extraction_logs" VALUES(4,4,'success','gemini-2.5-flash',29.99,'EUR',NULL,8483,'2026-01-21 13:33:33');
INSERT INTO "extraction_logs" VALUES(5,5,'success','gemini-2.5-flash',1.9,'EUR',NULL,26901,'2026-01-21 13:34:15');
INSERT INTO "extraction_logs" VALUES(6,5,'error',NULL,NULL,NULL,'1 validation error for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than',20212,'2026-01-21 13:36:24');
INSERT INTO "extraction_logs" VALUES(7,5,'success','gemini-2.5-flash',52.99,'EUR',NULL,10735,'2026-01-22 00:42:27');
INSERT INTO "extraction_logs" VALUES(8,6,'error',NULL,NULL,NULL,'2 validation errors for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value='''', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',10195,'2026-01-22 00:46:13');
INSERT INTO "extraction_logs" VALUES(9,6,'success','gemini-2.5-flash',24.99,'EUR',NULL,12115,'2026-01-22 00:47:10');
INSERT INTO "extraction_logs" VALUES(10,7,'success','gemini-2.5-flash',21.93,'EUR',NULL,10496,'2026-01-22 00:48:55');
INSERT INTO "extraction_logs" VALUES(11,8,'error',NULL,NULL,NULL,'2 validation errors for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=-1, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value=''N/A'', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',13938,'2026-01-22 00:57:45');
INSERT INTO "extraction_logs" VALUES(12,8,'error',NULL,NULL,NULL,'1 validation error for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than',10203,'2026-01-22 01:00:02');
INSERT INTO "extraction_logs" VALUES(13,8,'error',NULL,NULL,NULL,'1 validation error for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than',16103,'2026-01-22 01:24:21');
INSERT INTO "extraction_logs" VALUES(14,9,'error',NULL,NULL,NULL,'1 validation error for ExtractionResult
price
  Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than',9554,'2026-01-22 01:27:29');
INSERT INTO "extraction_logs" VALUES(15,8,'success','gemini-2.5-flash',45.99,'EUR',NULL,10785,'2026-01-22 01:28:08');
INSERT INTO "extraction_logs" VALUES(16,9,'success','gemini-2.5-flash',49.8,'EUR',NULL,15143,'2026-01-22 01:36:38');
INSERT INTO "extraction_logs" VALUES(17,5,'error','gemini-2.5-flash',NULL,NULL,'2 validation errors for ExtractionLog
price
  Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value=''N/A'', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',12635,'2026-01-22 01:37:12');
INSERT INTO "extraction_logs" VALUES(18,5,'success','gemini-2.5-flash',52.99,'EUR',NULL,16204,'2026-01-22 01:39:57');
INSERT INTO "extraction_logs" VALUES(19,9,'success','gemini-2.5-flash',49.8,'EUR',NULL,15821,'2026-01-22 01:40:23');
INSERT INTO "extraction_logs" VALUES(20,10,'success','gemini-2.5-flash',699.0,'EUR',NULL,8221,'2026-01-22 02:41:28');
INSERT INTO "extraction_logs" VALUES(21,12,'error','gemini-2.5-flash',NULL,NULL,'2 validation errors for ExtractionLog
price
  Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value=''N/A'', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',13069,'2026-01-22 12:47:13');
INSERT INTO "extraction_logs" VALUES(22,11,'error','gemini-2.5-flash',NULL,NULL,'2 validation errors for ExtractionLog
price
  Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value=''N/A'', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',13808,'2026-01-22 12:47:14');
INSERT INTO "extraction_logs" VALUES(23,4,'success','gemini-2.5-flash',29.99,'EUR',NULL,18788,'2026-01-22 12:47:19');
INSERT INTO "extraction_logs" VALUES(24,16,'success','gemini-2.5-flash',7.61,'EUR',NULL,31816,'2026-01-22 12:47:32');
INSERT INTO "extraction_logs" VALUES(25,13,'success','gemini-2.5-flash',18.99,'EUR',NULL,32533,'2026-01-22 12:47:32');
INSERT INTO "extraction_logs" VALUES(26,14,'success','gemini-2.5-flash',14.35,'EUR',NULL,33618,'2026-01-22 12:47:33');
INSERT INTO "extraction_logs" VALUES(27,2,'success','gemini-2.5-flash',70.99,'EUR',NULL,35746,'2026-01-22 12:47:36');
INSERT INTO "extraction_logs" VALUES(28,15,'success','gemini-2.5-flash',10.64,'EUR',NULL,35797,'2026-01-22 12:47:36');
INSERT INTO "extraction_logs" VALUES(29,3,'success','gemini-2.5-flash',14.99,'EUR',NULL,36465,'2026-01-22 12:47:36');
INSERT INTO "extraction_logs" VALUES(30,1,'success','gemini-2.5-flash',11.29,'EUR',NULL,37293,'2026-01-22 12:47:37');
INSERT INTO "extraction_logs" VALUES(31,11,'success','gemini-2.5-flash',15.99,'EUR',NULL,10719,'2026-01-22 13:41:10');
INSERT INTO "extraction_logs" VALUES(32,12,'success','gemini-2.5-flash',25.08,'EUR',NULL,10597,'2026-01-22 13:41:29');
INSERT INTO "extraction_logs" VALUES(33,5,'success','gemini-2.5-flash-lite',52.99,'EUR',NULL,23476,'2026-01-23 23:00:23');
INSERT INTO "extraction_logs" VALUES(34,6,'success','gemini-2.5-flash-lite',21.99,'EUR',NULL,26060,'2026-01-23 23:00:26');
INSERT INTO "extraction_logs" VALUES(35,10,'success','gemini-2.5-flash-lite',699.0,'EUR',NULL,26162,'2026-01-23 23:00:26');
INSERT INTO "extraction_logs" VALUES(36,9,'success','gemini-2.5-flash-lite',49.99,'EUR',NULL,27644,'2026-01-23 23:00:27');
INSERT INTO "extraction_logs" VALUES(37,1,'success','gemini-2.5-flash-lite',11.29,'EUR',NULL,34748,'2026-01-23 23:00:35');
INSERT INTO "extraction_logs" VALUES(38,7,'success','gemini-2.5-flash-lite',21.99,'EUR',NULL,36711,'2026-01-23 23:00:36');
INSERT INTO "extraction_logs" VALUES(39,3,'success','gemini-2.5-flash-lite',14.99,'EUR',NULL,39863,'2026-01-23 23:00:40');
INSERT INTO "extraction_logs" VALUES(40,4,'success','gemini-2.5-flash-lite',29.99,'EUR',NULL,42335,'2026-01-23 23:00:42');
INSERT INTO "extraction_logs" VALUES(41,12,'success','gemini-2.5-flash-lite',25.08,'EUR',NULL,23658,'2026-01-23 23:00:50');
INSERT INTO "extraction_logs" VALUES(42,13,'success','gemini-2.5-flash-lite',19.99,'EUR',NULL,27994,'2026-01-23 23:00:54');
INSERT INTO "extraction_logs" VALUES(43,14,'success','gemini-2.5-flash-lite',14.35,'EUR',NULL,32774,'2026-01-23 23:01:00');
INSERT INTO "extraction_logs" VALUES(44,16,'success','gemini-2.5-flash-lite',7.47,'EUR',NULL,26985,'2026-01-23 23:01:04');
INSERT INTO "extraction_logs" VALUES(45,18,'success','gemini-2.5-flash-lite',6.89,'EUR',NULL,25001,'2026-01-23 23:01:07');
INSERT INTO "extraction_logs" VALUES(46,11,'success','gemini-2.5-flash-lite',15.99,'EUR',NULL,44766,'2026-01-23 23:01:08');
INSERT INTO "extraction_logs" VALUES(47,19,'success','gemini-2.5-flash-lite',45.99,'EUR',NULL,21500,'2026-01-23 23:01:11');
INSERT INTO "extraction_logs" VALUES(48,20,'success','gemini-2.5-flash-lite',5.39,'EUR',NULL,17826,'2026-01-23 23:01:12');
INSERT INTO "extraction_logs" VALUES(49,8,'error',NULL,NULL,NULL,'',77942,'2026-01-23 23:01:18');
INSERT INTO "extraction_logs" VALUES(50,2,'error',NULL,NULL,NULL,'',94944,'2026-01-23 23:01:35');
INSERT INTO "extraction_logs" VALUES(51,15,'error',NULL,NULL,NULL,'',86126,'2026-01-23 23:02:01');
INSERT INTO "extraction_logs" VALUES(52,17,'error',NULL,NULL,NULL,'',93025,'2026-01-23 23:02:13');
INSERT INTO "extraction_logs" VALUES(53,17,'success','gemini-2.5-flash-lite',6.99,'EUR',NULL,14308,'2026-01-24 00:51:03');
INSERT INTO "extraction_logs" VALUES(54,5,'success','gemini-2.5-flash-lite',52.99,'EUR',NULL,15080,'2026-01-24 00:55:30');
INSERT INTO "extraction_logs" VALUES(55,10,'success','gemini-2.5-flash-lite',699.0,'EUR',NULL,17169,'2026-01-24 00:55:32');
INSERT INTO "extraction_logs" VALUES(56,6,'success','gemini-2.5-flash-lite',21.99,'EUR',NULL,20963,'2026-01-24 00:55:36');
INSERT INTO "extraction_logs" VALUES(57,8,'success','gemini-2.5-flash-lite',46.99,'EUR',NULL,27294,'2026-01-24 00:55:43');
INSERT INTO "extraction_logs" VALUES(58,4,'success','gemini-2.5-flash-lite',29.99,'EUR',NULL,35686,'2026-01-24 00:55:51');
INSERT INTO "extraction_logs" VALUES(59,1,'success','gemini-2.5-flash-lite',11.29,'EUR',NULL,38450,'2026-01-24 00:55:54');
INSERT INTO "extraction_logs" VALUES(60,7,'success','gemini-2.5-flash-lite',21.99,'EUR',NULL,39887,'2026-01-24 00:55:55');
INSERT INTO "extraction_logs" VALUES(61,12,'success','gemini-2.5-flash-lite',25.08,'EUR',NULL,23348,'2026-01-24 00:55:56');
INSERT INTO "extraction_logs" VALUES(62,2,'success','gemini-2.5-flash-lite',70.99,'EUR',NULL,43414,'2026-01-24 00:55:59');
INSERT INTO "extraction_logs" VALUES(63,13,'success','gemini-2.5-flash-lite',19.99,'EUR',NULL,31173,'2026-01-24 00:56:07');
INSERT INTO "extraction_logs" VALUES(64,14,'success','gemini-2.5-flash-lite',14.34,'EUR',NULL,34504,'2026-01-24 00:56:17');
INSERT INTO "extraction_logs" VALUES(65,16,'success','gemini-2.5-flash-lite',7.48,'EUR',NULL,26285,'2026-01-24 00:56:20');
INSERT INTO "extraction_logs" VALUES(66,15,'success','gemini-2.5-flash-lite',10.64,'EUR',NULL,29871,'2026-01-24 00:56:21');
INSERT INTO "extraction_logs" VALUES(67,19,'success','gemini-2.5-flash-lite',45.99,'EUR',NULL,25839,'2026-01-24 00:56:22');
INSERT INTO "extraction_logs" VALUES(68,20,'success','gemini-2.5-flash-lite',5.39,'EUR',NULL,23287,'2026-01-24 00:56:22');
INSERT INTO "extraction_logs" VALUES(69,11,'success','gemini-2.5-flash-lite',15.99,'EUR',NULL,52280,'2026-01-24 00:56:23');
INSERT INTO "extraction_logs" VALUES(70,18,'success','gemini-2.5-flash-lite',6.89,'EUR',NULL,27633,'2026-01-24 00:56:23');
INSERT INTO "extraction_logs" VALUES(71,9,'error',NULL,NULL,NULL,'',78443,'2026-01-24 00:56:34');
INSERT INTO "extraction_logs" VALUES(72,3,'error',NULL,NULL,NULL,'',100434,'2026-01-24 00:56:56');
INSERT INTO "extraction_logs" VALUES(73,20,'error',NULL,NULL,NULL,'[Errno 13] Permission denied: ''screenshots/20.png''',6929,'2026-01-24 05:19:06');
INSERT INTO "extraction_logs" VALUES(74,20,'success','gemini-2.5-flash-lite',5.39,'EUR',NULL,9506,'2026-01-24 05:21:36');
INSERT INTO "extraction_logs" VALUES(75,18,'success','gemini-2.5-flash-lite',6.89,'EUR',NULL,7603,'2026-01-24 05:46:17');
INSERT INTO "extraction_logs" VALUES(76,17,'success','gemini-2.5-flash-lite',6.99,'EUR',NULL,13310,'2026-01-24 05:47:00');
INSERT INTO "extraction_logs" VALUES(77,19,'success','gemini-2.5-flash-lite',45.99,'EUR',NULL,9124,'2026-01-24 05:47:27');
INSERT INTO "extraction_logs" VALUES(78,21,'error','gemini-2.5-flash-lite',NULL,NULL,'2 validation errors for ExtractionLog
price
  Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/greater_than
currency
  String should match pattern ''^[A-Z]{3}$'' [type=string_pattern_mismatch, input_value=''N/A'', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/string_pattern_mismatch',6406,'2026-01-24 06:36:16');
INSERT INTO "extraction_logs" VALUES(79,21,'success','gemini-2.5-flash-lite',7.49,'EUR',NULL,15997,'2026-01-24 06:39:26');
INSERT INTO "extraction_logs" VALUES(80,22,'success','gemini-2.5-flash-lite',28.99,'EUR',NULL,13368,'2026-01-24 14:52:20');
INSERT INTO "extraction_logs" VALUES(81,19,'error',NULL,NULL,NULL,'',67463,'2026-01-24 16:06:57');
INSERT INTO "extraction_logs" VALUES(82,19,'success','gemini-2.5-flash-lite',45.99,'EUR',NULL,8040,'2026-01-24 21:32:47');
INSERT INTO "extraction_logs" VALUES(83,23,'success','gemini-2.5-flash-lite',15.99,'EUR',NULL,10366,'2026-01-24 22:25:17');
INSERT INTO "extraction_logs" VALUES(84,24,'success','gemini-2.5-flash-lite',19.99,'EUR',NULL,12414,'2026-01-24 23:12:32');
INSERT INTO "extraction_logs" VALUES(85,25,'success','gemini-2.5-flash-lite',29.5,'EUR',NULL,12785,'2026-01-24 23:13:06');
INSERT INTO "extraction_logs" VALUES(86,26,'error',NULL,NULL,NULL,'',68653,'2026-01-24 23:14:29');
INSERT INTO "extraction_logs" VALUES(87,27,'success','gemini-2.5-flash-lite',29.99,'EUR',NULL,9078,'2026-01-24 23:15:04');
INSERT INTO "extraction_logs" VALUES(88,28,'success','gemini-2.5-flash-lite',47.0,'EUR',NULL,9467,'2026-01-24 23:15:33');
INSERT INTO "extraction_logs" VALUES(89,29,'success','gemini-2.5-flash-lite',112.2,'EUR',NULL,10373,'2026-01-24 23:15:56');
INSERT INTO "extraction_logs" VALUES(90,25,'success','gemini-2.5-flash-lite',29.5,'EUR',NULL,13237,'2026-01-24 23:20:57');
INSERT INTO "extraction_logs" VALUES(91,30,'success','gemini-2.5-flash-lite',29.99,'EUR',NULL,10193,'2026-01-25 15:11:38');
INSERT INTO "extraction_logs" VALUES(92,31,'success','gemini-2.5-flash-lite',52.99,'EUR',NULL,9178,'2026-01-25 15:13:30');
INSERT INTO "extraction_logs" VALUES(93,32,'success','gemini-2.5-flash-lite',50.0,'EUR',NULL,9458,'2026-01-25 15:26:06');
INSERT INTO "extraction_logs" VALUES(94,35,'error',NULL,NULL,NULL,'',68624,'2026-01-25 17:17:16');
INSERT INTO "extraction_logs" VALUES(95,37,'success','gemini-2.5-flash-lite',16.65,'EUR',NULL,14036,'2026-01-25 17:18:30');
INSERT INTO "extraction_logs" VALUES(96,34,'success','gemini-2.5-flash-lite',13.99,'EUR',NULL,9413,'2026-01-25 17:19:01');
INSERT INTO "extraction_logs" VALUES(97,36,'error',NULL,NULL,NULL,'',72100,'2026-01-25 17:43:31');
INSERT INTO "extraction_logs" VALUES(98,36,'success','gemini-2.5-flash-lite',28.95,'EUR',NULL,13732,'2026-01-25 17:44:19');
INSERT INTO "extraction_logs" VALUES(99,33,'success','gemini-2.5-flash-lite',12.99,'EUR',NULL,11927,'2026-01-25 17:45:34');
INSERT INTO "extraction_logs" VALUES(100,38,'error',NULL,NULL,NULL,'',69299,'2026-01-25 17:47:15');
INSERT INTO "extraction_logs" VALUES(101,39,'success','gemini-2.5-flash-lite',49.99,'EUR',NULL,11381,'2026-01-25 17:57:55');
INSERT INTO "extraction_logs" VALUES(102,26,'success','gemini-2.5-flash-lite',25.08,'EUR',NULL,30043,'2026-01-25 23:00:30');
INSERT INTO "extraction_logs" VALUES(103,40,'error',NULL,NULL,NULL,'1 validation error for ExtractionResult
available_sizes
  Input should be a valid array [type=list_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.12/v/list_type',36041,'2026-01-25 23:00:36');
INSERT INTO "extraction_logs" VALUES(104,38,'success','gemini-2.5-flash-lite',23.16,'EUR',NULL,38490,'2026-01-25 23:00:38');
INSERT INTO "extraction_logs" VALUES(105,23,'success','gemini-2.5-flash-lite',15.99,'EUR',NULL,38606,'2026-01-25 23:00:38');
INSERT INTO "extraction_logs" VALUES(106,35,'error',NULL,NULL,NULL,'',81945,'2026-01-25 23:01:22');
INSERT INTO "extraction_logs" VALUES(107,24,'error',NULL,NULL,NULL,'',86945,'2026-01-25 23:01:27');
INSERT INTO "extraction_logs" VALUES(108,25,'error',NULL,NULL,NULL,'',93944,'2026-01-25 23:01:34');
INSERT INTO "extraction_logs" VALUES(109,22,'error',NULL,NULL,NULL,'',97945,'2026-01-25 23:01:38');
CREATE TABLE labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "labels" VALUES(1,'Eco-friendly','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(2,'Sustainable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(3,'Recyclable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(4,'Biodegradable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(5,'Plastic-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(6,'Compostable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(7,'Zero-waste','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(8,'Carbon-neutral','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(9,'Ethically-sourced','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(10,'Fair-trade','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(11,'Cruelty-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(12,'Vegan','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(13,'Plant-based','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(14,'Organic','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(15,'Non-GMO','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(16,'Pesticide-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(17,'BPA-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(18,'Reusable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(19,'Refillable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(20,'Upcycled','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(21,'Local','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(22,'Handmade','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(23,'Artisanal','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(24,'B-Corp','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(25,'Rainforest-Alliance','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(26,'FSC-certified','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(27,'Animal-welfare','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(28,'Forest-friendly','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(29,'Oceans-safe','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(30,'Low-impact','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(31,'Gluten-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(32,'Dairy-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(33,'Nut-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(34,'Sugar-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(35,'Low-carb','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(36,'Keto','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(37,'Paleo','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(38,'Kosher','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(39,'Halal','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(40,'High-protein','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(41,'Low-sodium','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(42,'High-fiber','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(43,'No-additives','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(44,'No-preservatives','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(45,'Naturally-flavored','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(46,'Raw','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(47,'Sprouted','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(48,'Whole-grain','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(49,'Ancient-grains','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(50,'Soy-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(51,'Egg-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(52,'Shellfish-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(53,'Lactose-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(54,'Low-fat','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(55,'No-cholesterol','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(56,'Cold-pressed','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(57,'Wild-caught','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(58,'Grass-fed','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(59,'Free-range','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(60,'Pasture-raised','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(61,'Energy-star','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(62,'Wifi-enabled','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(63,'Bluetooth','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(64,'Smart','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(65,'Rechargeable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(66,'Wireless','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(67,'Compact','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(68,'High-speed','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(69,'4K-Ready','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(70,'HDR','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(71,'Waterproof','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(72,'Shockproof','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(73,'Dustproof','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(74,'Anti-glare','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(75,'Ergonomic','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(76,'Quick-charge','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(77,'Noise-cancelling','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(78,'Studio-grade','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(79,'Heavy-duty','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(80,'USB-C','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(81,'Thunderbolt','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(82,'OLED','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(83,'LED','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(84,'Long-battery-life','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(85,'Portable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(86,'Hypoallergenic','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(87,'Antibacterial','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(88,'Non-toxic','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(89,'Fragrance-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(90,'Odor-neutralizing','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(91,'Machine-washable','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(92,'Stain-resistant','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(93,'Wrinkle-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(94,'Flame-retardant','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(95,'Hand-wash-only','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(96,'Solid-wood','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(97,'Modular','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(98,'Space-saving','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(99,'Easy-assembly','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(100,'Child-safe','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(101,'Pet-safe','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(102,'Indoor-only','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(103,'Outdoor-use','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(104,'Weather-resistant','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(105,'Lightweight','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(106,'Premium','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(107,'Luxury','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(108,'Designer','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(109,'Limited-edition','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(110,'Bestseller','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(111,'Dermatologist-tested','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(112,'Paraben-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(113,'Sulfate-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(114,'Alcohol-free','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(115,'PH-balanced','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(116,'Anti-aging','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(117,'Moisturizing','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(118,'Sensitive-skin','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(119,'Natural-ingredients','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(120,'Essentials','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(121,'Travel-size','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(122,'Value-pack','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(123,'Refill','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(124,'Sample','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(125,'New-formula','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(126,'Fast-absorbing','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(127,'Long-lasting','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(128,'Water-resistant','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(129,'SPF-protection','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(130,'Professional-use','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(131,'Buy-1-Get-1','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(132,'Discounted','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(133,'On-sale','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(134,'New-arrival','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(135,'Trending','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(136,'Gift-idea','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(137,'Must-have','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(138,'Highly-rated','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(139,'Verified','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(140,'Authentic','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(141,'Exclusive','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(142,'Member-only','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(143,'Early-access','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(144,'Bulk-buy','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(145,'Stock-clearance','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(146,'Back-in-stock','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(147,'Seasonal','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(148,'Holiday-special','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(149,'Limited-stock','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(150,'Fan-favorite','2026-01-23 22:50:36');
INSERT INTO "labels" VALUES(151,'supplement','2026-01-24 14:40:46');
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    confidence REAL NOT NULL,
    url TEXT NOT NULL,
    store_name TEXT,
    page_type TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
, is_available INTEGER DEFAULT 1, notes TEXT, item_id INTEGER, original_price REAL, deal_type TEXT, deal_description TEXT, discount_percentage REAL, discount_fixed_amount REAL, available_sizes TEXT);
INSERT INTO "price_history" VALUES(1,'LEGO Botanicals Daisies - Artificial Flowers Bouquet with Daisies and Lavender - DIY Kit for Children for Nursery Decoration - Gift for Girls from 9 Years and Flower Lovers - 11508',11.29,'EUR',1.0,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/?_encoding=UTF8&pd_rd_w=1TaUy&content-id=amzn1.sym.0bd8095e-79f9-45c2-8e70-ee4034022f47:amzn1.symc.752cde0b-d2ce-4cce-9121-769ea438869e&pf_rd_p=0bd8095e-79f9-45c2-8e70-ee4034022f47&pf_rd_r=PA1HNHX1S7PQ1T7VHZPT&pd_rd_wg=6nYVk&pd_rd_r=471d265b-c2e8-49a4-a760-b6fb589b9605&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d','Amazon',NULL,'2026-01-21 13:08:09',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(2,'BTF-LIGHTING FCOB COB RGBCTT Flexible High Density RGB+Warm White+Cool White LED Strip 5M 960LED/M 4800LEDs DC24V 18W/M IP30 Non Waterproof Multicolor for DIY Home Decoration [Energy Class G]',70.99,'EUR',1.0,'https://www.amazon.nl/-/en/BTF-LIGHTING-Flexible-Waterproof-Multicolor-Decoration/dp/B0C3VMV5BP/ref=sr_1_2?crid=4G3PBKIR5ZSJ&dib=eyJ2IjoiMSJ9.40v-SQ54YW-SRJAeIw05m-Hg85YqppMxyUpL1b7Iwsj1H3TtE3Onti_S72Q9luoJ0fNQ4RaiRDbMS28tVM2Kz23BxtxX23SxDRlEa9wK0fARqowRI1lSanbPvHpg2ZsHwx0DFQojXS0BKNRWmkHjk4kCWeCW4mXKwCDPDrAt-KPncb04JogkbA1drNYSYOV4OBL2Z05zTtUOqq-xgF-7LENH50XkBcNq-VYcgbeNWC96ipNmsW0yidnQqCe-mZ5MCTXuPmyTFbdjp-DFNla1_1GS-2tFEf5O4nt9poCYuB8.W9jULAY2bcROfjUbMnwy9YcMvc8Xh9Vtnj_NuAbMHX0&dib_tag=se&keywords=BTF-LIGHTING%2BFCOB%2BRGBCCT%2B(24V%2C%2B960LED%2Fm)&qid=1769001366&sprefix=btf-lighting%2Bfcob%2Brgbcct%2B24v%2B960led%2Fm%2B%2Caps%2C229&sr=8-2&th=1','Amazon',NULL,'2026-01-21 13:19:11',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(3,'Arotelicht 24V 3A AC/DC-voeding Euro-stekkeradapter voor 3528/5050 COB LED-strip 72W maximale voeding, AC100-240V voedingsadapter',14.99,'EUR',1.0,'https://www.amazon.nl/dp/B09Y5RHJJ7/ref=sspa_dk_detail_3?pd_rd_i=B09Y5RHJJ7&pd_rd_w=RW6Ex&content-id=amzn1.sym.2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_p=2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_r=MNW2N8WHZXA9EWRSWRPQ&pd_rd_wg=tpEcw&pd_rd_r=24f37adc-9301-4644-88c0-95783e071f69&aref=iGaUDsXvlQ&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1','Amazon',NULL,'2026-01-21 13:26:31',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(4,'ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGB RGBW',29.99,'EUR',1.0,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=CQFNCJCCHHHX&dib=eyJ2IjoiMSJ9.5HMR8hr5boBzpMdf91yhRbDW_bmzSr1uzrlhuXzGs_67jfTFxhDdKihAQXq0_bvvkVZ2BceyDfdsvIdgvlmcyWPOVSI_NByiJOodDN97k-4sFUjn2QYyL0uX0zmZSIGIwpktVHYz8ZGgUH5dookZKpAHH6F8UknMUpu7XW_mrOSuOVHsnEHlYYIhitA_pdx14GW2DiR7vIeCamXhLPk6WV9HbFW7g-OGx4PEFABzdlb3ZMnHGanVaAJ-pfex5iRo27VL7ARoQFMnPkY1BaKJrxC90WZGB6_qB2LDul5zZXg.UzCEKXM89_XpK-aknj4Dnm6de1AkiNUXQGSh6IHbfnE&dib_tag=se&keywords=zigbee+pro%2Bsmart+led+controller+5-in-1+2.4ghz&qid=1769002105&sprefix=zigbee+pro+smart+led+controller+5-in-1+2.4ghz+%2Caps%2C244&sr=8-1','Amazon.nl',NULL,'2026-01-21 13:33:33',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(5,'Whiskas 7+ Kattenvoer',1.9,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com',NULL,'2026-01-21 13:34:15',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(6,'Whiskas 7+ Kattenvoer voor oudere katten - Natvoer - Kip - 4 x 85g',1.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/','bol.com','single_product','2026-01-21 15:53:16',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(7,'Whiskas 7+ Kattenvoer Natuurlijke Tonijn',1.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/','bol.com','single_product','2026-01-21 16:06:47',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(8,'Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',52.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.',NULL,'2026-01-22 00:42:27',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(9,'LEGO Botanicals Mini orchidee - 10343',24.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-miniorchidee-10343/9300000187249569/?cid=1769042624173-2224743527883&bltgh=dbd70ecd-e5ca-47fa-b254-15f0a7966210.ProductList_Middle.6.ProductTitle','bol.',NULL,'2026-01-22 00:47:10',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(10,'LEGO Botanicals Mini Orchid, Artificial Flowers Set, Plants Building Kit for Adults, Home Accessory and Office Decoration from the Botanical Collection, Gift for Valentine for Woman or Man 10343',21.93,'EUR',1.0,'https://www.amazon.nl/-/en/Botanicals-Artificial-Decoration-Collection-10343/dp/B01N6CJ1QW/ref=sr_1_1?crid=1LUSBYIDN00SB&dib=eyJ2IjoiMSJ9.5ns4G82SO2ZesIiBub3y2ORVCc_CncCqwT-yhmDgHS9Acv3us6w1czBhhnHC05aOLwKgGO04XkVbNzGhyvC5MmaXuE-SHJ8EVNnFNB3bvqdAibabFDl3bEcuiAD13IJ_5Uakk_YIBqWNfTe0Q9LL_3mtQflc1X5iswIrTXY363ARL3o7tKl2Zk7KsM5ydFX9mRiab9gZG0XHyeSpNPEZ8pm1plh5Fy0aH6qxgNh9sZkP89da68HwexCV5QTQuICahCThdXf4eTfeDVNfyBgcW0C45iqGQHhugwY0tsf9c-E.-skxwXVfmUhGSrRXv4Piu_PuQQo-wiSMMaynvHpIdDU&dib_tag=se&keywords=lego+mini+orchidee&qid=1769042886&sprefix=lego+mini+orch%2Caps%2C273&sr=8-1','Amazon.nl',NULL,'2026-01-22 00:48:55',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(11,'LEGO Icons Bloemen Boeket - Botanical Collection - 10280',45.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.com','single_product','2026-01-22 01:10:41',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(12,'LEGO Icons Bloemen Boeket - Botanical Collection - 10280',45.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.com','single_product','2026-01-22 01:20:15',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(13,'LEGO Icons Bloemen Bouquet',75.95,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.com','single_product','2026-01-22 01:21:01',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(14,'LEGO Icons Bloemen Boeket - Botanical Collection - 10280',45.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.',NULL,'2026-01-22 01:28:08',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(15,'LEGO Icons Botanical Collection Flower Bouquet',49.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.com','single_product','2026-01-22 01:29:46',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(16,'LEGO® Botanicals Boeket met Tulpen Bloemendecoratie - 11501',49.8,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-boeket-met-tulpen-bloemendecoratie-11501/9300000237345396/?cid=1769043000595-1735623380853&bltgh=gJhApsj8ojMIeMTzeUhL0w.4_96.99.ProductTitle','bol.com',NULL,'2026-01-22 01:36:38',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(17,'Whiskas 7+ Kattendryfood',0.0,'N/A',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com',NULL,'2026-01-22 01:37:12',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(18,'Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',52.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com',NULL,'2026-01-22 01:39:57',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(19,'LEGO® Botanicals Boeket met Tulpen Bloemendecoratie - 11501',49.8,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-boeket-met-tulpen-bloemendecoratie-11501/9300000237345396/?cid=1769043000595-1735623380853&bltgh=gJhApsj8ojMIeMTzeUhL0w.4_96.99.ProductTitle','bol.',NULL,'2026-01-22 01:40:23',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(20,'TORSBODA Integrated dishwasher',699.0,'EUR',1.0,'https://www.ikea.com/nl/en/p/torsboda-integrated-dishwasher-ikea-700-40548088/','IKEA',NULL,'2026-01-22 02:41:28',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(21,'N/A',0.0,'N/A',1.0,'https://www.douglas.nl/nl/p/5010033070','Douglas',NULL,'2026-01-22 12:47:13',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(22,'Silk Eau de Toilette No. 101, 100ml',0.0,'N/A',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','Stradivarius',NULL,'2026-01-22 12:47:14',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(23,'ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGB RGBW',29.99,'EUR',1.0,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=CQFNCJCCHHHX&dib=eyJ2IjoiMSJ9.5HMR8hr5boBzpMdf91yhRbDW_bmzSr1uzrlhuXzGs_67jfTFxhDdKihAQXq0_bvvkVZ2BceyDfdsvIdgvlmcyWPOVSI_NByiJOodDN97k-4sFUjn2QYyL0uX0zmZSIGIwpktVHYz8ZGgUH5dookZKpAHH6F8UknMUpu7XW_mrOSuOVHsnEHlYYIhitA_pdx14GW2DiR7vIeCamXhLPk6WV9HbFW7g-OGx4PEFABzdlb3ZMnHGanVaAJ-pfex5iRo27VL7ARoQFMnPkY1BaKJrxC90WZGB6_qB2LDul5zZXg.UzCEKXM89_XpK-aknj4Dnm6de1AkiNUXQGSh6IHbfnE&dib_tag=se&keywords=zigbee+pro%2Bsmart+led+controller+5-in-1+2.4ghz&qid=1769002105&sprefix=zigbee+pro+smart+led+controller+5-in-1+2.4ghz+%2Caps%2C244&sr=8-1','Amazon',NULL,'2026-01-22 12:47:19',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(24,'INSTITUTO ESPAÑOL Urea 20% restorative cream for rough or dry skin 150 ml',7.61,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-restorative-cream-rough/dp/B01CS5KK22/ref=sr_1_7?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-7','Amazon',NULL,'2026-01-22 12:47:32',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(25,'OLAPLEX No. 7 Bonding Oil, 30 ml',18.99,'EUR',1.0,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3/ref=sr_1_2?crid=3L5IO4YLCLAJR&dib=eyJ2IjoiMSJ9.U5W0cstTUnY_zz16rAT609WmZucTLAPIGGXSsHS-GXHCAWd60gmq-PmhRZLjer1ogPL5shI7rbfbQVO5kv-S7R37xJZlgxfCpmy0vpMg_7R8ZzCls6jtPBgwkQmqiysGBvTT3kgnD8ixykPxL7Ns0hn09t8RwienoAcaPExJAznwMz52pQec11Qylm3UZVSHhMe9me83mWTR-yvFtZa_bX2SEZcnrGGYEzGelnTsyLrimQUbzMWakdiVNLW6Dm1jSb-qpDBW4DrHvfMPei56RxLEWzBQmq1GxQGWBdXDcH0._QYvjFzXyy4C99JAub2Hbf3iKopnl6Oh8PBVCzq5eBQ&dib_tag=se&keywords=olaplex+oil&qid=1769049809&sprefix=olaplex+%2Caps%2C330&sr=8-2','Amazon',NULL,'2026-01-22 12:47:32',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(26,'INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml',14.35,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-Urea-lotion-dispenser/dp/B015OAQEHI/ref=sr_1_5_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-5','Amazon',NULL,'2026-01-22 12:47:33',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(27,'BTF-LIGHTING FCOB COB RGBCCCT Flexible High Density RGB+Warm White+Cool White LED Strip 5M 960LED/M 4800LEDs DC24V 18W/M IP30 Non Waterproof Multicolor for DIY Home Decoration',70.99,'EUR',1.0,'https://www.amazon.nl/-/en/BTF-LIGHTING-Flexible-Waterproof-Multicolor-Decoration/dp/B0C3VMV5BP/ref=sr_1_2?crid=4G3PBKIR5ZSJ&dib=eyJ2IjoiMSJ9.40v-SQ54YW-SRJAeIw05m-Hg85YqppMxyUpL1b7Iwsj1H3TtE3Onti_S72Q9luoJ0fNQ4RaiRDbMS28tVM2Kz23BxtxX23SxDRlEa9wK0fARqowRI1lSanbPvHpg2ZsHwx0DFQojXS0BKNRWmkHjk4kCWeCW4mXKwCDPDrAt-KPncb04JogkbA1drNYSYOV4OBL2Z05zTtUOqq-xgF-7LENH50XkBcNq-VYcgbeNWC96ipNmsW0yidnQqCe-mZ5MCTXuPmyTFbdjp-DFNla1_1GS-2tFEf5O4nt9poCYuB8.W9jULAY2bcROfjUbMnwy9YcMvc8Xh9Vtnj_NuAbMHX0&dib_tag=se&keywords=BTF-LIGHTING%2BFCOB%2BRGBCCT%2B(24V%2C%2B960LED%2Fm)&qid=1769001366&sprefix=btf-lighting%2Bfcob%2Brgbcct%2B24v%2B960led%2Fm%2B%2Caps%2C229&sr=8-2&th=1','Amazon',NULL,'2026-01-22 12:47:36',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(28,'INSTITUTO ESPAÑOL I.Spanish Urea Gel 1250 ml',10.64,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-I-Spanish-Urea-1250/dp/B00BN7XF1U/ref=sr_1_6_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-6','Amazon',NULL,'2026-01-22 12:47:36',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(29,'Arotelicht 24V 3A AC/DC-voeding Euro-stekkeradapter voor 3528/5050 COB LED-strip 72W maximale voeding, AC100-240V voedingsadapter',14.99,'EUR',1.0,'https://www.amazon.nl/dp/B09Y5RHJJ7/ref=sspa_dk_detail_3?pd_rd_i=B09Y5RHJJ7&pd_rd_w=RW6Ex&content-id=amzn1.sym.2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_p=2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_r=MNW2N8WHZXA9EWRSWRPQ&pd_rd_wg=tpEcw&pd_rd_r=24f37adc-9301-4644-88c0-95783e071f69&aref=iGaUDsXvlQ&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1','Amazon.nl',NULL,'2026-01-22 12:47:36',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(30,'LEGO Botanicals Daisies - Artificial Flowers Bouquet with Lavender - Building Kit for Children and Adults - Children''s Room Decoration - Gift for Valentine for Girls from 9 Years and Flower Lovers - 11508',11.29,'EUR',1.0,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/?_encoding=UTF8&pd_rd_w=1TaUy&content-id=amzn1.sym.0bd8095e-79f9-45c2-8e70-ee4034022f47:amzn1.symc.752cde0b-d2ce-4cce-9121-769ea438869e&pf_rd_p=0bd8095e-79f9-45c2-8e70-ee4034022f47&pf_rd_r=PA1HNHX1S7PQ1T7VHZPT&pd_rd_wg=6nYVk&pd_rd_r=471d265b-c2e8-49a4-a760-b6fb589b9605&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d','Amazon',NULL,'2026-01-22 12:47:37',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(31,'SILK EAU DE TOILETTE N
101 - 100 ML',15.99,'EUR',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','STRADIVARIUS',NULL,'2026-01-22 13:41:10',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(32,'Olaplex Bond Maintenance No. 7 Bonding Oil',25.08,'EUR',1.0,'https://www.douglas.nl/nl/p/5010033070','Douglas',NULL,'2026-01-22 13:41:29',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(33,'Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',52.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com B.V. (bol.com B.V.)',NULL,'2026-01-23 23:00:23',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(34,'LEGO Botanicals Mini orchidee - 10343',21.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-miniorchidee-10343/9300000187249569/?cid=1769042624173-2224743527883&bltgh=dbd70ecd-e5ca-47fa-b254-15f0a7966210.ProductList_Middle.6.ProductTitle','bol.com',NULL,'2026-01-23 23:00:26',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(35,'TORSBODA Integrated dishwasher',699.0,'EUR',1.0,'https://www.ikea.com/nl/en/p/torsboda-integrated-dishwasher-ikea-700-40548088/','IKEA',NULL,'2026-01-23 23:00:26',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(36,'LEGO Botanicals Boeket met Tulpen Bloemendecoratie - 11501',49.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-boeket-met-tulpen-bloemendecoratie-11501/9300000237345396/?cid=1769043000595-1735623380853&bltgh=gJhApsj8ojMIeMTzeUhL0w.4_96.99.ProductTitle','bol.com',NULL,'2026-01-23 23:00:27',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(37,'LEGO Botanicals Daisies - Artificial Flowers Bouquet with Lavender - Building Kit for Children and Children''s Room Decoration - Gift for Valentine for Girls from 9 Years and Flower Lovers - 11508',11.29,'EUR',1.0,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/?_encoding=UTF8&pd_rd_w=1TaUy&content-id=amzn1.sym.0bd8095e-79f9-45c2-8e70-ee4034022f47:amzn1.symc.752cde0b-d2ce-4cce-9121-769ea438869e&pf_rd_p=0bd8095e-79f9-45c2-8e70-ee4034022f47&pf_rd_r=PA1HNHX1S7PQ1T7VHZPT&pd_rd_wg=6nYVk&pd_rd_r=471d265b-c2e8-49a4-a760-b6fb589b9605&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d','Amazon',NULL,'2026-01-23 23:00:34',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(38,'LEGO Botanicals Mini Orchid, Artificial Flowers Set, Plants Building Kit for Adults, Home Accessory and Office Decoration from the Botanical Collection, Gift for Valentine for Woman or Man 10343',21.99,'EUR',1.0,'https://www.amazon.nl/-/en/Botanicals-Artificial-Decoration-Collection-10343/dp/B01N6CJ1QW/ref=sr_1_1?crid=1LUSBYIDN00SB&dib=eyJ2IjoiMSJ9.5ns4G82SO2ZesIiBub3y2ORVCc_CncCqwT-yhmDgHS9Acv3us6w1czBhhnHC05aOLwKgGO04XkVbNzGhyvC5MmaXuE-SHJ8EVNnFNB3bvqdAibabFDl3bEcuiAD13IJ_5Uakk_YIBqWNfTe0Q9LL_3mtQflc1X5iswIrTXY363ARL3o7tKl2Zk7KsM5ydFX9mRiab9gZG0XHyeSpNPEZ8pm1plh5Fy0aH6qxgNh9sZkP89da68HwexCV5QTQuICahCThdXf4eTfeDVNfyBgcW0C45iqGQHhugwY0tsf9c-E.-skxwXVfmUhGSrRXv4Piu_PuQQo-wiSMMaynvHpIdDU&dib_tag=se&keywords=lego+mini+orchidee&qid=1769042886&sprefix=lego+mini+orch%2Caps%2C273&sr=8-1','Amazon',NULL,'2026-01-23 23:00:36',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(39,'Arotelicht 24V 3A AC/DC-voeding Euro-stekkeradapter voor 3528/5050 COB LED-strip 72W maximale voeding, AC100-240V voedingsadapter',14.99,'EUR',1.0,'https://www.amazon.nl/dp/B09Y5RHJJ7/ref=sspa_dk_detail_3?pd_rd_i=B09Y5RHJJ7&pd_rd_w=RW6Ex&content-id=amzn1.sym.2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_p=2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_r=MNW2N8WHZXA9EWRSWRPQ&pd_rd_wg=tpEcw&pd_rd_r=24f37adc-9301-4644-88c0-95783e071f69&aref=iGaUDsXvlQ&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1','Amazon.nl',NULL,'2026-01-23 23:00:40',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(40,'ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGBW',29.99,'EUR',1.0,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=CQFNCJCCHHHX&dib=eyJ2IjoiMSJ9.5HMR8hr5boBzpMdf91yhRbDW_bmzSr1uzrlhuXzGs_67jfTFxhDdKihAQXq0_bvvkVZ2BceyDfdsvIdgvlmcyWPOVSI_NByiJOodDN97k-4sFUjn2QYyL0uX0zmZSIGIwpktVHYz8ZGgUH5dookZKpAHH6F8UknMUpu7XW_mrOSuOVHsnEHlYYIhitA_pdx14GW2DiR7vIeCamXhLPk6WV9HbFW7g-OGx4PEFABzdlb3ZMnHGanVaAJ-pfex5iRo27VL7ARoQFMnPkY1BaKJrxC90WZGB6_qB2LDul5zZXg.UzCEKXM89_XpK-aknj4Dnm6de1AkiNUXQGSh6IHbfnE&dib_tag=se&keywords=zigbee+pro%2Bsmart+led+controller+5-in-1+2.4ghz&qid=1769002105&sprefix=zigbee+pro+smart+led+controller+5-in-1+2.4ghz+%2Caps%2C244&sr=8-1','Amazon.nl, TANSHOP (Sold by is used for sold by, not store name as the screenshot is from amazon.nl, so the store name is Amazon.nl as a whole. TANSHOP is a third-party seller.)',NULL,'2026-01-23 23:00:42',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(41,'Olaplex Bond Maintenance No. 7 Bonding Oil',25.08,'EUR',1.0,'https://www.douglas.nl/nl/p/5010033070','Douglas',NULL,'2026-01-23 23:00:50',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(42,'OLAPLEX No. 7 Bonding Oil, 30 ml',19.99,'EUR',1.0,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3/ref=sr_1_2?crid=3L5IO4YLCLAJR&dib=eyJ2IjoiMSJ9.U5W0cstTUnY_zz16rAT609WmZucTLAPIGGXSsHS-GXHCAWd60gmq-PmhRZLjer1ogPL5shI7rbfbQVO5kv-S7R37xJZlgxfCpmy0vpMg_7R8ZzCls6jtPBgwkQmqiysGBvTT3kgnD8ixykPxL7Ns0hn09t8RwienoAcaPExJAznwMz52pQec11Qylm3UZVSHhMe9me83mWTR-yvFtZa_bX2SEZcnrGGYEzGelnTsyLrimQUbzMWakdiVNLW6Dm1jSb-qpDBW4DrHvfMPei56RxLEWzBQmq1GxQGWBdXDcH0._QYvjFzXyy4C99JAub2Hbf3iKopnl6Oh8PBVCzq5eBQ&dib_tag=se&keywords=olaplex+oil&qid=1769049809&sprefix=olaplex+%2Caps%2C330&sr=8-2','Amazon',NULL,'2026-01-23 23:00:54',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(43,'INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml',14.35,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-Urea-lotion-dispenser/dp/B015OAQEHI/ref=sr_1_5_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-5','Amazon',NULL,'2026-01-23 23:01:00',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(44,'INSTITUTO ESPAÑOL Urea 20% restorative cream for rough or dry skin 150 ml',7.47,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-restorative-cream-rough/dp/B01CS5KK22/ref=sr_1_7?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-7','Amazon',NULL,'2026-01-23 23:01:03',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(45,'Andrélon Levendige Kleur Kleurverzorgende Shampoo',6.89,'EUR',1.0,'https://www.kruidvat.nl/andrelon-levendige-kleur-kleurverzorgende-shampoo/p/6292452','Kruidvat',NULL,'2026-01-23 23:01:07',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(46,'SILK EAU DE TOILETTE N°101 - 100 ML',15.99,'EUR',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','STRADIVARIUS',NULL,'2026-01-23 23:01:08',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(47,'Oral-B iO Ultimate Clean Opzetborstels',45.99,'EUR',1.0,'https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290','Kruidvat',NULL,'2026-01-23 23:01:11',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(48,'Kruidvat Biologische Psylliumvezels',5.39,'EUR',1.0,'https://www.kruidvat.nl/kruidvat-biologische-psylliumvezels/p/4966221','Kruidvat',NULL,'2026-01-23 23:01:12',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(49,'Andrélon Pink Droogshampoo',6.99,'EUR',1.0,'https://www.etos.nl/producten/andrelon-pink-big-volume-droogshampoo-250-ml-120258111.html','Etos',NULL,'2026-01-24 00:51:03',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(50,'Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',52.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com',NULL,'2026-01-24 00:55:30',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(51,'TORSBODA Integrated dishwasher, IKEA 700, 60 cm',699.0,'EUR',1.0,'https://www.ikea.com/nl/en/p/torsboda-integrated-dishwasher-ikea-700-40548088/','IKEA',NULL,'2026-01-24 00:55:32',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(52,'LEGO Botanicals Mini orchidee - 10343',21.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-botanicals-miniorchidee-10343/9300000187249569/?cid=1769042624173-2224743527883&bltgh=dbd70ecd-e5ca-47fa-b254-15f0a7966210.ProductList_Middle.6.ProductTitle','bol.com',NULL,'2026-01-24 00:55:36',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(53,'LEGO Icons Bloemen Boeket - Botanical Collection - 10280',46.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','bol.com',NULL,'2026-01-24 00:55:43',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(54,'ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGBW',29.99,'EUR',1.0,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=CQFNCJCCHHHX&dib=eyJ2IjoiMSJ9.5HMR8hr5boBzpMdf91yhRbDW_bmzSr1uzrlhuXzGs_67jfTFxhDdKihAQXq0_bvvkVZ2BceyDfdsvIdgvlmcyWPOVSI_NByiJOodDN97k-4sFUjn2QYyL0uX0zmZSIGIwpktVHYz8ZGgUH5dookZKpAHH6F8UknMUpu7XW_mrOSuOVHsnEHlYYIhitA_pdx14GW2DiR7vIeCamXhLPk6WV9HbFW7g-OGx4PEFABzdlb3ZMnHGanVaAJ-pfex5iRo27VL7ARoQFMnPkY1BaKJrxC90WZGB6_qB2LDul5zZXg.UzCEKXM89_XpK-aknj4Dnm6de1AkiNUXQGSh6IHbfnE&dib_tag=se&keywords=zigbee+pro%2Bsmart+led+controller+5-in-1+2.4ghz&qid=1769002105&sprefix=zigbee+pro+smart+led+controller+5-in-1+2.4ghz+%2Caps%2C244&sr=8-1','amazon.nl',NULL,'2026-01-24 00:55:51',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(55,'LEGO Botanicals Daisies – Artificial Flowers Bouquet with Lavender – Building Kit for Children and Children''s Room Decoration – Gift for Valentine for Girls from 9 Years and Flower Lovers – 11508',11.29,'EUR',1.0,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/?_encoding=UTF8&pd_rd_w=1TaUy&content-id=amzn1.sym.0bd8095e-79f9-45c2-8e70-ee4034022f47:amzn1.symc.752cde0b-d2ce-4cce-9121-769ea438869e&pf_rd_p=0bd8095e-79f9-45c2-8e70-ee4034022f47&pf_rd_r=PA1HNHX1S7PQ1T7VHZPT&pd_rd_wg=6nYVk&pd_rd_r=471d265b-c2e8-49a4-a760-b6fb589b9605&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d','Amazon.nl',NULL,'2026-01-24 00:55:54',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(56,'LEGO Botanicals Mini Orchid, Artificial Flowers Set, Plants Building Kit for Adults, Home Accessory and Office Decoration from the Botanical Collection, Gift for Valentine for Woman or Man 10343',21.99,'EUR',1.0,'https://www.amazon.nl/-/en/Botanicals-Artificial-Decoration-Collection-10343/dp/B01N6CJ1QW/ref=sr_1_1?crid=1LUSBYIDN00SB&dib=eyJ2IjoiMSJ9.5ns4G82SO2ZesIiBub3y2ORVCc_CncCqwT-yhmDgHS9Acv3us6w1czBhhnHC05aOLwKgGO04XkVbNzGhyvC5MmaXuE-SHJ8EVNnFNB3bvqdAibabFDl3bEcuiAD13IJ_5Uakk_YIBqWNfTe0Q9LL_3mtQflc1X5iswIrTXY363ARL3o7tKl2Zk7KsM5ydFX9mRiab9gZG0XHyeSpNPEZ8pm1plh5Fy0aH6qxgNh9sZkP89da68HwexCV5QTQuICahCThdXf4eTfeDVNfyBgcW0C45iqGQHhugwY0tsf9c-E.-skxwXVfmUhGSrRXv4Piu_PuQQo-wiSMMaynvHpIdDU&dib_tag=se&keywords=lego+mini+orchidee&qid=1769042886&sprefix=lego+mini+orch%2Caps%2C273&sr=8-1','Amazon.nl',NULL,'2026-01-24 00:55:55',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(57,'OLAPLEX BOND MAINTENANCE NO. 7 BONDING OIL',25.08,'EUR',1.0,'https://www.douglas.nl/nl/p/5010033070','DOUGLAS, OLAPLEX',NULL,'2026-01-24 00:55:56',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(58,'BTF-LIGHTING FCOB COB RGB CCT Flexible High Density RGB+Warm White+Cool White LED Strip 5M 960LED/M 4800LEDs DC24V 18W/M IP30 Non Waterproof Multicolor for DIY Home Decoration [Energy Class G]',70.99,'EUR',1.0,'https://www.amazon.nl/-/en/BTF-LIGHTING-Flexible-Waterproof-Multicolor-Decoration/dp/B0C3VMV5BP/ref=sr_1_2?crid=4G3PBKIR5ZSJ&dib=eyJ2IjoiMSJ9.40v-SQ54YW-SRJAeIw05m-Hg85YqppMxyUpL1b7Iwsj1H3TtE3Onti_S72Q9luoJ0fNQ4RaiRDbMS28tVM2Kz23BxtxX23SxDRlEa9wK0fARqowRI1lSanbPvHpg2ZsHwx0DFQojXS0BKNRWmkHjk4kCWeCW4mXKwCDPDrAt-KPncb04JogkbA1drNYSYOV4OBL2Z05zTtUOqq-xgF-7LENH50XkBcNq-VYcgbeNWC96ipNmsW0yidnQqCe-mZ5MCTXuPmyTFbdjp-DFNla1_1GS-2tFEf5O4nt9poCYuB8.W9jULAY2bcROfjUbMnwy9YcMvc8Xh9Vtnj_NuAbMHX0&dib_tag=se&keywords=BTF-LIGHTING%2BFCOB%2BRGBCCT%2B(24V%2C%2B960LED%2Fm)&qid=1769001366&sprefix=btf-lighting%2Bfcob%2Brgbcct%2B24v%2B960led%2Fm%2B%2Caps%2C229&sr=8-2&th=1','Amazon.nl',NULL,'2026-01-24 00:55:59',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(59,'OLAPLEX No. 7 Bonding Oil, 30 ml',19.99,'EUR',1.0,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3/ref=sr_1_2?crid=3L5IO4YLCLAJR&dib=eyJ2IjoiMSJ9.U5W0cstTUnY_zz16rAT609WmZucTLAPIGGXSsHS-GXHCAWd60gmq-PmhRZLjer1ogPL5shI7rbfbQVO5kv-S7R37xJZlgxfCpmy0vpMg_7R8ZzCls6jtPBgwkQmqiysGBvTT3kgnD8ixykPxL7Ns0hn09t8RwienoAcaPExJAznwMz52pQec11Qylm3UZVSHhMe9me83mWTR-yvFtZa_bX2SEZcnrGGYEzGelnTsyLrimQUbzMWakdiVNLW6Dm1jSb-qpDBW4DrHvfMPei56RxLEWzBQmq1GxQGWBdXDcH0._QYvjFzXyy4C99JAub2Hbf3iKopnl6Oh8PBVCzq5eBQ&dib_tag=se&keywords=olaplex+oil&qid=1769049809&sprefix=olaplex+%2Caps%2C330&sr=8-2','Amazon',NULL,'2026-01-24 00:56:07',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(60,'INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml',14.34,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-Urea-lotion-dispenser/dp/B015OAQEHI/ref=sr_1_5_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-5','Amazon',NULL,'2026-01-24 00:56:17',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(61,'INSTITUTO ESPAÑOL Urea 20% restorative cream for rough or dry skin 150 ml',7.48,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-restorative-cream-rough/dp/B01CS5KK22/ref=sr_1_7?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-7','Amazon',NULL,'2026-01-24 00:56:20',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(62,'INSTITUTO ESPAÑOL I.Spanish Urea Gel 1250 ml',10.64,'EUR',1.0,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-I-Spanish-Urea-1250/dp/B00BN7XF1U/ref=sr_1_6_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-6','Amazon',NULL,'2026-01-24 00:56:21',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(63,'Oral-B iO Ultimate Clean Opzetborstels',45.99,'EUR',1.0,'https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290','Kruidvat.nl',NULL,'2026-01-24 00:56:22',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(64,'Kruidvat Biologische Psylliumvezels',5.39,'EUR',1.0,'https://www.kruidvat.nl/kruidvat-biologische-psylliumvezels/p/4966221','Kruidvat',NULL,'2026-01-24 00:56:22',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(65,'SILK EAU DE TOILETTE N°101 - 100 ML',15.99,'EUR',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','STRADIVARIUS',NULL,'2026-01-24 00:56:23',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(66,'Andrélon Levendige Kleur Kleurverzorgende Shampoo',6.89,'EUR',1.0,'https://www.kruidvat.nl/andrelon-levendige-kleur-kleurverzorgende-shampoo/p/6292452','Kruidvat',NULL,'2026-01-24 00:56:23',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(67,'Kruidvat Biologische Psylliumvezels',5.39,'EUR',1.0,'https://www.kruidvat.nl/kruidvat-biologische-psylliumvezels/p/4966221','Kruidvat',NULL,'2026-01-24 05:21:36',1,'Gratis verzending badge is present. Action badge indicates ''Kruidvat maaltijdverrijkers''.',NULL,0.0,'second_half_price','2e HALVE PRIJS',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(68,'André Rellon Levendige Kleur Kleurverzorgende Shampoo',6.89,'EUR',1.0,'https://www.kruidvat.nl/andrelon-levendige-kleur-kleurverzorgende-shampoo/p/6292452','Kruidvat',NULL,'2026-01-24 05:46:17',1,NULL,NULL,0.0,'multibuy','3 voor 11.00',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(69,'Andrélon Pin Droogshampoo',6.99,'EUR',1.0,'https://www.etos.nl/producten/andrelon-pink-big-volume-droogshampoo-250-ml-120258111.html','Etos',NULL,'2026-01-24 05:47:00',1,NULL,NULL,0.0,'bogo','1+1 gratis',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(70,'Oral-B iO Ultimate Clean Opzetborstels',45.99,'EUR',1.0,'https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290','Kruidvat',NULL,'2026-01-24 05:47:27',1,NULL,NULL,114.99,'none','Voor 45.99',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(71,'Oral-B iO Ultimate Clean Opzetborstels',45.99,'EUR',1.0,'https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290','Kruidvat Online - Verkocht en verstuurd door Kruidvat','single_product','2026-01-24 06:35:43',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(72,'N/A',0.0,'N/A',1.0,'https://www.ah.nl/producten/product/wi411496/andre%CC%81lon-pink-big-volume-droogshampoo','N/A',NULL,'2026-01-24 06:36:16',0,'The provided image is completely blank and does not contain any product information.',NULL,NULL,'none','N/A',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(73,'Andrélon Pink big volume droogshampoo',7.49,'EUR',1.0,'https://www.ah.nl/producten/product/wi411496/andre%CC%81lon-pink-big-volume-droogshampoo','Albert Heijn online
(Not explicitly written, inferred from logo and URL fragment if available in real scenario. ''Albert Heijn'' is mentioned in a banner at the top.)

Note: The banner text ''Mijn Albert Heijn Premium'' and ''10 Mijn Bonus Box aanbiedingen'' suggests the retailer is Albert Heijn. The logo also matches Albert Heijn. No specific online store name is explicitly mentioned on the main product page, but the context strongly implies it''s Albert Heijn''s online store. The search bar includes ''Waar ben je naar op zoek?'' which means ''What are you looking for?'', further indicating a retail context. The breadcrumb ''Terug > Home > Drogisterij > Haarverzorging > Shampoo > Droogshampoo'' also points to a retail category listing. Hence, ''Albert Heijn'' is the most appropriate store name inferred from the context.

Since the prompt requested to infer from the screenshot, and the Albert Heijn logo and banner are visible, it''s reasonable to infer the store name as ''Albert Heijn''. If a more specific online store name was present, it would be used. Given the information, ''Albert Heijn'' is the best representation. The ''online bestellen'' button also suggests an online retail presence. The context of the price and product listing is clearly within an online shop. Hence, ''Albert Heijn'' is the inferred store name based on visual cues and common knowledge of the brand''s presence in the Netherlands, where the Dutch language is used.

In summary, the store name is inferred to be ''Albert Heijn'' based on the visible logo and brand mentions on the page, particularly the banner at the top which mentions ''Mijn Albert Heijn Premium''. The context is clearly an online retail environment, indicated by the ''online bestellen'' button and product listing format.

Final decision for store_name: Albert Heijn (inferred from logo and banner text). If a more precise online store name was available, it would be used. However, given the visual cues, this is the most appropriate inference.

Revisiting the provided hints, the logo is clearly that of Albert Heijn. The banner at the top states ''Mijn Albert Heijn Premium voor €14.99 per jaar'' and ''10 Mijn Bonus Box aanbiedingen''. This solidifies Albert Heijn as the retailer. The phrase ''online bestellen'' is also present. Therefore, inferring ''Albert Heijn'' as the store name is accurate.

It''s important to note that this is an inference. If a specific domain or explicit store name was visible on the page itself (e.g., ''ah.nl''), that would be preferred. However, given the constraints of analyzing a screenshot, ''Albert Heijn'' is the most reasonable conclusion.

Final Answer: Albert Heijn is inferred from the logo and the banner text. The presence of an ''online bestellen'' button confirms it''s an online store. Hence, the store name is Albert Heijn.

Reconsidering the requirement for',NULL,'2026-01-24 06:39:26',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(74,'Biojoy Psyllium fibres Organic (1kg), 99% purity, Psyllium Husk (Plantago ovata)',28.99,'EUR',1.0,'https://www.amazon.nl/-/en/Biojoy-Psyllium-fibres-Organic-Plantago/dp/B07VXNHCSJ/ref=pd_ci_mcx_mh_mcx_views_0_title?pd_rd_w=1HiZc&content-id=amzn1.sym.b6f16ce2-9329-4558-a9be-475a6c764044%3Aamzn1.symc.30e3dbb4-8dd8-4bad-b7a1-a45bcdbc49b8&pf_rd_p=b6f16ce2-9329-4558-a9be-475a6c764044&pf_rd_r=E2YVTT0SSY6T815KXVFQ&pd_rd_wg=f3H39&pd_rd_r=f36c2c89-165e-4075-853f-c73bff0b7d38&pd_rd_i=B07VXNHCSJ&th=1','Amazon.nl B.V. (Amazon.nl Store, formerly known as Amazon.co.uk Ltd.) is not a retailer. Amazon Europe Core S.à r.l. is the seller of record for many items sold on Amazon.nl. Amazon Europe Core S.à r.l. is responsible for all aspects of the transaction, including sales, fulfillment, and customer service.  Amazon.nl B.V. provides customer service and handles returns for items sold by Amazon Europe Core S.à r.l.. Visit Amazon.nl Store for more products from Amazon Europe Core S.à r.l.. Seller: Biojoy. Sold by: Biojoy. Dispatches from: Amazon. This means Amazon fulfils and ships this product. They offer fast, free delivery for Prime members. For non-Prime members, delivery is free on orders over €20. You can return this product within 30 days of receipt for a refund. The seller is responsible for all aspects of the transaction, including sales, fulfillment, and customer service.  See Returns Policy for more details.',NULL,'2026-01-24 14:52:20',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(75,'Oral-B iO Ultimate Clean Opzetborstels',45.99,'EUR',1.0,'https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290','Kruidvat',NULL,'2026-01-24 21:32:47',1,'zwart, 10 stuks',NULL,114.99,'value_pack','Value Pack',0.0,0.0,NULL);
INSERT INTO "price_history" VALUES(76,'SILK EAU DE TOILETTE N°101 - 100 ML',15.99,'EUR',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','STRADIVARIUS',NULL,'2026-01-24 22:25:17',1,NULL,NULL,0.0,'none','none',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(77,'OLAPLEX No. 7 Bonding Oil, 30 ml',19.99,'EUR',1.0,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3?pd_rd_w=skz4Y&content-id=amzn1.sym.d8cc06e3-3f8f-4b61-8fd5-c32f2ba4e8ee&pf_rd_p=d8cc06e3-3f8f-4b61-8fd5-c32f2ba4e8ee&pf_rd_r=G8SV5DC367RBBZ09KSS2&pd_rd_wg=zJDLw&pd_rd_r=df5bad41-2d86-45ec-b383-9b98098a4c38&psc=1&ref_=pd_bap_d_grid_rp_csi_pd_ys_c_rfy_rp_crs_0_pr_t','Amazon',NULL,'2026-01-24 23:12:32',1,NULL,NULL,29.5,'percentage_off','Buy 4, save 5%',5.0,NULL,NULL);
INSERT INTO "price_history" VALUES(78,'Olaplex No.7 Bonding Oil',29.5,'EUR',1.0,'https://www.etos.nl/producten/olaplex-no.-7-bond-oil-30-ml%C2%A0-120799558.html','Etos',NULL,'2026-01-24 23:13:06',1,'Gratis bezorging vanaf €35. Gratis retour binnen 30 dagen.',NULL,0.0,'member_only','Korting op Etos Merk met Mijn Etos',0.0,0.0,NULL);
INSERT INTO "price_history" VALUES(79,'Olaplex No.7 Bonding Oil',29.99,'EUR',1.0,'https://www.kruidvat.nl/olaplex-no7-bonding-oil/p/mp-00046276','Kruidvat',NULL,'2026-01-24 23:15:04',1,NULL,NULL,0.0,'none','Online op voorraad.',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(80,'Olaplex No.7 Bonding Oil',47.0,'EUR',1.0,'https://www.kruidvat.nl/olaplex-no7-bonding-oil/p/mp-00045602','Kruidvat Online (via Kaviaarvoorjehaar.nl partner)

Verkocht en verstuurd door Kaviaarvoorjehaar.nl, but the item is also available for purchase via Kruidvat''s website. The actual fulfillment is through Kaviaarvoorjehaar.nl, and the product information page is hosted on Kruidvat''s website which is a retail platform.

Therefore, the store name is Kruidvat, and the partner selling it is Kaviaarvoorjehaar.nl. It''s important to note that Kaviaarvoorjehaar.nl is a partner of Kruidvat, not the primary store or retailer in the traditional sense but a marketplace seller.

Given the provided schema, it''s best to represent the primary selling platform as the store name, and if there''s a partner involved, it can be mentioned in notes if it''s significant. In this case, the product page is clearly on Kruidvat''s domain, and it is being sold *via* Kruidvat''s marketplace by Kaviaarvoorjehaar.nl. Hence, Kruidvat is the store_name.

If the intention is to identify the entity fulfilling the order, that would be Kaviaarvoorjehaar.nl, but the schema asks for `store_name` which usually refers to the platform where the product is listed and purchased from.

In this context, Kruidvat is the store, and Kaviaarvoorjehaar.nl is a fulfillment partner.

Final Decision: Kruidvat is the store name. The fact that it''s sold via Kaviaarvoorjehaar.nl is a detail for the notes field or description if needed, but the store name is Kruidvat.

For clarity, given the options, and considering that the product listing is on Kruidvat''s website, Kruidvat is the store. The',NULL,'2026-01-24 23:15:33',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(81,'Olaplex 5X No7 Bonding Oil 30ml',112.2,'EUR',1.0,'https://www.kruidvat.nl/olaplex-5x-no7-bonding-oil-30ml/p/mp-00054926','Kruidvat.nl, Kaviarvoorjehaar.nl (seller is Kaviarvoorjehaar.nl, Kruidvat is the store name that is selling it via a marketplace model or as a partner.) 
Note: The actual product is sold by Kaviarvoorjehaar.nl, not directly by Kruidvat.nl. The URL for the seller is displayed as Kaviarvoorjehaar.nl and is listed as ''Verkocht en verstuurd door''. However, the main website displayed is Kruidvat.nl, hence listing both as store_name. We are listing Kaviarvoorjehaar.nl as the seller and Kruidvat.nl as the platform where it is being sold from. The page also mentions ''Verkocht en verstuurd door Kaviarvoorjehaar.nl'', implying a third-party seller on Kruidvat.nl marketplace. Since the prompt requests for the store name, and Kruidvat is the main brand shown on the page, it is being included. If only the direct seller was to be considered, it would be Kaviarvoorjehaar.nl. The context of the prompt implies a direct retail purchase, and in this case, Kruidvat.nl is the platform presented to the user. Therefore, it is reasonable to list Kruidvat.nl as the store name, and Kaviarvoorjehaar.nl as the seller.  The prompt does not have a separate field for ''seller''.  Therefore, to provide the most context, both are included in the store_name field with a note.  However, if only one should be chosen, then Kaviarvoorjehaar.nl would be the correct choice for the direct seller.  Given the prompt asks for ''store/retailer name'', and Kruidvat.nl is the retailer platform, it should be listed first. For clarity, we are listing both to avoid ambiguity. If only one should be chosen, Kaviarvoorjehaar.nl is the seller. The product is available online, indicated by ''Online op voorraad.'' and the ''Voeg toe'' button, despite no explicit stock information like ''In stock''. The price is displayed as a discounted price with a yellow tag and',NULL,'2026-01-24 23:15:56',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(82,'Olaplex No.7 Bonding Oil',29.5,'EUR',1.0,'https://www.etos.nl/producten/olaplex-no.-7-bond-oil-30-ml%C2%A0-120799558.html','Etos',NULL,'2026-01-24 23:20:57',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(83,'ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGBW',29.99,'EUR',1.0,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=3KJFSUOFW9KK&dib=eyJ2IjoiMSJ9.7Az3zpxSW3xYEMYzQmVlCUgJDtuPAMTVhy4aovkVQzC7jfTFxhDdKihAQXq0_bvvuWvbGWsmJpZ1BOAwd5wP8AhOWOyZ0pJdrCqTf4C4t5a6eQuEC62gGOt1V0vaRms3HBtu6Hp0YbgiIPaEVG3GW1zdNta20SEGxfZempAfYeEHIeoxX2I6ecea2OE3ZB0F_mpElLk7WVN95YsK9j7S78taU73Ao0rgLqk4M945MtCatpIL0UJZKCniTngmDKYwNunZKYHWFdAG8CDIu78xk_X5r1BzTanTKN9rhH2KNX8.pJHofQ12tn8kgRAF7YSHkHJ1iX7HibYhsc-lpX3zIvU&dib_tag=se&keywords=ZigBee+3.0+Pro%2B+Smart+LED+Controller&qid=1769353809&sprefix=zigbee+3.0+pro+smart+led+controller%2Caps%2C243&sr=8-1','amazon.nl (Tanshop is the seller, not the store name for this context.) (The Toys Store is for play fun, irrelevant to product.)',NULL,'2026-01-25 15:11:38',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(84,'Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',52.99,'EUR',1.0,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','bol.com',NULL,'2026-01-25 15:13:30',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(85,'ACIDIC BONDING CONCENTRATE conditioner',50.0,'EUR',1.0,'https://www.amazon.nl/-/en/916-89702-ACIDIC-BONDING-CONCENTRATE-conditioner/dp/B0C31QQYVL/ref=sr_1_15?crid=2G2LWT0HV2IEY&dib=eyJ2IjoiMSJ9.ZqzK-u2o4rC2tz2rBeC3zJFBnapphKtmXIg7fK7U0axvLAS1bFzwnFd7ittp-oMVznEl4bEJIYqDXOBuhUEbIG0rhc60RbvDWli7ek7FYHvK94VxsfF4AAEqOfoKJ9hbnI1DwNDBSsB7y5E5EvhG9gy_T9trKW4pM--xBxBu8opPW7t4EMPB-tu2MKv4O30-ElLLATCHdqeaGeqI5QrNWwV-o8pMhGH-nHaQr3NiiVTIbZ-Wgk1FCu8e4SALD2J8uz_hDA9M2jT4o86tQhtY-a-7Q6kUeUt4WBdZvGeA3Ks.AJGKCFhfsQpvfc78_ZVkOlJcrngMD7xQeupbs-_WCM8&dib_tag=se&keywords=Redken+Acidic+Bonding+Concentrate+conditioner&qid=1769354336&sprefix=redken+acidic+bonding+concentrate+conditione%2Caps%2C247&sr=8-15','Amazon.nl (Redken Store is mentioned, but Amazon is the retailer of the page itself.)',NULL,'2026-01-25 15:26:06',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(86,'CeraVe Schuimende Reiniger Navulling 473 ml',16.65,'EUR',1.0,'https://www.etos.nl/producten/cerave-schuimende-reinigingsgel-navulling-473-ml-120850931.html','Etos',NULL,'2026-01-25 17:18:30',1,'Online bijna uitverkocht. Voor 22:00 uur besteld, morgen in huis. Beperkt beschikbaar in winkels.',NULL,0.0,'none','Nóg meer voordeel met Mijn Etos',0.0,0.0,NULL);
INSERT INTO "price_history" VALUES(87,'L''Oréal Paris Elvive Bond Repair Rescue Pre-Shampoo',13.99,'EUR',1.0,'https://www.kruidvat.nl/loreal-paris-elvive-bond-repair-rescue-pre-shampoo/p/5786583','Kruidvat',NULL,'2026-01-25 17:19:01',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(88,'CeraVe Schuimende reiniger',28.95,'EUR',1.0,'https://www.etos.nl/producten/cerave-schuimende-reinigingsgel-976-ml-120599556.html','Etos',NULL,'2026-01-25 17:44:19',1,'Online op voorraad',NULL,0.0,'none','Gratis bezorging vanaf €35',NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(89,'L''Oréal Paris Elvive Bond Repair Pre-shampoo',12.99,'EUR',1.0,'https://www.etos.nl/producten/loreal-paris-elvive-bond-repair-pre-shampoo-200-ml-120662519.html','Etos.nl (inferred from logo and URL structure if available, but not explicitly in the image elements that were provided to analyze on its own.)',NULL,'2026-01-25 17:45:34',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(90,'LEGO Botanicals madeliefjes 11508',49.99,'EUR',1.0,'https://www.intertoys.nl/lego-botanicals-madeliefjes-11508','Intertoys',NULL,'2026-01-25 17:57:55',1,'50 minuten korting!',NULL,0.0,'percentage_off','Op dit moment 50 minuten korting!',0.0,0.0,NULL);
INSERT INTO "price_history" VALUES(91,'BOND MAINTENANCE NO. 7 BONDING OIL',25.08,'EUR',1.0,'https://www.douglas.nl/nl/p/5010033070','DOUGLAS COLLECTION OLAPLEX HOME & LIFESTYLE ACTIES OUTLET VIDEO''S SKINCARE DEALS KLAN HEALTHY LIVING MAKE-UP PARFUM MERKEN NIEUW & TRENDING GEZICHT LICHAAM HAAR GEZONDHEID HOME & LIFESTYLE DOUGLAS COLLECTION ACTIES OUTLET VIDEO''S SKINCARE DEALS KLAN ACTIES OUTLET VIDEO''S SKINCARE DEALS KLAN BEAUTY CARD STORES GIFT CARD KLANTENSERVICE OLAPLEX HAAROLIE BOND MAINTENANCE NO. 7 BONDING OIL 30 ml Adviesprijs* € 29,50 € 25,08 Dit is 14% lager dan de adviesprijs BESTE PRIJS DÖUGUS PRIJSTIP Online: Op voorraad Gratis verzending Nu besteld, di, 27.01.2026 in huis. Info *De adviesprijs is de prijs die een fabrikant of leverancier aanraadt voor een artikel VOEG TOE AAN WINKELMANDJE Click & Collect Bekijk de voorraad in je favoriete store HIGHLIGHTS - Geeft glans, soepelheid en heldere kleuren - Temt pluisig en weerbarstig haar - UV- en hittebescherming tot 232 °C - Styling en bescherming in één Vrij Van Parabenen Sulfmaat Vrij Veganistisch PH-Niveau Neutraal OLAPLEX BOND MAINTENANCE NO. 7 BONDING OIL HAAROLIE 30 ml Adviesprijs* € 29,50 € 25,08 Dit is 14% lager dan de adviesprijs BESTE PRIJS DÖUGUS PRIJSTIP Online: Op voorraad Gratis verzending Nu besteld, di, 27.01.2026 in huis. Info *De adviesprijs is de prijs die een fabrikant of leverancier aanraadt voor een artikel VOEG TOE AAN WINKELMANDJE Click & Collect Bekijk de voorraad in je favoriete store HIGHLIGHTS - Geeft glans, soepelheid en heldere kleuren - Temt pluisig en weerbarstig haar - UV- en hittebescherming tot 232 °C - Styling en bescherming in één Vrij Van Parabenen Sulfmaat Vrij Veganistisch PH-Niveau Neutraal',NULL,'2026-01-25 23:00:30',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(92,'Cerave Moisturizing Cleansing Foam 1l',23.16,'EUR',1.0,'https://www.amazon.nl/-/en/Cerave-Moisturizing-Cleansing-Foam-1l/dp/B07HF991NV/ref=sr_1_1?crid=27345PXLH8UFV&dib=eyJ2IjoiMSJ9.25cFludDdSedIn9rU8Kttm2NGT1hEv-WfRrRxylpBOxfH3kXlEoAKwg-JFmT4L6IqRVRfUxanEY1uL_9__4lnM9sK_xcMlhaj1Go_9lx5W9p84t3bQ318x5ehGwvZh7qNqyJxwmKU4kZXZKSFZDGEma3PRlsaRC1IbIGgdcbUwdtG333gAMPTt5woXkK9pQI1AUWthldiXGxKj6xIHPAQRSoncVkw6Ew1l2ZF2diPtQLiufAFF809KkIh1iAz1tYajd4V3Y9to86d1lvGGy9rMo9Wmtv9wCrsNCws-zCqCc.rKXuS6CYv0o8ZdlePhzWgE6M8VTismUwWDTcQDEFWgo&dib_tag=se&keywords=CeraVe%2BFoaming%2BCleansing%2BGel&qid=1769360669&sprefix=cerave%2Bfoaming%2Bcleansing%2Bgel%2Caps%2C318&sr=8-1&th=1','Amazon.nl (implied from URL and cookie banner mentions of Amazon services/stores/on Fire TV and Amazon.nl header, however not explicitly stated as the retailer for THIS product necessarily, but the platform.) If you mean the brand name, that is Cerave. Since ''store_name'' is typically the retailer/platform, I''m going with Amazon.nl context.) NOTE: The screenshot is from Amazon.nl, which functions as the retailer/platform. Therefore, Amazon.nl is the most appropriate value for ''store_name''. Explicitly stating this to avoid confusion with the Brand name ''Cerave''. The brand name ''Cerave'' is provided separately below, if needed, but it is not the ''store_name''. Actual retailer name is derived from the URL and context of the website, as the platform where the product is sold. Thus, ''Amazon.nl'' is the most accurate representation of the store/retailer, as it is the marketplace hosting the product listing. The provided crops do not contain any explicit mention of the retailer''s name other than ''Amazon.nl'' in the header, which is the platform, and thus serves as the store_name in this context. This is standard practice for e-commerce platforms where multiple sellers may list their products. Therefore, ''Amazon.nl'' is the correct store name. The context of the question specifies to extract store/retailer name ''if visible''. The URL and header clearly indicate Amazon.nl is the platform, which is the retailer in this context. Thus, ''Amazon.nl'' is extracted. Also, The value ''Amazon.nl'' is derived from the website''s header, which is the platform where the product is listed. Therefore, it functions as the retailer in this scenario. Thus, ''Amazon.nl'' is the most accurate value for ''store_name''. It is not explicitly stated as the seller, but the platform name which is common practice. Based on the provided screenshot and context, ''Amazon.nl'' represents the store/retailer where the product is being sold. This is evident from the URL and the website''s header. Therefore, ''Amazon.nl'' is the correct value for ''store_name''. The screenshot clearly displays ''Amazon.nl'' in the header, indicating the platform and thus the retailer for this transaction. Therefore, the store_name is ''Amazon.nl''. The website''s header shows',NULL,'2026-01-25 23:00:38',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "price_history" VALUES(93,'SILK EAU DE TOILETTE N°101 - 100 ML',15.99,'EUR',1.0,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','STRADIVARIUS',NULL,'2026-01-25 23:00:38',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    purchase_type TEXT DEFAULT 'recurring',
    target_price REAL,
    target_unit TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "products" VALUES(2,'LED Strip','Lighting','recurring',65.0,NULL,'2026-01-21 13:17:17');
INSERT INTO "products" VALUES(3,'Power Supply Light Strip','Electronics','recurring',13.0,NULL,'2026-01-21 13:23:10');
INSERT INTO "products" VALUES(4,'ZigBee 3.0 Pro+ Smart LED Controller','Smart home devices','recurring',25.0,'unit','2026-01-21 13:29:58');
INSERT INTO "products" VALUES(5,'Whiskas 7+ Kattenbrokken','Pet food','recurring',51.0,'pack','2026-01-21 13:32:13');
INSERT INTO "products" VALUES(10,'Perfumes','Personal care','recurring',100.0,'l','2026-01-22 02:52:34');
INSERT INTO "products" VALUES(11,'OLAPLEX No. 7 Bonding Oil','Hair care','recurring',666.33,'l','2026-01-22 03:26:55');
INSERT INTO "products" VALUES(18,'Psyllium Husk','Health foods','recurring',20.0,'kg','2026-01-23 22:50:36');
INSERT INTO "products" VALUES(19,'ABC Conditioner','Hair care','recurring',50.0,'L','2026-01-25 15:24:58');
INSERT INTO "products" VALUES(20,'Bond Repair Pre-shampoo','Hair care','recurring',NULL,NULL,'2026-01-25 15:31:31');
INSERT INTO "products" VALUES(21,'ABC Shampoo','Hair care','recurring',40.0,'L','2026-01-25 15:42:03');
INSERT INTO "products" VALUES(29,'Moisturizing Cleansing Foam','Skincare','recurring',25.0,'L','2026-01-25 17:05:59');
INSERT INTO "products" VALUES(30,'Botanicals Bouquet with Tulips','Home decor','recurring',35.0,'unit','2026-01-25 17:23:21');
INSERT INTO "products" VALUES(31,'Botanicals Daisies','Home decor','recurring',11.0,'unit','2026-01-25 17:55:33');
INSERT INTO "products" VALUES(33,'Overall','Clothing','recurring',75.0,'unit','2026-01-26 03:16:33');
CREATE TABLE profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO "profiles" VALUES(1,'Yuyi','2026-01-25 19:56:34');
CREATE TABLE purchase_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT INTO "purchase_types" VALUES(1,'recurring');
INSERT INTO "purchase_types" VALUES(2,'one_time');
CREATE TABLE scheduler_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')) NOT NULL DEFAULT 'running',
    items_total INTEGER NOT NULL DEFAULT 0,
    items_success INTEGER NOT NULL DEFAULT 0,
    items_failed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);
INSERT INTO "scheduler_runs" VALUES(1,'2026-01-22 12:47:00','2026-01-22 12:47:37','completed',10,8,2,NULL);
INSERT INTO "scheduler_runs" VALUES(2,'2026-01-23 23:00:00','2026-01-23 23:02:13','completed',20,16,4,NULL);
INSERT INTO "scheduler_runs" VALUES(3,'2026-01-24 00:55:15','2026-01-24 00:56:56','completed',19,17,2,NULL);
INSERT INTO "scheduler_runs" VALUES(4,'2026-01-25 23:00:00','2026-01-25 23:01:38','completed',8,3,5,NULL);
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    shipping_cost_standard REAL DEFAULT 0,
    free_shipping_threshold REAL,
    notes TEXT
);
INSERT INTO "stores" VALUES(1,'Amazon',5.0,50.0,NULL);
INSERT INTO "stores" VALUES(2,'bol',5.0,50.0,'check shipping cost');
INSERT INTO "stores" VALUES(3,'Ikea',50.0,0.0,NULL);
INSERT INTO "stores" VALUES(4,'Stradivarius',5.0,0.0,NULL);
INSERT INTO "stores" VALUES(5,'Douglas',5.0,NULL,NULL);
INSERT INTO "stores" VALUES(6,'Etos',0.0,20.0,NULL);
INSERT INTO "stores" VALUES(7,'Kruidvat',2.99,20.0,NULL);
INSERT INTO "stores" VALUES(8,'Albert Heijn',0.0,NULL,NULL);
INSERT INTO "stores" VALUES(9,'Intertoys',0.0,NULL,NULL);
INSERT INTO "stores" VALUES(10,'Levis',0.0,NULL,NULL);
CREATE TABLE tracked_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    item_name_on_site TEXT,
    quantity_size REAL NOT NULL,
    quantity_unit TEXT NOT NULL,
    items_per_lot INTEGER DEFAULT 1,
    last_checked_at TEXT,
    is_active INTEGER DEFAULT 1,
    alerts_enabled INTEGER DEFAULT 1, preferred_model TEXT, target_size TEXT, target_size_label TEXT,
    FOREIGN KEY(product_id) REFERENCES "products_old"(id),
    FOREIGN KEY(store_id) REFERENCES stores(id)
);
INSERT INTO "tracked_items" VALUES(1,1,1,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/?_encoding=UTF8&pd_rd_w=1TaUy&content-id=amzn1.sym.0bd8095e-79f9-45c2-8e70-ee4034022f47:amzn1.symc.752cde0b-d2ce-4cce-9121-769ea438869e&pf_rd_p=0bd8095e-79f9-45c2-8e70-ee4034022f47&pf_rd_r=PA1HNHX1S7PQ1T7VHZPT&pd_rd_wg=6nYVk&pd_rd_r=471d265b-c2e8-49a4-a760-b6fb589b9605&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d','LEGO Botanicals Daisies',1.0,'1',1,'2026-01-24 00:55:54',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(2,2,1,'https://www.amazon.nl/-/en/BTF-LIGHTING-Flexible-Waterproof-Multicolor-Decoration/dp/B0C3VMV5BP/ref=sr_1_2?crid=4G3PBKIR5ZSJ&dib=eyJ2IjoiMSJ9.40v-SQ54YW-SRJAeIw05m-Hg85YqppMxyUpL1b7Iwsj1H3TtE3Onti_S72Q9luoJ0fNQ4RaiRDbMS28tVM2Kz23BxtxX23SxDRlEa9wK0fARqowRI1lSanbPvHpg2ZsHwx0DFQojXS0BKNRWmkHjk4kCWeCW4mXKwCDPDrAt-KPncb04JogkbA1drNYSYOV4OBL2Z05zTtUOqq-xgF-7LENH50XkBcNq-VYcgbeNWC96ipNmsW0yidnQqCe-mZ5MCTXuPmyTFbdjp-DFNla1_1GS-2tFEf5O4nt9poCYuB8.W9jULAY2bcROfjUbMnwy9YcMvc8Xh9Vtnj_NuAbMHX0&dib_tag=se&keywords=BTF-LIGHTING%2BFCOB%2BRGBCCT%2B(24V%2C%2B960LED%2Fm)&qid=1769001366&sprefix=btf-lighting%2Bfcob%2Brgbcct%2B24v%2B960led%2Fm%2B%2Caps%2C229&sr=8-2&th=1','BTF-LIGHTING FCOB COB RGBCCT Flexible High Density LED Strip 5M 960LED/M 4800LEDs DC24V ]',1.0,'1',1,'2026-01-24 00:55:59',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(3,3,1,'https://www.amazon.nl/dp/B09Y5RHJJ7/ref=sspa_dk_detail_3?pd_rd_i=B09Y5RHJJ7&pd_rd_w=RW6Ex&content-id=amzn1.sym.2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_p=2ecceb92-891b-4f6a-8f2e-861d1c3c6df9&pf_rd_r=MNW2N8WHZXA9EWRSWRPQ&pd_rd_wg=tpEcw&pd_rd_r=24f37adc-9301-4644-88c0-95783e071f69&aref=iGaUDsXvlQ&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1','Arotelicht 24V 3A AC/DC Power Supply',1.0,'1',1,'2026-01-23 23:00:40',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(4,4,1,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=CQFNCJCCHHHX&dib=eyJ2IjoiMSJ9.5HMR8hr5boBzpMdf91yhRbDW_bmzSr1uzrlhuXzGs_67jfTFxhDdKihAQXq0_bvvkVZ2BceyDfdsvIdgvlmcyWPOVSI_NByiJOodDN97k-4sFUjn2QYyL0uX0zmZSIGIwpktVHYz8ZGgUH5dookZKpAHH6F8UknMUpu7XW_mrOSuOVHsnEHlYYIhitA_pdx14GW2DiR7vIeCamXhLPk6WV9HbFW7g-OGx4PEFABzdlb3ZMnHGanVaAJ-pfex5iRo27VL7ARoQFMnPkY1BaKJrxC90WZGB6_qB2LDul5zZXg.UzCEKXM89_XpK-aknj4Dnm6de1AkiNUXQGSh6IHbfnE&dib_tag=se&keywords=zigbee+pro%2Bsmart+led+controller+5-in-1+2.4ghz&qid=1769002105&sprefix=zigbee+pro+smart+led+controller+5-in-1+2.4ghz+%2Caps%2C244&sr=8-1','ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGB RGBW',1.0,'1',1,'2026-01-24 00:55:51',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(5,5,2,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',1.0,'1',6,'2026-01-24 00:55:30',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(6,6,2,'https://www.bol.com/nl/nl/p/lego-botanicals-miniorchidee-10343/9300000187249569/?cid=1769042624173-2224743527883&bltgh=dbd70ecd-e5ca-47fa-b254-15f0a7966210.ProductList_Middle.6.ProductTitle','LEGO Botanicals Mini orchidee - 10343',1.0,'1',1,'2026-01-24 00:55:36',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(7,6,1,'https://www.amazon.nl/-/en/Botanicals-Artificial-Decoration-Collection-10343/dp/B01N6CJ1QW/ref=sr_1_1?crid=1LUSBYIDN00SB&dib=eyJ2IjoiMSJ9.5ns4G82SO2ZesIiBub3y2ORVCc_CncCqwT-yhmDgHS9Acv3us6w1czBhhnHC05aOLwKgGO04XkVbNzGhyvC5MmaXuE-SHJ8EVNnFNB3bvqdAibabFDl3bEcuiAD13IJ_5Uakk_YIBqWNfTe0Q9LL_3mtQflc1X5iswIrTXY363ARL3o7tKl2Zk7KsM5ydFX9mRiab9gZG0XHyeSpNPEZ8pm1plh5Fy0aH6qxgNh9sZkP89da68HwexCV5QTQuICahCThdXf4eTfeDVNfyBgcW0C45iqGQHhugwY0tsf9c-E.-skxwXVfmUhGSrRXv4Piu_PuQQo-wiSMMaynvHpIdDU&dib_tag=se&keywords=lego+mini+orchidee&qid=1769042886&sprefix=lego+mini+orch%2Caps%2C273&sr=8-1','LEGO Botanicals Mini Orchid, Artificial Flowers Set, Plants Building Kit for Adults, Home Accessory and Office Decoration from the Botanical Collection, Gift for Valentine for Woman or Man 10343',1.0,'1',1,'2026-01-24 00:55:55',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(8,7,2,'https://www.bol.com/nl/nl/p/lego-creator-expert-bloemen-boeket-botanical-collection-10280/9300000015132290/?cid=1769042990299-9654515405834&bltgh=4f7e1bb0-52c5-42ce-b6fd-9d52ec9cf68b.ProductList_Middle.12.ProductTitle','LEGO Icons Bloemen Boeket - Botanical Collection - 10280',1.0,'1',1,'2026-01-24 00:55:43',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(9,8,2,'https://www.bol.com/nl/nl/p/lego-botanicals-boeket-met-tulpen-bloemendecoratie-11501/9300000237345396/?cid=1769043000595-1735623380853&bltgh=gJhApsj8ojMIeMTzeUhL0w.4_96.99.ProductTitle','LEGO® Botanicals Boeket met Tulpen Bloemendecoratie - 11501',1.0,'1',1,'2026-01-23 23:00:27',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(10,9,3,'https://www.ikea.com/nl/en/p/torsboda-integrated-dishwasher-ikea-700-40548088/','TORSBODA Integrated dishwasher, IKEA 700, 60 cm',1.0,'1',1,'2026-01-24 00:55:32',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(11,10,4,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','Silk eau de toilette Nº101 - 100 ml',100.0,'ml',1,'2026-01-24 00:56:23',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(12,11,5,'https://www.douglas.nl/nl/p/5010033070','Bond Maintenance No. 7 Bonding Oil',30.0,'ml',1,'2026-01-24 00:55:56',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(13,11,1,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3/ref=sr_1_2?crid=3L5IO4YLCLAJR&dib=eyJ2IjoiMSJ9.U5W0cstTUnY_zz16rAT609WmZucTLAPIGGXSsHS-GXHCAWd60gmq-PmhRZLjer1ogPL5shI7rbfbQVO5kv-S7R37xJZlgxfCpmy0vpMg_7R8ZzCls6jtPBgwkQmqiysGBvTT3kgnD8ixykPxL7Ns0hn09t8RwienoAcaPExJAznwMz52pQec11Qylm3UZVSHhMe9me83mWTR-yvFtZa_bX2SEZcnrGGYEzGelnTsyLrimQUbzMWakdiVNLW6Dm1jSb-qpDBW4DrHvfMPei56RxLEWzBQmq1GxQGWBdXDcH0._QYvjFzXyy4C99JAub2Hbf3iKopnl6Oh8PBVCzq5eBQ&dib_tag=se&keywords=olaplex+oil&qid=1769049809&sprefix=olaplex+%2Caps%2C330&sr=8-2','OLAPLEX No. 7 Bonding Oil, 30 ml',30.0,'ml',1,'2026-01-24 00:56:07',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(14,12,1,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-Urea-lotion-dispenser/dp/B015OAQEHI/ref=sr_1_5_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-5','INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml',950.0,'ml',1,'2026-01-24 00:56:17',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(15,13,1,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-I-Spanish-Urea-1250/dp/B00BN7XF1U/ref=sr_1_6_pp?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-6','INSTITUTO ESPAÑOL I.Spanish Urea Gel 1250 ml',1250.0,'ml',1,'2026-01-24 00:56:21',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(16,14,1,'https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-restorative-cream-rough/dp/B01CS5KK22/ref=sr_1_7?crid=K6TD4KN9EOUW&dib=eyJ2IjoiMSJ9.uUJ62Jgx_N6vmYW2DlIAlct5mnWPUNZFk2tRYnYI-ZCKb-xpLUN79IqzB3sYcAz9IGgzTc1XfFVDu9F2qfWBW24WVmCpCSEUnHhJ_VFK2MtJmnlkwgA6vXrsDTbVAZI3rIQmsIPeGe74yo7Gady9GSFUWGtgW45fiZVX_NSwiL2IQd_JSN9P0n43JC3UBx027zqHZWAqlTKVoY-SsqmpgM_RVAb-PwYZ4WT_htsqJcl-k04Wy-2XeSaToj8_JrasaKZClyxYhIhxq0nmboEuDcFaxP2LUmLYcLXHYlS8gIM.8fes7PNwp2D3ZxJ1yTg1YfuYlIjY_pybnFERwI3VCGY&dib_tag=se&keywords=instituto+espa%C3%B1ol+urea&qid=1769049762&sprefix=instituto+esp%2Caps%2C821&sr=8-7','INSTITUTO ESPAÑOL Urea 20% restorative cream for rough or dry skin 150 ml',150.0,'ml',1,'2026-01-24 00:56:20',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(20,18,7,'https://www.kruidvat.nl/kruidvat-biologische-psylliumvezels/p/4966221',NULL,120.0,'g',1,'2026-01-24 05:21:36',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(22,18,1,'https://www.amazon.nl/-/en/Biojoy-Psyllium-fibres-Organic-Plantago/dp/B07VXNHCSJ/ref=pd_ci_mcx_mh_mcx_views_0_title?pd_rd_w=1HiZc&content-id=amzn1.sym.b6f16ce2-9329-4558-a9be-475a6c764044%3Aamzn1.symc.30e3dbb4-8dd8-4bad-b7a1-a45bcdbc49b8&pf_rd_p=b6f16ce2-9329-4558-a9be-475a6c764044&pf_rd_r=E2YVTT0SSY6T815KXVFQ&pd_rd_wg=f3H39&pd_rd_r=f36c2c89-165e-4075-853f-c73bff0b7d38&pd_rd_i=B07VXNHCSJ&th=1','Biojoy Psyllium fibres Organic (1kg), 99% purity, Psyllium Husk (Plantago ovata)',1.0,'kg',1,'2026-01-24 14:52:20',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(23,10,4,'https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125','Silk eau de toilette Nº101 - 100 ml',100.0,'ml',1,'2026-01-25 23:00:38',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(24,11,1,'https://www.amazon.nl/-/en/OLAPLEX-No-Bonding-Oil-30/dp/B07ZHKTQL3?pd_rd_w=skz4Y&content-id=amzn1.sym.d8cc06e3-3f8f-4b61-8fd5-c32f2ba4e8ee&pf_rd_p=d8cc06e3-3f8f-4b61-8fd5-c32f2ba4e8ee&pf_rd_r=G8SV5DC367RBBZ09KSS2&pd_rd_wg=zJDLw&pd_rd_r=df5bad41-2d86-45ec-b383-9b98098a4c38&psc=1&ref_=pd_bap_d_grid_rp_csi_pd_ys_c_rfy_rp_crs_0_pr_t','OLAPLEX No. 7 Bonding Oil, 30 ml',30.0,'ml',1,'2026-01-24 23:12:32',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(25,11,6,'https://www.etos.nl/producten/olaplex-no.-7-bond-oil-30-ml%C2%A0-120799558.html','Olaplex No. 7 Bond Oil 30 ml',30.0,'ml',1,'2026-01-24 23:20:57',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(26,11,5,'https://www.douglas.nl/nl/p/5010033070','Bond Maintenance No. 7 Bonding Oil',30.0,'ml',1,'2026-01-25 23:00:30',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(27,11,7,'https://www.kruidvat.nl/olaplex-no7-bonding-oil/p/mp-00046276','Olaplex No. 7 Bonding Oil',30.0,'ml',1,'2026-01-24 23:15:04',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(28,11,7,'https://www.kruidvat.nl/olaplex-no7-bonding-oil/p/mp-00045602','Olaplex No.7 Bonding Oil',60.0,'ml',1,'2026-01-24 23:15:33',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(29,11,7,'https://www.kruidvat.nl/olaplex-5x-no7-bonding-oil-30ml/p/mp-00054926','Olaplex 5X No7 Bonding Oil 30ml',30.0,'ml',5,'2026-01-24 23:15:56',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(30,4,1,'https://www.amazon.nl/-/en/ZigBee-Controller-DC12-24V-Compatible-Control/dp/B0CXJF6DRM/ref=sr_1_1?crid=3KJFSUOFW9KK&dib=eyJ2IjoiMSJ9.7Az3zpxSW3xYEMYzQmVlCUgJDtuPAMTVhy4aovkVQzC7jfTFxhDdKihAQXq0_bvvuWvbGWsmJpZ1BOAwd5wP8AhOWOyZ0pJdrCqTf4C4t5a6eQuEC62gGOt1V0vaRms3HBtu6Hp0YbgiIPaEVG3GW1zdNta20SEGxfZempAfYeEHIeoxX2I6ecea2OE3ZB0F_mpElLk7WVN95YsK9j7S78taU73Ao0rgLqk4M945MtCatpIL0UJZKCniTngmDKYwNunZKYHWFdAG8CDIu78xk_X5r1BzTanTKN9rhH2KNX8.pJHofQ12tn8kgRAF7YSHkHJ1iX7HibYhsc-lpX3zIvU&dib_tag=se&keywords=ZigBee+3.0+Pro%2B+Smart+LED+Controller&qid=1769353809&sprefix=zigbee+3.0+pro+smart+led+controller%2Caps%2C243&sr=8-1','ZigBee 3.0 Pro+ Smart LED Controller, 5-in-1, 2.4GHz, WiFi, PWM, LED Controller, 20A Max DC12-24V, Compatible with Alexa, Google Home, Smart Life, Tuya, Smart APP Control for Dimmer, CCT RGB RGBW',1.0,'unit',1,'2026-01-25 15:11:38',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(31,5,2,'https://www.bol.com/nl/nl/p/whiskas-1-kattenbrokken-kip-zak-6-x-1-9kg/9200000072257568/?cid=1768770255524-1740561506859&bltgh=tvPN9yKWu3yjWl3bpZ1BNw.4_25.28.ProductImage','Whiskas 7+ Kattenbrokken - Kip - Zak 6 x 1.9kg',1.9,'kg',6,'2026-01-25 15:13:30',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(32,19,1,'https://www.amazon.nl/-/en/916-89702-ACIDIC-BONDING-CONCENTRATE-conditioner/dp/B0C31QQYVL/ref=sr_1_15?crid=2G2LWT0HV2IEY&dib=eyJ2IjoiMSJ9.ZqzK-u2o4rC2tz2rBeC3zJFBnapphKtmXIg7fK7U0axvLAS1bFzwnFd7ittp-oMVznEl4bEJIYqDXOBuhUEbIG0rhc60RbvDWli7ek7FYHvK94VxsfF4AAEqOfoKJ9hbnI1DwNDBSsB7y5E5EvhG9gy_T9trKW4pM--xBxBu8opPW7t4EMPB-tu2MKv4O30-ElLLATCHdqeaGeqI5QrNWwV-o8pMhGH-nHaQr3NiiVTIbZ-Wgk1FCu8e4SALD2J8uz_hDA9M2jT4o86tQhtY-a-7Q6kUeUt4WBdZvGeA3Ks.AJGKCFhfsQpvfc78_ZVkOlJcrngMD7xQeupbs-_WCM8&dib_tag=se&keywords=Redken+Acidic+Bonding+Concentrate+conditioner&qid=1769354336&sprefix=redken+acidic+bonding+concentrate+conditione%2Caps%2C247&sr=8-15','ACIDIC BONDING CONCENTRATE conditioner',1.0,'L',1,'2026-01-25 15:26:06',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(33,20,6,'https://www.etos.nl/producten/loreal-paris-elvive-bond-repair-pre-shampoo-200-ml-120662519.html','L''Oréal Paris Elvive Bond Repair Pre-shampoo 200 ML',200.0,'ml',1,'2026-01-25 17:45:34',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(34,20,7,'https://www.kruidvat.nl/loreal-paris-elvive-bond-repair-rescue-pre-shampoo/p/5786583','L''Oréal Paris Elvive Bond Repair Rescue Pre-Shampoo',200.0,'ml',1,'2026-01-25 17:19:01',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(35,21,1,'https://www.amazon.nl/-/en/REDKEN-Acidic-Bonding-Concentrate-Shampoo/dp/B093QNKSYR/ref=pd_bxgy_d_sccl_1/260-1856934-5132330?pd_rd_w=5uDZy&content-id=amzn1.sym.f55d1bfa-6e70-4525-8a1e-d27f38476426&pf_rd_p=f55d1bfa-6e70-4525-8a1e-d27f38476426&pf_rd_r=JCXHMAPQWYV6JP5TJZSB&pd_rd_wg=hEwbq&pd_rd_r=46f5e312-c293-4f76-a698-d15ab20bd67b&pd_rd_i=B093QNKSYR&psc=1','REDKEN, Acidic Bonding Concentrate Shampoo,1 L (1er Pack),No',1.0,'L',1,NULL,0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(36,29,6,'https://www.etos.nl/producten/cerave-schuimende-reinigingsgel-976-ml-120599556.html','CeraVe Foaming Cleansing Gel 976 ml',976.0,'ml',1,'2026-01-25 17:44:19',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(37,29,6,'https://www.etos.nl/producten/cerave-schuimende-reinigingsgel-navulling-473-ml-120850931.html','CeraVe Foaming Cleansing Gel Refill 473 ml',473.0,'ml',1,'2026-01-25 17:18:30',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(38,29,1,'https://www.amazon.nl/-/en/Cerave-Moisturizing-Cleansing-Foam-1l/dp/B07HF991NV/ref=sr_1_1?crid=27345PXLH8UFV&dib=eyJ2IjoiMSJ9.25cFludDdSedIn9rU8Kttm2NGT1hEv-WfRrRxylpBOxfH3kXlEoAKwg-JFmT4L6IqRVRfUxanEY1uL_9__4lnM9sK_xcMlhaj1Go_9lx5W9p84t3bQ318x5ehGwvZh7qNqyJxwmKU4kZXZKSFZDGEma3PRlsaRC1IbIGgdcbUwdtG333gAMPTt5woXkK9pQI1AUWthldiXGxKj6xIHPAQRSoncVkw6Ew1l2ZF2diPtQLiufAFF809KkIh1iAz1tYajd4V3Y9to86d1lvGGy9rMo9Wmtv9wCrsNCws-zCqCc.rKXuS6CYv0o8ZdlePhzWgE6M8VTismUwWDTcQDEFWgo&dib_tag=se&keywords=CeraVe%2BFoaming%2BCleansing%2BGel&qid=1769360669&sprefix=cerave%2Bfoaming%2Bcleansing%2Bgel%2Caps%2C318&sr=8-1&th=1','Cerave Moisturizing Cleansing Foam 1l',976.0,'ml',1,'2026-01-25 23:00:38',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(39,31,9,'https://www.intertoys.nl/lego-botanicals-madeliefjes-11508','LEGO Botanicals Daisies 11508',1.0,'unit',1,'2026-01-25 17:57:55',0,0,NULL,NULL,NULL);
INSERT INTO "tracked_items" VALUES(40,31,1,'https://www.amazon.nl/-/en/LEGO-Botanicals-Daisies-Artificial-Decoration/dp/B0FPXDY3X2/ref=pd_bxgy_d_sccl_1/260-1856934-5132330?pd_rd_w=OYdup&content-id=amzn1.sym.75142c34-87ae-4c36-8448-6beafeb35427&pf_rd_p=75142c34-87ae-4c36-8448-6beafeb35427&pf_rd_r=8KJ8VYFM9K2CF5MNBJ29&pd_rd_wg=9DuqP&pd_rd_r=d60108d7-aa92-446d-9e7d-4020d765d07a&pd_rd_i=B0FPXDY3X2&psc=1','LEGO Botanicals Daisies – Artificial Flowers Bouquet with Lavender – Building Kit for Children and Children''s Room Decoration – Gift for Valentine for Girls from 9 Years and Flower Lovers – 11508',1.0,'unit',1,NULL,0,0,NULL,NULL,NULL);
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT INTO "units" VALUES(1,'ml');
INSERT INTO "units" VALUES(2,'cl');
INSERT INTO "units" VALUES(3,'dl');
INSERT INTO "units" VALUES(4,'L');
INSERT INTO "units" VALUES(5,'g');
INSERT INTO "units" VALUES(6,'kg');
INSERT INTO "units" VALUES(7,'lb');
INSERT INTO "units" VALUES(8,'oz');
INSERT INTO "units" VALUES(9,'fl oz');
INSERT INTO "units" VALUES(10,'piece');
INSERT INTO "units" VALUES(11,'pack');
INSERT INTO "units" VALUES(12,'pair');
INSERT INTO "units" VALUES(13,'set');
INSERT INTO "units" VALUES(14,'tube');
INSERT INTO "units" VALUES(15,'bottle');
INSERT INTO "units" VALUES(16,'can');
INSERT INTO "units" VALUES(17,'box');
INSERT INTO "units" VALUES(18,'bag');
INSERT INTO "units" VALUES(19,'tub');
INSERT INTO "units" VALUES(20,'jar');
INSERT INTO "units" VALUES(21,'unit');
CREATE INDEX idx_tracked_items_url ON tracked_items(url);
CREATE INDEX idx_tracked_items_product ON tracked_items(product_id);
CREATE INDEX idx_tracked_items_active ON tracked_items(is_active);
CREATE INDEX idx_price_history_url ON price_history(url);
CREATE INDEX idx_price_history_created_at ON price_history(created_at);
CREATE INDEX idx_error_log_created_at ON error_log(created_at);
CREATE INDEX idx_extraction_logs_item ON extraction_logs(tracked_item_id);
CREATE INDEX idx_extraction_logs_created_at ON extraction_logs(created_at);
CREATE INDEX idx_extraction_logs_status ON extraction_logs(status);
CREATE INDEX idx_api_usage_date ON api_usage(date);
CREATE INDEX idx_scheduler_runs_started_at ON scheduler_runs(started_at);
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_labels_name ON labels(name);
CREATE INDEX idx_brand_sizes_brand_cat ON brand_sizes(brand, category);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('stores',10);
INSERT INTO "sqlite_sequence" VALUES('tracked_items',40);
INSERT INTO "sqlite_sequence" VALUES('api_usage',86);
INSERT INTO "sqlite_sequence" VALUES('price_history',93);
INSERT INTO "sqlite_sequence" VALUES('extraction_logs',109);
INSERT INTO "sqlite_sequence" VALUES('scheduler_runs',4);
INSERT INTO "sqlite_sequence" VALUES('categories',161);
INSERT INTO "sqlite_sequence" VALUES('labels',151);
INSERT INTO "sqlite_sequence" VALUES('error_log',4);
INSERT INTO "sqlite_sequence" VALUES('profiles',1);
INSERT INTO "sqlite_sequence" VALUES('brand_sizes',1);
INSERT INTO "sqlite_sequence" VALUES('purchase_types',2);
INSERT INTO "sqlite_sequence" VALUES('units',21);
INSERT INTO "sqlite_sequence" VALUES('products',33);
COMMIT;
