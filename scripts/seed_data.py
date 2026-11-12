import random
from app.db import Base, engine, SessionLocal
from app.models import Product
from app.module_c_agents.rag import add_document

Base.metadata.create_all(engine)

CATEGORIES = ["camiseta", "calça", "tênis", "vestido"]
SIZES = ["PP", "P", "M", "G", "GG"]


def seed() -> None:
    with SessionLocal() as session:
        if session.query(Product).count() == 0:
            for i in range(200):
                price = round(random.uniform(50, 500), 2)
                cost = round(price * random.uniform(0.35, 0.6), 2)
                session.add(
                    Product(
                        sku=f"SKU-{i:04d}",
                        category=random.choice(CATEGORIES),
                        size=random.choice(SIZES),
                        price=price,
                        cost=cost,
                        logistics_cost=round(random.uniform(10, 40), 2),
                        return_rate=round(random.uniform(0.02, 0.45), 4),
                    )
                )
            session.commit()

    add_document(
        "Política de Trocas",
        "Trocas permitidas em até 30 dias corridos após o recebimento, "
        "com etiqueta e produto sem uso. Frete de troca gratuito.",
    )
    add_document(
        "Política de Reembolso",
        "Reembolsos acima de R$200 exigem aprovação de supervisor. "
        "Prazo de estorno: 5 dias úteis no cartão.",
    )
    add_document(
        "Manual de Produtos",
        "Tênis: recomendamos comprar um número acima. Camisetas: tamanho fiel.",
    )
    print("Seed concluído.")


if __name__ == "__main__":
    seed()