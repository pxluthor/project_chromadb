from qdrant_client import QdrantClient
import sys

# Configurações (Ajuste se necessário)
HOST = "http://10.1.254.180"
PORT = 6333
COLLECTION = "pdf_documents"

print(f"🔌 Conectando a {HOST}:{PORT}...")
client = QdrantClient(url=HOST, port=PORT, check_compatibility=False)

# 1. Verifica se a coleção existe
if not client.collection_exists(COLLECTION):
    print(f"❌ Coleção '{COLLECTION}' NÃO existe!")
    sys.exit(1)

# 2. Pega status
info = client.get_collection(COLLECTION)
print(f"✅ Coleção encontrada! Total de pontos: {info.points_count}")

if info.points_count == 0:
    print("⚠️ A coleção está vazia.")
    sys.exit()

# 3. Espiar os dados (Payload)
print("\n🕵️  Espiando os primeiros 5 registros para ver os metadados...")
points, _ = client.scroll(
    collection_name=COLLECTION,
    limit=5,
    with_payload=True,
    with_vectors=False
)

for p in points:
    print(f"\nID: {p.id}")
    if p.payload:
        print("Payload (Metadados):")
        # Lista as chaves para vermos se 'source' ou 'filename' existe
        for k, v in p.payload.items():
            val_str = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
            print(f"  - {k}: {val_str}")
            
        if "source" not in p.payload:
            print("⚠️  AVISO: Campo 'source' NÃO encontrado neste ponto!")
    else:
        print("⚠️  Ponto sem payload!")

print("\n" + "="*50)