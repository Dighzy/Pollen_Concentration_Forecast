import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd


# Reference https://community.plotly.com/t/gauge-chart-with-python/57279/4
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def gauge(value, threshold_text, threshold):
    if isinstance(value, pd.Series):
        value = value.iloc[0]  # Extract the single value from Series

    plot_bgcolor = "#f0f0f0"  # Gray background
    quadrant_colors = [plot_bgcolor, "#f25829", "#eff229", "#2bad4e"]
    quadrant_text = ["", "<b>Very high</b>", "<b>Medium</b>", "<b>Very low</b>"]
    n_quadrants = len(quadrant_colors) - 1

    current_value = value
    min_value = 0
    max_value = threshold + (threshold * 20/100)
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    fig = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                rotation=90,
                hole=0.5,
                marker_colors=quadrant_colors,
                text=quadrant_text,
                textinfo="text",
                hoverinfo="skip",
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=10, l=10, r=10),
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>Pollen Concentration:</b><br>{current_value}<br><br>{threshold_text}",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                    font=dict(size=18, color='black')  # Text in black
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                )
            ]
        )
    )
    return fig


def line_chart(data_df, date_column, pollen_column, threshold):
    # Add a color column based on the threshold
    data_df['Color'] = data_df[pollen_column].apply(lambda x: 'red' if x > threshold else 'green')

    # Create the line chart
    fig = px.line(data_df, x=date_column, y=pollen_column, title='Pollen Concentration Over Time')
    fig.update_traces(line=dict(color='yellow'))

    # Add scatter plot with text labels
    fig.add_scatter(x=data_df[date_column],
                    y=data_df[pollen_column],
                    mode='markers+text',
                    marker=dict(color=data_df['Color'], size=10),
                    text=data_df[pollen_column],  # Show pollen concentration values
                    textposition='top center',  # Position text labels
                    name='Pollen Concentration')

    return fig
