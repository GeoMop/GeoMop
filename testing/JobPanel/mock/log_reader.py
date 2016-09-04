import re
from datetime import datetime

class Log:
    def __init__(self, file):
        self.errors = []
        self.warnings = []
        self.infos = []
        self.debugs = []
        self.start = None
        self.stop = None
        self.records = 0
        with open(file) as f:
            res = f.readlines()
            cat = None
            for line in res:
                # 2016-07-26 10:09:46,016 INFO Application delegator is started
                record = re.search(r'^\s*(\d+-\d+-\d+\s+\d+:\d+:\d+[,\d]*)\s+(\S+)\s+(.+)$', line)
                if record:
                    self.records += 1
                    time = datetime.strptime(record.group(1), "%Y-%m-%d %H:%M:%S,%f")
                    if self.start is None:
                        self.start = time
                    self.stop = time    
                    cat = record.group(2)
                    text = record.group(3)
                    if cat=='ERROR':
                        self.errors.append(text)
                    elif cat=='WARNING':
                        self.warnings.append(text)
                    elif cat=='INFO':
                        self.infos.append(text)
                    elif cat=='DEBUG':
                        self.debugs.append(text)
                elif cat is not None and line is not None and \
                    len(line)>0 and not line.isspace():
                    if cat=='ERROR':
                        self.errors[-1] += "\n" + line
                    elif cat=='WARNING':
                        self.warnings[-1] += "\n" + line
                    elif cat=='INFO':
                        self.infos[-1] += "\n" + line
                    elif cat=='DEBUG':
                        self.debugs[-1] += "\n" + line
                        
    def get_pid(self):
        for mess in self.debugs:
            pid = re.search(r'^PID:\s+(.+)$', mess)
            if pid:
                return pid.group(1)
        return None
