"""
Bayesian model with binomial likelihood.
"""

# Guillermo Navas-Palencia <g.navas.palencia@gmail.com>
# Copyright (C) 2019

import numpy as np

from scipy import special

from .cdist import BetaABTest
from .cdist import BetaModel
from .cdist.utils import check_models


class BinomialModel(BetaModel):
    """
    Bayesian model with a binomial likelihood and a beta prior distribution.

    Given data samples :math:`\mathbf{x} = (x_1, \ldots, x_n)`
    from a binomial distribution with parameters :math:`m` and :math:`p`, the
    posterior distribution is

    .. math::

        p | \\mathbf{x} \\sim \\mathcal{B}\\left(\\alpha + \\sum_{i=1}^n x_i,
        \\beta + mn - \sum_{i=1}^n x_i\\right),
    
    with prior parameters :math:`\\alpha` and :math:`\\beta`.

    Parameters
    ----------
    m : int
        Number of trials.

    alpha : int or float (default=1)
        Prior parameter alpha.

    beta: int or float (default=1)
        Prior parameter beta.
    """
    def __init__(self, m, alpha=1, beta=1):
        super().__init__(alpha, neta)

        self.m = m

    def update(self, data):
        """
        Update posterior parameters with new data samples.

        Parameters
        ----------
        data : array-like, shape = (n_samples)
            Data samples from a binomial distribution.
        """
        n = len(data)
        n_success = np.sum(data)
        self._alpha_posterior += n_success
        self._beta_posterior += self.m * n - n_success

    def pppdf(self, x):
        """
        Posterior predictive probability density function.

        If :math:`X` follows a binomial distribution with parameters :math:`m`
        and :math:`p`, then the posterior predictive probability density
        function is given by

        .. math::

            f(x; m, \\alpha, \\beta) = \\binom{m}{x} \\frac{B(\\alpha + x, m -
            x + \\beta)}{B(\\alpha, \\beta)},

        where :math:`\\alpha` and :math:`\\beta` are the posterior values
        of the parameters.

        Parameters
        ----------
        x : array-like
            Quantiles.

        Returns
        -------
        pdf : float
            Probability density function evaluated at x.        
        """
        a = self._shape_posterior
        b = self._rate_posterior
        
        loggm = special.gammaln(self.m + 1)
        loggx = special.gammaln(x + 1)
        loggmx = special.gammaln(self.m - x + 1)

        logcomb = loggm - loggx - loggmx
        logbeta = special.betaln(a + x, b + self.m - x) - special.betaln(a, b)
        logpdf = logcomb + logbeta
        return np.exp(logpdf)

    def ppmean(self):
        """
        Posterior predictive mean.

        If :math:`X` follows a binomial distribution with parameters :math:`m`
        and :math:`p`, then the posterior predictive expected value is given by

        .. math::
            
            \\mathrm{E}[X] = m \\frac{\\alpha}{\\alpha + \\beta},

        where :math:`\\alpha` and :math:`\\beta` are the posterior values
        of the parameters.

        Returns
        -------
        mean : float  
        """
        a = self._alpha_posterior
        b = self._beta_posterior

        return self.m * a / (a + b)

    def ppvar(self):
        """
        Posterior predictive variance.

        If :math:`X` follows a binomial distribution with parameters :math:`m`
        and :math:`p`, then the posterior predictive variance is given by

        .. math::

            \\mathrm{Var}[X] = \\frac{m \\alpha \\beta (m + \\alpha + \\beta)}
            {(\\alpha + \\beta)^2 (\\alpha + \\beta + 1)}

        where :math:`\\alpha` and :math:`\\beta` are the posterior values
        of the parameters.

        Returns
        -------
        var : float        
        """
        a = self._alpha_posterior
        b = self._beta_posterior

        return self.m * (self.m + a + b) * a * b / (a + b) ** 2 / (a + b + 1)


class BinomialABTest(BetaABTest):
    """
    Binomial A/B test.

    Parameters
    ----------
    modelA : object
        The control model.

    modelB : object
        The variation model.

    simulations : int or None (default=1000000)
        Number of Monte Carlo simulations.

    random_state : int or None (default=None)
        The seed used by the random number generator.
    """
    def __init__(self, modelA, modelB, simulations=1000000, random_state=None):
        super().__init__(modelA, modelB, simulations, random_state)

        check_models(BinomialModel, modelA, modelB)
