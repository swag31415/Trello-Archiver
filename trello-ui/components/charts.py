"""Chart creation functions for Trello Archive UI."""
import plotly.graph_objects as go
import plotly.express as px
from utils.data_processing import process_completion_data, process_list_stats, process_complexity_data


def create_completion_trend_chart(completion_data, x_range=None):
    """
    Create a histogram showing card completion over time with fixed bins.

    Args:
        completion_data: List of completion data from database (day-level)
        x_range: Optional tuple of (start_date, end_date) to filter and set range

    Returns:
        plotly.graph_objects.Figure: Histogram chart
    """
    import pandas as pd

    if not completion_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No completion data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Card Completion Over Time",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            height=400
        )
        return fig

    # Convert to dataframe and parse dates
    df = pd.DataFrame(completion_data)

    # Parse the period as datetime
    df['date'] = pd.to_datetime(df['period'])

    # Filter by x_range if provided
    if x_range and len(x_range) == 2:
        start_date = pd.to_datetime(x_range[0])
        end_date = pd.to_datetime(x_range[1])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Create list of dates repeated by count for histogram
    dates = []
    for _, row in df.iterrows():
        dates.extend([row['date']] * int(row['count']))

    if not dates:
        # No data in range
        fig = go.Figure()
        fig.add_annotation(
            text="No completion data in selected range",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Card Completion Over Time",
            height=400
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=dates,
        nbinsx=30,  # Fixed number of bins
        marker=dict(
            color='#28a745',
            line=dict(color='#1e7e34', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Cards: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Card Completion Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Cards Completed",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        bargap=0.05,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Set x_range if provided
    if x_range and len(x_range) == 2:
        fig.update_xaxes(range=x_range)

    return fig


def create_list_statistics_chart(list_data):
    """
    Create a bar chart showing statistics by list.

    Args:
        list_data: List statistics from database

    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    df = process_list_stats(list_data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No list data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Cards by List",
            height=400
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['list'],
        y=df['card_count'],
        name='Total Cards',
        marker_color='#007bff',
        hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df['list'],
        y=df['completed_count'],
        name='Completed',
        marker_color='#28a745',
        hovertemplate='<b>%{x}</b><br>Completed: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Cards by List",
        xaxis_title="List",
        yaxis_title="Number of Cards",
        barmode='group',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_completion_rate_chart(list_data):
    """
    Create a horizontal bar chart showing completion rates by list.

    Args:
        list_data: List statistics from database

    Returns:
        plotly.graph_objects.Figure: Horizontal bar chart
    """
    df = process_list_stats(list_data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No list data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Completion Rate by List",
            height=400
        )
        return fig

    # Sort by completion rate
    df = df.sort_values('completion_rate', ascending=True)

    # Color scale based on completion rate
    colors = df['completion_rate'].apply(
        lambda x: f'rgb({int(255 - x * 2.55)}, {int(x * 2.55)}, 50)'
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['completion_rate'],
        y=df['list'],
        orientation='h',
        marker=dict(color=colors),
        text=df['completion_rate'].apply(lambda x: f'{x}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Completion Rate: %{x}%<extra></extra>'
    ))

    fig.update_layout(
        title="Completion Rate by List",
        xaxis_title="Completion Rate (%)",
        yaxis_title="List",
        template='plotly_white',
        height=max(400, len(df) * 30),
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )

    fig.update_xaxes(range=[0, 105])

    return fig


def create_complexity_chart(complexity_data, top_n=20):
    """
    Create a bar chart showing card complexity.

    Args:
        complexity_data: Card complexity data from database
        top_n: Number of top complex cards to show

    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    df = process_complexity_data(complexity_data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No complexity data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Card Complexity Analysis",
            height=400
        )
        return fig

    # Get top N most complex cards
    df = df.head(top_n)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['attachment_count'],
        name='Attachments',
        marker_color='#6c757d'
    ))

    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['comment_count'],
        name='Comments',
        marker_color='#17a2b8'
    ))

    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['checklist_count'],
        name='Checklists',
        marker_color='#ffc107'
    ))

    fig.update_layout(
        title=f"Top {top_n} Most Complex Cards",
        xaxis_title="Card Name",
        yaxis_title="Count",
        barmode='stack',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=150),
        xaxis=dict(tickangle=-45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_activity_heatmap(cards_data):
    """
    Create a heatmap showing card creation activity over time.

    Args:
        cards_data: List of cards with creation dates

    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    import pandas as pd

    if not cards_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No activity data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Card Creation Activity",
            height=400
        )
        return fig

    df = pd.DataFrame(cards_data)

    try:
        df['create_date'] = pd.to_datetime(df['create_date'])
        df['day_of_week'] = df['create_date'].dt.day_name()
        df['hour'] = df['create_date'].dt.hour

        # Create pivot table
        heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
        pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)

        # Reorder days of week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = pivot.reindex([day for day in days_order if day in pivot.index])

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Blues',
            hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Cards: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title="Card Creation Activity by Day and Hour",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            template='plotly_white',
            height=400,
            margin=dict(l=100, r=50, t=50, b=50)
        )

        return fig

    except Exception:
        fig = go.Figure()
        fig.add_annotation(
            text="Unable to create activity heatmap",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Card Creation Activity",
            height=400
        )
        return fig


def create_pie_chart(data, labels_col, values_col, title):
    """
    Create a generic pie chart.

    Args:
        data: Data for the chart
        labels_col: Column name for labels
        values_col: Column name for values
        title: Chart title

    Returns:
        plotly.graph_objects.Figure: Pie chart
    """
    import pandas as pd

    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(title=title, height=400)
        return fig

    df = pd.DataFrame(data)

    fig = go.Figure(data=[go.Pie(
        labels=df[labels_col],
        values=df[values_col],
        hole=.3,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=title,
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


def create_day_of_week_chart(day_data):
    """
    Create a bar chart showing card completion by day of week.

    Args:
        day_data: List of completion data by day of week from database

    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    import pandas as pd

    if not day_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No completion data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Completions by Day of Week",
            height=400
        )
        return fig

    df = pd.DataFrame(day_data)

    # Define color scale from blue to green
    colors = ['#3b82f6', '#60a5fa', '#34d399', '#10b981', '#059669', '#047857', '#065f46']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['day_name'],
        y=df['count'],
        marker=dict(
            color=colors[:len(df)],
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Cards Completed: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Card Completions by Day of Week",
        xaxis_title="Day of Week",
        yaxis_title="Number of Cards Completed",
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )

    return fig


