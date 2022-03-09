import requests

def general_info(tournament_id,number_of_players):
    response = requests.get("https://api2.splinterlands.com/tournaments/find?id=%s&player_limit=%s" % (tournament_id,number_of_players))
    return response.json()

def round_info(tournament_id,round,swiss_group='0'):
    response = requests.get("https://api2.splinterlands.com/tournaments/battles?id=%s&round=%s&swiss_group=%s" %(tournament_id,round,swiss_group))
    return response.json()

async def battle_info(client,battle_id):
    async with client.get("https://api2.splinterlands.com/battle/result?id=%s" %(battle_id)) as rq:
        body = await rq.json(content_type=None)
    return body

def splinterlands_general_info():
    response = requests.get("https://api2.splinterlands.com/settings").json()    
    return response

def player_details(player_name):
    response = requests.get("https://api2.splinterlands.com/players/details?name=%s" %(player_name)).json()    
    return response    

def sort_summoner(card_id):
    card_dict = {440:"Tarsa",260:"Qid Yuff",167:"Pyre",5:"Malric Inferno",70:"Talia Firestorm",110:"Plado Emberstorm",236:"Yodin Zaku",
                437:"Kelya Frendul",178:"Bortus",257:"Vera Salacia",71:"Xia Seachan",254:"Lir Deepswimmer",16:"Alric Stormbringer",111:"Valnamor",
                189:"Wizard of Eastwood",439:"Obsidian",27:"Lyanna Natura",72:"Xander Foxwood",259:"Mylor Crowling",112:"Prince Rennyn",278:"Scarred Llama Mage",
                441:"General Sloan",156:"Mother Khala",261:"Lorna Shine",38:"Tyrus Paladium",73:"Kiara Lightbringer",239:"Chanseus the Great",113:"The Peakrider",
                438:"Thaddius Brood",145:"Contessa L'ament",258:"Owster Rotwell",49:"Zintar Mortalis",74:"Jarlax the Undead",235:"Mimosa Nightshade",109:"Crypt Mancer",
                224:"Drake of Arnak",240:"Kretch Tallevor",114:"Delwyn Dragonscale",262:"Brighton Bloom",78:"Neb Seni",88:"Daria Dragonscale",442:"Quix the Devious",200:"Camila Sungazer",56:"Selenia Sky",291:"Byzantine Kitty",205:"Prince Julian",130:"Archmage Arius"}
    return card_dict[card_id]

