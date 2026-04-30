from etl.clients.rahvaalgatus import RahvaalgatusClient
client = RahvaalgatusClient()
details = client.get_initiative_details('d400bf12-f212-4df0-88a5-174a113c443a')
print(details)
