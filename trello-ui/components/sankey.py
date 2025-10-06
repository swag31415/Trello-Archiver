"""Sankey diagram component for visualizing card flow."""
import plotly.graph_objects as go
from utils.data_processing import process_sankey_data


def create_sankey_diagram(flow_data, title="Card Flow Between Lists"):
    """
    Create a Sankey diagram showing card movement between lists.

    Args:
        flow_data: Card flow data from database
        title: Chart title

    Returns:
        plotly.graph_objects.Figure: Sankey diagram
    """
    processed_data = process_sankey_data(flow_data)

    if not processed_data['source']:
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
            height=500
        )
        return fig

    # Create color palette for nodes
    num_nodes = len(processed_data['labels'])
    colors = generate_node_colors(num_nodes)

    # Create link colors (semi-transparent versions of source node colors)
    link_colors = [
        colors[source].replace('rgb', 'rgba').replace(')', ', 0.4)')
        for source in processed_data['source']
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=processed_data['labels'],
            color=colors
        ),
        link=dict(
            source=processed_data['source'],
            target=processed_data['target'],
            value=processed_data['value'],
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>Cards: %{value}<extra></extra>'
        )
    )])

    fig.update_layout(
        title=title,
        font=dict(size=12),
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        template='plotly_white'
    )

    return fig


def generate_node_colors(num_nodes):
    """
    Generate a list of distinct colors for Sankey nodes.

    Args:
        num_nodes: Number of colors to generate

    Returns:
        list: List of RGB color strings
    """
    # Predefined color palette
    color_palette = [
        'rgb(31, 119, 180)',   # Blue
        'rgb(255, 127, 14)',   # Orange
        'rgb(44, 160, 44)',    # Green
        'rgb(214, 39, 40)',    # Red
        'rgb(148, 103, 189)',  # Purple
        'rgb(140, 86, 75)',    # Brown
        'rgb(227, 119, 194)',  # Pink
        'rgb(127, 127, 127)',  # Gray
        'rgb(188, 189, 34)',   # Olive
        'rgb(23, 190, 207)',   # Cyan
        'rgb(174, 199, 232)',  # Light blue
        'rgb(255, 187, 120)',  # Light orange
        'rgb(152, 223, 138)',  # Light green
        'rgb(255, 152, 150)',  # Light red
        'rgb(197, 176, 213)',  # Light purple
        'rgb(196, 156, 148)',  # Light brown
        'rgb(247, 182, 210)',  # Light pink
        'rgb(199, 199, 199)',  # Light gray
        'rgb(219, 219, 141)',  # Light olive
        'rgb(158, 218, 229)',  # Light cyan
    ]

    # If we need more colors than in palette, cycle through
    colors = []
    for i in range(num_nodes):
        colors.append(color_palette[i % len(color_palette)])

    return colors


def create_mini_sankey(flow_data, max_flows=10):
    """
    Create a smaller Sankey diagram showing top flows.

    Args:
        flow_data: Card flow data from database
        max_flows: Maximum number of flows to show

    Returns:
        plotly.graph_objects.Figure: Sankey diagram
    """
    import pandas as pd

    if not flow_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No flow data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=300)
        return fig

    # Get top flows by value
    df = pd.DataFrame(flow_data)
    df = df.nlargest(max_flows, 'value')

    processed_data = process_sankey_data(df.to_dict('records'))

    if not processed_data['source']:
        fig = go.Figure()
        fig.add_annotation(
            text="No flow data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=300)
        return fig

    num_nodes = len(processed_data['labels'])
    colors = generate_node_colors(num_nodes)

    link_colors = [
        colors[source].replace('rgb', 'rgba').replace(')', ', 0.4)')
        for source in processed_data['source']
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=15,
            line=dict(color="black", width=0.5),
            label=processed_data['labels'],
            color=colors
        ),
        link=dict(
            source=processed_data['source'],
            target=processed_data['target'],
            value=processed_data['value'],
            color=link_colors
        )
    )])

    fig.update_layout(
        title=f"Top {max_flows} Card Flows",
        font=dict(size=10),
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        template='plotly_white'
    )

    return fig


def create_journey_visualization(path_data, card_name="Card"):
    """
    Create a simple journey visualization for a single card.

    Args:
        path_data: Card movement history
        card_name: Name of the card

    Returns:
        plotly.graph_objects.Figure: Journey visualization
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
            height=200
        )
        return fig

    import pandas as pd

    df = pd.DataFrame(path_data)

    # Build the journey path
    all_lists = [df.iloc[0]['from_list']] + df['to_list'].tolist()

    # Create a simple flow diagram
    sources = []
    targets = []
    values = []
    labels = []
    label_dict = {}

    for i, list_name in enumerate(all_lists):
        if list_name not in label_dict:
            label_dict[list_name] = len(label_dict)

    for i in range(len(all_lists) - 1):
        sources.append(label_dict[all_lists[i]])
        targets.append(label_dict[all_lists[i + 1]])
        values.append(1)

    labels = list(label_dict.keys())

    colors = generate_node_colors(len(labels))
    link_colors = [colors[s].replace('rgb', 'rgba').replace(')', ', 0.6)') for s in sources]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=15,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        title=f"Journey: {card_name[:50]}{'...' if len(card_name) > 50 else ''}",
        font=dict(size=10),
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        template='plotly_white'
    )

    return fig
