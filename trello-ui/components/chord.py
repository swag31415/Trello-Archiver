"""Chord diagram component for visualizing card flow."""
import plotly.graph_objects as go
import numpy as np


def create_chord_diagram(flow_data, title="Card Flow Between Lists"):
    """
    Create a chord diagram showing card movement between lists.

    Args:
        flow_data: Card flow data from database (source, target, value)
        title: Chart title

    Returns:
        plotly.graph_objects.Figure: Chord diagram
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
            height=500
        )
        return fig

    # Extract unique nodes and calculate flow
    sources = [item['source'] for item in flow_data]
    targets = [item['target'] for item in flow_data]
    values = [item['value'] for item in flow_data]

    all_nodes_set = set(sources + targets)

    # Calculate total flow for each node (sum of incoming and outgoing)
    node_flow = {}
    for item in flow_data:
        source = item['source']
        target = item['target']
        value = item['value']

        node_flow[source] = node_flow.get(source, 0) + value
        node_flow[target] = node_flow.get(target, 0) + value

    # Sort nodes by total flow (descending)
    all_nodes = sorted(all_nodes_set, key=lambda x: node_flow.get(x, 0), reverse=True)
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    n_nodes = len(all_nodes)

    # Create adjacency matrix
    matrix = np.zeros((n_nodes, n_nodes))
    for item in flow_data:
        source_idx = node_dict[item['source']]
        target_idx = node_dict[item['target']]
        matrix[source_idx][target_idx] = item['value']

    # Generate colors for nodes
    colors = generate_chord_colors(n_nodes)

    # Create chord diagram using a circular layout
    fig = go.Figure()

    # Position nodes in a circle
    theta = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
    node_x = np.cos(theta)
    node_y = np.sin(theta)

    # Draw chords (connections between nodes)
    for i in range(n_nodes):
        for j in range(n_nodes):
            if matrix[i][j] > 0:
                # Create a curved line from node i to node j
                # Use quadratic Bezier curve through the center
                x_start, y_start = node_x[i], node_y[i]
                x_end, y_end = node_x[j], node_y[j]

                # Control point (slightly towards center for curve)
                control_x = (x_start + x_end) / 2 * 0.3
                control_y = (y_start + y_end) / 2 * 0.3

                # Generate points along the curve
                t = np.linspace(0, 1, 50)
                curve_x = (1-t)**2 * x_start + 2*(1-t)*t * control_x + t**2 * x_end
                curve_y = (1-t)**2 * y_start + 2*(1-t)*t * control_y + t**2 * y_end

                # Normalize line width by value
                max_value = max(values)
                line_width = max(1, (matrix[i][j] / max_value) * 10)

                # Add chord as a line
                fig.add_trace(go.Scatter(
                    x=curve_x,
                    y=curve_y,
                    mode='lines',
                    line=dict(
                        color=colors[i],
                        width=line_width
                    ),
                    opacity=0.4,
                    hovertemplate=f'<b>{all_nodes[i]} → {all_nodes[j]}</b><br>Cards: {int(matrix[i][j])}<extra></extra>',
                    showlegend=False
                ))

    # Draw nodes as scatter points
    node_sizes = [sum(matrix[i]) + sum(matrix[:, i]) for i in range(n_nodes)]
    max_size = max(node_sizes) if node_sizes else 1
    normalized_sizes = [30 + (size / max_size) * 40 for size in node_sizes]

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=normalized_sizes,
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=all_nodes,
        textposition='top center',
        textfont=dict(size=10, color='black'),
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
            range=[-1.5, 1.5]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1.5, 1.5]
        ),
        plot_bgcolor='white',
        height=500,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def generate_chord_colors(n_colors):
    """
    Generate distinct colors for chord diagram nodes.

    Args:
        n_colors: Number of colors to generate

    Returns:
        list: List of RGB color strings
    """
    # Use HSV color space for evenly distributed colors
    colors = []
    for i in range(n_colors):
        hue = i / n_colors
        # Convert HSV to RGB (with S=0.7, V=0.9 for pleasant colors)
        rgb = hsv_to_rgb(hue, 0.7, 0.9)
        colors.append(f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})')
    return colors


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


def create_mini_chord(flow_data, max_flows=10):
    """
    Create a smaller chord diagram showing top flows.

    Args:
        flow_data: Card flow data from database
        max_flows: Maximum number of flows to show

    Returns:
        plotly.graph_objects.Figure: Chord diagram
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

    return create_chord_diagram(df.to_dict('records'), title=f"Top {max_flows} Card Flows")
