"""Database initialization script"""
from sqlalchemy import text
from .database import engine
from .models import Base


def init_database():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_database():
    """Drop all tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped!")


def create_sample_data():
    """Create sample customer data for testing"""
    from .database import SessionLocal
    from .models import Customer
    from datetime import date

    db = SessionLocal()
    try:
        # Sample KT members
        sample_customers = [
            Customer(
                phone_number="01012345678",
                name="김철수",
                birth_date=date(1990, 5, 15),
                is_kt_member=True,
                current_plan="5G 슬림 14GB",
                subscription_date=date(2022, 3, 1)
            ),
            Customer(
                phone_number="01087654321",
                name="이영희",
                birth_date=date(1985, 8, 22),
                is_kt_member=True,
                current_plan="요고 다이렉트 49",
                subscription_date=date(2021, 7, 15)
            ),
            Customer(
                phone_number="01011112222",
                name="박지민",
                birth_date=date(2000, 12, 3),
                is_kt_member=True,
                current_plan="5G Y 베이직",
                subscription_date=date(2023, 1, 10)
            ),
            Customer(
                phone_number="01055556666",
                name="최민수",
                birth_date=date(1955, 2, 28),
                is_kt_member=True,
                current_plan="5G 시니어 베이직",
                subscription_date=date(2020, 11, 5)
            ),
            # Non-KT member (for testing)
            Customer(
                phone_number="01099998888",
                name="정미영",
                birth_date=date(1995, 6, 10),
                is_kt_member=False,
                current_plan=None,
                subscription_date=None
            ),
        ]

        for customer in sample_customers:
            existing = db.query(Customer).filter(
                Customer.phone_number == customer.phone_number
            ).first()
            if not existing:
                db.add(customer)

        db.commit()
        print(f"Sample data created: {len(sample_customers)} customers")

    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    create_sample_data()
