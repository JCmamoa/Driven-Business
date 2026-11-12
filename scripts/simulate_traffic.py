import httpx
import random

SAMPLES = [
    ("Troca de tamanho", "Comprei uma camiseta M mas ficou apertada, quero trocar."),
    ("Pedido atrasado", "Meu pedido está há 10 dias parado, preciso de ajuda urgente!"),
    ("Dúvida de produto", "O tênis modelo X tem numeração grande?"),
    ("Reembolso", "Quero reembolso de R$350 do pedido #12345, produto veio com defeito."),
    ("Rastreio", "Qual o código de rastreio do meu pedido?"),
]


def run() -> None:
    for i in range(20):
        subject, body = random.choice(SAMPLES)
        payload = {
            "ticket": {
                "id": random.randint(10000, 99999),
                "requester": {"email": f"user{i}@example.com"},
                "subject": subject,
                "description": body,
            }
        }
        r = httpx.post("http://localhost:8000/webhooks/zendesk", json=payload)
        print(r.status_code, r.json())


if __name__ == "__main__":
    run()