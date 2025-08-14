import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

df = pd.read_csv("KaggleV2-May-2016.csv")

# Convert date columns to datetime
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])

# Extract day of week from appointment date
df['DayOfWeek'] = df['AppointmentDay'].dt.day_name()

# Calculate no-show and show-up rates by day of week
day_data = df.groupby('DayOfWeek')['No-show'].value_counts(normalize=True).unstack() * 100
day_data = day_data.astype(int)
day_data = day_data.reset_index()
day_data = day_data.rename(columns={'Yes': 'No-show Rate %', 'No': 'Show-up Rate %'})
day_data['y'] = 'No-show Rate %'

# Create show_status column (0 = showed up, 1 = no-show)
df['show_status'] = df['No-show'].map({'No': 0, 'Yes': 1})

# Count total shows and no-shows
show_counts = df['show_status'].value_counts().rename(index={0: 'Showed Up', 1: 'No-show'})

# Age groups
bins = [0, 12, 18, 60, 100]
labels = ['Child', 'Teen', 'Adult', 'Old']
df['age_class'] = pd.cut(df['Age'], bins=bins, labels=labels)

#no-show rate by age group and gender
grouped = df.groupby(['age_class', 'Gender'])['show_status'].mean().reset_index()
grouped['show_status'] = (grouped['show_status'] * 100).astype(int)

# bar chart: overall show-up vs no-show
fig1 = px.bar(
    x=show_counts.index,
    y=show_counts.values,
    labels={'x': 'Status', 'y': 'Count'},
    title='No-show vs Show-up Rates'
)

# bar chart: no-show rate by age group and gender
fig2 = px.bar(
    grouped,
    x='age_class',
    y='show_status',
    color='Gender',
    barmode='group',
    labels={'age_class': 'Age Class', 'show_status': 'No-show Rate %'},
    title='Age and Gender Impact on No-show Rates'
)

# bar chart: no-show rate by day of week
fig3 = px.bar(
    day_data,
    x='DayOfWeek',
    y='No-show Rate %',
    color='No-show Rate %',
    color_continuous_scale='Reds',
    title='No-show Rate by Day of Week'
)


app = Dash(__name__)
app.title = "Medical Appointment No-Show Dashboard"


app.layout = html.Div([
    html.H1("Medical Appointment No-Show Dashboard", style={'textAlign': 'center'}),

    dcc.Tabs([
        # Tab 1: Overall no-show vs show-up
        dcc.Tab(label='Overall No-show vs Show-up', children=[
            html.Div([
                html.H3("No-show vs Show-up Rates", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig1)
            ], style={'padding': '20px'})
        ]),
        # Tab 2: Age & gender analysis
        dcc.Tab(label='Age & Gender Analysis', children=[
            html.Div([
                html.H3("Impact of Age & Gender on No-show Rates", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig2)
            ], style={'padding': '20px'})
        ]),
        # Tab 3: Day of week analysis
        dcc.Tab(label='Day of Week Analysis', children=[
            html.Div([
                html.H3("No-show Rate by Day of the Week", style={'textAlign': 'center'}),
                dcc.Graph(figure=fig3)
            ], style={'padding': '20px'})
        ])
    ])
])


if __name__ == '__main__':
    app.run(debug=True)

