# Categories 🏷️

Categories allow you to group related **Products** for better organization and smarter price tracking.

## Database Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_size_sensitive INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- `is_size_sensitive`: A flag specifically for **Clothing, Footwear, Bedding, and Accessories**. While Food (like milk) can have different sizes (1L vs 2L), `is_size_sensitive` is reserved for items where the **physical size/fit** is the primary tracking factor (e.g., "Pants Size 32" vs "Pants Size 34").

---

## Seeded Categories
Price Spy comes pre-seeded with a comprehensive list of over 100 categories to ensure your data is structured from day one:

<details>
<summary>Click to view full Category list (A-Z)</summary>

| | | | |
|---|---|---|---|
| Accessories | Alcohol-Free Alternatives | Antiques | Air Purifiers & Humidifiers |
| Aromatherapy & Essential Oils | Artisanal Cheeses | Audio | Automotive |
| Baby Care | Baby Food | Bakery | Baking Supplies |
| Barware | Bath Linens | Bedding | Beer |
| Beverages | Bicycle Accessories | Board Games | Books - Children |
| Books - Educational | Books - Fiction | Books - Non-Fiction | Breakfast Foods |
| Camping & Outdoors | Canned Goods | Cleaning Supplies | Clothing |
| Coffee & Tea | Collectibles | Computer Accessories | Condiments & Sauces |
| Cooking Oils | Cookware | Cosmetics | Crafts & Hobbies |
| Curtains & Blinds | Dairy | Deli Meats | Delicatessen |
| Dessert Toppings | Dinnerware | Dishwashing | Drones & RC Vehicles |
| Electrical | Electronics | Exercise Monitors | Feminine Care |
| Fine Art | First Aid | Fish Tank Supplies | Fitness |
| Fitness Large Equipment | Flatware | Foot Care | Footwear |
| Fresh Herbs | Frozen Foods | Fruits | Furniture |
| Gaming | Gardening | Gift Wrapping | Glassware |
| Gluten-Free Products | Gum & Mints | Hair Care | Health Foods |
| Hearing Care | Home Decor | Home Office Furniture | Home Security |
| Honey & Syrups | Household | International Foods - Asian | International Foods - Mediterranean |
| International Foods - Mexican | Jewelry | Kitchen Appliances | Kitchen Linens |
| Kitchen Utensils | Laundry Care | Lighting | Luggage & Bags |
| Magazines & Newspapers | Massage & Relaxation | Meat & Poultry | Mobile Accessories |
| Musical Instruments | Nuts & Dried Fruits | Office Supplies | Oral Care |
| Organic Foods | Outdoor Tools | Over-the-Counter Medicine | Painting & Decorating |
| Paper Products | Party Supplies | Pasta & Grains | Personal Care |
| Pest Control | Pet Accessories | Pet Food | Pet Supplies |
| Pharmacy | Photography | Photography Equipment | Plumbing |
| Pool Maintenance | Prepared Meals | Professional Equipment | Protective Gear |
| Religious & Spiritual Items | Safety Equipment | School Supplies | Seafood |
| Seasonal Decor | Seeds | Shaving & Grooming | Skincare |
| Small Animal Supplies | Small Home Appliances | Smart Home Devices | Smoked Fish |
| Snacks | Special Diets | Spices & Seasonings | Spirits |
| Sports Equipment | Spreads | Stationery | Storage & Organization |
| Sweets & Confectionery | Swimming Gear | Team Sports | Terrarium Supplies |
| Tofu & Meat Substitutes | Tools & Hardware | Toys | Travel Accessories |
| Underwear & Sleepwear | Vegan & Plant-Based | Vegetables | Video Projectors & Screens |
| Vinegar | Vitamins & Minerals | Water Filtration | Water Softening Salts |
| Wearable Tech | Wine | Yoga & Pilates | |
</details>

---

## How Categories Interact with Products

Categories and Products have a **Strict Association**:

1.  **Mandatory Field**: You **must** provide a category name when creating a new Product.
2.  **Auto-Creation and Formatting**: If the category doesn't exist, Price Spy creates it automatically. All category names are **automatically capitalized** (e.g., `laundry care` becomes `Laundry care`) to maintain database cleanliness.
3.  **Protected Deletion**: You **cannot delete** a Category if it is currently assigned to any products. You must first reassign those products or remove them before the category can be deleted.
4.  **Cascade Updates**: Renaming a Category via the API will automatically update all linked products to the new name.

---

## Backend Implementation

### Repository Layer (`CategoryRepository`)
- **`get_all()`**: Lists every available category.
- **`get_by_name(name)`**: Finds a specific category record.
- **`insert(category)`**: Manual creation of a category.
- **`update(id, category)`**: Rename or toggle size sensitivity.
- **`delete(id)`**: Remove the category and clean up product links.

### API Layer (`/api/categories`)
- **`GET /`**: Fetch all categories.
- **`GET /search?q=...`**: Fuzzy search for categories.
- **`POST /`**: Create a new category manually.
- **`PUT /{id}`**: Update category details.
- **`DELETE /{id}`**: Delete a category.