def create_time_of_day_chart(hour_data):
    """
    Create a bar chart showing card completion by hour of day.

    Args:
        hour_data: List of completion data by hour from database

    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    import pandas as pd

    if not hour_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No completion data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Completions by Time of Day",
            height=400
        )
        return fig

    df = pd.DataFrame(hour_data)

    # Ensure all hours 0-23 are present
    all_hours = pd.DataFrame({'hour': range(24)})
    df = all_hours.merge(df, on='hour', how='left').fillna(0)
    df['count'] = df['count'].astype(int)

    # Convert to 12-hour format with AM/PM
    def hour_to_12h(hour):
        if hour == 0:
            return '12 AM'
        elif hour < 12:
            return f'{hour} AM'
        elif hour == 12:
            return '12 PM'
        else:
            return f'{hour - 12} PM'

    df['hour_label'] = df['hour'].apply(hour_to_12h)

    # Create color gradient based on time of day
    # Morning (6-12): yellows, Afternoon (12-18): oranges, Evening/Night: blues/purples
    colors = []
    for hour in df['hour']:
        if 6 <= hour < 12:  # Morning
            colors.append('#fbbf24')
        elif 12 <= hour < 18:  # Afternoon
            colors.append('#f97316')
        elif 18 <= hour < 22:  # Evening
            colors.append('#8b5cf6')
        else:  # Night
            colors.append('#3b82f6')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['hour'],
        y=df['count'],
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=df['hour_label'],
        hovertemplate='<b>%{text}</b><br>Cards Completed: %{y}<extra></extra>',
        customdata=df['hour_label']
    ))

    # Create custom tick labels for AM/PM
    tickvals = list(range(24))
    ticktext = [hour_to_12h(h) for h in range(24)]

    fig.update_layout(
        title="Card Completions by Time of Day",
        xaxis_title="Hour",
        yaxis_title="Number of Cards Completed",
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            range=[-0.5, 23.5]
        )
    )

    return fig
