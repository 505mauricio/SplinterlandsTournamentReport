import os
import datetime
import requests
import splinterlands_tournament_info
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import Paragraph, Frame, KeepInFrame,Image,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib import utils
from typing import List
from io import BytesIO,StringIO
import PIL
import iso8601
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


league_dict= {0:'Novice',1:'Bronze',2:'Bronze',3:'Bronze',4:'Silver',5:'Silver',6:'Silver',7:'Gold',8:'Gold',9:'Gold',10:'Diamond',11:'Diamond',12:'Diamond',13:'Champion',14:'Champion',15:'Champion'}

def pie_plot(data,background_color=(0,0,0),title=None,exp = True,colors = None,labels = None,figsize = (20,20),dpi = 150,fontsize = 40,shadow = True,startangle = 90, pctdistance= .5, labeldistance= 1.1,left = .125):  
    plt.rcdefaults()
    #plt.rcParams['font.family'] = 'Franklin Gothic Medium'
    plt.rcParams["figure.figsize"] = figsize
    plt.rcParams["figure.dpi"] = dpi

    if exp == True:
        explode = ((0.05),)*len(data)

    centre_circle = plt.Circle((0,0),0.8,fc=background_color)
    fig1, ax1 = plt.subplots(figsize=figsize)

    ax1.pie(data, labels=labels,
        autopct= lambda p : '{:.2f}%  ({:,.0f})'.format(p,p * sum(data)/100),
        colors = colors,shadow=shadow, startangle=startangle,explode = explode,textprops={'fontsize': fontsize},pctdistance = pctdistance , labeldistance= labeldistance)   

    plt.subplots_adjust(left = left)
    ax1.axis("equal")
    ax1.set_title(title)
    ax1.add_artist(centre_circle)
    ax1.patch.set_visible(False)
    #plt.show()
    return plt.gcf()

def matchup_chart(data:pd.DataFrame,figsize=(50,50),dpi=80):
    plt.rcdefaults()
    #plt.rcParams['font.family'] = 'Franklin Gothic Medium'
    plt.rcParams["figure.figsize"] = figsize
    plt.rcParams["figure.dpi"] = dpi
    fig, ax = plt.subplots()
    fig.subplots_adjust(left = 0.3, top = 0.9, bottom=0.3,right = 0.9)
    #plt.figure(figsize = figsize)
    #plt.figure(figsize = (162/25.4,162/25.4))
    summoners_list = pd.concat([data['team1summoner'],data['team2summoner']]).value_counts()[:5].index.tolist()
    summoners_wr = []
    summoners_score = []
    for i in summoners_list:
       loss_perc,score,win,loss =summoner_win_loss(i,data)
       summoners_wr.append(loss_perc)
       summoners_score.append(score)
    chart_wr= pd.concat(summoners_wr,axis=1).fillna(0)
    chart_txt = pd.concat(summoners_score,axis=1).fillna('0-0')
    cmap = sns.diverging_palette(0, 230, 90, 60, as_cmap=True)
    chart = sns.heatmap(chart_wr,annot=chart_txt,cmap = cmap,fmt = '',xticklabels = True, yticklabels = True, linewidths=.5, linecolor='black')
    
    
    #plt.subplot_tool()
    return plt.gcf()

def summoner_win_loss(summoner:str,dataframe:pd.DataFrame) -> pd.Series:
    a = pd.concat([dataframe[dataframe['winner']==dataframe['player1']]['team1summoner'],dataframe[dataframe['winner']!=dataframe['player1']]['team2summoner']],ignore_index=True)
    b = pd.concat([dataframe[dataframe['winner']==dataframe['player1']]['team2summoner'],dataframe[dataframe['winner']!=dataframe['player1']]['team1summoner']],ignore_index=True)
    #a = dataframe[dataframe['winner']==dataframe['player1']]['team1summoner'].append(dataframe[dataframe['winner']!=dataframe['player1']]['team2summoner'],ignore_index=True)
    #b = dataframe[dataframe['winner']==dataframe['player1']]['team2summoner'].append(dataframe[dataframe['winner']!=dataframe['player1']]['team1summoner'],ignore_index=True)
    matchup = pd.DataFrame([a,b]).transpose()
    win = matchup[matchup[0]==summoner][1].value_counts().rename('win')
    loss = matchup[matchup[1]==summoner][0].value_counts().rename('loss')
    loss_win_df = pd.DataFrame([loss,win]).transpose().fillna(0).astype('int32')
    loss_win_df['loss_perc'] = loss_win_df['loss']/(loss_win_df['win']+loss_win_df['loss'])
    loss_win_df['win'] = loss_win_df['win'].astype(str)
    loss_win_df['loss'] =  loss_win_df['loss'].astype(str)
    resp = loss_win_df['loss']+'-'+loss_win_df['win']  
    #return resp.rename(summoner),win_loss_df['win'].rename(summoner),win_loss_df['loss'].rename(summoner)
    return loss_win_df['loss_perc'].rename(summoner),resp.rename(summoner),loss_win_df['win'].rename(summoner),loss_win_df['loss'].rename(summoner)

