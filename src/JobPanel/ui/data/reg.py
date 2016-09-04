import pickle
import os
import stat
class Regs():
    def __init__(self, home):
        self.file = os.path.join(home, ".reg")
    def get_id(self, reg):
        if os.path.isfile(self.file):
            with open(self.file, 'rb') as f:
                recs = pickle.load(f)
                for rec in recs:
                    if rec[1] == reg:
                        return rec[0], rec[2] 
        return None, None
    def set_id(self, id, reg, code):
        recs = []
        new = True
        if os.path.isfile(self.file):
            with open(self.file, 'rb') as f:
                recs = pickle.load(f)
                for rec in recs:
                    if rec[1] == reg:
                        if rec[2]==code and rec[0]==id:
                            return
                        rec[0]=id
                        rec[2]=code
                        new = False
                        break
        if new:
            recs.append([id, reg, code])
        with open(self.file, 'wb') as f:
            pickle.dump(recs, f)
        os.chmod(self.file,stat.S_IRUSR | stat.S_IWUSR )
    def del_id(self, reg):
        if os.path.isfile(self.file):
            recs = []
            with open(self.file, 'rb') as f:
                recs = pickle.load(f)
                rec_del = None
                for rec in recs:
                    if rec[1] == reg:
                        rec_del = rec
                        break
            if rec_del is not None:
                recs.remove(rec_del)
            with open(self.file, 'wb') as f:
                pickle.dump(recs, f)
        os.chmod(self.file,stat.S_IRUSR | stat.S_IWUSR)
