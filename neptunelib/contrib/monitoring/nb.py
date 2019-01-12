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


class NotebookChannel:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.y = []
        self.x = []
    
    def update(self, metrics):
        self.x.append(metrics['x'])
        self.y.append(metrics['y'])
        
        if None in self.x:
            self.x = range(len(self.y))
    
    def plot(self):
        clear_output(wait=True)
        plt.plot(self.x, self.y, label=self.channel_name)
        plt.legend()
        plt.show()
        
        
def NotebookContext(context, config_filepath):
    if context.params.__class__.__name__ == 'OfflineContextParams':
        context = NotebookOfflineContext(context, config_filepath)
    return context


class NotebookOfflineContext:
    def __init__(self, context, config_filepath):
        self.context = context
        self.config = NeptuneConfig(config_filepath)
        self.channels={}
        
    @property
    def params(self):
        return self.config.params
    
    def channel_send(self, channel_name, x=None, y=None):
        self.channels[channel_name] = self.channels.get(channel_name, NotebookChannel(channel_name))
        self.channels[channel_name].update({'x':x, 'y':y})
        self.channels[channel_name].plot()