import altair as alt

from ..api.utils import create_progress_df


def project_progress(leaderboard, metric_colname, 
                     width=800, 
                     heights=[50,400], 
                     line_size=5, 
                     text_size=15):
    
    top_height, bottom_height = heights
    
    progress_df = create_progress_df(leaderboard, metric_colname)
    
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['finished'], empty='none')

    brush = alt.selection(type='interval', encodings=['x'])

    top_view = alt.Chart(height=top_height, width=width).mark_line(interpolate='step-after', size=line_size).encode(
        x='finished:T',
        y=alt.Y('{}:Q'.format(metric_colname),scale=alt.Scale(zero=False), axis=None),
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

    line = alt.Chart().mark_line(interpolate='step-after', size=line_size).encode(
        x=alt.X('finished:T', scale=alt.Scale()),
        y=alt.Y('{}:Q'.format(metric_colname),scale=alt.Scale(zero=False)),
        color='best_or_actual:N'
    ).transform_filter(
        brush
    )

    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = line.mark_text(align='left', dx=5, dy=-5, size=text_size).encode(
        text=alt.condition(nearest, '{}:Q'.format(metric_colname), alt.value(' ')),
        color='best_or_actual:N'
    )

    rules = alt.Chart().mark_rule(color='gray').encode(
        x=alt.X('finished:T', scale=alt.Scale()),
    ).transform_filter(
        nearest
    )

    metrics = alt.layer(line, points, text, rules, selectors).properties(
        height=bottom_height,
        width=width,
    )


    exp_line = alt.Chart().mark_area(interpolate='step-after', size=line_size).encode(
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

    exp_text = exp_line.mark_text(align='left', dx=5, dy=-5, fontWeight='bold', size=text_size).encode(
        text=alt.condition(nearest, 'daily_experiment_counts:Q'.format(metric_colname), alt.value(' ')),
        color=alt.ColorValue('black')
    )

    exp_rules = alt.Chart().mark_rule(color='gray').encode(
        x=alt.X('finished:T', scale=alt.Scale()),
    ).transform_filter(
        nearest
    )

    exps = alt.layer(exp_line, exp_points, exp_rules, exp_text).properties(
        height=bottom_height,
        width=width,
    )

    main_view = alt.layer(metrics, exps).properties(
        height=bottom_height,
        width=width,
    ).resolve_scale(
        y='independent'
    )

    tags = alt.Chart(height=1, width=1).mark_text(align='left', size=text_size, fontWeight='bold').encode(
            x=alt.X('finished:T', axis=None),
            text=alt.condition(nearest, 'tags:N', alt.value(' ')),
    )

    combined = alt.vconcat(top_view, tags, main_view, data=progress_df)
    return combined