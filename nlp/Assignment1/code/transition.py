class Transition(object):
    """
    This class defines a set of transitions which are applied to a
    configuration to get the next configuration.

    s(wi): the next node in Sigma(stack),
    b(wj): the next node in B(buffer),
    A: the set of arcs that represent the dependency relations
    L: relation label
    """
    # Define set of transitions
    LEFT_ARC = 'LEFTARC'
    RIGHT_ARC = 'RIGHTARC'
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'

    def __init__(self):
        raise ValueError('Do not construct this object!')

    @staticmethod
    def left_arc(conf, relation):
        """
            Add the arc(b,L,s) to A, and pop Sigma.
            :param configuration: is the current configuration
            :return : A new configuration or -1 if the pre-condition is not satisfied
        """
        # raise NotImplementedError('Please implement left_arc!')
        if not conf.buffer or not conf.stack:
            return -1

        idx_wi = conf.stack.pop()
        idx_wj = conf.buffer[0]
        conf.arcs.append((idx_wj, relation, idx_wi))    # adding arc relation(Wj, Wi)

    @staticmethod
    def right_arc(conf, relation):
        """
            Add the arc(s,L,b) to A, and push b onto Sigma.
            :param configuration: is the current configuration
            :return : A new configuration or -1 if the pre-condition is not satisfied
        """
        if not conf.buffer or not conf.stack:
            return -1

        # You get this one for free! Use it as an example.

        idx_wi = conf.stack[-1]
        idx_wj = conf.buffer.pop(0)

        conf.stack.append(idx_wj)
        conf.arcs.append((idx_wi, relation, idx_wj))

    @staticmethod
    def reduce(conf):
        """
            Pop Sigma.
            :param configuration: is the current configuration
            :return : A new configuration or -1 if the pre-condition is not satisfied
        """
        # raise NotImplementedError('Please implement reduce!')
        if not conf.stack:
            return -1
        conf.stack.pop()


    @staticmethod
    def shift(conf):
        """
            Remove b from B and add it to Sigma.
            :param configuration: is the current configuration
            :return : A new configuration or -1 if the pre-condition is not satisfied
        """
        # raise NotImplementedError('Please implement shift!')
        if not conf.buffer:
            return -1
        idx_wi = conf.buffer.pop(0)
        conf.stack.append(idx_wi)
