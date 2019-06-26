import attr
from common.analysis.code import dummy, wrap
from common.analysis import action_workflow as wf
from common.analysis import action_base as base

class _Variables:
    """
    Helper class to store local variables of the workflow and use
    their names as instance names for the assigned actions, i.e.
    variables.x = action_y(...)
    will set the instance name of 'action_y' to 'x'. This allows to
    use 'x' as the variable name in subsequent code generation. Otherwise
    a Python variable name is not accessible at runtime.
    """
    def __setattr__(self, key, value):
        value = wrap.into_action(value)
        value = value.set_name(key)
        self.__dict__[key] = value




def workflow(func):
    """
    Decorator to crate a Workflow class from a function.
    """
    workflow_name = func.__name__

    params, output_type = base.extract_func_signature(func, skip_self=False)
    param_names = [param.name for param in params]
    func_args = []
    variables = _Variables()
    if param_names[0] == 'self':
        func_args.append(variables)
        param_names = param_names[1:]

    slots = [wf.SlotInstance(name) for i, name in enumerate(param_names)]
    dummies = [dummy.Dummy(slot) for slot in slots]
    func_args.extend(dummies)
    print(func)
    output_action = wrap.into_action(func(*func_args))

    new_workflow = wf._Workflow(workflow_name)
    new_workflow.set_from_source(slots, output_type, output_action)
    return wrap.public_action(new_workflow)


def analysis(func):
    """
    Decorator for the main analysis workflow of the module.
    """
    w: wrap.ActionWrapper = workflow(func)
    assert isinstance(w.action, wf._Workflow)
    assert len(w.action._slots) == 0
    w.action.is_analysis = True
    return w


def Class(data_class):
    """
    Decorator to add dunder methods using attr.
    Moreover dot access returns the converter.Get action instead of the value itself.
    This is necessary to catch it in the workflow decorator.
    """
    data_class = attr.s(data_class, auto_attribs=True)
    dataclass_action = base.ClassActionBase(data_class)
    return wrap.public_action(dataclass_action)


def action(func):
    """
    Decorator to make an action class from the evaluate function.
    Action name is given by the nama of the function.
    Input types are given by the type hints of the function params.
    """
    action_name = func.__name__
    action = base._ActionBase(action_name, evaluate=func)
    return wrap.public_action(action)
