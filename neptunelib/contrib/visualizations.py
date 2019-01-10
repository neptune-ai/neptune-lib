from itertools import product

import altair as alt
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt


def fig2pil(fig):
    fig.canvas.draw()

    w,h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)
    buf = np.roll(buf, 3, axis=2)

    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w , h), buf.tostring())

        
def axes2fig(axes):
    try:
        shape = axes.shape
        fig = plt.figure(figsize=(shape[0]*3,shape[1]*3))
        for i,j in product(range(shape[0]), range(shape[1])):
            fig._axstack.add(fig._make_key(axes[i,j]), axes[i,j])
    except AttributeError:
        fig = plt.figure(figsize=(6,6))
        fig._axstack.add(fig._make_key(axes), axes)
        
    return fig


def combine_channel_df(experiments, channel_name):
    combined_df = []
    for experiment in experiments:
        channel_df = experiment.get_numeric_channels_values(channel_name) 
        channel_df['id'] = experiment.id
        combined_df.append(channel_df)
    combined_df = pd.concat(combined_df, axis=0)
    return combined_df


def curve_compare(experiments, channel_name):
    combined_df = combine_channel_df(experiments, channel_name)
    combined_df.columns = [col.replace('_{}'.format(channel_name),'') for col in combined_df.columns]

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['x'], empty='none')
    interval = alt.selection(type='interval', encodings=['x'])
    legend_selection = alt.selection_multi(fields=['id'])

    legend = alt.Chart().mark_point(filled=True, size=100).encode(
        y=alt.Y('id:N'),
        color=alt.condition(legend_selection, alt.Color('id:N', legend=None), alt.value('lightgray'))
    ).add_selection(
        legend_selection
    )

    selectors = alt.Chart().mark_point().encode(
        x='x:Q',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    top_view = alt.Chart(width=800, height=100).mark_line().encode(
        x=alt.X('x:Q', title=None),
        y=alt.Y('y:Q', scale=alt.Scale(zero=False), title=None),        
        color=alt.Color('id:N', legend=None),
        opacity=alt.condition(legend_selection, alt.OpacityValue(1), alt.OpacityValue(0.0))
    ).add_selection(
        interval
    )


    line = alt.Chart().mark_line().encode(
        x=alt.X('x:Q',title='iteration'),
        y=alt.Y('y:Q', scale=alt.Scale(zero=False), title=channel_name),
        color=alt.Color('id:N', legend=None),
        opacity=alt.condition(legend_selection, alt.OpacityValue(1), alt.OpacityValue(0.0))
    )

    points = line.mark_point().encode(
        color=alt.condition(legend_selection, alt.Color('id:N', legend=None), alt.value('white')),
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' ')),
        opacity=alt.condition(legend_selection, alt.OpacityValue(1), alt.OpacityValue(0.0))
    )

    rules = alt.Chart().mark_rule(color='gray').encode(
        x='x:Q',
    ).transform_filter(
        nearest
    )

    bottom_view = alt.layer(line, selectors, points, rules, text,
                            width=800, height=400
    ).transform_filter(
        interval
    )

    combined = alt.hconcat(alt.vconcat(top_view, bottom_view),
                           legend, 
                           data=combined_df)
    return combined


def hyperparam_histograms(data, metric_col, param_cols, 
                          metric_agg='max',
                          max_width=800,
                          param_bins=10,
                          metric_bins=20
                         ):
    width=max_width/(len(param_cols)+1)
    height=100
        
    interval = alt.selection(type='interval', encodings=['y'])

    top_charts = alt.Chart(data).mark_bar().encode(
            x=alt.X(alt.repeat('column'), type='quantitative', bin=alt.Bin(maxbins=param_bins), title=None),
            y=alt.Y('count()', title=None),
            color=alt.Color('{}({}):Q'.format(metric_agg,metric_col), scale=alt.Scale(scheme='yelloworangered'), legend=None),
            ).properties(
                width=width,
                height=height
            ).transform_filter(
                interval
            ).repeat(
            column=param_cols
            )

    base_bottom = alt.Chart().mark_bar().encode(
            x=alt.X(alt.repeat('column'), type='quantitative', bin=alt.Bin(maxbins=param_bins)),
            y=alt.Y('count()', title=None),
            color=alt.value('lightblue')
            ).properties(
                width=width
            )

    highlight_bottom = base_bottom.encode(
                    color=alt.value('darkblue'),
                ).transform_filter(
                interval
            )

    best_score = alt.Chart(data).mark_rule().encode(
                    x=alt.X(alt.repeat('column'), aggregate='mean',type='quantitative', axis=None),
                    color=alt.value('firebrick'),
                    size=alt.SizeValue(3),
                ).transform_filter(
                interval
            )
    #TODO get best score not mock https://altair-viz.github.io/user_guide/transform.html
    
    bottom_charts = alt.layer(
        base_bottom,
        highlight_bottom,
        best_score,
        data=data
        ).repeat(
            column=param_cols,
        )
    
    metric_line = alt.Chart(data, width=width).mark_area(filled=False).encode(
            y=alt.Y("{}:Q".format(metric_col),bin=alt.Bin(maxbins=metric_bins), title=None),
            x=alt.X('count()', title=metric_col),
            color=alt.Color('mean({}):Q'.format(metric_col), scale=alt.Scale(scheme='yelloworangered'), legend=None),
            ).add_selection(
                interval
            )
    metric_bar = alt.Chart(data, width=width).mark_bar().encode(
            y=alt.Y("{}:Q".format(metric_col),bin=alt.Bin(maxbins=metric_bins), title=None),
            x=alt.X('count()', title=metric_col),
            color=alt.Color('mean({}):Q'.format(metric_col), scale=alt.Scale(scheme='yelloworangered'), legend=None),
            )
    
    metric_chart = alt.layer(metric_bar, metric_line)
    
    combined_chart = alt.vconcat(top_charts,
                                 alt.hconcat(bottom_charts, metric_chart))
    
    return combined_chart