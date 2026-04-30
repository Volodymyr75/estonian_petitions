from etl.clients.rahvaalgatus import RahvaalgatusClient
client = RahvaalgatusClient()
initiatives = client.get_initiatives(limit=1)
print(initiatives)
