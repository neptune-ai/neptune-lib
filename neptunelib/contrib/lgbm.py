from deepsense import neptune

ctx = neptune.Context()


def neptune_monitor(prefix=''):
    def callback(env):
        for name, loss_name, loss_value, _ in env.evaluation_result_list:
            if prefix != '':
                channel_name = '{}_{}_{}'.format(prefix, name, loss_name)
            else:
                channel_name = '{}_{}'.format(name, loss_name)
            ctx.channel_send(channel_name, x=env.iteration, y=loss_value)

    return callback