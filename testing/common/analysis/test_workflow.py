import pytest
import common.analysis.action_instance as instance
import common.analysis.action_workflow as wf
import common.analysis.action_base as base

def test_workflow_modification():
    w = wf._Workflow("tst_wf")

    ## Slot modifications
    # insert_slot
    w.insert_slot(0, wf.Slot("a_slot"))
    w.insert_slot(1, wf.Slot("b_slot"))
    assert w.parameters.size() == 2
    assert w.parameters.get_index(0).name == 'a_slot'
    assert w.parameters.get_index(1).name == 'b_slot'

    # move_slot
    w.insert_slot(2, wf.Slot("c_slot"))
    # A B C
    w.move_slot(1, 2)
    # A C B
    assert w.parameters.get_index(2).name == 'b_slot'
    assert w.parameters.get_index(1).name == 'c_slot'
    w.move_slot(2, 0)
    # B A C
    assert w.parameters.get_index(0).name == 'b_slot'
    assert w.parameters.get_index(1).name == 'a_slot'
    assert w.parameters.get_index(2).name == 'c_slot'

    # remove_slot
    w.remove_slot(2)
    assert w.parameters.size() == 2

    ## Action modifications
    result = w.result
    slots = w.slots
    list_1 = instance.ActionInstance.create( base.List())
    w.set_action_input(list_1, 0, slots[0])
    w.set_action_input(list_1, 1, slots[1])
    w.set_action_input(result, 0, list_1)
    assert slots[0].output_actions[0][0] == list_1
    assert slots[1].output_actions[0][0] == list_1
    assert list_1.output_actions[0][0] == result
    assert list_1.name == 'List_1'
    assert len(w._actions) == 4