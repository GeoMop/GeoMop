import common.analysis as wf


@wf.workflow
def test_list(self, a, b):
    self.c = [a]
    List_1 = [a, b]
    List_2 = [self.c, List_1]
    return List_2
