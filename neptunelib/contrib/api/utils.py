import pandas as pd
import numpy as np


def get_channel_columns(columns):
    return [col for col in columns if col.startswith('channel_')]


def get_parameter_columns(columns):
    return [col for col in columns if col.startswith('parameter_')]


def get_property_columns(columns):
    return [col for col in columns if col.startswith('property_')]


def get_system_columns(columns):
    excluded_prefices = ['channel_','parameter_','property_']
    return [col for col in columns if not any([col.startswith(prefix) for prefix in excluded_prefices])]


def combine_channel_df(experiments, channel_name):
    combined_df = []
    for experiment in experiments:
        channel_df = experiment.get_numeric_channels_values(channel_name) 
        channel_df['id'] = experiment.id
        combined_df.append(channel_df)
    combined_df = pd.concat(combined_df, axis=0)
    return combined_df


def create_progress_df(leaderbaord, metric_colname):
    system_columns = ['owner','running_time','finished', 'tags']
    progress_columns = system_columns + [metric_colname]
    progress_df = leaderbaord[progress_columns]
    
    progress_df['finished'] = pd.to_datetime(progress_df['finished'])

    progress_df[metric_colname] = progress_df[metric_colname].astype(float)

    progress_df.sort_values('finished',inplace=True)
    progress_df[metric_colname] = progress_df[metric_colname].fillna(method='bfill')
    progress_df.dropna(subset=[metric_colname], how='all', inplace = True)
    
    current_best = progress_df[metric_colname].cummax()
    current_best = current_best.fillna(method='bfill')
    progress_df['{}_current_best'.format(metric_colname)] = current_best
        
    progress_df = progress_df.melt(id_vars=system_columns,
                        value_vars=[metric_colname, '{}_current_best'.format(metric_colname)],
                        var_name='best_or_actual',
                        value_name=metric_colname
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