from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

#load data
def load_data():
    df=pd.read_csv("assets/amazon_sales_2025.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce', format="%d-%m-%y")
    df['Week'] = df['Date'].dt.strftime('%Y-W%U')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    return df
df = load_data()

#Global variables
total_orders = len(df)
total_revenue = df['Total Sales'].sum()
payment_methods = [{'label': method, 'value': method} for method in df['Payment Method'].unique()]
location = [{'label': location, 'value': location} for location in df['Customer Location'].unique()]
category = [{'label': category, 'value': category} for category in df['Category'].unique()]

#create web app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#app layout and design
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Amazon Dashboard"), width=15, className="text-center my-1")
    ]), 
#Descriptive stats
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(f"Total Orders: {total_orders}", className="card-text"),
                    html.Div(f"Total Revenue: {total_revenue}", className="card-text"),
                ]),
                className="shadow-sm p-3"
            ),
            width=6
        )
    ], className="d-flex justify-content-center mb-4"),
    
                
#Payment method
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Payment Methods Distributtion", className="card-title"),
                    dcc.Dropdown(
                         id="payment_filter", 
                         options= payment_methods,
                         value=None,
                         placeholder= "Select Payment Method"
                    ),
                    dcc.Graph(id="payment_method")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Order Status", className="card-title"),
                    dcc.Graph(id="order-status")
                ])

            ])
        ,], width=6)

    ]),

#Sales by category  
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Sales by customer location", className="card-title"),
                    dcc.RadioItems(
                         id="category_filter",
                         inline=True, 
                         options= category,
                         inputStyle={"margin-left": "10px"}
                    ),

                    dcc.Graph(id="sales-category")
                ])
            ])
        ], width= 12)
    ]),

#Sales by product type
   
#Sales trends
    dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Sales Trends", className="card-title"),
                        dcc.RadioItems(
                            id="chart-type",
                            options=[{"label":"Line Chart", 'value':'line'}, {"label":"Bar Chart", 'value':'bar'}],
                            value='line',
                            inline=True,
                            className='mb-4'
                            

                        ),  
                        dcc.Dropdown(
                         id='location filter', 
                         options= location,
                         value=None,
                         placeholder= "Select a location"
                        ),
                        dcc.Graph(
                            id="Sales Trends per location"
                        )
                
                    ])
                ])
            ], width= 12)
        ])
], fluid=True)




#Create callbacks
#Payment method distribution
@app.callback(
    Output('payment_method', 'figure'),
    Input('payment_filter', 'value')
)
def update_payment_distribution(payment_chosen): 
    if payment_chosen:
        filtered_df = df[df["Payment Method"]== payment_chosen]
    else:
        filtered_df = df

    if filtered_df.empty:
        return {}
    
    fig = px.histogram(
        filtered_df,
        x='Total Sales',
        #y=,
        color= "Payment Method",
        nbins=10,
        title="Distribution of payment methods used"
    )

    return fig


#oder status proportions
@app.callback(
    Output("order-status", 'figure'),
    Input("payment_filter", 'value')
)
def update_order_status(payment_chosen):
    filtered_df = df[df['Payment Method']== payment_chosen] if payment_chosen else df
    fig = px.pie(
        filtered_df,
        names ='Status',
        title= 'Order Status percentages',
        color= "Status"
        )
    return fig

#location comparison
@app.callback(
    Output("sales-category", "figure"),
    Input("category_filter", 'value')
)

def update_location(chosen_category):
    filtered_df = df[df['Category']== chosen_category] if chosen_category else df
    fig = px.histogram(filtered_df, x= "Customer Location", y="Total Sales", title='Total sales per product category and location')
    return fig

#Sales trend
@app.callback(
    Output("Sales Trends per location", "figure"),
    Input("chart-type", "value"),
    Input("location filter", "value")
)

def update_trends(chart_type, selected_location):
    filtered_df = df[df["Customer Location"] == selected_location] if selected_location else df 

    trend_df = filtered_df.groupby("Date")["Total Sales"].sum().reset_index()
    trend_df["Date"] = trend_df["Date"].astype(str)

    if chart_type == "line":
        fig = px.line(trend_df, x="Date", y="Total Sales", title='Daily sales')
    else:
        fig = px.bar(trend_df, x="Date", y="Total Sales", title='Daily sales')    

    return fig

if __name__ == "__main__":
    app.run(debug=True)
