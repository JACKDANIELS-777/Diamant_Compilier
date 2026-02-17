class Data_Types:
    Types_Info = {"db": {"max":255,"min":0}}
    db = 1
    dw = 2
    dd = 4

class Generate_Type_Update:

    @staticmethod
    def add_to_var(varname, value, self,opp="none"):
        """Generate NASM to add an immediate or variable to varname."""

        vartype = self.segments["section .data"][varname]["type"]

        if vartype == "db":
            size = "byte"
        elif vartype == "dw":
            size = "word"
        elif vartype == "dd":
            size = "dword"
        else:
            raise Exception(f"Unknown variable type: {vartype}")

        asm = f"{opp} {size} [{varname}], {value}"
        self.segments["section .text"]["main"].append(asm)

    @staticmethod
    def Left_Var(node, self,opp):
        varname = node[1][1]           # left side var
        rhs_val = self.walkTree(node[2])
        Generate_Type_Update.add_to_var(varname, rhs_val, self,opp)

    @staticmethod
    def Right_Var(node, self,opp):
        varname = node[2][1]           # right side var
        lhs_val = self.walkTree(node[1])
        Generate_Type_Update.add_to_var(varname, lhs_val, self,opp)

    @staticmethod
    def Both_Var(node,self,opp):
        return
        varname = node[1][1]
        varname1 = node[2][1]
        Generate_Type_Update.add_to_var(varname, varname1, self,opp)



