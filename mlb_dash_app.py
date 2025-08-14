import dash
from dash import dcc, html, dash_table
import pandas as pd
import elo
import statsapi
from datetime import datetime

# Run the notebook logic
schedule = statsapi.schedule(start_date='03/01/2025', end_date=datetime.today().strftime("%m/%d/%Y"))
schedule = [x for x in schedule if x["game_type"] == 'R' and x["status"] == "Final"]
teams = dict()
K = 800 / (len(schedule) * 2 / 30)
for game in schedule:
    if game["winning_team"] not in teams:
        teams[game["winning_team"]] = elo.Rating()
    if game["losing_team"] not in teams:
        teams[game["losing_team"]] = elo.Rating()
    elo.update_elo(teams[game["winning_team"]], teams[game["losing_team"]], K=K)
data = pd.DataFrame(data={
    "Team": teams.keys(),
    "Rating": [x.get_elo() for key, x in teams.items()]
})
data = data.sort_values("Rating", ascending=False)

# Dash app

# MLB logo URL (public domain or official MLB logo)
mlb_logo_url = "https://upload.wikimedia.org/wikipedia/commons/a/a6/Major_League_Baseball_logo.svg"


from dash.dependencies import Input, Output

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Img(src=mlb_logo_url, style={
            'height': '80px', 'marginBottom': '10px', 'display': 'block', 'marginLeft': 'auto', 'marginRight': 'auto'
        }),
        html.H1("MLB Elo Ratings", style={
            'textAlign': 'center',
            'color': '#002D72',
            'fontFamily': 'Arial Black, Arial, sans-serif',
            'marginBottom': '20px',
            'textShadow': '1px 1px 2px #888'
        }),
        # --- Probability Section ---
        html.Div([
            html.H2("Head-to-Head Win Probability", style={
                'textAlign': 'center',
                'color': '#002D72',
                'fontFamily': 'Arial Black, Arial, sans-serif',
                'marginBottom': '10px',
                'marginTop': '10px',
            }),
            html.Div([
                dcc.Dropdown(
                    id='team1-dropdown',
                    options=[{'label': t, 'value': t} for t in data['Team']],
                    value=data['Team'].iloc[0],
                    style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}
                ),
                dcc.Dropdown(
                    id='team2-dropdown',
                    options=[{'label': t, 'value': t} for t in data['Team']],
                    value=data['Team'].iloc[1],
                    style={'width': '48%', 'display': 'inline-block'}
                )
            ], style={'marginBottom': '10px', 'textAlign': 'center'}),
            html.Div(id='probability-output', style={
                'textAlign': 'center',
                'fontSize': '20px',
                'marginTop': '10px',
                'fontWeight': 'bold',
                'color': '#002D72',
                'background': '#e9ecef',
                'borderRadius': '8px',
                'padding': '10px',
                'maxWidth': '400px',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'boxShadow': '0 2px 8px 0 rgba(0,0,0,0.08)'
            })
        ], style={
            'background': 'rgba(255,255,255,0.95)',
            'borderRadius': '12px',
            'boxShadow': '0 4px 16px 0 rgba(0,0,0,0.10)',
            'padding': '18px 18px 10px 18px',
            'marginBottom': '24px',
            'marginTop': '10px',
            'border': '1px solid #e3e3e3',
            'maxWidth': '600px',
            'marginLeft': 'auto',
            'marginRight': 'auto'
        }),
        # --- Elo Table ---
        dash_table.DataTable(
            id='elo-table',
            columns=[{"name": i, "id": i} for i in data.columns],
            data=data.to_dict('records'),
            sort_action="native",
            style_table={
                'overflowX': 'auto',
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'boxShadow': '0 4px 24px 0 rgba(0,0,0,0.10)',
                'padding': '10px',
                'marginBottom': '20px'
            },
            style_cell={
                'textAlign': 'left',
                'fontFamily': 'Segoe UI, Arial, sans-serif',
                'fontSize': '18px',
                'padding': '8px',
                'backgroundColor': '#f8f9fa',
                'color': '#222'
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': '#002D72',
                'color': 'white',
                'fontSize': '20px',
                'borderTopLeftRadius': '12px',
                'borderTopRightRadius': '12px',
                'textAlign': 'center',
                'letterSpacing': '1px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#e9ecef'
                }
            ],
            style_as_list_view=True
        )
    ], style={
        'maxWidth': '600px',
        'margin': '40px auto',
        'background': 'rgba(255,255,255,0.95)',
        'borderRadius': '16px',
        'boxShadow': '0 8px 32px 0 rgba(0,0,0,0.18)',
        'padding': '32px 24px 24px 24px',
        'border': '1px solid #e3e3e3'
    })
], style={
    'minHeight': '100vh',
    'background': 'linear-gradient(135deg, #d1e7fd 0%, #f8f9fa 100%)',
    'padding': '0',
    'margin': '0'
})

# --- Callbacks for probability calculation ---
@app.callback(
    Output('probability-output', 'children'),
    [Input('team1-dropdown', 'value'), Input('team2-dropdown', 'value')]
)
def update_probability(team1, team2):
    if not team1 or not team2 or team1 == team2:
        return "Select two different teams."
    rating1 = float(data[data['Team'] == team1]['Rating'].values[0])
    rating2 = float(data[data['Team'] == team2]['Rating'].values[0])
    prob1 = elo.probability(elo.Rating(rating1), elo.Rating(rating2))
    prob2 = 1.0 - prob1
    return f"{team1} win probability: {prob1:.1%} | {team2} win probability: {prob2:.1%}"

if __name__ == "__main__":
    app.run(debug=True)
