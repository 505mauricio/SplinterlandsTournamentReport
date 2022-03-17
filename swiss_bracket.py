import pandas as pd
from pdf_report import matchup_chart
import seaborn as sns

def swiss_bracket(tournament_df:pd.DataFrame,figsize=(190/25.4,190/25.4),dpi=80):
    sns.set(font_scale=3)
    player_list = pd.unique(tournament_df[(tournament_df['phase']==1) & (tournament_df['group']==1)][['player1',"player2"]].values.ravel('K')).tolist()
    cmap = sns.diverging_palette(0, 150, 90, 60, as_cmap=True)
    filterA = "player1"
    filterB = "player2"
    bracket = matchup_chart(tournament_df[(tournament_df['phase']==1) & (tournament_df['group']==1)],player_list,filterA,filterB,cmap,figsize,dpi)
    return bracket