def horizontal_bar_plot(Summoners:dict,figsize=(50,50),dpi=80):
    plt.rcdefaults()
    #plt.rcParams['font.family'] = 'Franklin Gothic Medium'
    plt.rcParams["figure.figsize"] = figsize
    plt.rcParams["figure.dpi"] = dpi
    Summoners = dict(sorted(Summoners.items(), key=lambda item: item[1],reverse=True))
    fig, ax = plt.subplots()
    #plt.subplot_tool()
    fig.subplots_adjust(left = 0.4, top = 1, bottom=0)
    plt.hlines(y=list(Summoners.keys()), xmin=1, xmax=list(Summoners.values()), color='#007acc', alpha=0.4, linewidth=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_axisbelow(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.patch.set_visible(False)
    plt.rcParams['axes.edgecolor']='#333F4B'
    plt.rcParams['axes.linewidth']=0.8
    plt.rcParams['xtick.color']='#333F4B'
    plt.rcParams['ytick.color']='#333F4B'
    plt.tick_params(axis='x', which='major')
    ax.axes.get_xaxis().set_visible(False)
    plt.box(False)
    for i, bar in enumerate(list(Summoners.values())):
        plt.text(bar, i, str(bar),fontsize=10)
    #
    plt.xlim(xmin=0)
    return plt.gcf()

def plot_to_img(plot):
    imgdata = BytesIO()
    plot.savefig(imgdata, format='png',transparent=True)
    imgdata.seek(0)
    Image = utils.ImageReader(imgdata)  
    return Image

def get_image(path, width=1*mm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

def allowed_editions(editions :List[int]) ->List[str]:
    alpha_icon = os.environ.get('ALPHA_ICON')
    beta_icon = os.environ.get('BETA_ICON')
    promo_icon = os.environ.get('PROMO_ICON')
    reward_icon = os.environ.get('REWARD_ICON')
    untamed_icon = os.environ.get('UNTAMED_ICON')
    dice_icon = os.environ.get('DICE_ICON')
    chaos_icon = os.environ.get('CHAOS_ICON')    
    edition_dict= {0:alpha_icon,1:beta_icon,2:promo_icon,3:reward_icon,4:untamed_icon,5:dice_icon,7:chaos_icon}
    allowed_editions = []
    if editions:
        for i in editions:
            allowed_editions.append(get_image(edition_dict[i], width=7*mm))
            allowed_editions.append(Spacer(2*mm, 2*mm))
    else:
        allowed_editions = [
            get_image(alpha_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(beta_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(promo_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(reward_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(untamed_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(dice_icon, width=7*mm),Spacer(2*mm, 2*mm),
            get_image(chaos_icon, width=7*mm)]
    return allowed_editions

def first_page(general_info,pdf_title,tournament_id):
    
    load_dotenv(os.getcwd())
    resp = requests.get(general_info['sponsor_logo_url'],stream=True)
    tournamentLogo = utils.ImageReader(PIL.Image.open(BytesIO(resp.content)))
    splinterlands_logo =   os.environ.get("SPLINTERLANDS_LOGO")
    template1 = os.environ.get('TEMPLATE1')
    novice_icon = os.environ.get('NOVICE_ICON')
    bronze_icon = os.environ.get('BRONZE_ICON')
    silver_icon = os.environ.get('SILVER_ICON')
    gold_icon = os.environ.get('GOLD_ICON')
    diamond_icon = os.environ.get('DIAMOND_ICON')
    legendary_icon = os.environ.get('LEGENDARY_ICON')
    no_legendary_icon = os.environ.get('NO_LEGENDARY_ICON')
    no_legendary_summoners = os.environ.get('NO_LEGENDARY_SUMMONERS')
    
    league_dict_icons = {0:novice_icon,1:bronze_icon,2:silver_icon,3:gold_icon,4:diamond_icon}
    legendary_rulings_dict = {"no_legendaries":no_legendary_icon,'all':legendary_icon,"no_legendary_summoners":no_legendary_summoners} 

    imgDoc = canvas.Canvas('./pdfs/'+pdf_title+'.pdf',pagesize=landscape(A4))    
    imgDoc.setFillColorRGB(218/255,241/255,248/255)
    imgDoc.rect(0,0,95*mm,100*mm,fill=1,stroke=0)
    imgDoc.rect(105*mm,0,192*mm,100*mm,fill=1,stroke=0)
    imgDoc.rect(0*mm,110*mm,297*mm,100*mm,fill=1,stroke=0)

    #imgDoc.drawImage(template1,0,0,A4[1],A4[0], mask='auto') ## PDF Background
    imgDoc.drawImage(tournamentLogo, 30, A4[0]-47*mm-60/2*mm, 60*mm, 60*mm, mask='auto')    ## TournamentLogo
    imgDoc.drawImage(splinterlands_logo, 208*mm, 5*mm , 90*mm, 90*mm, mask='auto')    ## Splinterlands Logo
    
    tournament_title_frame = Frame(120*mm,185*mm, 150*mm , 20*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph(general_info['name'].replace("\n", "<br />"), styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    tournament_title_frame.addFromList([story_inframe1], imgDoc) ## Tournament Title

    desc_frame = Frame(125*mm,113*mm,169*mm,75*mm)
    story2 = [Paragraph(general_info['description'].replace("\n", "<br />"), styles['Normal'])]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    desc_frame.addFromList([story_inframe2], imgDoc) ## Tournament Description Text

    editions = allowed_editions(general_info['data']['allowed_cards']['editions']) #Editions Allowed
    edition_frame = Frame(110*mm,5*mm,16*mm,80*mm,showBoundary=0)
    edition_frame.addFromList(editions, imgDoc)

    league_frame = Frame(133*mm,5*mm,16*mm,90*mm,showBoundary=0)
    league_frame.addFromList([ ##League Cap and Legendary Allowed
    Spacer(2*mm,15*mm),
    get_image(league_dict_icons[general_info['data']['rating_level']], width=15*mm),Spacer(2*mm, 2*mm),
    get_image(legendary_rulings_dict[general_info['data']['allowed_cards']['type']], width=15*mm)]
    , imgDoc)
    
    entrants_frame = Frame(3*mm,3*mm,89*mm,75*mm,showBoundary=0)
    entrants_frame_story = [
    Paragraph('Tournament id: ' + tournament_id, styles['Normal']),    
    Paragraph('&nbsp Minimum Entrants:' + str(general_info['min_entrants']), styles['Normal']),
    Paragraph('&nbsp Maximum Entrants:' + str(general_info['max_entrants']), styles['Normal']),
    Paragraph('&nbsp Total Entrants:' + str(len(general_info['players'])),   styles['Normal'])
    ]
    entrants_frame_story_inframe = KeepInFrame(A4[0], A4[1], entrants_frame_story)
    entrants_frame.addFromList([entrants_frame_story_inframe],imgDoc)


    if general_info['data']['alternate_fee']['value'] == 'none':
        alternative_fee_text = "&nbsp Alternative Fee : None"
    elif league_dict[general_info['data']['alternate_fee']['min_league']] != league_dict[general_info['data']['alternate_fee']['max_league']]:
        alternative_fee_text = f"&nbsp Alternative Fee: {general_info['data']['alternate_fee']['value']} for  {league_dict[general_info['data']['alternate_fee']['min_league']]} to {league_dict[general_info['data']['alternate_fee']['max_league']]}"
    else:
        alternative_fee_text = f"&nbsp Alternative Fee: {general_info['data']['alternate_fee']['value']} for  {league_dict[general_info['data']['alternate_fee']['min_league']]}"

    if general_info['data']['spsp_min']:
        min_sps_text = f"&nbsp Minimum SPS stacked: {general_info['data']['spsp_min']}"
    else:
        min_sps_text = f'&nbsp Minimum SPS stacked: 0'

    tournament_fee_frame = Frame(103.5*mm,105*mm,95*mm,24*mm,showBoundary=0)
    tournament_fee_frame_story = [Paragraph("&nbsp Entry Fee:" + general_info['entry_fee'],styles['Normal']),
    Paragraph(alternative_fee_text,   styles['Normal']),
    Paragraph(f"&nbsp Minimum Power: {general_info['data']['cp_min']}",   styles['Normal']),
    Paragraph(min_sps_text,   styles['Normal']),    
    Paragraph('&nbsp Tournament Start Date:' + iso8601.parse_date(general_info['start_date']).strftime('%X %x %Z'),   styles['Normal']),
    Paragraph('&nbsp Prize in USD:' + str(general_info['total_prizes_usd']),   styles['Normal']),
    Paragraph(f"&nbsp Tournament Format: {general_info['format'].replace('_', ' ')}",   styles['Normal']),
    ]
    tournament_fee_frame_story_inframe = KeepInFrame(A4[0], A4[1], tournament_fee_frame_story)
    entrants_frame.addFromList([tournament_fee_frame_story_inframe],imgDoc)
    imgDoc.showPage()
    return imgDoc

def second_page(doc,tournament_df):
    doc.setFillColorRGB(1,0.95,0.918)
    doc.rect(0,0,150*mm,120*mm,fill=1,stroke=0)
    doc.rect(155*mm,0,142*mm,210*mm,fill=1,stroke=0)
    #doc.setFillColorRGB(0.84,0.94,0.97)
    doc.setFillColorRGB(255/255,228/255,183/255)
    doc.rect(0*mm,125*mm,150*mm,85*mm,fill=1,stroke=0)


    summoner_distribution = pd.concat([tournament_df['team1summoner'],tournament_df['team2summoner']]).value_counts().to_dict()
    color_distribution = pd.concat([tournament_df['team1summoner_color'],tournament_df['team2summoner_color']]).value_counts().to_dict()
    picked_color = sorted(color_distribution.items(), key=lambda item: item[1],reverse=True)[0][0]

    element_dict = {'Blue':'Water','White':'Life','Gold':'Dragon','Black':'Death','Green':'Earth','Red':'Fire'}
    color_dict = {'Gold':'#ffa900','White':'#EDE9DF','Black':'#c064ff','Blue':'#1761ff','Red':'#ff6860','Green':'#40b700'}

    labels = []
    data = []
    colors = []
    for x, y in color_distribution.items():
        labels.append(element_dict[x])
        data.append(y)
        colors.append(color_dict[x])    

    if picked_color == 'Blue':
        title = 'Another glimpse of the madman across the Water'
    elif picked_color == 'Red':
        title = 'Come on baby, light my Fire'
    elif picked_color == 'Black':
        title = "The lust of Death's possession"
    elif picked_color == 'White':
        title =  "All my Life, I've been searching for something"
    elif picked_color == 'Green':
        title = 'Read between the sky and every piece of the Earth'
    elif picked_color == 'Gold':
        title = "Hey it's a Dragon attack"
    else:
        title = "Well, that's awkward"


    Page_title_frame= Frame(3*mm,155*mm, 145*mm , 25*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph(title, styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    Page_title_frame.addFromList([story_inframe1], doc)

    popular_element = element_dict[picked_color]
    total_picks = sum(color_distribution.values())
    desc= Frame(3*mm,120*mm, 145*mm , 40*mm, showBoundary=0)
    story2 = [Paragraph(f'{popular_element} was the most picked element, with {color_distribution[picked_color]} of {total_picks}! These are the amount each Element and Summoner were chosen, forfeited games are not taken into account:', styles['Normal'])]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    desc.addFromList([story_inframe2], doc) 



    summoner_color_pie = pie_plot(data,(1,0.95,0.918),colors = colors, labels = labels,shadow=False)
    doc.drawImage(plot_to_img(summoner_color_pie), 10*mm,0,120*mm, 120*mm,mask='auto')
    
    summoner_plot = horizontal_bar_plot(summoner_distribution,(120/25.4,198/25.4),250)

    doc.drawImage(plot_to_img(summoner_plot), 165*mm,10*mm,120*mm, 198*mm,mask='auto')
    doc.showPage()
    return doc

def third_page(doc,tournament_df):
    doc.setFillColorRGB(0.95,0.99,0.91)
    doc.rect(0,0,15*mm,210*mm,fill=1,stroke=0)
    doc.rect(130*mm,0,167*mm,210*mm,fill=1,stroke=0)
    #doc.setFillColorRGB(0.95,0.95,0.95)
    doc.setFillColorRGB(0.85,0.99,0.80)
    doc.rect(15*mm,0,115*mm,210*mm,fill=1,stroke=0)
    m_chart = matchup_chart(tournament_df,(161/25.4,161*1.15/25.4),250)
    doc.drawImage(plot_to_img(m_chart), 133*mm,8*mm,161*mm, 180*mm,mask='auto')

    Page_title_frame= Frame(16*mm,100*mm, 113*mm , 20*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph('Know Your Enemy', styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    Page_title_frame.addFromList([story_inframe1], doc)

    desc= Frame(20*mm,20*mm, 108*mm , 85*mm, showBoundary=0)
    story2 = [Paragraph(f'Need help beating the meta? Find out how well any summoner did against the top 5 most picked Summoners!', styles['Normal'])]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    desc.addFromList([story_inframe2], doc) 

    doc.showPage()
    return doc

def forth_page(doc,tournament_df):
    #doc.setFillColorRGB(238/255,221/255,255/255)
    doc.setFillColorRGB(255/255,255/255,255/255)
    doc.rect(0,190*mm,297*mm,20*mm,fill=1,stroke=0)

    doc.setFillColorRGB(255/255,228/255,183/255)
    doc.rect(0*mm,0,99*mm,190*mm,fill=1,stroke=0)

    doc.setFillColorRGB(218/255,241/255,248/255)
    doc.rect(99*mm,0,99*mm,190*mm,fill=1,stroke=0)

    doc.setFillColorRGB(242.25/255,252.45/255,211.1655/255)
    doc.rect(99*2*mm,0,99*mm,190*mm,fill=1,stroke=0)


    red_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='Red'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='Red'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    red_monster_chart = horizontal_bar_plot(red_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(red_monster_chart), 0*mm,0*mm,99*mm, 190*mm,mask='auto')

    blue_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='Blue'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='Blue'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    blue_monster_chart = horizontal_bar_plot(blue_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(blue_monster_chart), 99*mm,0*mm,99*mm, 190*mm,mask='auto')

    green_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='Green'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='Green'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    green_monster_chart = horizontal_bar_plot(green_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(green_monster_chart), 99*2*mm,0*mm,99*mm, 190*mm,mask='auto')

    Page_title_frame= Frame(99*mm,190*mm, 99*mm , 20*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph('Scary monsters, super creeps', styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    Page_title_frame.addFromList([story_inframe1], doc)

    desc= Frame(101*mm,190*mm, 99*mm , 10*mm, showBoundary=0)
    story2 = [Paragraph(f'Top 50 picked monsters as each element', styles['Normal'])]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    desc.addFromList([story_inframe2], doc) 

    doc.showPage()
    return doc

def fifth_page(doc,tournament_df):
    #doc.setFillColorRGB(238/255,221/255,255/255)
    doc.setFillColorRGB(255/255,255/255,255/255)
    doc.rect(0,190*mm,297*mm,20*mm,fill=1,stroke=0)

    doc.setFillColorRGB(237/255,233/255,223/255)
    doc.rect(0*mm,0,99*mm,190*mm,fill=1,stroke=0)

    doc.setFillColorRGB(238/255,221/255,255/255)
    doc.rect(99*mm,0,99*mm,190*mm,fill=1,stroke=0)

    doc.setFillColorRGB(243/255,233/255,190/255)
    doc.rect(99*2*mm,0,99*mm,190*mm,fill=1,stroke=0)


    white_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='White'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='White'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    white_monster_chart = horizontal_bar_plot(white_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(white_monster_chart), 0*mm,0*mm,99*mm, 190*mm,mask='auto')

    black_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='Black'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='Black'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    black_monster_chart = horizontal_bar_plot(black_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(black_monster_chart), 99*mm,0*mm,99*mm, 190*mm,mask='auto')

    gold_monster_count = pd.concat([tournament_df.iloc[:,-12:-6][tournament_df['team1summoner_color']=='Gold'].reset_index(drop=True),tournament_df.iloc[:,-6:][tournament_df['team2summoner_color']=='Gold'].reset_index(drop=True)],axis=1).apply(pd.Series.value_counts).sum(axis=1).sort_values().astype(int)
    gold_monster_chart = horizontal_bar_plot(gold_monster_count[-50:],(99/25.4,190/25.4),250)
    doc.drawImage(plot_to_img(gold_monster_chart), 99*2*mm,0*mm,99*mm, 190*mm,mask='auto')

    Page_title_frame= Frame(99*mm,190*mm, 99*mm , 20*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph('Scary monsters, super creeps', styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    Page_title_frame.addFromList([story_inframe1], doc)

    desc= Frame(101*mm,190*mm, 99*mm , 10*mm, showBoundary=0)
    story2 = [Paragraph(f'Top 50 picked monsters as each element', styles['Normal'])]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    desc.addFromList([story_inframe2], doc) 

    doc.showPage()
    return doc

def sixth_to_ninth_page(doc,tournament_df,general_info):
    #doc.setFillColorRGB(238/255,221/255,255/255)
    titles = ["When I First wanted I never ever thought twice","Ain't in the race for Second place","It's quite possible that I'm your Third man, girl"]

    for i in range(0,3):
        player_d = splinterlands_tournament_info.player_details(general_info["players"][i]['player'])
        styles = getSampleStyleSheet()
        doc.setFillColorRGB(218/255,241/255,248/255)
        doc.rect(0*mm,0,99*2*mm,210*mm,fill=1,stroke=0)
        #doc.setFillColorRGB(164/255,197/255,208/255)
        doc.rect(99*2*mm+2*mm,0,97*mm,210*mm,fill=1,stroke=0)


        player_join_date = datetime.datetime.strptime(player_d['join_date'],"%Y-%m-%dT%H:%M:%S.%fZ").date().strftime('%m/%d/%Y')
        player_rating = player_d['rating']
        player_power = player_d['collection_power']
        league = league_dict[player_d['league']]

        player_frame = Frame(10*mm,140*mm,99*2*mm-10*mm,50*mm,showBoundary=0)
        player_frame_story = [
        Paragraph('Player Name: ' + general_info["players"][i]['player'], styles['Normal']),    
        Paragraph('Player since: ' + player_join_date, styles['Normal']),    
        Paragraph('Player Power:' + str(player_power), styles['Normal']),
        Paragraph('Player Rating:' + str(player_rating), styles['Normal']),
        Paragraph('Current League: ' + league,   styles['Normal']),
        Paragraph(f"Won Against: {','.join(tournament_df[tournament_df['winner'] == general_info['players'][i]['player']]['loser'].to_list())}" ,styles['Normal']),
        Paragraph(f"Lost to: {','.join(tournament_df[tournament_df['loser'] == general_info['players'][i]['player']]['winner'].to_list())}" ,styles['Normal'])
        ]
        player_frame_story_inframe = KeepInFrame(A4[0], A4[1], player_frame_story)
        player_frame.addFromList([player_frame_story_inframe],doc)


        player_summoners = pd.concat([tournament_df.loc[(tournament_df['player1']==general_info["players"][i]['player'])]['team1summoner'],tournament_df.loc[(tournament_df['player2']==general_info["players"][i]['player'])]['team2summoner']]).value_counts()
        player_summoners_graph = horizontal_bar_plot(player_summoners,((99)/25.4,105/25.4),250)
        doc.drawImage(plot_to_img(player_summoners_graph), 45.5*mm,10*mm,99*mm, 105*mm,mask='auto')

        Page_title_frame= Frame(99*2*mm,105*mm, 99*mm , 20*mm, showBoundary=0)
        styles = getSampleStyleSheet()
        story1 = [Paragraph(titles[i], styles['Title'])]
        story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
        Page_title_frame.addFromList([story_inframe1], doc)

        desc= Frame(99*2*mm+ 7.3*mm,98*mm, (297-99*2-7.3)*mm , 10*mm, showBoundary=0)
        story2 = [Paragraph(f'Summoners chosen by ' + general_info["players"][i]['player'], styles['Normal'])]
        story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
        desc.addFromList([story_inframe2], doc) 

        
        doc.showPage()

    return doc

def tenth_page(doc,players_report):

    splinterlands_info = splinterlands_tournament_info.splinterlands_general_info()
    season_end_date = datetime.datetime.strptime(splinterlands_info['season']['ends'],"%Y-%m-%dT%H:%M:%S.%fZ")
    splinterlands_time = datetime.datetime.utcfromtimestamp((splinterlands_info['timestamp']/1000))
    days_until_eos = (season_end_date-splinterlands_time).days


    doc.setFillColorRGB(218/255,241/255,248/255)
    doc.rect(0*mm,0,235*mm,170*mm,fill=1,stroke=0)
    doc.rect(237*mm,0,60*mm,170*mm,fill=1,stroke=0)
    doc.rect(0*mm,172*mm,297*mm,38*mm,fill=1,stroke=0)

    plt.rcParams["figure.figsize"] = (235/25.4,170*(1+len(players_report['power_league'].unique())//4)/2/25.4)
    plt.rcParams["figure.dpi"] = 250
    
    plot = sns.relplot(data=players_report.rename(columns={'power_league': 'Power League','league':'League'}), x="collection_power",
     y=players_report["wins"]*100/(players_report['wins']+players_report['losses']), hue="League",col='Power League',col_wrap=3,facet_kws=dict(sharex=False)).set_axis_labels("Power", "Winrate %")
    doc.drawImage(plot_to_img(plot), 0*mm,0*mm,235*mm, 170*(1+len(players_report['power_league'].unique())//4)/2*mm,mask='auto')

    power_league_pie = pie_plot(players_report['power_league'].value_counts(),background_color=(218/255,241/255,248/255),labels = players_report['power_league'].value_counts().index,
    figsize=(54/25.4,54/25.4),fontsize = 7,shadow = False,pctdistance=.6, labeldistance=1.02,startangle= 45,left = 0.1,title= 'Players by Power League')
    doc.drawImage(plot_to_img(power_league_pie), 240*mm,90*mm,54*mm, 54*mm,mask='auto')

    power_league_pie = pie_plot(players_report['league'].value_counts(),background_color=(218/255,241/255,248/255),labels = players_report['league'].value_counts().index,
    figsize=(54/25.4,54/25.4),fontsize = 7,shadow = False,pctdistance=.6, labeldistance=1.02,startangle= 45,left = 0.1,title= 'Players by League')
    doc.drawImage(plot_to_img(power_league_pie), 240*mm,15*mm,54*mm, 54*mm,mask='auto')


    Page_title_frame= Frame(10*mm,188*mm, 2/3*297*mm , 20*mm, showBoundary=0)
    styles = getSampleStyleSheet()
    story1 = [Paragraph("You've got the money and the Power", styles['Title'])]
    story_inframe1 = KeepInFrame(A4[0], A4[1], story1)
    Page_title_frame.addFromList([story_inframe1], doc)


    subtitle = ParagraphStyle(name='subtitle',
                    parent=styles['Normal'],
                                       font='Helvetica-Bold',
                                       fontSize=16,
                                       leading=22,
                                       alignment=TA_LEFT,
                                       spaceBefore = 0)

    subt= Frame(54*mm,188*mm, 2/3*297*mm , 10*mm, showBoundary=0)
    story2 = [Paragraph("Find out how well did players from each league did!", subtitle)]
    story_inframe2 = KeepInFrame(A4[0], A4[1], story2) 
    subt.addFromList([story_inframe2], doc) 

    desc= Frame(5*mm,173*mm, 287*mm , 15*mm, showBoundary=0)
    story3 = [Paragraph("Power league meaning the league which the player has enough power to be in. League being the league where the player was in by the time the report was made.", styles['Normal'])]
    story_inframe3 = KeepInFrame(A4[0], A4[1], story3) 
    desc.addFromList([story_inframe3], doc) 

    eos_frame= Frame(297*mm-50*mm,173*mm, 50*mm , 15*mm, showBoundary=0)
    story4 = [Paragraph(f"Days until the end of the season: {days_until_eos}", styles['Normal'])]
    story_inframe4 = KeepInFrame(A4[0], A4[1], story4) 
    eos_frame.addFromList([story_inframe4], doc) 


    doc.showPage()
    return doc