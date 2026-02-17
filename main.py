from sly import Lexer
from sly import Parser
from copy import  deepcopy
import Builtins
import Var_Classes
import re
from Var_Classes import *
from Builtins import Builtins
from Builtins import Generate

class BasicLexer(Lexer):
    tokens = {STRUCT,WHILE,INPUT,PRINT, NAME, NUMBER, STRING, IF, THEN, ELSE, FOR, FUN, TO, ARROW, EQEQ,GEQEQ, LEQEQ,OR,AND,NOT }
    ignore = '\t '

    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';' ,'.','{','}','>','<','[',']',':','&'}
    PRINT = r'print'
    STRUCT = r'struct'
    WHILE = r'while'
    INPUT = r'input'
    #NASM = r'nasm'
    EQEQ = r'=='
    GEQEQ = r'>='
    LEQEQ = r'<='
    AND = r'and'
    OR = r'or'
    NOT = r'not'
    # Define tokens
    IF = r'IF'

    THEN = r'THEN'

    ELSE = r'ELSE'
    FOR = r'FOR'
    FUN = r'FUN'
    TO = r'TO'
    ARROW = r'->'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    #STRING = r'\".*?\"'
    STRING = r'\"[\s\S]*?\"'




    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self,t ):
        self.lineno = t.value.count('\n')

