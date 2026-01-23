from app.storage.database import get_database
from app.storage.repositories import StoreRepository, ProductRepository, TrackedItemRepository
from app.models.schemas import Store, Product, TrackedItem
from datetime import datetime

def seed_real_data():
    db = get_database()
    db.initialize()
    
    store_repo = StoreRepository(db)
    product_repo = ProductRepository(db)
    tracked_repo = TrackedItemRepository(db)
    
    # Stores
    etos = store_repo.insert(Store(name="Etos", shipping_cost_standard=0.0, free_shipping_threshold=20.0))
    kruidvat = store_repo.insert(Store(name="Kruidvat", shipping_cost_standard=2.99, free_shipping_threshold=20.0))
    
    # Products
    items = [
        {
            "name": "Andrélon Pink Big Volume Droogshampoo",
            "category": "Hair",
            "target": 5.0,
            "url": "https://www.etos.nl/producten/andrelon-pink-big-volume-droogshampoo-250-ml-120258111.html",
            "store_id": etos
        },
        {
            "name": "Andrélon Levendige Kleur Shampoo",
            "category": "Hair",
            "target": 4.50,
            "url": "https://www.kruidvat.nl/andrelon-levendige-kleur-kleurverzorgende-shampoo/p/6292452",
            "store_id": kruidvat
        },
        {
            "name": "Oral-B iO Ultimate Clean Opzetborstels",
            "category": "Personal Care",
            "target": 50.0,
            "url": "https://www.kruidvat.nl/oral-b-io-ultimate-clean-opzetborstels/p/6214290",
            "store_id": kruidvat
        },
        {
            "name": "Kruidvat Biologische Psylliumvezels",
            "category": "Health",
            "target": 6.0,
            "url": "https://www.kruidvat.nl/kruidvat-biologische-psylliumvezels/p/4966221",
            "store_id": kruidvat
        }
    ]
    
    for item in items:
        prod_id = product_repo.insert(Product(
            name=item["name"],
            category=item["category"],
            target_price=item["target"]
        ))
        tracked_repo.insert(TrackedItem(
            product_id=prod_id,
            store_id=item["store_id"],
            url=item["url"],
            is_active=True
        ))
    
    print("Real-world items seeded successfully.")
    db.close()

if __name__ == "__main__":
    seed_real_data()
