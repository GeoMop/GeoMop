class Formater:
    
    @staticmethod
    def indent(lines, spaces):
        """indent code in line"""
        for i in range(0, len(lines)):
            lines[i] = spaces*" "+lines[i]  
        