class BasicParser(Parser):
    tokens = BasicLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', 'AND', 'OR'),
        ('left', '>', '<', 'GEQEQ', 'LEQEQ', 'EQEQ',"."),
        ('right', 'UMINUS',"NOT","deref","addr"),
        )

    def __init__(self):
        self.env = { }

    @_('')
    def statement(self, p):
        pass

    @_("Body")
    def statement(self, p):
        return p.Body

    @_("'{' procs '}'")
    def Body(self, p):
        return p.procs

    # for classes


    @_("procs ',' proc")
    def procs(self, p):
        return p.procs + [p.proc]

    @_('proc')
    def procs(self, p):
        return [p.proc]

    @_('statement')
    def proc(self, p):
        return p.statement


    @_('FOR var_assign TO expr THEN statement')
    def statement(self, p):
        return ("for_loop", p.var_assign, p.expr, p.statement)
        return ('for_loop', ('for_loop_setup', p.var_assign, p.expr), p.statement)



    @_('IF expr THEN statement ELSE statement')
    def statement(self, p):
        return ('if_stmt', p.expr, ('branch', p.statement0, p.statement1))

    @_('FUN NAME tuple statement')
    def statement(self, p):
        return ('fun_def_args', p.NAME,p.tuple, p.statement)

    @_('FUN NAME "(" ")" ARROW statement')
    def statement(self, p):
        return ('fun_def', p.NAME, p.statement)

    @_('NAME tuple')
    def statement(self, p):
        return ('fun_call_args', p.NAME,p.tuple)



    @_('NAME "(" ")"')
    def statement(self, p):
        return ('fun_call', p.NAME)

    @_('NAME NAME "(" ")"')
    def statement(self, p):
        return ('fun_call_mod', p.NAME1,p.NAME1)

    @_('expr EQEQ expr')
    def expr(self, p):
        return ('condition_eqeq', p.expr0, p.expr1)

    @_("expr GEQEQ expr")
    def expr(self, p):
        return ("expr_GEQEQ", p.expr0, p.expr1)

    @_("expr LEQEQ expr")
    def expr(self, p):
        return ("expr_LEQEQ", p.expr0, p.expr1)

    @_('expr ">" expr')
    def expr(self, p):
        return ('bigger_than', p.expr0, p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return ('less_than', p.expr0, p.expr1)

    @_('expr AND expr')
    def expr(self, p):
        return ('and', p.expr0, p.expr1)

    @_('expr OR expr')
    def expr(self, p):
        return ('or', p.expr0, p.expr1)

    @_('NOT expr %prec NOT')
    def expr(self, p):
        return ('not', p.expr)

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    #@_('NAME "=" STRING')
    #def var_assign(self, p):
     #   return ('var_assign', p.NAME, p.STRING)

    @_('expr')
    def statement(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)

    @_("PRINT NAME")
    def statement(self, p):
        return ('print', p.NAME)

    @_("INPUT NAME NUMBER")
    def statement(self, p):
        return ('input', p.NAME, p.NUMBER)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_("'.' NAME NUMBER")
    def statement(self, p):
        return ("SET_GLOBAL", p.NAME, p.NUMBER)

    @_("NAME '{' STRING '}' ")
    def statement(self, p):

        return ('nasm_block',p.NAME, p.STRING)

    @_('array')
    def expr(self, p):
        return p.array

    @_('tuple')
    def expr(self, p):
        return p.tuple

    @_("'(' items ')'")
    def tuple(self,p):
        return ('tuple', p.items)
    @_("'[' items ']'")
    def array(self,p):
        return ("array", p.items)
    @_("items ',' item")
    def items(self, p):
        return p.items + [p.item]
    @_("item")
    def items(self,p):
        return [p.item]
    @_("expr")
    def item(self,p):
        return p.expr


    @_("NAME ARROW NAME '=' expr")
    def statement(self, p):
        return ("var_assign_type", p.NAME0,p.NAME1,p.expr)

    @_('WHILE expr ARROW statement')
    def statement(self, p):

        return ("while_loop", p.expr, p.statement)

    @_("STRUCT NAME struct_body")
    def statement(self, p):
        return ("def_struct",p.NAME, p.struct_body)

    @_("NAME '=' STRUCT NAME tuple")
    def statement(self, p):
        return ('assign_struct', p.NAME0,p.NAME1, p.tuple)

    @_("'{' struct_items '}'")
    def struct_body(self,p):
        return p.struct_items
    @_("struct_items ',' struct_item")
    def struct_items(self, p):
        return p.struct_items + [p.struct_item]
    @_("struct_item")
    def struct_items(self,p):
        return [p.struct_item]

    @_("NAME ':' NAME")
    def struct_item(self,p):
        return ("struct_item", p.NAME0,p.NAME1)

    @_('"*" NAME %prec deref')
    def expr(self, p):
        return ('deref', p.NAME)

    @_('"&" NAME %prec addr')
    def expr(self, p):
        return ('addr', p.NAME)

    @_('expr "." expr')
    def expr(self, p):
        return ('dot', p.expr0,p.expr1)
class BasicExecute:
    """align 4
multiboot_header:
    dd 0x1BADB002            ; magic number
    dd 0x0                   ; flags (can set bits later)
    dd -(0x1BADB002 + 0x0)   ; checksum"""
    def __init__(self, tree, env,segments,any_args,general={"counter":0,"for_loop_counter":0,"while_loop_counter":0}):
        self.env = env
        self.segments = segments
        self.general = general
        result = self.walkTree(tree)

        self.any_args = any_args
        self.temp_env = {}
        self.vga_text = "0xb8000"

        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)
    #add a flag to check if we are inside an expr like y = x+1 behaves diff than x+1 to
    #avoid dubble operations
    def walkTree(self, node,flag = 0):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node+",0"

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])



        if node[0] == 'num':
            #returns a num ie int
            return node[1]

        if node[0] == 'str':
            #returns the str with quotes and ,0 for easy acess this does cause some diff later but easy fix
            return node[1]+",0"

        if node[0]=="input":
            #adds input if not added
            if "input:" not in self.segments["section .text"]:


                self.segments["section .text"]["input:"] = {"code": [Builtins.code["input"]], "state": 1}

            #creates the var
            if node[1] not in self.env:
                self.env[node[1]] = {"name":node[1], "type":"str","inf_type":"byte"}
                self.segments["section .bss"].append(f"{node[1]} resb {self.walkTree(node[2])+1}\n")

            #inside main func

            if flag==0:
                self.segments["section .text"]["main"].append(f"mov bl, 0")
                self.segments["section .text"]["main"].append(f"for_loop{self.general["for_loop_counter"]}:")
                self.segments["section .text"]["main"].append(f"\tcmp bl, {self.walkTree(node[2])}")
                self.segments["section .text"]["main"].append(f"\tjg end_for{self.general["for_loop_counter"]}")

                self.segments["section .text"]["main"].append("call input\n")
                self.segments["section .text"]["main"].append(f"mov ecx, {node[1]}\n")
                self.segments["section .text"]["main"].append("add cl, bl\n")
                self.segments["section .text"]["main"].append(f"mov byte [ecx], al\n")


                self.segments["section .text"]["main"].append(f"\tadd bl,1")

                self.segments["section .text"]["main"].append(f"\tjmp for_loop{self.general["for_loop_counter"]}")
                self.segments["section .text"]["main"].append(f"end_for{self.general["for_loop_counter"]}:")
                self.segments["section .text"]["main"].append(f"mov byte [{node[1]}+{self.walkTree(node[2])}], 0")
                self.general["for_loop_counter"] += 1
                return 0


        #for now vga print
        if node[0]=="print":
            #needs to be implemented
            if flag==1:
               return
            num = 0

            #have to fix inside functions havse to copy vars over ie a(1,2) a(a,b) a is 1 with the correct format
            arg_type = self.env[node[1]]["type"]

            if arg_type=="num" or arg_type=="int" or arg_type=="byte" or arg_type=="long":

                if "int_to_str:" not in self.segments["section .text"]:
                    self.segments["section .text"]["int_to_str:"] = {"code": [Builtins.code["int_to_str"]], "state": 1}
                    if self.env[node[1]]["inf_type"]=="byte" or self.env[node[1]]["inf_type"]=="qword" or self.env[node[1]]["inf_type"]=="dword":
                        self.segments["section .bss"].append(f"print_str: resb 12")
                num = 1


            if "print:" not in self.segments["section .text"]:
                self.segments["section .text"]["print:"] = {"code": [Builtins.code["print"]], "state": 1}
                self.segments["section .data"]["vga"]= {"type":"dd", "data":"0xb8000"}
            if flag==0:

                if num==1:
                    print(9)
                    self.segments["section .text"]["main"].append(f"xor eax,eax\nmov al, byte [{node[1]}]\n push eax\n")
                    self.segments["section .text"]["main"].append(f"push print_str\n")

                    self.segments["section .text"]["main"].append(f"call int_to_str\n")
                    self.segments["section .text"]["main"].append(f"""mov esi, print_str\n call print""")

                    return
                self.segments["section .text"]["main"].append(f"""mov esi, {node[1]}\n call print""")
            if flag == 2 or flag ==1:
                if num==1:
                    code = ""
                    code+=f"xor eax,eax\nmov al, byte [{node[1]}]\n push eax\n"
                    code+=f"push print_str\n"

                    code+=f"call int_to_str\n"
                    code+=f"""mov esi, print_str\n call print"""
                    return code
                return f"""mov esi, {node[1]}\n call print"""


        #a.a.b
        if node[0]=="dot":
            #the first time this is ran we set the index
            if "index" not in self.any_args:
                self.any_args["index"] = 0
            #100 or 1001 flag the 100 is for the first time this is ran in a a=... assignment anv
            #any other version from there is 1001 the 100 allows us to know its the last onr in the recursion step
            if flag==100 or flag==1001:


                expr1 = self.walkTree(node[1],1001)
                expr2 = self.walkTree(node[2], 1001)

                #basically its  at the end a.b.c.d .... its at a.b returns b
                #only runs 1 time find the orginal a.b.c its a.b a is orginal returns b
                if expr1 in self.env and self.any_args["index"]==0:

                    var = self.env[expr1]
                    type = var["type"]

                    if type=="struct":
                        inf_type =var["inf_type"]
                        struct = self.env["structs"][inf_type]

                        #print(struct)
                        index =0
                        for i in struct["items"].items():
                            #print(i,1

                            if(i[0]==expr2):
                                #print(i
                                #test case a.a etc maybe fix?
                                if flag==100:
                                    return 0
                                #we are at the end
                                self.any_args["index"]+=i[1]["size"]
                                self.any_args[i[0]]=i[1]
                                self.any_args["orginal"]=expr1
                                return expr2
                            index+=i[1]["size"]
                else:
                    #very last code to run
                    if flag==100:
                        self.segments["section .text"]["main"].append(f"mov al, [{self.any_args["orginal"]}+{self.any_args["index"]}]")
                        return "al"
                    #other code that runs after in between the fitst ie a.b and .c the above would be d etc
                    if expr1 in self.any_args:
                        var = self.any_args[expr1]
                        typ = var["type"]
                        #if type isnt below it wouldnt make sense we because any other type doesnt have .dot notation for now
                        if typ=="struct":
                            inf_type =var["inf_type"]
                            struct = self.env["structs"][inf_type]
                            index = 0
                            for i in struct["items"].items():
                                # print(i,1

                                if (i[0] == expr2):
                                    # print(i

                                    # we are at the end
                                    self.any_args["index"] += i[1]["size"]
                                    self.any_args[i[0]] = i[1]
                                    return expr2
                                index += i[1]["size"]

                    return

                return self.any_args["index"]

        #returns the address ie &x
        if node[0]=="addr":
            if flag == 100:

                if node[1] in self.env:

                    return f"{node[1]}"
            pass

        #returns the deref the ptr ie the value at ptr
        if node[0]=="deref":
            #var_assign
            if flag==1001:

                if node[1] in self.env:
                    if "main" not in self.any_args:
                        self.any_args["main"] = []
                    self.any_args["main"].append(f"mov al, {self.env[node[1]]["type"]} [{node[1]}]")
                    return ("deref", f"al")
                else:
                    raise Exception(f"Undefined variable {node[1]}")
                return
            if flag == 100:

                if node[1] in self.env:

                    return f"[{node[1]}]"
                    pass

            return


        #assigns struct
        if node[0]=="assign_struct":

            #add in flag == 0 etc
            if flag==1:
                #not implemented
                return
            #if the sturct is in structs
            if node[2] in self.env["structs"]:
                struct = self.env["structs"][node[2]]
                name = node[1]
                if hasattr(self, "any_args") and "index" in self.any_args:
                    # Now it is safe to use self.any_args["index"]
                    #have to do this to avoid losing the index later on
                    index = self.any_args["index"]
                else:
                    self.any_args ={}
                #print(self.any_args)
                counter =0
                #creates the tuple of tuples node[0]=="tuple"
                self.walkTree(node[3],1000)

                tup  = self.any_args["tuple"]
                #print(len(struct["items"]))
                values = {}

                #add in memory
                if node[1] not in self.env:
                    self.segments["section .bss"].append(f"{node[1]} resb {struct["collective_size"]}")
                    self.env[node[1]] = {}
                if flag == 700:
                    #worked had to be scrapped for the above ver
                    pass
                    #index = self.any_args["index"]

                else:
                    index = 0

                    #loop through all the items
                for i,key in enumerate(struct["items"]):

                    type_item = struct["items"][key]["type"]

                    if type_item=="struct":
                        #run through all this sctructs items
                        #print(stru)
                        inf_type = struct["items"][key]["inf_type"]
                        self.any_args ={"index":index}
                        self.walkTree(("assign_struct",node[1],inf_type,node[3][1][i]),700)
                        index+=struct["items"][key]["size"]


                        continue

                    #if the item ie 100+1 is computed for now mov al,100 add al,1 it adds 2 lines of code
                    #the below line checks and adds in the diff ie 4 and 2 adds 2 lines of code
                    if self.any_args["counter"]!= counter:
                        #main holds the code
                        if "main" in self.any_args:

                            for j in self.any_args["main"][counter:self.any_args["counter"][i]]:

                                self.segments["section .text"]["main"].append(f"{j}")
                            counter = self.any_args["counter"][i]

                    self.segments["section .text"]["main"].append(f"mov {Builtins.map_types_init[type_item]} [{node[1]}+{index}], {tup[i]}")
                    index += struct["items"][key]["size"]
                self.env[node[1]] = {"name":node[1],"type":"struct","inf_type":node[2]}
                return
            raise ValueError("STRUCT not defined")


        if node[0]=="init_struct":
            #not implemented
            return

        if node[0]=="struct_item":


            if node[2] in self.env["structs"]:

                return {"name":node[1],"type":"struct","inf_type":node[2], "size": self.env["structs"][node[2]]["collective_size"]}
            return {"name": node[1],"type": node[2],"size":Builtins.map_type_sizes[node[2]]}

        if node[0]=="def_struct":
            if "structs" not in self.env:
                self.env["structs"] = {}
            collective_size = 0
            items={}
            for i in node[2]:
                item = self.walkTree(i)
                print(item)
                items[item["name"]]={"type":item["type"], "size":item["size"], "inf_type": item["inf_type"] if 'inf_type' in item else ""}
                collective_size += item["size"]
            self.env["structs"][node[1]] = {"items":items,"collective_size":collective_size}
            #print(self.env["structs"])

            #easy uses the for loops witha  twist
        if node[0]=="while_loop":
            self.any_args = {}
            expr = self.walkTree(node[1],2)
            #no flag ==1 yet
            if flag==0:
                self.segments["section .text"]["main"].append(f"while_loop_{self.general['while_loop_counter']}:")
                if "main" in self.any_args:
                    for i in self.any_args["main"]:
                        self.segments["section .text"]["main"].append(i)
                self.segments["section .text"]["main"].append(f"cmp bl, 1")
                self.segments["section .text"]["main"].append(f"jne while_loop_exit_{self.general['while_loop_counter']}")

                for i in node[2]:
                    self.segments["section .text"]["main"].append(self.walkTree(i,2))
                self.segments["section .text"]["main"].append(f"jmp while_loop_{self.general['while_loop_counter']}\n")
                self.segments["section .text"]["main"].append( f"while_loop_exit_{self.general['while_loop_counter']}:")
                self.general["while_loop_counter"] += 1


        #uses self.any args for any added code
        if node[0] == 'if_stmt':
            self.any_args = {}
            result = self.walkTree(node[1])

            #any args has one exstra
            code = self.any_args["main"]
            #for i in code:
             #   print(i)

            code.append("cmp bl,1\n")
            code.append(f"je if_{self.general['counter']}\n")
            code.append(f"jmp else_{self.general['counter']}\n")
            code.append(f"if_{self.general['counter']}:\n")
            for i in node[2][1]:
                code.append(f"{self.walkTree(i,2)}\n")
            code.append(f"jmp no_else_{self.general['counter']}\n")
            code.append(f"else_{self.general['counter']}:\n")
            for i in node[2][2]:
                code.append(f"{self.walkTree(i,2)}\n")
            code.append(f"no_else_{self.general['counter']}:\n")
            if flag == 0:
                for i in code:
                    self.segments["section .text"]["main"].append(f"""{i}""")
            elif flag==1:
                #have to update counter or funcs doesnt work correclty
                self.general["counter"] += 1
                return "\t".join(code)

                return ""

            self.general["counter"] += 1


            if result:
                print(self.walkTree(node[2][1]))
                return self.walkTree(node[2][1])
            return self.walkTree(node[2][2])


        if node[0]=="and":
            #infinite ands and ors
            if "main" not in self.any_args:
                self.any_args["main"] = []

            # Append node[1] and node[2] processed with flag 200
            node_1 = self.walkTree(node[1],200)
            if node_1:
                self.any_args["main"].append(node_1)

            self.any_args["main"].append(self.walkTree(node[2], 200))

        if node[0]=="or":
            if "main" not in self.any_args:
                self.any_args["main"] = []

                # Append node[1] and node[2] processed with flag 200
            node_1 = self.walkTree(node[1], 201)
            if node_1:
                self.any_args["main"].append(node_1)

            self.any_args["main"].append(self.walkTree(node[2], 201))

        if node[0] == 'condition_eqeq':

            mov_code = f"mov al, {self.walkTree(node[1], 100)}\n" \
                       f"\tcmp al, {self.walkTree(node[2], 100)}\n" \
                       f"\tsete al\n"

            if flag == 200 and self.any_args["main"]:
                mov_code += "\tand bl, al\n"
            elif flag==201 and self.any_args["main"]:
                mov_code += "\tor bl, al\n"
            else:
                #if self.any not in it its the first in the sequence ie 7==7 and 7==8 7==7 is first
                mov_code += "\tmov bl, al\n"

            #this is for if its only 1 == and not part of and or or
            if "main" not in self.any_args:
                self.any_args["main"] = [mov_code]

                return

            return mov_code

        if node[0]=="expr_GEQEQ":
            mov_code=f"mov al, {self.walkTree(node[1], 100)}\n" \
                       f"\tcmp al, {self.walkTree(node[2], 100)}\n" \
                       f"\tsetge al\n"

            if flag == 200 and self.any_args["main"]:
                mov_code += "\tand bl, al\n"
            elif flag==201 and self.any_args["main"]:
                mov_code += "\tor bl, al\n"
            else:
                mov_code += "\tmov bl, al\n"


            if "main" not in self.any_args:
                self.any_args["main"] = [mov_code]
                return
            return mov_code

        if node[0] == "expr_LEQEQ":
            mov_code = f"mov al, {self.walkTree(node[1], 100)}\n" \
                           f"\tcmp al, {self.walkTree(node[2], 100)}\n" \
                           f"\tsetle al\n"

            if flag == 200 and self.any_args["main"]:
                mov_code += "\tand bl, al\n"
            elif flag==201 and self.any_args["main"]:
                mov_code += "\tor bl, al\n"
            else:
               mov_code += "\tmov bl, al\n"


            if "main" not in self.any_args:
                self.any_args["main"] = [mov_code]
                return
            return  mov_code


        if node[0] == "bigger_than":
            mov_code = f"mov al, {self.walkTree(node[1], 100)}\n" \
                       f"\tcmp al, {self.walkTree(node[2], 100)}\n" \
                       f"\tsetg al\n"

            if flag == 200 and self.any_args["main"]:
                mov_code += "\tand bl, al\n"
            elif flag==201 and self.any_args["main"]:
                mov_code += "\tor bl, al\n"
            else:
                mov_code += "\tmov bl, al\n"

            if "main" not in self.any_args:
                self.any_args["main"] = [mov_code]
                return
            return mov_code

        if node[0] == "less_than":
            mov_code = f"mov al, {self.walkTree(node[1], 100)}\n" \
                       f"\tcmp al, {self.walkTree(node[2], 100)}\n" \
                       f"\tsetl al\n"

            if flag == 200 and self.any_args["main"]:
                mov_code += "\tand bl, al\n"
            elif flag==201 and self.any_args["main"]:
                mov_code += "\tor bl, al\n"
            else:
                mov_code += "\tmov bl, al\n"


            if "main" not in self.any_args:
                self.any_args["main"] = [mov_code]
                return
            return mov_code




            #return self.walkTree(node[1]) == self.walkTree(node[2])

        if node[0] == 'fun_def':

            self.env[node[1]] = node[2]
            #easy just sets the func base and 0 means it wont be added no time wsted compiling a func if not used
            self.segments["section .text"][node[1]+":"] = {"code":[node[2]],"state":0}
            return


        #inline
        if node[0]=="fun_call_mod":
            try:
                # add in
                if flag == 1:
                    return
                # checks the state of the function if it hasnt been called no need to add into the comp version
                if self.segments["section .text"][node[1] + ":"]["state"] == 0 or True:
                    self.segments["section .text"][node[1] + ":"]["state"] = 0

                    code = "push ebp\n\tmov  ebp, esp\n"

                    # prologue
                    func_list = []
                    func_list.append(code)
                    self.any_args = {"type": "function", "name": node[1]}

                    # print(self.segments["section .text"][node[1]+":"]["code"]) this is its own list the {,,}

                    for i, v in enumerate(self.segments["section .text"][node[1] + ":"]["code"][0]):
                        # self.segments["section .text"][node[1] + ":"]["code"][i] = self.walkTree(v,1) if self.walkTree(v,1) else ""
                        res = self.walkTree(v, 1)

                        if res != None:
                            func_list.append(res)

                    code = "mov esp, ebp\n\tpop ebp\n"
                    func_list.append(code)
                    #self.segments["section .text"][node[1] + ":"]["code"] = func_list
                    for i in func_list:
                        self.segments["section .text"]["main"].append(i)
                    #self.segments["section .text"]["main"].append(f"call {node[1]}")

                    return
                #func_list = self.segments["section .text"][node[1] + ":"]["code"]
                #for i in func_list:
                 #   self.segments["section .text"]["main"].append(i)

                return self.walkTree(self.env[node[1]])
            except LookupError:
                print("Undefined function '%s'" % node[1])
                return 0

        if node[0] == 'fun_call':
            try:
                #add in
                if flag==1:
                    return
                #checks the state of the function if it hasnt been called no need to add into the comp version
                if self.segments["section .text"][node[1]+":"]["state"] == 0:
                    self.segments["section .text"][node[1]+":"]["state"] = 1
                    code = "push ebp\n\tmov  ebp, esp\n"

                    #prologue
                    func_list = []
                    func_list.append(code)
                    self.any_args = {"type":"function", "name":node[1]}

                    #print(self.segments["section .text"][node[1]+":"]["code"]) this is its own list the {,,}

                    for i,v in enumerate(self.segments["section .text"][node[1] + ":"]["code"][0]):
                        #self.segments["section .text"][node[1] + ":"]["code"][i] = self.walkTree(v,1) if self.walkTree(v,1) else ""
                        res = self.walkTree(v,1)
                        if res!= None:
                            func_list.append(res)


                    code = "mov esp, ebp\n\tpop ebp\n"
                    func_list.append(code)
                    self.segments["section .text"][node[1] + ":"]["code"] = func_list

                    self.segments["section .text"]["main"].append(f"call {node[1]}")

                    return
                self.segments["section .text"]["main"].append(f"call {node[1]}")
                return self.walkTree(self.env[node[1]])
            except LookupError:
                print("Undefined function '%s'" % node[1])
                return 0



        if node[0] == 'add' or node[0]=="sub":
            #have to add in squishing
            if flag == 101:
                if node[0]=="add":

                    if node[1][0] not in ["add","sub","mul","div","num"]:
                        return ("Error")
                    return self.walkTree(node[1],101)+ self.walkTree(node[2],101)
                else:
                    return self.walkTree(node[1], 101) - self.walkTree(node[2], 101)
            if flag == 100 or flag==1001 :

                # Inside the 'except' block of an 'add' node:
                # Walk the first operand to get var or immediate

                first = self.walkTree(node[1], 100)  # returns [x] or immediate

                # Prepend the initial mov al instruction in place
                if "main" not in self.any_args:

                    self.any_args.setdefault("main", []).insert(0, f"mov al, {first}")

                else:
                    if "reset" in self.any_args and self.any_args["reset"]==0:
                        self.any_args["main"].append(f"mov al, {first}")
                        self.any_args["reset"]=1
                    else:
                        pass#self.any_args["main"].append(f"{node[0]} al, {first}")


                # Walk the second operand and append add instruction
                second = self.walkTree(node[2],100)

                self.any_args["main"].append(f"{node[0]} al, {second}")


                # At the end, store the result in the target variable
                #target_var = node[0]  # assuming node[0] is the assignment target
                #self.any_args["main"].append(f"mov [{target_var}], al")

                return "al"
            return
            if node[1][0] == "var" or node[2][0]=='var':
                if node[1][0] == "var" and node[2][0] == 'var':
                    Var_Classes.Generate_Type_Update.Both_Var(node, self,node[0])
                    return self.walkTree(node[1]) + self.walkTree(node[2])
                #add in if both are vars
                if node[1][0] == 'var':
                    Var_Classes.Generate_Type_Update.Left_Var(node,self,node[0])
                    return  self.walkTree(node[1]) + self.walkTree(node[2])
                if node[2][0]=="var":
                    Var_Classes.Generate_Type_Update.Right_Var(node, self,node[0])
                    return self.walkTree(node[1]) + self.walkTree(node[2])




            #return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            if flag == 101:
                if node[0] == "mul":

                    if node[1][0] not in ["add", "sub", "mul", "div", "num"]:
                        return ("Error")
                    return self.walkTree(node[1], 101) * self.walkTree(node[2], 101)

            if flag==0:
                pass
            if flag ==100:

                first = self.walkTree(node[1], 100)  # returns [x] or immediate

                # Prepend the initial mov al instruction in place
                if "main" not in self.any_args:
                    self.any_args.setdefault("main", []).insert(0, f"mov al, {first}")

                # Walk the second operand and append add instruction
                second = self.walkTree(node[2], 100)
                self.any_args["main"].append(f";mov cl,al\n mov al, {first}\n")
                self.any_args["main"].append(f"mov bl, {second}\ni{node[0]} bl")
                self.any_args["main"].append(f"mov bl,al\n")
                #self.any_args["main"].append(f"mov al,cl\n")
                #return where the ans is svaed
                return "bl"
            return #self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            if flag == 101:
                if node[0] == "div":

                    if node[1][0] not in ["add", "sub", "mul", "div", "num"]:
                        return ("Error")
                    return self.walkTree(node[1], 101) / self.walkTree(node[2], 101)

            if flag==0:
                pass
            if flag ==100:
                first = self.walkTree(node[1], 100)  # returns [x] or immediate

                # Prepend the initial mov al instruction in place
                if "main" not in self.any_args:
                    self.any_args.setdefault("main", []).insert(0, f"mov al, {first}")

                # Walk the second operand and append add instruction
                second = self.walkTree(node[2], 100)

                self.any_args["main"].append(f";mov cl,al\n mov al, {first}\n")
                self.any_args["main"].append(f"mov ah,0\nmov bl, {second}\ni{node[0]} bl")
                self.any_args["main"].append(f"mov bl,al\n")
                #self.any_args["main"].append(f"mov al,cl\n")
                # return where the ans is svaed
                return "bl"
            #return self.walkTree(node[1]) / self.walkTree(node[2])


        if node[0]=="var_assign_type":
            if flag==0:
                if node[1] in self.env:
                    raise ValueError(f"Cannot reassign type of variable {node[1]} has been already defined")
                var_type = node[2]
                if var_type in Builtins.map_types_bss:
                    if var_type=="str":
                        return
                    self.segments["section .bss"].append(f"{node[1]} {Builtins.map_types_bss[var_type]} 1")
                    self.segments["section .text"]["main"].append(f"mov {Builtins.map_types_init[var_type]} [{node[1]}], {self.walkTree(node[3])}")
                    self.env[node[1]] = {"name":node[1], "type":var_type, "inf_type":Builtins.map_types_init[var_type], "Static":1}

        if node[0] == 'var_assign':

            if flag == 0:
                if node[1] not in self.env:

                    if node[2][0]=="array":
                        self.any_args={}
                        #we say type is num for now or byte
                        arr = node[2][1]
                        type_arr=arr[0][0]

                        # for i in arr:
                        #     print(self.walkTree(i,100),10)


                        if type_arr=="str":
                            #find the longest one in the arra
                            res = self.walkTree(node[2])

                            len_arr = res[0]
                            max_item_len = len(max(res[1],key=len))-3
                            init_strings = [f"resb {max_item_len}" for i in range(len_arr)]

                            self.segments["section .bss"].append(f"{node[1]}:  {"\n".join(init_strings)}")
                            self.segments["section .bss"].append(f"arr_{node[1]}: resd {len_arr}")

                            for i, v in enumerate(res[1]):
                                self.segments["section .text"]["main"].append(Generate.str_reassign_i(node[1],v,i*max_item_len))
                                self.segments["section .text"]["main"].append(f"mov dword [arr_{node[1]}+{i*4}],  {node[1]}+{i*max_item_len}")

                            self.env[node[1]] = {"name": node[1], "type": "array_string", "inf_type": "byte"}

                            return
                        self.walkTree(node[2], 100)
                        res = self.any_args["list"]
                        if "main" in self.any_args:
                            added_code = self.any_args["main"]
                        else:
                            added_code = []
                        counter = self.any_args["counter"]
                        current_count=0
                        self.segments["section .bss"].append(f"{node[1]}: resb {len(res)}")

                        for i,v in enumerate(res):
                            if current_count!=counter[i]:
                                for j in added_code[current_count:counter[i]]:
                                    self.segments["section .text"]["main"].append(f"{j}")
                                current_count = counter[i]
                            if v!="al":

                                self.segments["section .text"]["main"].append(f" mov al, {v}")
                            self.segments["section .text"]["main"].append(f"mov byte [{node[1]}+{1*i}], al")

                        self.env[node[1]] = {"name": node[1],"type":"array","inf_type":"byte"}
                        return

                    #self.segments["section .data"][node[1]] = {"type":"db", "data":self.walkTree(node[2])}
                    #find a better way to get the type;
                    #print(self.walkTree(node[2],101))
                    self.env[node[1]] = {"name": node[1], "type": node[2][0], "inf_type": "byte", "len":0}

                    if self.env[node[1]]["type"] == "str":
                        string = self.walkTree(node[2])
                        len_str = len(string) - 3  # minus 3 "" and ,

                        self.segments["section .bss"].append(f"{node[1]}: resb {len_str}")
                        str_code = Generate.str_reassign(node[1], string)

                        self.segments["section .text"]["main"].append(str_code)
                        self.env[node[1]]["len"] = len_str
                        return

                    self.any_args={}
                    res=self.walkTree(node[2],101)
                    #check the size and fix the type byte long etc.


                    if isinstance(res,tuple) and res[0]=="Error":
                        pass
                    else:
                        self.env[node[1]]["type"] = Builtins.get_smallest_type(res)
                        self.env[node[1]]["value"] = res

                    if self.env[node[1]]["type"] == "num" or True:

                        self.segments["section .bss"].append(f"{node[1]}: resb {Builtins.map_type_sizes[self.env[node[1]]["type"]]}")
                        self.segments["section .text"]["main"].append(f"mov {Builtins.map_types_init[self.env[node[1]]["type"]]} [{node[1]}], {self.env[node[1]]["value"]}")

                        return
                        self.segments["section .text"]["main"].append(f"mov byte [{node[1]}], {self.walkTree(node[2])}")
                    return

                    #handles strings


                #this is for var_assign after its already been declared

                #if "Static" in self.env[node[1]]:
                 #   if self.env[node[1]]["type"]!=node[2][0]:

                if node[2][0]=="array":
                    self.any_args={}
                    self.walkTree(node[2],100)
                    res=self.any_args["list"]

                    return
                  #      raise ValueError(f"Cannot reassign static variable {node[1]} has been already defined")
                if node[2][0]=="str":
                    string = self.walkTree(node[2])
                    len_str = len(string)-3
                    orginal_len = self.env[node[1]]["len"]

                    if len_str<=orginal_len:
                        str_code = Generate.str_reassign(node[1],string)
                        self.segments["section .text"]["main"].append(str_code)

                        return
                    raise MemoryError(f"String {node[1]} is too long orginal len {orginal_len} now len {len_str}")
                    return

                #the below is for ints etc where we repeatedly do add etc and then mov [],al etc
                self.any_args = {} #needs to be set
                #self.any_args["vars"] = []
                #self.any_args["constants"] = 0
                out = self.walkTree(node[2],100)

                if "main" not in self.any_args:
                    #if its a single expr like y=5 not y=5+1+- etc......

                    self.segments["section .text"]["main"].append(f"mov byte [{node[1]}], {out}")
                    return

                target_var = node[1]  # assuming node[0] is the assignment target
                self.any_args["main"].append(f"mov byte [{target_var}], al")
                output = self.any_args["main"]

                for i in output:
                    self.segments["section .text"]["main"].append(i)
                #self.env[node[1]] = self.walkTree(node[2])

                return node[1]

            if flag == 2:

                #inside a if statement
                if node[1] not in self.env:
                    self.env[node[1]] = {"name": node[1], "type": node[2][0], "inf_type": "byte"}
                    if self.env[node[1]]["type"] == "num":
                        self.segments["section .bss"].append(f"{node[1]}: resb 1")
                        return f"mov byte [{node[1]}], {self.walkTree(node[2])}"

                    if self.env[node[1]]["type"] == "str":
                        string = self.walkTree(node[2])
                        len_str = len(string) - 3  # minus 3 "" and
                        self.env[node[1]] = {"name": node[1], "type": node[2][0], "inf_type": "byte", "len": len_str}
                        self.segments["section .bss"].append(f"{node[1]}: resb {len_str}")



                        str_code = Generate.str_reassign(node[1], string)



                        return str_code

                if node[2][0]=="str":
                    string = self.walkTree(node[2])
                    len_str = len(string)-3
                    orginal_len = self.env[node[1]]["len"]

                    if len_str<=orginal_len:
                        str_code = Generate.str_reassign(node[1],string)
                        return str_code
                        return
                    raise MemoryError(f"String {node[1]} is too long orginal len {orginal_len} now len {len_str}")
                    return

                #int or number
                self.any_args = {}

                out = self.walkTree(node[2], 100)
                code = ""
                if "main" not in self.any_args:

                    # if its a single expr like y=5 not y=5+1+- etc......
                    code+=f"mov byte [{node[1]}], {self.walkTree(node[2])}\n"
                    return code

                target_var = node[1]  # assuming node[0] is the assignment target
                self.any_args["main"].append(f"mov byte [{target_var}], al\n")
                output = self.any_args["main"]
                for i in output:
                    code += i+"\n"

                return code
                return


            if self.any_args["type"]=="function":
                if self.any_args["name"]+"_"+node[1] not in self.env:
                    self.segments["section .data"][self.any_args["name"]+"_"+node[1]] = {"type":"db", "data":self.walkTree(node[2])}
                    self.env[self.any_args["name"]+"_"+node[1]] = self.walkTree(node[2])

                    self.env[self.any_args["name"]+"_"+node[1]] = {"name": self.any_args["name"]+"_"+node[1], "type": node[2][0], "inf_type": "byte"}
                    return

                #we are in a function we return the code to be appended between the prologue en epi
                return f"mov byte [{self.any_args["name"]+"_"+node[1]}], {self.walkTree(node[2])}"
                self.segments["section .text"][self.any_args["name"]+":"]["code"].append(f"mov byte [{self.any_args["name"]+"_"+node[1]}], {self.walkTree(node[2])}")
                self.env[self.any_args["name"]+"_"+node[1]] = self.walkTree(node[2])
                #self.segments["section .data"][self.any_args["name"]+"_"+node[1]] = {"type": "db", "data": self.walkTree(node[2])}
                return ""
            self.env[node[1]] = self.walkTree(node[2])
            return ""


            return node[1]

        if node[0] == 'var':
            try:

                if flag ==0:

                    return node[1]
                if flag == 1001:
                    return node[1]
                if flag == 100:

                    return f"[{node[1]}]"
                if flag == 101:
                    if node[1] in self.env:
                        if self.env[node[1]]["type"] == "num":

                            return self.env[node[1]]["value"]
                return self.walkTree(self.env[node[1]])
                self.segments["section .text"]["main"].append(f"""
                push {node[1]}
                push 1
                push 100
                push 100
                call put_str
                add esp,16
                """)
                return self.env[node[1]]
            except LookupError:
                raise MemoryError(f"Undefined variable {node[1]} found")
                print("Undefined variable '"+node[1]+"' found!")
                return 0

        if node[0] == 'for_loop':
            if flag == 0:
                if node[1][0]=="var_assign":
                    var_name = node[1][1]
                    if var_name not in self.env:
                        self.env[var_name] = {"name": var_name,"type":"num","inf_type": "byte"}
                        self.segments["section .bss"].append(f"{var_name}: resb 1")

                    #self.segments["section .text"]["main"].append(f"mov al, {node[1][2][1]}")
                    self.segments["section .text"]["main"].append(f"mov al, byte [{var_name}]")
                    self.segments["section .text"]["main"].append(f"for_loop{self.general["for_loop_counter"]}:")
                    self.segments["section .text"]["main"].append(f"\tcmp al, {self.walkTree(node[2])}")
                    self.segments["section .text"]["main"].append(f"\tjg end_for{self.general["for_loop_counter"]}")

                    for i in node[3]:
                        self.segments["section .text"]["main"].append("\t"+self.walkTree(i,2))


                    self.segments["section .text"]["main"].append(f"\tadd al,1")
                    self.segments["section .text"]["main"].append(f"\tmov byte [{var_name}],al")
                    self.segments["section .text"]["main"].append(f"\tjmp for_loop{self.general["for_loop_counter"]}")
                    self.segments["section .text"]["main"].append(f"end_for{self.general["for_loop_counter"]}:")
                    self.general["for_loop_counter"] += 1
                    return
            pass


        if node[0] == 'for_loop_setup':
            return (self.walkTree(node[1]), self.walkTree(node[2]))

        if node[0]=="SET_GLOBAL":
            if node[1].lower() == "stack":
                self.segments["section .bss"].append(f"""{node[1]}:    resb {self.walkTree(node[2])}""")
                self.segments["section .text"]["_start"].append(f"\tmov esp, {node[1]} + {self.walkTree(node[2])}\n")
                return
            if node[1].lower()==".REG_POOL":
                pass #.REG_POOL 2048 4 registers 512 bits 32 bytes
            if node[1].lower() == "heap":
                self.segments["pre-section"].append(f"""%define HEADER_STATUS_OFFSET 0       ; VAR_BYTE Status (0=FREE, 1=USED)
%define HEADER_SIZE_OFFSET   1       ; VAR_DWORD Size (Usable size)
%define HEADER_NEXT_OFFSET   5       ; PTR_DWORD Next Pointer
%define HEADER_TOTAL_SIZE    9        ; Total header size""")
                self.segments["section .bss"].append(f"""{node[1]}:    resb {self.walkTree(node[2])}""")
                self.segments["section .bss"].append(f"""{node[1]}_head:    resd 1""")
                self.segments["section .bss"].append(f"""{node[1]}_ret_ptr:    resd 1""")
                return
            if node[1].lower() == "grub":
                self.segments["pre-section"].append(f"""align 4
multiboot_header:
    dd 0x1BADB002            ; magic number
    dd 0x0                   ; flags (can set bits later)
    dd -(0x1BADB002 + 0x0)   ; checksum""")


        if node[0]=="nasm_block":

            if flag == 0:
                if node[1]=="nasm":

                    self.segments["section .text"]["main"].append(node[2][1:-1])
                    return
                if node[1]=="bss":
                    self.segments["section .bss"].append(node[2][1:-1])
                if node[1]=="data":
                    #self.segments["section .data"].append(node[2][1:-1])
                    pass

            if node[1]=="nasm":

                if self.any_args["type"]=="function":
                    return node[2][1:-1]

        if node[0]=="array":
            code = []

            if "list" not in self.any_args:
                self.any_args = {"list":[],"counter":[]}
            if flag == 100:

                for i in node[1]:

                    if i[0]=="array":
                        res = self.walkTree(i,100)
                        if res is not None:
                            self.any_args["list"].append(res)
                            self.any_args["counter"].append(len(self.any_args["main"]))

                        continue

                    self.any_args["list"].append(self.walkTree(i,100))
                    ###########jfjwajf
                    if "main" in self.any_args:
                        self.any_args["counter"].append(len(self.any_args["main"]))
                    else:
                        self.any_args["counter"].append(0)
                return

            #first time array is init
            #make space in the bss return 2 codes (,) to var_assign

            part1=0
            for i in node[1]:
                part1+=1
                if code==[]:
                    code.append(self.walkTree(i))
                    continue
                code.append(self.walkTree(i))
            return (part1, code)


        if node[0]=="fun_def_args":
            self.any_args={}
            tup = self.walkTree(node[2],1000) #[a,b] etc
            self.env[node[1]] = node[3]
            self.segments["section .text"][node[1] + ":"] = {"code": [node[3]], "args":tup,"state": 0}


        if node[0]=="fun_call_args":
            try:
                if node[1]=="delay":
                    if flag == 0:
                        self.any_args = {"flag":100} #seems redunded it isnt
                        self.segments["section .text"][node[1] + ":"] = {"code": [Builtins.code[node[1]]], "state": 1}
                        tup = self.walkTree(node[2], 100)
                        for i in tup:
                            self.segments["section .text"]["main"].append(f"mov eax, {i}")
                            self.segments["section .text"]["main"].append(f"push eax")
                        self.segments["section .text"]["main"].append(f"call {node[1]}\n")
                        return
                    if flag==2:
                        return
                if node[1]=="color_screen":
                    if flag==0:

                        self.any_args={}
                        self.segments["section .text"][node[1]+":"] = {"code":[Builtins.code[node[1]]],"state":1}
                        tup=self.walkTree(node[2],1000)


                        for i in tup:
                            self.segments["section .text"]["main"].append(f"mov eax, {i}")
                            self.segments["section .text"]["main"].append(f"push eax")

                        self.segments["section .text"]["main"].append(f"call {node[1]}\n")
                    if flag ==2:
                        self.segments["section .text"][node[1] + ":"] = {"code": [Builtins.code[node[1]]], "state": 1}
                        tup = self.walkTree(node[2], 1000)
                        code = ""
                        for i in tup:
                            code+= f"push {i}\n"
                        code += f"call {node[1]}\n"
                        return code
                    return

                if self.segments["section .text"][node[1] + ":"]["state"] == 0:

                    self.segments["section .text"][node[1] + ":"]["state"] = 1
                    self.temp_env = deepcopy(self.env)
                    self.env = {}
                    self.any_args ={}
                    #the tuple args
                    args = self.walkTree(node[2])

                    origin_counter = len(args)

                    #org_str = f"[esp+{(i + 2) * 4}]"
                    #v is the arg passed and i is the arg for the function ie a(1,2) v is 1 and a(a,b) a is i
                    for i,v  in zip(self.segments["section .text"][node[1] + ":"]["args"],args):
                        origin_counter -= 1


                        if v in self.temp_env:

                            self.env[i] = self.temp_env[v]
                            self.env[i]["origin"] = (origin_counter + 2) * 4

                        else:
                            ##add in some checks
                            #print(i,v)
                            #later add in a flag to help
                            if isinstance(v,int):
                                self.env[i]={"name": i, "type": "num", "inf_type": Builtins.get_smallest_type(v),"value":v}

                            if isinstance(v,str):
                                self.env[i]= {"name": i, "type": "str", "inf_type": "byte", "len":len(v)-3}
                            if isinstance(v,list):
                                pass#self.env[i]={}




                    code = "push ebp\n\tmov  ebp, esp\n"

                # prologue
                    func_list = []
                    func_list.append(code)
                    self.any_args = {"type": "function", "name": node[1]}
                    """args_passed = self.walkTree(node[2])
                    try:
                        for i,v in zip(self.segments["section .text"][node[1] + ":"]["args"], args_passed):

                            if i in self.temp_env:

                                self.env[i] = self.temp_env[v]
                                print(self.env[i])
                                continue
                            self.env[i]= {"type": f"{Builtins.get_smallest_type(v)}", "inf_type":f"{Builtins.get_smallest_type(v)}", "value": v}
                    except:
                        pass"""

                    for i, v in enumerate(self.segments["section .text"][node[1] + ":"]["code"][0]):
                    # self.segments["section .text"][node[1] + ":"]["code"][i] = self.walkTree(v,1) if self.walkTree(v,1) else ""

                        res = self.walkTree(v, 1)
                        if res != None:
                            for i, v in enumerate(self.segments["section .text"][node[1] + ":"]["args"][::-1]):


                                #replacement_addr = f"[ebp+{(i + 2) * 4}]"
                                #print(i,v)
                                #pattern_standalone = rf'(?<!\[)\b{re.escape(v)}\b(?!\])'
                                #res = re.sub(pattern_standalone, replacement_addr, res)

                                # --- Step 2: Replace Bracketed Variable (e.g., '[a]' -> '[ebp+8]') ---
                                # Pattern: Matches the literal string '[v]'
                                # This handles the case where the variable was already meant to be an address.
                                #pattern_bracketed = rf'\[{re.escape(v)}\]'
                                #res = re.sub(pattern_bracketed, replacement_addr, res)

                                pattern = rf'\b{re.escape(v)}\b'

                                res = re.sub(pattern, f'[esp+{(i + 2) * 4}]', res)
                                fixed_pattern = r'(\b(mov|add|sub|cmp)\s+[a-z]+,\s*)\[\s*\[\s*((ebp|esp)\+\d+)\s*\]\s*\]'
                                print(res)
                                # Assuming 'self' is the compiler instance containing the method

                                #res = re.sub(fixed_pattern, Generate.rewrite_double_dereference, res)

                            func_list.append(res)

                    code = "mov esp, ebp\n\tpop ebp\n"

                    func_list.append(code)

                    self.segments["section .text"][node[1] + ":"]["code"] = func_list

                    args_passed = self.walkTree(node[2])




                    #i is the value ie 1 and v is the var ie a
                    for i,v  in zip(args_passed,self.segments["section .text"][node[1] + ":"]["args"]):
                        #here i can decide to pass the value or a ptr strinhs will be passed as ptrs
                        #fix lol add in a("hey")
                        #the below works for [c] strs addrs

                        if self.env[v]["type"] in ["str"]:
                            self.segments["section .text"]["main"].append(f"mov eax, {i}")
                            self.segments["section .text"]["main"].append(f"push eax")

                        else:
                            self.segments["section .text"]["main"].append(f"mov eax, {i}")
                            self.segments["section .text"]["main"].append(f"push eax")

                    self.segments["section .text"]["main"].append(f"call {node[1]}")
                    self.segments["section .text"]["main"].append(f"add esp, {len(args_passed)*4}")
                    env = self.temp_env

                    return

                self.segments["section .text"]["main"].append(f"call {node[1]}")

            except LookupError as e:
                print(e)
                pass
        if node[0]=="tuple":
            if flag == 100:

                tup = []

                for i in node[1]:
                    res = self.walkTree(i, 100)

                    res = self.walkTree(i, 100)

                    tup.append(res)
                return tup


            if "tuple" not in self.any_args:
                    self.any_args = {"tuple": [], "counter": []}
            #structs
            if flag == 1000 or flag==1001:

                tup=[]

                for i in node[1]:

                    res = self.walkTree(i, 1001)

                    if res is not None:
                        if isinstance(res, tuple):
                            typ = res[0] #ie deref
                            if typ=="deref":
                                loc = res[1]

                                self.any_args["tuple"].append(loc)


                        if res in self.env:

                            if "value" in self.env[res]:

                                self.any_args["tuple"].append(self.env[res]["value"])
                            else:
                                if "type" in self.env[res]:
                                    if self.env[res]["type"] == "str":
                                        self.any_args["tuple"].append(f"{res}")


                        else:
                            self.any_args["tuple"].append(res)
                        if "main" in self.any_args:
                            #this is needed for nested stuff to make sure that mov al gets done not just add.
                            #the first time is mive then al gets returned and moved to the dest
                            #after that "main" is in self.any_args so it does "add" al not mov "al"

                            self.any_args["reset"]=0
                            self.any_args["counter"].append(len(self.any_args["main"]))

                        else:
                            self.any_args["counter"].append(0)


                    tup.append(res)
                return tup

            tup = []

            #self.env = self.temp_env

            for i in node[1]:

                tup.append(self.walkTree(i))
            return tup



