
import numpy as np  
import pandas as pd
import requests
import splinterlands_tournament_info
import json
import pdf_report
import aiohttp
import asyncio
from PdfToImage import transform_to_png
import re
import iso8601
import os

async def swiss(tournament_info,tournament_id):
    num_groups = tournament_info['rounds'][0]['num_swiss_groups']
    phases = tournament_info['total_rounds']
    cards = pd.DataFrame(requests.get('https://api.splinterlands.io/cards/get_details').json())
    df = pd.DataFrame()
    for h in range(1,phases+1):
        for i in range(1,num_groups+1):
            round = splinterlands_tournament_info.round_info(tournament_id,h,i)
            for j in round:
                if j['winner'] != 'no contest':

                    connector = aiohttp.TCPConnector(limit_per_host=50)
                    async with aiohttp.ClientSession(connector=connector) as client:
                        task = asyncio.create_task(splinterlands_tournament_info.battle_info(client,j['battles'][0]['battle_queue_id_1']))
                    #battle = splinterlands_tournament_info.battle_info(j['battles'][0]['battle_queue_id_1'])
                        battle = await task
                        if 'type' in json.loads(battle['details']).keys():
                            continue

                        team1summoner = splinterlands_tournament_info.sort_summoner(json.loads(battle['details'])['team1']['summoner']['card_detail_id'])            
                        team1summoner_color = json.loads(battle['details'])['team1']['color']
                        team1monsters = []
                        team2monsters = []
                        for m in range(0,len(json.loads(battle['details'])['team1']['monsters'])):
                            card_id = json.loads(battle['details'])['team1']['monsters'][m]["card_detail_id"]
                            card_name = cards.loc[cards['id']==card_id]['name'].values[0]
                            team1monsters.append(card_name)
                    
                        team2summoner = splinterlands_tournament_info.sort_summoner(json.loads(battle['details'])['team2']['summoner']['card_detail_id'])
                        team2summoner_color = json.loads(battle['details'])['team2']['color']
                        for n in range(0,len(json.loads(battle['details'])['team2']['monsters'])):
                            card_id = json.loads(battle['details'])['team2']['monsters'][n]["card_detail_id"]
                            card_name = cards.loc[cards['id']==card_id]['name'].values[0]
                            team2monsters.append(card_name)
                        

                        player1 = battle['player_1']
                        player2 = battle['player_2']
                        winner = battle['winner']                    
                        df = df.append({'team1summoner':team1summoner,'team1summoner_color':team1summoner_color,'team2summoner':team2summoner,'team2summoner_color':team2summoner_color,'player1':player1,'player2':player2,'winner':winner,'team1monsters':team1monsters,'team2monsters':team2monsters},ignore_index=True)

    team1_slots = pd.DataFrame(df['team1monsters'].to_list(), columns = ['team1_slot1', 'team1_slot2', 'team1_slot3','team1_slot4','team1_slot5','team1_slot6'])
    team2_slots = pd.DataFrame(df['team2monsters'].to_list(), columns = ['team2_slot1', 'team2_slot2', 'team2_slot3','team2_slot4','team2_slot5','team2_slot6'])
    df = pd.concat([df, team1_slots], axis=1)
    df = pd.concat([df, team2_slots], axis=1)    
    return df

async def single_elimination(tournament_info_response,tournament_id):
    df = pd.DataFrame()
    cards = pd.DataFrame(requests.get('https://api.splinterlands.io/cards/get_details').json())
    rounds = tournament_info_response['total_rounds']
    for i in range(1,rounds+1):
        round = splinterlands_tournament_info.round_info(tournament_id,i)
        for battles in round:            
            for battle_entry in battles['battles']:
                if battle_entry['battle_queue_id_1'] == None or battle_entry['battle_queue_id_2'] == None:
                    continue
                connector = aiohttp.TCPConnector(limit_per_host=50)
                async with aiohttp.ClientSession(connector=connector) as client:
                    task = asyncio.create_task(splinterlands_tournament_info.battle_info(client,battle_entry['battle_queue_id_1']))
                    battle = await task

                    if 'type' in json.loads(battle['details']).keys():
                        continue
                    team1summoner = splinterlands_tournament_info.sort_summoner(json.loads(battle['details'])['team1']['summoner']['card_detail_id'])
                    team1summoner_color = json.loads(battle['details'])['team1']['color']
                    team1monsters = []
                    team2monsters = []       
                    for m in range(0,len(json.loads(battle['details'])['team1']['monsters'])):
                        card_id = json.loads(battle['details'])['team1']['monsters'][m]["card_detail_id"]
                        card_name = cards.loc[cards['id']==card_id]['name'].values[0]
                        team1monsters.append(card_name)                 

                    team2summoner = splinterlands_tournament_info.sort_summoner(json.loads(battle['details'])['team2']['summoner']['card_detail_id'])
                    team2summoner_color = json.loads(battle['details'])['team2']['color']

                    for n in range(0,len(json.loads(battle['details'])['team2']['monsters'])):
                        card_id = json.loads(battle['details'])['team2']['monsters'][n]["card_detail_id"]
                        card_name = cards.loc[cards['id']==card_id]['name'].values[0]
                        team2monsters.append(card_name)

                    player1 = battle['player_1']
                    player2 = battle['player_2']
                    winner = battle['winner']
                    df = df.append({'team1summoner':team1summoner,'team1summoner_color':team1summoner_color,'team2summoner':team2summoner,'team2summoner_color':team2summoner_color,'player1':player1,'player2':player2,'winner':winner,'team1monsters':team1monsters,'team2monsters':team2monsters},ignore_index=True)

    team1_slots = pd.DataFrame(df['team1monsters'].to_list(), columns = ['team1_slot1', 'team1_slot2', 'team1_slot3','team1_slot4','team1_slot5','team1_slot6'])
    team2_slots = pd.DataFrame(df['team2monsters'].to_list(), columns = ['team2_slot1', 'team2_slot2', 'team2_slot3','team2_slot4','team2_slot5','team2_slot6'])
    df = pd.concat([df, team1_slots], axis=1)
    df = pd.concat([df, team2_slots], axis=1)

    return df

