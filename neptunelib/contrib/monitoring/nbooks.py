import yaml
from attrdict import AttrDict
import matplotlib.pyplot as plt
from IPython.display import clear_output


class NeptuneConfig:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = NeptuneConfig.read_yaml(filepath)
        self.params = self.config.parameters
        
    @staticmethod
    def read_yaml(filepath):
        with open(filepath) as f:
            config = yaml.load(f)
        return AttrDict(config) 


class NotebookChannels(dict):
    def __init__(self, figsize, max_cols):
        super().__init__(self)
        self.figsize=figsize
        self.max_cols=max_cols
        
    def plot(self):
        plt.figure(figsize=self.figsize)
        clear_output(wait=True)
        for metric_id, (channel_name, channel) in enumerate(self.items()):
            plt.subplot((len(self) + 1) // self.max_cols + 1, self.max_cols, metric_id + 1)
            plt.plot(channel.x, channel.y, label=channel.channel_name)
            plt.legend()
        plt.show()
        
        
class NotebookChannel:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.y = []
        self.x = []
    
    def update(self, metrics):
        self.x.append(metrics['x'])
        self.y.append(metrics['y'])
        
        if None in self.x:
            self.x = list(range(len(self.y)))
    
    
def NotebookContext(context, config_filepath):
    if context.params.__class__.__name__ == 'OfflineContextParams':
        context = NotebookOfflineContext(context, config_filepath)
    return context


class NotebookOfflineContext:
    def __init__(self, context, config_filepath, 
                 figsize=(16,12), max_cols=2):
        self.context = context
        self.config = NeptuneConfig(config_filepath)
        self.numeric_channels = NotebookChannels(figsize=figsize, max_cols=max_cols)
        self.other_channels = {}
        
    @property
    def params(self):
        return self.config.params
    
    def channel_send(self, channel_name, x=None, y=None):
        try:
            y = float(y)
            self.numeric_channels[channel_name] = self.numeric_channels.get(channel_name, NotebookChannel(channel_name))
            self.numeric_channels[channel_name].update({'x':x, 'y':y})
            self.numeric_channels.plot()
        except Exception:
            self.other_channels[channel_name] = self.other_channels.get(channel_name, NotebookChannel(channel_name))
            self.other_channels[channel_name].update({'x':x, 'y':y})