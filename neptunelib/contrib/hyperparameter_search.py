import matplotlib
matplotlib.use('Agg')

import subprocess

import numpy as np
import neptune
import skopt
import skopt.plots as sk_plots
from scipy.optimize import OptimizeResult

from .visualizations import fig2pil, axes2fig

CTX = neptune.Context()

def make_objective(param_set, script_name, metric_name, tag):    
    cmd = ["neptune", "run",
           "--snapshot",
           "--tag " "{}".format(tag),
           "--exclude", "'*'",
           "--config", "neptune_local.yaml"]
    
    for name, value in param_set.items():
        cmd.append("--parameter {}:{}".format(name, value))
    cmd.append(script_name)
    cmd = " ".join(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    score = _get_score(p, metric_name)    
    return score


class Monitor:
    def __init__(self):
        self.iteration = 0
        
    def __call__(self, res):
        CTX.channel_send('hyperparameter_search_score', 
                         x=self.iteration, y=res.func_vals[-1])
        CTX.channel_send('search_parameters', 
                         x=self.iteration, y=res.x_iters[-1])
        self.iteration+=1
        
        
class CheckpointSaver:
    """
    Save current state after each iteration with `skopt.dump`.
    Example usage:
        import skopt
        checkpoint_callback = skopt.callbacks.CheckpointSaver("./result.pkl")
        skopt.gp_minimize(obj_fun, dims, callback=[checkpoint_callback])
    Parameters
    ----------
    * `checkpoint_path`: location where checkpoint will be saved to;
    * `dump_options`: options to pass on to `skopt.dump`, like `compress=9`
    """
    def __init__(self, checkpoint_path, **dump_options):
        self.checkpoint_path = checkpoint_path
        self.dump_options = dump_options

    def __call__(self, res):
        """
        Parameters
        ----------
        * `res` [`OptimizeResult`, scipy object]:
            The optimization as a OptimizeResult object.
        """
        skopt.dump(res, self.checkpoint_path, **self.dump_options)


def send_skopt_results(results, ctx, metric_name):
    ctx.channel_send(metric_name, results.fun)
    ctx.channel_send('best_parameters', results.x)

    convergence = fig2pil(axes2fig(sk_plots.plot_convergence(results)))
    ctx.channel_send('convergence', neptune.Image(
            name='convergence',
            description="plot_convergence from skopt",
            data=convergence))

    evaluations = fig2pil(axes2fig(sk_plots.plot_evaluations(results, bins=10)))
    ctx.channel_send('evaluations', neptune.Image(
            name='evaluations',
            description="plot_evaluations from skopt",
            data=evaluations))
    
    try:
        objective = fig2pil(axes2fig(sk_plots.plot_objective(results)))
        ctx.channel_send('objective', neptune.Image(
                name='objective',
                description="plot_objective from skopt",
                data=objective))
    except Exception:
        print('Could not create ans objective chart')
        

def send_hyperopt_results(results, ctx, metric_name):
    send_skopt_results(results, ctx, metric_name)
    
    for i, loss in enumerate(results.func_vals):
        ctx.channel_send('hyperparameter_search_score', x=i, y=loss)
        
        
def send_bayes_opt_results(results, ctx, metric_name):
    send_skopt_results(results, ctx, metric_name)

    for i, loss in enumerate(results.func_vals):
        ctx.channel_send('hyperparameter_search_score', x=i, y=loss)
    
    
def convert_results(results, space, convert_from='hyperopt', convert_to='skopt'):
    if convert_to !='skopt':
        raise NotImplementedError
    elif convert_from =='skopt':
        raise NotImplementedError
    elif convert_from =='hyperopt' and convert_to == 'skopt':
        return _convert_results_hop_skopt(results, space)
    elif convert_from =='bayes_opt' and convert_to == 'skopt':
        return _convert_results_bayes_skopt(results, space) 
    else:
        raise NotImplementedError


def _get_score(popen, metric_name):
    output, _ = popen.communicate()
    output = str(output).split('\\n')
    output = [l for l in output if metric_name in l]
    score = float(output[-1].split(' ')[-1])
    return score
        
    
def _convert_results_hop_skopt(results, space):
    param_names = list(space.keys())
    skopt_space = _convert_space_hop_skopt(space)
    results_ = {}
    for trial in results.trials:
        trial_params=[trial['misc']['vals'][name][0] for name in param_names]
        results_.setdefault('x_iters',[]).append(trial_params)
        results_.setdefault('func_vals',[]).append(trial['result']['loss'])
    optimize_results = OptimizeResult()
    optimize_results.x = list(results.argmin.values())
    optimize_results.x_iters = results_['x_iters']
    optimize_results.fun = results.best_trial['result']['loss']
    optimize_results.func_vals = results_['func_vals']
    optimize_results.space = skopt_space
    return optimize_results


def _convert_results_bayes_skopt(results, space):
    param_names = list(space.keys())
    skopt_space = _convert_space_bayes_opt_skopt(space)
    best_iter = np.argmax(results.Y)
    
    optimize_results = OptimizeResult()
    optimize_results.x = results.X[best_iter]
    optimize_results.x_iters = results.X.astype(int)
    optimize_results.fun = -1.0 * results.Y[best_iter]
    optimize_results.func_vals = -1.0 * results.Y
    optimize_results.space = skopt_space
    return optimize_results


def _convert_space_bayes_opt_skopt(space):
    dimensions = []
    for name, bounds in space.items():
        low, high = bounds
        dimensions.append(skopt.space.Integer(low, high, name=name))
    skopt_space = skopt.Space(dimensions)    
    return skopt_space


def _convert_space_hop_skopt(space):
    dimensions = []
    for name, specs in space.items():
        specs = str(specs).split('\n')
        method = specs[3].split(' ')[-1]
        bounds = specs[4:]
        if len(bounds) == 1:
            bounds = bounds[0].split('range')[-1]
            bounds = bounds.replace('(','').replace(')','').replace('}','')
            low, high = [float(v) for v in bounds.split(',')]
        else:
            vals = [float(b.split('Literal')[-1].replace('}','').replace('{',''))
                   for b in bounds]
            low = min(vals)
            high = max(vals)
        if method == 'randint':
            dimensions.append(skopt.space.Integer(low, high, name=name))
        elif method == 'uniform':
            dimensions.append(skopt.space.Real(low, high, name=name, prior='uniform'))
        elif method == 'loguniform':
            dimensions.append(skopt.space.Real(low, high, name=name, prior='log-uniform'))
        else:
            raise NotImplementedError
    skopt_space = skopt.Space(dimensions)    
    return skopt_space


def _clean_columns(columns):
    columns_ = []
    for col in columns:
        if col.startswith('#'):
            col = col.split(' ')[-1]
        col = col.strip()
        columns_.append(col)
    return columns_