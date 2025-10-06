"""State diagram component for visualizing card journey."""
import plotly.graph_objects as go
import numpy as np
import math


def create_state_diagram(flow_data, title="Card Journey State Diagram"):
    """
    Create a state diagram showing card movement between lists.

    Args:
        flow_data: Card flow data from database (source, target, value)
        title: Chart title

    Returns:
        plotly.graph_objects.Figure: State diagram
    """
    if not flow_data:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No card movement data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            height=600
        )
        return fig

    # Extract nodes and calculate flow
    sources = [item['source'] for item in flow_data]
    targets = [item['target'] for item in flow_data]
    values = [item['value'] for item in flow_data]

    all_nodes = sorted(list(set(sources + targets)))
    n_nodes = len(all_nodes)

    # Calculate total flow for each node (for node sizing)
    node_flow = {}
    for item in flow_data:
        source = item['source']
        target = item['target']
        value = item['value']
        node_flow[source] = node_flow.get(source, 0) + value
        node_flow[target] = node_flow.get(target, 0) + value

    # Position nodes in a circular layout
    theta = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
    node_x = np.cos(theta) * 2
    node_y = np.sin(theta) * 2

    # Create node position mapping
    node_pos = {node: (node_x[i], node_y[i]) for i, node in enumerate(all_nodes)}

    fig = go.Figure()

    # Draw edges (arrows) first so they appear behind nodes
    max_value = max(values)
    for item in flow_data:
        source = item['source']
        target = item['target']
        value = item['value']

        x0, y0 = node_pos[source]
        x1, y1 = node_pos[target]

        # Calculate arrow parameters
        # Shorten line to not overlap with nodes
        dx = x1 - x0
        dy = y1 - y0
        dist = math.sqrt(dx**2 + dy**2)

        # Adjust endpoints to account for node size
        offset = 0.25  # Node radius
        x0_adj = x0 + (dx / dist) * offset
        y0_adj = y0 + (dy / dist) * offset
        x1_adj = x1 - (dx / dist) * offset
        y1_adj = y1 - (dy / dist) * offset

        # Line width based on value
        line_width = 1 + (value / max_value) * 8

        # Add edge line
        fig.add_trace(go.Scatter(
            x=[x0_adj, x1_adj],
            y=[y0_adj, y1_adj],
            mode='lines',
            line=dict(
                color='rgba(100, 100, 100, 0.4)',
                width=line_width
            ),
            hovertemplate=f'<b>{source} → {target}</b><br>Cards: {value}<extra></extra>',
            showlegend=False
        ))

        # Add arrowhead annotation
        fig.add_annotation(
            x=x1_adj,
            y=y1_adj,
            ax=x0_adj,
            ay=y0_adj,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=line_width/2,
            arrowcolor='rgba(100, 100, 100, 0.6)',
            text='',
        )

    # Draw nodes
    node_sizes = [node_flow.get(node, 0) for node in all_nodes]
    max_size = max(node_sizes) if node_sizes else 1
    normalized_sizes = [20 + (size / max_size) * 40 for size in node_sizes]

    # Generate colors for nodes
    colors = []
    for i in range(n_nodes):
        hue = i / n_nodes
        rgb = hsv_to_rgb(hue, 0.7, 0.9)
        colors.append(f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})')

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=normalized_sizes,
            color=colors,
            line=dict(color='white', width=3),
            symbol='circle'
        ),
        text=all_nodes,
        textposition='middle center',
        textfont=dict(size=10, color='white', family='Arial Black'),
        hovertemplate='<b>%{text}</b><br>Total flow: %{customdata}<extra></extra>',
        customdata=node_sizes,
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        title=title,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-3, 3]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-3, 3]
        ),
        plot_bgcolor='white',
        height=600,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def create_journey_state_diagram(path_data, card_name="Card"):
    """
    Create a timeline visualization for a single card's journey.

    Args:
        path_data: Card movement history with 'from_list', 'to_list', and 'time' keys
        card_name: Name of the card

    Returns:
        plotly.graph_objects.Figure: Timeline visualization
    """
    if not path_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No movement history",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title=f"Journey: {card_name}",
            height=400
        )
        return fig

    import pandas as pd
    from datetime import datetime

    # Parse timestamps - format is MM:DD:YY HH:MM
    def parse_timestamp(time_str):
        if not time_str:
            return None
        try:
            # Convert MM:DD:YY HH:MM to datetime
            parts = time_str.split(' ')
            date_parts = parts[0].split(':')
            time_parts = parts[1].split(':') if len(parts) > 1 else ['00', '00']

            month = int(date_parts[0])
            day = int(date_parts[1])
            year = 2000 + int(date_parts[2])
            hour = int(time_parts[0])
            minute = int(time_parts[1])

            return datetime(year, month, day, hour, minute)
        except:
            return None

    # Convert to dataframe and parse timestamps
    df = pd.DataFrame(path_data)
    df['parsed_time'] = df['time'].apply(parse_timestamp)

    # Sort by actual datetime, not string representation
    df = df.sort_values('parsed_time').reset_index(drop=True)

    # Build timeline data
    # Each row in path_data represents: card moved FROM from_list TO to_list AT time
    timeline_data = []

    # Process each move
    for i, row in df.iterrows():
        move_time = row['parsed_time']  # Already parsed above
        to_list = row['to_list']

        if not move_time:
            continue

        # Determine when this list period ends
        # It ends when the next move happens, or None if this is the last move
        if i < len(df) - 1:
            next_move_time = parse_timestamp(df.iloc[i + 1]['time'])
            end_time = next_move_time if next_move_time else move_time
            is_current = False
        else:
            # Last move - card is currently in this list
            # For visualization, show a small bar
            from datetime import timedelta
            end_time = move_time + timedelta(hours=1)  # Show 1 hour placeholder for current list
            is_current = True

        timeline_data.append({
            'list': to_list,
            'start': move_time,
            'end': end_time,
            'step': i,
            'is_current': is_current
        })

    if not timeline_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No timestamp data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title=f"Journey: {card_name}",
            height=400
        )
        return fig

    # Prepare data for plotly express timeline
    import plotly.express as px

    # Get unique lists for color mapping
    unique_lists = list(set([item['list'] for item in timeline_data]))
    colors_map = {}
    for i, list_name in enumerate(unique_lists):
        hue = i / len(unique_lists)
        rgb = hsv_to_rgb(hue, 0.7, 0.9)
        colors_map[list_name] = f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})'

    # Build dataframe for timeline with formatted strings for hover
    timeline_df = pd.DataFrame([
        {
            'Task': f"Step {item['step'] + 1}",
            'Task_Order': item['step'],  # For sorting
            'Start': item['start'],
            'Finish': item['end'],
            'List': item['list'],
            'Duration_Hours': (item['end'] - item['start']).total_seconds() / 3600,
            'Start_Str': item['start'].strftime('%Y-%m-%d %H:%M'),
            'Finish_Str': item['end'].strftime('%Y-%m-%d %H:%M'),
            'Is_Current': item['is_current']
        }
        for item in timeline_data
    ])

    # Create custom hover text for each row
    timeline_df['hover_text'] = timeline_df.apply(
        lambda row: f"<b>{row['List']}</b><br>" +
                   f"Start: {row['Start_Str']}<br>" +
                   f"Finish: {row['Finish_Str']}<br>" +
                   f"Duration: {row['Duration_Hours']:.1f}h" if row['Duration_Hours'] < 24
                   else f"<b>{row['List']}</b><br>" +
                        f"Start: {row['Start_Str']}<br>" +
                        f"Finish: {row['Finish_Str']}<br>" +
                        f"Duration: {row['Duration_Hours']/24:.1f}d" +
                        (" (current)" if row['Is_Current'] else ""),
        axis=1
    )

    # Create the Gantt chart using plotly express
    fig = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="List",
        color_discrete_map=colors_map,
        text="List",
        custom_data=['hover_text']
    )

    # Update traces to show list name as text and fix hover
    fig.update_traces(
        textposition='inside',
        textfont=dict(color='white', size=11),
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    # Update layout with proper Y-axis ordering
    title_text = f"Journey: {card_name[:50]}{'...' if len(card_name) > 50 else ''}"

    # Create ordered list of step labels for Y-axis
    step_labels = [f"Step {i+1}" for i in range(len(timeline_data))]

    fig.update_layout(
        title=title_text,
        xaxis=dict(title="Time"),
        yaxis=dict(
            title="",
            categoryorder='array',
            categoryarray=step_labels  # Force chronological order
        ),
        height=max(300, len(timeline_data) * 40 + 100),
        margin=dict(l=80, r=20, t=50, b=50),
        template='plotly_white',
        showlegend=True,
        legend=dict(title="Lists")
    )

    return fig


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.

    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value (0-1)

    Returns:
        tuple: (r, g, b) values (0-1)
    """
    if s == 0.0:
        return (v, v, v)

    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)
