import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

# Load your data
df = pd.read_csv("C://Users//Zeke//Downloads//overall_sales_1.csv")

# Convert dates
df['Entry Date'] = pd.to_datetime(df['Entry Date'], dayfirst=True, errors='coerce')
df['Month'] = df['Entry Date'].dt.to_period('M')
df['Month'] = df['Month'].dt.to_timestamp()

# Prepare data for different visualizations
# 1. Sales Agent Performance
agent_perf = df.groupby(['Sls Agnt', pd.Grouper(key='Entry Date', freq='ME')]).agg(
    Total_Sales=('Ext Price', 'sum'),
    Order_Count=('Ref Number', 'nunique')
).reset_index()

# 2. Product Category Performance
prod_cat_perf = df.groupby(['Prod Class', pd.Grouper(key='Entry Date', freq='ME')]).agg(
    Total_Sales=('Ext Price', 'sum'),
    Quantity_Sold=('Quantity', 'sum')
).reset_index()

# 3. Customer Purchase Patterns
cust_purchase = df.groupby(['Customer Name', pd.Grouper(key='Entry Date', freq='ME')]).agg(
    Purchase_Count=('Ref Number', 'nunique'),
    Total_Spend=('Ext Price', 'sum')
).reset_index()

# 4. Customer order rate overtime
order_counts = df.groupby(['Month','Customer Name']).size().reset_index(name='Order Count')

# 5. Product growth overtime
product_growth = df.groupby(['Month', 'Prod Class']).agg(
    Total_Sales=('Ext Price', 'sum'),
    Quantity_Sold=('Quantity', 'sum'),
    Order_Count=('Ref Number', 'nunique')
).reset_index()

#6. Top packages by sale
top_packages = df.groupby('Packaging')['Ext Price'].sum().sort_values(ascending=False).head(10).reset_index()
top_packages.columns = ['Packaging', 'Total Sales']


# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Multi-Graph Analytics Dashboard", style={'textAlign': 'center'}),
    
    # Graph selection dropdown
    html.Div([
        html.Label("Select Graph to Display:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='graph-selector',
            options=[
                {'label': 'Sales Agent Performance', 'value': 'agent'},
                {'label': 'Product Category Trends', 'value': 'product'},
                {'label': 'Customer Purchase Patterns', 'value': 'customer'},
                {'label': 'Customer Order Rate', 'value': 'customer_rate'},
                {'label': 'Product Growth Over Time', 'value': 'product-growth'},
                {'label': "Profit Analysis", 'value': 'profit-analysis'}],
            value='agent',
            clearable=False,
            style={'width': '50%', 'margin': '10px auto'}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Container for the selected graph and its controls
    html.Div(id='graph-container')
])

# Callback to show the selected graph and its controls
@app.callback(
    Output('graph-container', 'children'),
    [Input('graph-selector', 'value')]
)
def update_graph_container(selected_graph):
    if selected_graph == 'agent':
        agents = sorted(df['Sls Agnt'].unique())
        return [
            html.Div([
                html.Label("Select Sales Agent:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='agent-dropdown',
                    options=[{'label': agent, 'value': agent} for agent in agents],
                    value=agents[0] if agents else None,
                    clearable=False,
                    style={'width': '50%'}
                )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            
            dcc.Graph(id='agent-graph')
        ]
    elif selected_graph == 'product':
        categories = sorted(df['Prod Class'].unique())
        return [
            html.Div([
                html.Label("Select Product Category:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='product-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in categories],
                    value=categories[0] if categories else None,
                    clearable=False,
                    style={'width': '50%'}
                )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            
            dcc.Graph(id='product-graph')
        ]
    elif selected_graph == 'customer':
        customers = sorted(df['Customer Name'].unique())
        return [
            html.Div([
                html.Label("Select Customer:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='customer-dropdown',
                    options=[{'label': cust, 'value': cust} for cust in customers],
                    value=customers[0] if customers else None,
                    clearable=False,
                    style={'width': '50%'}
                )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            
            dcc.Graph(id='customer-graph')
        ]
    elif selected_graph == "customer_rate":
        customers = sorted(df['Customer Name'].unique())
        return [
            html.Div([
                html.Label("Select Customer:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='customer-rate-dropdown',
                    options=[{'label': cust, 'value': cust} for cust in customers],
                    value=customers[0] if customers else None,
                    clearable=False,
                    style={'width': '50%'}, 
                    searchable=True
                )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            dcc.Graph(id='customer-rate-graph')
        ]
    elif selected_graph == "product-growth":
        prod_name = sorted(df['Prod Class'].unique())
        return [
            html.Div([
                html.Label("Select Product:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='prod-growth-dropdown',
                    options=[{'label': prod, 'value': prod} for prod in prod_name],
                    value=prod_name[0] if prod_name else None,
                    clearable=False,
                    searchable=True,
                    style={'width': '50%'}
                )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            dcc.Graph(id='product-growth-graph')
        ]
    elif selected_graph == 'profit-analysis':
        pack = sorted(df['Packaging'].unique())
        prod = sorted(df['Product Name'].unique())
        agents = sorted(df['Sls Agnt'].unique())
        cust  = sorted(df['Customer Name'].unique())
        return [
            html.Div([
                html.P("Profit or Gross Profit Percentage", style={'fontWeight': 'bold', 'textAlign':'Left'}),
                dcc.Dropdown(
                    id ='profit-gpp-dropdown',
                    options=['Profit',"Gross Profit Percentage"],
                    value = None,
                    clearable = False,
                    style = {'width': '50%','margin-bottom': '20px'}
                    ),
                    
                html.P("Packaging: ", style={'fontWeight': 'bold', 'textAlign':'Left'}),
                dcc.Dropdown(
                    id='packaging-dropdown',
                    options=[{'label': prod, 'value': prod} for prod in pack],
                    value=None,
                    clearable=True,
                    searchable=True,
                    style={'width': '50%','margin-bottom': '20px'}
                ), html.P("Product", style={'fontWeight': 'bold','textAlign':'left'}),
                dcc.Dropdown(
                    id = 'product-dropdown-profit',
                    options = [{'label': x,'value':x} for x in prod],
                    value=None,
                    clearable=True,
                    searchable=True,
                    style={'width': '50%'}
                    ), html.P("Sales Agent", style = {'fontWeight': 'bold','textAlign': 'left'}),
                dcc.Dropdown(
                    id = 'sls-agent-dropdown',
                    options = [{'label': x, 'value':x } for x in agents],
                    value = None,
                    clearable = True,
                    searchable = True,
                    style = {'width': '50%'}
                    ),
                html.P("Customer: ", style = {'fontWeight': 'bold','textAlign': 'Left'}),
                dcc.Dropdown(
                    id = "cust-dropdown",
                    options = [{'label':x, 'value':x } for x in cust],
                    value=None,
                    clearable = True,
                    searchable = True,
                    style = {'width': '50%'}
                    )
            ], style={'padding': '20px', 'textAlign': 'center'}),
            dcc.Graph(id='profit-graph')
        ]

# Callbacks for each graph type
@app.callback(
    Output('agent-graph', 'figure'),
    [Input('agent-dropdown', 'value')]
)
def update_agent_graph(selected_agent):
    if selected_agent is None:
        raise PreventUpdate
        
    agent_data = agent_perf[agent_perf['Sls Agnt'] == selected_agent]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agent_data['Entry Date'],
        y=agent_data['Total_Sales'],
        name='Total Sales',
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Bar(
        x=agent_data['Entry Date'],
        y=agent_data['Order_Count'],
        name='Order Count',
        yaxis='y2',
        marker_color='lightseagreen'
    ))
    
    fig.update_layout(
        title=f'Sales Performance for {selected_agent}',
        xaxis_title='Month',
        yaxis_title='Total Sales ($)',
        yaxis2=dict(
            title='Order Count',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified'
    )
    
    return fig

@app.callback(
    Output('product-graph', 'figure'),
    [Input('product-dropdown', 'value')]
)
def update_product_graph(selected_category):
    if selected_category is None:
        raise PreventUpdate
        
    category_data = prod_cat_perf[prod_cat_perf['Prod Class'] == selected_category]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=category_data['Entry Date'],
        y=category_data['Total_Sales'],
        name='Total Sales',
        line=dict(color='firebrick', width=2)
    ))
    fig.add_trace(go.Bar(
        x=category_data['Entry Date'],
        y=category_data['Quantity_Sold'],
        name='Quantity Sold',
        marker_color='goldenrod'
    ))
    
    fig.update_layout(
        title=f'Sales Trends for {selected_category}',
        xaxis_title='Month',
        yaxis_title='Total Sales ($)',
        hovermode='x unified',
        barmode='group'
    )
    
    return fig

@app.callback(
    Output('customer-graph', 'figure'),
    [Input('customer-dropdown', 'value')]
)
def update_customer_graph(selected_customer):
    if selected_customer is None:
        raise PreventUpdate
        
    customer_data = cust_purchase[cust_purchase['Customer Name'] == selected_customer]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=customer_data['Entry Date'],
        y=customer_data['Total_Spend'],
        name='Total Spend',
        line=dict(color='darkgreen', width=2)
    ))
    fig.add_trace(go.Bar(
        x=customer_data['Entry Date'],
        y=customer_data['Purchase_Count'],
        name='Purchase Count',
        marker_color='mediumpurple',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'Purchase Patterns for {selected_customer}',
        xaxis_title='Month',
        yaxis_title='Total Spend ($)',
        hovermode='x unified',
        yaxis2=dict(
            title='Purchase Count',
            overlaying='y',
            side='right'
        )
    )
    
    return fig

@app.callback(
    Output('customer-rate-graph', 'figure'),
    [Input('customer-rate-dropdown', 'value')]
)
def update_customer_rate_graph(selected_customer_rate):
    if not selected_customer_rate:
        raise PreventUpdate
        
    customer_rate_data = order_counts[order_counts['Customer Name'] == selected_customer_rate]
    
    fig = px.line(
        customer_rate_data,
        x="Month",
        y='Order Count',
        markers=True,
        title=f"Order Rate Over Time for {selected_customer_rate}",
        labels={"Month": "Order Month", "Order Count": "Number of Orders"}
    )

    # Add red markers where orders exist
    fig.add_trace(go.Scatter(
        x=customer_rate_data[customer_rate_data['Order Count'] > 0]['Month'],
        y=customer_rate_data[customer_rate_data['Order Count'] > 0]['Order Count'],
        mode='markers',
        marker=dict(color='red', size=8),
        name='Actual Orders'
    ))

    fig.update_layout(
        xaxis=dict(dtick="M1", tickformat="%b\n%Y"),
        hovermode="x unified"
    )

    return fig

@app.callback(
    Output('product-growth-graph', 'figure'),
    [Input('prod-growth-dropdown', 'value')]
)
def update_prod_growth_rate_graph(selected_prod):
    if selected_prod is None:
        raise PreventUpdate
        
    category_data = product_growth[product_growth['Prod Class'] == selected_prod]
    
    fig = px.line(
        category_data,
        x='Month',
        y='Total_Sales',
        markers=True,
        title=f'Sales Growth Over Time for {selected_prod}',
        labels={
            'Month': 'Month',
            'Total_Sales': 'Total Sales ($)'
        }
    )
    
    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(dtick='M1', tickformat='%b\n%Y')
    )
    return fig

@app.callback(
    Output('profit-graph','figure'),
    [Input("packaging-dropdown",'value'),
     Input('product-dropdown-profit','value'),
     Input("cust-dropdown",'value'),
     Input('sls-agent-dropdown', 'value'),
     Input('profit-gpp-dropdown','value')]
    )
def update_profit_graph(selected_packaging, selected_product, selected_cust, selected_agent, gpp_profit):
 
    filtered_df = df.copy()
    title_parts = []
    
    if selected_packaging:
        if isinstance(selected_packaging, str):
            selected_packaging = [selected_packaging]
        filtered_df = filtered_df[filtered_df['Packaging'].isin(selected_packaging)]
        title_parts.append(f"Packaging: {', '.join(selected_packaging)}")
    
    if selected_product:
        if isinstance(selected_product, str):
            selected_product = [selected_product]
        filtered_df = filtered_df[filtered_df['Product Name'].isin(selected_product)]
        title_parts.append(f"Product: {', '.join(selected_product)}")
        
    if selected_cust:
        if isinstance(selected_cust, str):
            selected_cust = [selected_cust]
        filtered_df = filtered_df[filtered_df['Customer Name'].isin(selected_cust)]
        title_parts.append(f"Packaging: {', '.join(selected_cust)}")
        
    if selected_agent:
        if isinstance(selected_agent, str):
            selected_agent = [selected_agent]
        filtered_df = filtered_df[filtered_df['Sls Agnt'].isin(selected_agent)]
        title_parts.append(f"Packaging: {', '.join(selected_agent)}")

    # Group by month and calculate profit
    if gpp_profit == 'Gross Profit Percentage':
        
        profit_by_month = filtered_df.groupby('Month')['Gross Profit Percentage'].sum().reset_index()
        
        fig = px.bar(
            profit_by_month,
            x='Month',
            y='Gross Profit Percentage',
            title="Monthly Profit - " + " | ".join(title_parts),
            labels={'Month': 'Month', 'Profit': 'Profit ($)'}
        )
        fig.update_layout(
           xaxis=dict(tickformat="%b\n%Y"), 
            hovermode='x unified',
            barmode='group'
       )  
        return fig
        
    elif gpp_profit == 'Profit':
        
        profit_by_month = filtered_df.groupby('Month')['Profit'].sum().reset_index()
        
        fig = px.bar(
            profit_by_month,
            x='Month',
            y='Profit',
            title="Monthly Profit - " + " | ".join(title_parts),
            labels={'Month': 'Month', 'Profit': 'Profit ($)'}
        )
        fig.update_layout(
           xaxis=dict(tickformat="%b\n%Y"), 
            hovermode='x unified',
            barmode='group'
       )  
        return fig
    
    
   

    
server = app.server

if __name__ == '__main__':
    app.run(debug=True)