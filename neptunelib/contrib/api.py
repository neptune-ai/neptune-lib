def get_channel_columns(columns):
    return [col for col in columns if col.startswith('channel_')]

def get_parameter_columns(columns):
    return [col for col in columns if col.startswith('parameter_')]

def get_property_columns(columns):
    return [col for col in columns if col.startswith('property_')]

def get_system_columns(columns):
    excluded_prefices = ['channel_','parameter_','property_']
    return [col for col in columns if not any([col.startswith(prefix) for prefix in excluded_prefices])]