def summoner_summary(tournament_info,tournament_id):
    if tournament_info['format'] == 'single_elimination':
        tournament_df = asyncio.get_event_loop().run_until_complete(single_elimination(tournament_info,tournament_id))
    elif tournament_info['format'] == 'swiss':
        tournament_df = asyncio.get_event_loop().run_until_complete(swiss(tournament_info,tournament_id))

    return tournament_df


def players_report(general_info:pd.DataFrame) -> pd.DataFrame: 
    league_dict= {0:'Novice',1:'Bronze',2:'Bronze',3:'Bronze',4:'Silver',5:'Silver',6:'Silver',7:'Gold',8:'Gold',9:'Gold',10:'Diamond',11:'Diamond',12:'Diamond',13:'Champion',14:'Champion',15:'Champion'}
    df = pd.DataFrame(general_info['players'])
    df['collection_power']= df.apply(lambda x: x['player_data']['collection_power'],axis=1)
    df['league']= df.apply(lambda x: x['player_data']['league'],axis=1)
    df['league'] = df['league'].apply(lambda x: league_dict[x])
    df['power_league'] = ''
    df.loc[(0 <= df['collection_power']) & (df['collection_power'] < 100),'power_league'] = 'Novice'
    df.loc[(100 <= df['collection_power']) & (df['collection_power'] < 15000),'power_league'] = 'Bronze'
    df.loc[(15000 <= df['collection_power']) & (df['collection_power'] < 100000),'power_league'] = 'Silver'
    df.loc[(100000 <= df['collection_power']) & (df['collection_power'] < 250000),'power_league'] = 'Gold'
    df.loc[(250000 <= df['collection_power']) & (df['collection_power'] < 500000),'power_league'] = 'Diamond'
    df.loc[(500000 <= df['collection_power']),'power_league'] = 'Champion'
    return df



def main():  
    #4958535b4f5b27e57c062cd79034dd61b3954967
    #a758575ae819bf06be4db5319dce46e2a0fb6792
    if not os.path.exists('pdfs'):
        os.mkdir('pdfs')

    general_info= splinterlands_tournament_info.general_info('b0acc0c00dcd829b00d59f2738f9298d21d58f18',1000)
    pdf_title = re.sub(r"\s+", "", general_info['name'], flags=re.UNICODE)+'_'+iso8601.parse_date(general_info['start_date']).strftime('%x').replace('/','_')
    first_page = pdf_report.first_page(general_info,pdf_title,'b0acc0c00dcd829b00d59f2738f9298d21d58f18')
    tournament_df = summoner_summary(general_info,'b0acc0c00dcd829b00d59f2738f9298d21d58f18')
    players_report_df = players_report(general_info)

    second_page = pdf_report.second_page(first_page,tournament_df)
    third_page = pdf_report.third_page(second_page,tournament_df)    
    forth_page = pdf_report.forth_page(third_page,tournament_df)
    fifth_page = pdf_report.fifth_page(forth_page,tournament_df)
    sixth_to_ninth_page = pdf_report.sixth_to_ninth_page(fifth_page,tournament_df,general_info)
    tenth_page = pdf_report.tenth_page(sixth_to_ninth_page,players_report_df)
    tenth_page.save()
    transform_to_png('./pdfs',pdf_title+'.pdf')



if __name__ == "__main__":  
    main()