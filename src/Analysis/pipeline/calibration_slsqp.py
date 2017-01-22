"""
replacement of _minimize_slsqp from scipy.optimize.slsqp
scipy version 0.18.1
"""

import numpy as np
from scipy.optimize._slsqp import slsqp
from numpy import zeros, array, linalg, append, asfarray, concatenate, finfo, \
                  sqrt, vstack, exp, inf, where, isfinite, atleast_1d
from scipy.optimize.optimize import wrap_function, OptimizeResult, _check_unknown_options
from scipy.optimize.slsqp import approx_jacobian

__docformat__ = "restructuredtext en"

_epsilon = sqrt(finfo(float).eps)


def min_slsqp(func, x0, args=(), jac=None, bounds=None,
                    constraints=(),
                    maxiter=100, ftol=1.0E-6, iprint=1, disp=False,
                    eps=_epsilon, callback=None, ter_crit=None,
                    **unknown_options):
    """
    Minimize a scalar function of one or more variables using Sequential
    Least SQuares Programming (SLSQP).

    Options
    -------
    ftol : float
        Precision goal for the value of f in the stopping criterion.
    eps : float
        Step size used for numerical approximation of the jacobian.
    disp : bool
        Set to True to print convergence messages. If False,
        `verbosity` is ignored and set to 0.
    maxiter : int
        Maximum number of iterations.

    """
    _check_unknown_options(unknown_options)
    fprime = jac
    iter = maxiter
    acc = ftol
    epsilon = eps

    if not disp:
        iprint = 0

    # Constraints are triaged per type into a dictionnary of tuples
    if isinstance(constraints, dict):
        constraints = (constraints, )

    cons = {'eq': (), 'ineq': ()}
    for ic, con in enumerate(constraints):
        # check type
        try:
            ctype = con['type'].lower()
        except KeyError:
            raise KeyError('Constraint %d has no type defined.' % ic)
        except TypeError:
            raise TypeError('Constraints must be defined using a '
                            'dictionary.')
        except AttributeError:
            raise TypeError("Constraint's type must be a string.")
        else:
            if ctype not in ['eq', 'ineq']:
                raise ValueError("Unknown constraint type '%s'." % con['type'])

        # check function
        if 'fun' not in con:
            raise ValueError('Constraint %d has no function defined.' % ic)

        # check jacobian
        cjac = con.get('jac')
        if cjac is None:
            # approximate jacobian function.  The factory function is needed
            # to keep a reference to `fun`, see gh-4240.
            def cjac_factory(fun):
                def cjac(x, *args):
                    return approx_jacobian(x, fun, epsilon, *args)
                return cjac
            cjac = cjac_factory(con['fun'])

        # update constraints' dictionary
        cons[ctype] += ({'fun': con['fun'],
                         'jac': cjac,
                         'args': con.get('args', ())}, )

    exit_modes = {-1: "Gradient evaluation required (g & a)",
                    0: "Optimization terminated successfully.",
                    1: "Function evaluation required (f & c)",
                    2: "More equality constraints than independent variables",
                    3: "More than 3*n iterations in LSQ subproblem",
                    4: "Inequality constraints incompatible",
                    5: "Singular matrix E in LSQ subproblem",
                    6: "Singular matrix C in LSQ subproblem",
                    7: "Rank-deficient equality constraint subproblem HFTI",
                    8: "Positive directional derivative for linesearch",
                    9: "Iteration limit exceeded"}

    # Wrap func
    feval, func = wrap_function(func, args)

    # Wrap fprime, if provided, or approx_jacobian if not
    if fprime:
        geval, fprime = wrap_function(fprime, args)
    else:
        geval, fprime = wrap_function(approx_jacobian, (func, epsilon))

    # Transform x0 into an array.
    x = asfarray(x0).flatten()

    # Set the parameters that SLSQP will need
    # meq, mieq: number of equality and inequality constraints
    meq = sum(map(len, [atleast_1d(c['fun'](x, *c['args'])) for c in cons['eq']]))
    mieq = sum(map(len, [atleast_1d(c['fun'](x, *c['args'])) for c in cons['ineq']]))
    # m = The total number of constraints
    m = meq + mieq
    # la = The number of constraints, or 1 if there are no constraints
    la = array([1, m]).max()
    # n = The number of independent variables
    n = len(x)

    # Define the workspaces for SLSQP
    n1 = n + 1
    mineq = m - meq + n1 + n1
    len_w = (3*n1+m)*(n1+1)+(n1-meq+1)*(mineq+2) + 2*mineq+(n1+mineq)*(n1-meq) \
            + 2*meq + n1 + ((n+1)*n)//2 + 2*m + 3*n + 3*n1 + 1
    len_jw = mineq
    w = zeros(len_w)
    jw = zeros(len_jw)

    # Decompose bounds into xl and xu
    if bounds is None or len(bounds) == 0:
        xl = np.empty(n, dtype=float)
        xu = np.empty(n, dtype=float)
        xl.fill(np.nan)
        xu.fill(np.nan)
    else:
        bnds = array(bounds, float)
        if bnds.shape[0] != n:
            raise IndexError('SLSQP Error: the length of bounds is not '
                             'compatible with that of x0.')

        bnderr = where(bnds[:, 0] > bnds[:, 1])[0]
        if bnderr.any():
            raise ValueError('SLSQP Error: lb > ub in bounds %s.' %
                             ', '.join(str(b) for b in bnderr))
        xl, xu = bnds[:, 0], bnds[:, 1]

        # Mark infinite bounds with nans; the Fortran code understands this
        infbnd = ~isfinite(bnds)
        xl[infbnd[:, 0]] = np.nan
        xu[infbnd[:, 1]] = np.nan

    # Initialize the iteration counter and the mode value
    mode = array(0,int)
    acc = array(acc,float)
    majiter = array(iter,int)
    majiter_prev = 0

    # Print the header if iprint >= 2
    if iprint >= 2:
        print("%5s %5s %16s %16s" % ("NIT","FC","OBJFUN","GNORM"))

    terminator = ter_crit.get_terminator()

    while 1:
        if mode == 0 or mode == 1:  # objective and constraint evaluation requird

            # Compute objective function
            fx = func(x)
            # Compute the constraints
            if cons['eq']:
                c_eq = concatenate([atleast_1d(con['fun'](x, *con['args']))
                                     for con in cons['eq']])
            else:
                c_eq = zeros(0)
            if cons['ineq']:
                c_ieq = concatenate([atleast_1d(con['fun'](x, *con['args']))
                                     for con in cons['ineq']])
            else:
                c_ieq = zeros(0)

            # Now combine c_eq and c_ieq into a single matrix
            c = concatenate((c_eq, c_ieq))

        if mode == 0 or mode == -1:  # gradient evaluation required

            # Compute the derivatives of the objective function
            # For some reason SLSQP wants g dimensioned to n+1
            g = append(fprime(x),0.0)

            # Compute the normals of the constraints
            if cons['eq']:
                a_eq = vstack([con['jac'](x, *con['args'])
                               for con in cons['eq']])
            else:  # no equality constraint
                a_eq = zeros((meq, n))

            if cons['ineq']:
                a_ieq = vstack([con['jac'](x, *con['args'])
                                for con in cons['ineq']])
            else:  # no inequality constraint
                a_ieq = zeros((mieq, n))

            # Now combine a_eq and a_ieq into a single a matrix
            if m == 0:  # no constraints
                a = zeros((la, n))
            else:
                a = vstack((a_eq, a_ieq))
            a = concatenate((a,zeros([la,1])),1)

        # Call SLSQP
        slsqp(m, meq, x, xl, xu, fx, c, g, a, acc, majiter, mode, w, jw)

        # call callback if major iteration has incremented
        if callback is not None and majiter > majiter_prev:
            callback(x)

        # Print the status of the current iterate if iprint > 2 and the
        # major iteration has incremented
        if iprint >= 2 and majiter > majiter_prev:
            print("%5i %5i % 16.6E % 16.6E" % (majiter,feval[0],
                                               fx,linalg.norm(g)))

        # If exit mode is not -1 or 1, slsqp has completed
        if abs(mode) != 1:
            break

        # ToDo:
        if majiter > majiter_prev:
            if terminator(x, fx, g[:-1]):
                break

        majiter_prev = int(majiter)

    # Optimization loop complete.  Print status if requested
    if iprint >= 1:
        print(exit_modes[int(mode)] + "    (Exit mode " + str(mode) + ')')
        print("            Current function value:", fx)
        print("            Iterations:", majiter)
        print("            Function evaluations:", feval[0])
        print("            Gradient evaluations:", geval[0])

    return OptimizeResult(x=x, fun=fx, jac=g, nit=int(majiter), nfev=feval[0],
                          njev=geval[0], status=int(mode),
                          message=exit_modes[int(mode)], success=(mode == 0))
