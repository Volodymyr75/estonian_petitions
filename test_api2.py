from etl.clients.rahvaalgatus import RahvaalgatusClient
client = RahvaalgatusClient()
initiatives = client.get_initiatives()
has_created = False
for i in initiatives[:50]:
    if 'createdAt' in i or 'created_at' in i:
        has_created = True
        print("Found:", i)
        break
print("Has created field?", has_created)
