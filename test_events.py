from etl.clients.rahvaalgatus import RahvaalgatusClient
client = RahvaalgatusClient()
events = client.get_events(limit=5)
print(events)
