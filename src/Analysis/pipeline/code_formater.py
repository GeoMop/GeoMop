class Formater:
    
    @staticmethod
    def indent(lines, spaces):
        """indent code in line"""
        res = []
        for i in range(0, len(lines)):
            if len(lines[i])==0 or  lines[i].isspace():
                res.append("")
            else:
                res.append(spaces*" "+lines[i])
        return res

    @classmethod
    def format_parameter(cls, param, spaces):
        """
        if param is one line, return indented one line,
        otherwise indented lines in bracket
        """
        if len(param)==0:
            return []
        elif len(param)==1:
            return [spaces*" "+param[0] + ","]
        res=[]
        res.append(spaces*" "+"(")
        res.extend(cls.indent(param, spaces+4))
        res.append(spaces*" "+"),")
        return res