if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python basic.py <file>")
        sys.exit(1)

    filename = sys.argv[1]

    lexer = BasicLexer()
    parser = BasicParser()
    env = {}
    #.rodata
    segments={"pre-section":[],"section .bss":[""],"section .data":{},"section .text":{"_start":[],"main":[]}}
    any_args = {}
    # Read file content
    with open(filename, 'r') as f:
        content = f.read()

    # Split by semicolon and strip whitespace
    statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]

    # Execute each statement
    for stmt in statements:
        tree = parser.parse(lexer.tokenize(stmt))
        BasicExecute(tree, env,segments,any_args)

    print(segments)
    with open("output.asm", "w") as f:
        for i in segments["pre-section"]:
            f.write(i+"\n")
        f.write("section .bss\n")
        for i in segments["section .bss"]:
            f.write(f"\t{i}\n")


        f.write("section .data\n")
        data_section = segments.get('section .data', {})

        for var_name, var_info in data_section.items():
            var_type = var_info['type']
            var_data = var_info['data']

            f.write(f"{var_name} {var_type} {var_data}\n")


        f.write("section .text\n")
        f.write("global _start\n")
        f.write("_start:\n")

        for i in segments["section .text"]["_start"]:
            f.write(f"\n{i}\n")
        f.write("\tjmp main\n")
        text_section = segments.get('section .text', {})


        for var_name, var_info in text_section.items():
            if var_name=="main" or var_name=="_start":
                continue
            if var_info['state']==0:
                continue

            f.write(f"{var_name}\n")
            var_code = var_info['code']
            for i in var_code:
                f.write(f"\t{i}\n")
            f.write("\tret\n")

        f.write("main:\n")
        f.write("\tpush ebp\n\tmov  ebp, esp\n")
        for i in segments['section .text']['main']:
            f.write(f"\t{i}\n")
        f.write("\tmov esp,ebp\n\tpop ebp\n")
