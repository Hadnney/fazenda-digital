from database import engine, SessionLocal
from models import Base, Paddock, Animal, Inventory, Task
import datetime


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if data already exists
    if db.query(Paddock).first():
        print("Database already initialized.")
        db.close()
        return

    # Seed Paddocks
    paddocks = [
        Paddock(
            name="Piquete 1",
            area=10.0,
            capacity=50,
            geometry='{"type": "Polygon", "coordinates": ...}',
            current_load=0
        ),
        Paddock(
            name="Piquete 2",
            area=12.5,
            capacity=60,
            geometry='{"type": "Polygon", "coordinates": ...}',
            current_load=0
        ),
        Paddock(
            name="Curral Principal",
            area=1.0,
            capacity=200,
            geometry='{"type": "Polygon", "coordinates": ...}',
            current_load=0
        ),
    ]
    db.add_all(paddocks)

    # Seed Animals
    animals = [
        Animal(
            rfid="1001",
            breed="Nelore",
            birth_date=datetime.date(2023, 1, 15),
            initial_weight=180.0,
            current_weight=450.0,
            status="active",
            paddock_id=1
        ),
        Animal(
            rfid="1002",
            breed="Angus",
            birth_date=datetime.date(2023, 2, 10),
            initial_weight=200.0,
            current_weight=480.0,
            status="active",
            paddock_id=1
        ),
        Animal(
            rfid="1003",
            breed="Nelore",
            birth_date=datetime.date(2023, 3, 5),
            initial_weight=175.0,
            current_weight=420.0,
            status="active",
            paddock_id=2
        ),
    ]
    db.add_all(animals)

    # Seed Inventory
    inventory = [
        Inventory(
            item_name="Sal Mineral",
            category="feed",
            quantity=500,
            unit="kg",
            cost_per_unit=5.50,
            expiry_date=datetime.date(2024, 12, 1)
        ),
        Inventory(
            item_name="Vacina Aftosa",
            category="medicine",
            quantity=100,
            unit="doses",
            cost_per_unit=2.00,
            expiry_date=datetime.date(2025, 6, 1)
        ),
    ]
    db.add_all(inventory)

    # Seed Tasks
    tasks = [
        Task(
            description="Verificar cerca do Piquete 2",
            assignee="João",
            status="pending",
            due_date=datetime.date.today()
        ),
        Task(
            description="Pesagem do lote 1",
            assignee="Maria",
            status="pending",
            due_date=datetime.date.today() + datetime.timedelta(days=2)
        ),
    ]
    db.add_all(tasks)

    db.commit()
    db.close()
    print("Database initialized and seeded.")


if __name__ == "__main__":
    init_db()
