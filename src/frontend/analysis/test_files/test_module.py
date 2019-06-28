import common.analysis as wf


@wf.workflow
def test_list(self, a, b):
    self.c = [a]
    List_1 = [a, b]
    List_2 = [self.c, List_1]
    return List_2

@wf.workflow
def test_list1(self, a, b):
    self.c = [a]
    List_1 = [a, b]
    return List_1

