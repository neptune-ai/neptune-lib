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


def create_progress_df(leaderbaord, metric_name):
    system_columns = ['owner','running_time','finished', 'tags']
    progress_columns = system_columns + [metric_name]
    progress_df = leaderbaord[progress_columns]
    
    progress_df['finished'] = pd.to_datetime(progress_df['finished'])

    progress_df[metric_name] = progress_df[metric_name].astype(float)

    progress_df.sort_values('finished',inplace=True)
    progress_df[metric_name] = progress_df[metric_name].fillna(method='bfill')
    progress_df.dropna(subset=[metric_name], how='all', inplace = True)
    
    current_best = progress_df[metric_name].cummax()
    current_best = current_best.fillna(method='bfill')
    progress_df['{}_current_best'.format(metric_name)] = current_best
        
    progress_df = progress_df.melt(id_vars=system_columns,
                        value_vars=[metric_name, '{}_current_best'.format(metric_name)],
                        var_name='best_or_actual',
                        value_name=metric_name
                       )
        
    progress_df['running_time'] = np.round(progress_df['running_time'] / (60 * 60 * 24), 2)
    progress_df['finished_date'] = [d.date() for d in progress_df['finished']]
    daily_counts = progress_df.groupby('finished_date').count()['finished'].reset_index()
    daily_counts.columns = ['finished_date','daily_experiment_counts']
    progress_df = pd.merge(progress_df, daily_counts, on='finished_date')

    progress_df['tags'] = progress_df['tags'].apply(lambda x: ' | '.join(x))
    
    progress_df['finished'] = progress_df['finished'].astype(str)
    progress_df['finished_date'] = progress_df['finished_date'].astype(str)
    return progress_df


def curve_compare(experiments, channel_name):
    fig = plt.figure(figsize=(16,12))
    for experiment in experiments:
        channel_df = experiment.get_numeric_channels_values(channel_name) 
        plt.plot( 'x_{}'.format(channel_name),
                 'y_{}'.format(channel_name), 
                 data=channel_df, 
                 marker='', linewidth=2, label=experiment.id)
    plt.legend()
    return fig

def interacvite_curve_compare(experiments, channel_name):
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


def interactive_project_progress(leaderboard, metric_name):
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['finished'], empty='none')

    brush = alt.selection(type='interval', encodings=['x'])

    top_view = alt.Chart(height=50, width=800).mark_line(interpolate='step-after', size=5).encode(
        x='finished:T',
        y=alt.Y('{}:Q'.format(metric_name),scale=alt.Scale(zero=False), axis=None),
        color='best_or_actual:N'
    ).add_selection(
        brush
    )

    selectors = alt.Chart().mark_point().encode(
        x=alt.X('finished:T', scale=alt.Scale()),
        opacity=alt.value(0),
    ).add_selection(
        nearest
    ).transform_filter(
        brush
    )

    line = alt.Chart().mark_line(interpolate='step-after', size=5).encode(
        x=alt.X('finished:T', scale=alt.Scale()),
        y=alt.Y('{}:Q'.format(metric_name),scale=alt.Scale(zero=False)),
        color='best_or_actual:N'
    ).transform_filter(
        brush
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5, size=15).encode(
        text=alt.condition(nearest, '{}:Q'.format(metric_name), alt.value(' ')),
        color='best_or_actual:N'
    )

    rules = alt.Chart().mark_rule(color='gray').encode(
        x=alt.X('finished:T', scale=alt.Scale()),
    ).transform_filter(
        nearest
    )

    metrics = alt.layer(line, points, text, rules, selectors).properties(
        height=400,
        width=800,
    )


    exp_line = alt.Chart().mark_area(interpolate='step-after', size=5).encode(
        x=alt.X('finished:T', scale=alt.Scale()),
        y=alt.Y('daily_experiment_counts:Q',scale=alt.Scale(zero=False)),
        color=alt.ColorValue('pink'),
        opacity=alt.OpacityValue(0.5)
    ).transform_filter(
        brush
    )

    exp_points = exp_line.mark_point(filled=True).encode(
        color=alt.ColorValue('black'),
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    exp_text = exp_line.mark_text(align='left', dx=5, dy=-5, fontWeight='bold', size=15).encode(
        text=alt.condition(nearest, 'daily_experiment_counts:Q'.format(metric_name), alt.value(' ')),
        color=alt.ColorValue('black')
    )

    exp_rules = alt.Chart().mark_rule(color='gray').encode(
        x=alt.X('finished:T', scale=alt.Scale()),
    ).transform_filter(
        nearest
    )

    exps = alt.layer(exp_line, exp_points, exp_rules, exp_text).properties(
        height=400,
        width=800,
    )

    main_view = alt.layer(metrics, exps).properties(
        height=400,
        width=800,
    ).resolve_scale(
        y='independent'
    )

    tags = alt.Chart(height=1, width=1).mark_text(align='left', size=15, fontWeight='bold').encode(
            x=alt.X('finished:T', axis=None),
            text=alt.condition(nearest, 'tags:N', alt.value(' ')),
    )

    combined = alt.vconcat(top_view, tags, main_view,
                           data=progress_df)
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