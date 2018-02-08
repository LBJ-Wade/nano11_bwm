from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import numpy as np


class JumpProposal(object):
    
    def __init__(self, pta):
        """Set up some custom jump proposals
        
        :param params: A list of `enterprise` parameters
        
        """
        self.params = pta.params
        self.npar = len(pta.params)
        self.ndim = sum(p.size or 1 for p in pta.params)
        
        # parameter map
        self.pmap = {}
        ct = 0
        for p in pta.params:
            size = p.size or 1
            self.pmap[p] = slice(ct, ct+size)
            ct += size
            
        # parameter indices map
        self.pimap = {}
        for ct, p in enumerate(pta.param_names):
            self.pimap[p] = ct
            
        self.snames = {}
        for sc in pta._signalcollections:
            for signal in sc._signals:
                self.snames[signal.signal_name] = signal.params


    def draw_from_prior(self, x, iter, beta):
        """Prior draw.
        
        The function signature is specific to PTMCMCSampler.
        """
        
        q = x.copy()
        lqxy = 0
        
        # randomly choose parameter
        idx = np.random.randint(0, self.npar)
        
        # if vector parameter jump in random component
        param = self.params[idx]
        if param.size:
            idx2 = np.random.randint(0, param.size)
            q[self.pmap[param]][idx2] = param.sample()[idx2]

        # scalar parameter
        else:
            q[idx] = param.sample()
        
        # forward-backward jump probability
        lqxy = param.get_logpdf(x[self.pmap[param]]) - param.get_logpdf(q[self.pmap[param]])
                
        return q, float(lqxy)


    def draw_from_gwb_prior(self, x, iter, beta):
        q = x.copy()
        lqxy = 0
        
        signal_name = 'red noise'
        
        # draw parameter from signal model
        param = np.random.choice(self.snames[signal_name])
        if param.size:
            idx2 = np.random.randint(0, param.size)
            q[self.pmap[param]][idx2] = param.sample()[idx2]

        # scalar parameter
        else:
            q[self.pmap[param]] = param.sample()
        
        # forward-backward jump probability
        lqxy = param.get_logpdf(x[self.pmap[param]]) - param.get_logpdf(q[self.pmap[param]])
                        
        return q, float(lqxy)


    def draw_from_bwm_prior(self, x, iter, beta):
        q = x.copy()
        lqxy = 0
        
        signal_name = 'bwm'
        
        # draw parameter from signal model
        param = np.random.choice(self.snames[signal_name])
        if param.size:
            idx2 = np.random.randint(0, param.size)
            q[self.pmap[param]][idx2] = param.sample()[idx2]

        # scalar parameter
        else:
            q[self.pmap[param]] = param.sample()
        
        # forward-backward jump probability
        lqxy = param.get_logpdf(x[self.pmap[param]]) - param.get_logpdf(q[self.pmap[param]])
                        
        return q, float(lqxy)


    def draw_from_ephem_prior(self, x, iter, beta):        
        q = x.copy()
        lqxy = 0
        
        signal_name = 'phys_ephem'
        
        # draw parameter from signal model
        param = np.random.choice(self.snames[signal_name])
        if param.size:
            idx2 = np.random.randint(0, param.size)
            q[self.pmap[param]][idx2] = param.sample()[idx2]

        # scalar parameter
        else:
            q[self.pmap[param]] = param.sample()
        
        # forward-backward jump probability
        lqxy = param.get_logpdf(x[self.pmap[param]]) - param.get_logpdf(q[self.pmap[param]])
                
        return q, float(lqxy) 


# utility function for finding global parameters
def get_global_parameters(pta):
    pars = []
    for sc in pta._signalcollections:
        pars.extend(sc.param_names)
    
    gpars = np.unique(filter(lambda x: pars.count(x)>1, pars))
    ipars = np.array([p for p in pars if p not in gpars])
        
    return gpars, ipars


# utility function to get parameter groupings for sampling
def get_parameter_groups(pta):
    ndim = len(pta.param_names)
    groups  = [range(0, ndim)]
    params = pta.param_names
    
    # get global and individual parameters
    gpars, ipars = get_global_parameters(pta)
    if any(gpars):
        groups.extend([[params.index(gp) for gp in gpars]])

    for sc in pta._signalcollections:
        for signal in sc._signals:
            ind = [params.index(p) for p in signal.param_names if p not in gpars]
            if ind:
                groups.extend([ind])
    
    return groups
