import sys
script_name = sys.argv[0]
if len(sys.argv)>1:
    filename = sys.argv[1]
else:
    print("Missing Filename. Filename should be given.")
    sys.exit(1)
try:
    with open (filename,"r",encoding="utf-8") as p:
        source = p.read()
except FileNotFoundError:
    print(f"No Such Filename '{filename}' Exists.")
    sys.exit(1)

keywords = {
    "set":"SET",    "to":"TO",
    "show":"SHOW",      "plus":"PLUS",
    "minus":"MINUS",     "times":"TIMES",
    "divided":"DIVIDED",    "by":"BY",
    "(" : "LPAREN",     ")" : "RPAREN",
    "if": "IF",     "{" : "LBRACE",
    "}": "RBRACE",      "is":"IS",
    "greater":"GREATER",    "than":"THAN",
    "smaller":"SMALLER",    "otherwise":"OTHERWISE",
    "while":"WHILE",    "++":"INCREMENT",
    "--":"DECREMENT",   "repeat":"REPEAT",
    "time":"TIME",  "function":"FUNCTION",
    "call":"CALL" , "input":"INPUT","at":"AT",
    "most":"MOST", "least":"LEAST","not":"NOT"
}
valid_conditions = ["isgreaterthan","issmallerthan","is","isnot","isatmost","isatleast"]
class Token:
    def __init__(self,type,value,line,column):
        self.type = type 
        self.value = value
        self.line = line
        self.column = column



def tokenize(source):
    line = 1
    column = 1
    i = 0
    tokens = []
    single=""
    in_string = False
    stack =[]
    def add_token(single):
        if single=="":
            return
        else:
            if single[0].isalpha():
                if single in keywords:
                    tokens.append(Token(keywords[single],single,line,column))
                else:
                    tokens.append(Token("IDENTIFIER",single,line,column))
            elif single[0].isdigit():
                if '.' in single:
                    if single.count('.')==1:
                        single = float(single)
                    else:
                        raise Exception("Talk Error: Invalid Floating point Value.")
                else:
                    single=int(single)
                tokens.append(Token("NUMBER",single,line,column))
            elif single[0]=='"':
                tokens.append(Token("STRING",single[1:len(single)-1],line,column))
            elif single in ['(',')','{','}','++','--']:
                tokens.append(Token(keywords[single],single,line,column))
            else:
                raise Exception("Talk ERROR: Unknown Value")

    while i<len(source):
        if not in_string:
            if source[i].isspace():
                if source[i]=='\n':
                    line += 1
                    column = 1
                    add_token(single)
                else:
                    column+=1
                    add_token(single)
                single=""
                i+=1
            elif source[i] in ['(',')']:
                add_token(single)
                single = ""
                add_token(source[i])
                if source[i]=='(':
                    stack.append('(')
                else:
                    if stack and stack[-1]=='(':
                        stack.pop()
                    else:
                        raise Exception(f"Talk Error: misplaced Paenthesis at Line:{line} and Column:{column}")
                i+=1
                column +=1
            elif source[i] in ['{','}']:
                add_token(single)
                single = ""
                add_token(source[i])
                if source[i]=='{':
                    stack.append('{')
                else:
                    if stack and stack[-1]=='{':
                        stack.pop()
                    else:
                        raise Exception(f"Talk Error: misplaced Braces at Line:{line} and Column:{column}")
                i+=1
                column+=1
            elif source[i]=='+':
                if i+1<len(source) and source[i+1]=='+':
                    add_token(single)
                    single = ""
                    add_token("++")
                    i+=2
                    column+=2
                else: 
                    raise Exception(f"Talk Error at Line:{line} and Column:{column}: '+' is not supported right now. use 'plus'")
            elif source[i]=='-':
                if i+1<len(source) and source[i+1]=='-':
                    add_token(single)
                    single = ""
                    add_token("--")
                    i+=2
                    column+=2
                else: 
                    raise Exception(f"Talk Error at Line:{line} and Column:{column}: '-' is not supported right now. use 'minus'")
            elif source[i].isalpha() or source[i]=='_':
                if single:
                    if single[0].isdigit():
                        single += source[i]
                        raise Exception(f"Talk Error at Line:{line} and Column:{column}: '{single}' is not a valid numeric value. or Variable name")
                single += source[i]
                i+=1
                column += 1
                continue
            elif source[i]=='.':
                single += source[i]
                i+=1
                column += 1
            elif source[i].isdigit():
                single += source[i]
                i+=1
                column+=1
                continue
            elif source[i]=='"':
                beginning = (line,column)
                single+='"'
                in_string=True
                i+=1
                column += 1
            else:
                raise Exception(f"Talk Error: Unexpected Token Type {source[i]} at Line:{line} and Column:{column}")
        else:
            if source[i]=='"':
                in_string=False
                beginning = None
            elif source[i]=='\n':
                line += 1
                column = 0
            single+=source[i]
            i+=1
            column += 1
    if in_string:
        raise Exception(f"Talk Error: Unterminated String. String started from Line:{beginning[0]} and Column:{beginning[1]}")
    elif stack:
        if stack[-1]=='(':
            raise Exception("Talk Error: Some Parenthesis are not Closed.")
        else:
           raise Exception("Talk Error: Some Braces are not Closed.") 
    else:
        add_token(single)
    return tokens

class ShowNode:
    def __init__(self,value):
        self.value = value

class SetNode:
    def __init__(self,name,value):
        self.name = name
        self.value = value

class IfNode:
    def __init__(self,condition,body,else_body=None):
        self.condition = condition
        self.body = body 
        self.else_body = else_body

class WhileNode:
    def __init__(self,condition,body):
        self.condition = condition
        self.body = body 

class RepeatNode:
    def __init__(self,expression,body):
        self.expression = expression
        self.body = body

class FuncNode:
    def __init__(self,name,body,parameters):
        self.name = name
        self.body = body
        self.parameters = parameters

class CallNode:
    def __init__(self,name,values):
        self.name = name
        self.values = values

class InputNode:
    def __init__(self,name):
        self.name = name

class FuncNameNode:
    def __init__(self,value):
        self.name = value

class FuncParaNode:
    def __init__(self,value):
        self.name = value

class NumberNode:
    def __init__(self,value):
        self.value = value     

class StringNode:
    def __init__(self,value):
        self.value = value

class VariableNode:
    def __init__(self,name):
        self.name = name
class ParenNode:
    def __init__(self,value):
        self.value =value
class BraceNode:
    def __init__(self,value):
        self.value = value
class IncrementNode:
    def __init__(self,variable):
        self.variable = variable
class DecrementNode:
    def __init__(self,variable):
        self.variable = variable
class BinaryExpressionNode:
    def __init__(self,left,operator,right):
        self.left = left
        self.operator = operator
        self.right = right


class Parser:
    def __init__(self,tokens,position=0):
        self.tokens = tokens
        self.position = position

    def current_token(self):
        if self.position<len(self.tokens):
            return self.tokens[self.position]
        else:
            return None

    def previous_token(self):
        if self.position-1>=0:
            return self.tokens[self.position-1]
        else:
            return None
    
    def next_token(self):
        if self.position+1<len(self.tokens):
            return self.tokens[self.position+1]
        else:
            return None

    def advance(self):
        self.position+=1

    def parse_program(self):
        statements = []
        token = len(self.tokens)
        while(self.position<token):
            # print("Current Token: ",self.current_token().type, self.current_token().value)
            if self.current_token().type=="SHOW":
                node=self.parse_show()
                statements.append(node)
            elif self.current_token().type=="IF":
                node = self.parse_if()
                statements.append(node)
            elif self.current_token().type=="SET":
                node = self.parse_set()
                statements.append(node)
            elif self.current_token().type=="WHILE":
                node = self.parse_while()
                statements.append(node)
            elif self.current_token().type == "IDENTIFIER":
                node = self.parse_increments()
                statements.append(node)
            elif self.current_token().type == "REPEAT":
                node = self.parse_repeat()
                statements.append(node)
            elif self.current_token().type == "FUNCTION":
                node = self.parse_function()
                statements.append(node)
            elif self.current_token().type == "CALL":
                node = self.parse_call()
                statements.append(node)
            elif self.current_token().type == "INPUT":
                node = self.parse_input()
                statements.append(node)
            else:
                print(self.current_token().type)
                raise Exception("Talk Error: Expected Valid Statement")
        return statements

    def parse_show(self):
        if self.current_token().type=="SHOW":
            self.advance()
            expression = self.parse_expression()
            node = ShowNode(expression)
            return node 
        else:
            raise Exception("Talk Error: Expected 'show'")

    def parse_set(self):
        if self.current_token().type=="SET":
            self.advance()
            varname = self.parse_identifier()
            if self.current_token().type=="TO":
                self.advance()
                expression = self.parse_expression()
            else:
                raise Exception("Talk Error: Expected 'to'")
            node = SetNode(varname,expression)
            return node 
        else:
            raise Exception("Talk Error: Exprected 'set'")

    def parse_if(self):
        self.advance()
        condition = self.parse_condition()
        body= self.parse_body()
        if self.current_token() != None:
            if self.current_token().type == "OTHERWISE":
                if self.next_token().type == "IF":
                    self.advance()
                    n = self.parse_if()
                    elif_condition = n.condition
                    elif_body = n.body
                    else_body = n.else_body
                    else_if = IfNode(elif_condition,elif_body,else_body)
                    node = IfNode(condition,body,else_if)
                else:
                    self.advance()
                    else_body = self.parse_body()
                    node = IfNode(condition,body,else_body)
            else:
                node = IfNode(condition,body,None)
            return node 
        else:
            node = IfNode(condition,body,None)
            return node

    def parse_while(self):
        self.advance()
        condition = self.parse_condition()
        body = self.parse_body()
        node = WhileNode(condition,body)
        return node 

    def parse_repeat(self):
        self.advance()
        expression = self.parse_expression()
        self.advance()
        body = self.parse_body()
        node = RepeatNode(expression, body)
        return node

    def parse_function(self):
        parameters = []
        self.advance()
        name = FuncNameNode(self.current_token().value)
        self.advance()
        if self.current_token().type=="LPAREN":
            self.advance()
            while self.current_token().type!="RPAREN":
                pname = FuncParaNode(self.current_token().value)
                parameters.append(pname)
                self.advance()
        self.advance()
        body = self.parse_body()
        node = FuncNode(name,body,parameters)
        return node 

    def parse_call(self):
        values = []
        self.advance()
        name = FuncNameNode(self.current_token().value)
        self.advance()
        if self.current_token().type=="LPAREN":
            self.advance()
            while self.current_token().type!="RPAREN":
                pvalue = self.parse_expression()
                values.append(pvalue)
            self.advance()
        node = CallNode(name,values)
        return node 

    def parse_input(self):
        self.advance()
        name = StringNode(self.current_token().value)
        self.advance()
        node = InputNode(name)
        return node 
    

    def parse_condition(self,opr=""):
        left = self.parse_expression()
        while self.current_token().value in keywords:
            opr += self.current_token().value
            self.advance()
        if opr not in valid_conditions:
            print(opr)
            raise Exception("Talk Error: Not A Valid Condition")
        right = self.parse_expression()
        node = BinaryExpressionNode(left,opr,right)
        return node

    def parse_body(self):
        body = []
        if self.current_token().type == "LBRACE":
            self.advance()
            while self.current_token().type != "RBRACE":
                if self.current_token().type == "SHOW":
                    statement = self.parse_show()
                elif self.current_token().type == "SET":
                    statement = self.parse_set()
                elif self.current_token().type == "IF":
                    statement = self.parse_if()
                elif self.current_token().type == "IDENTIFIER":
                    statement = self.parse_increments()
                elif self.current_token().type == "WHILE":
                    statement = self.parse_while()
                elif self.current_token().type == "REPEAT":
                    statement = self.parse_repeat()
                elif self.current_token().type == "FUNCTION":
                    statement = self.parse_function()
                elif self.current_token().type == "CALL":
                    statement = self.parse_call()
                elif self.current_token().type == "INPUT":
                    statement = self.parse_input()
                else:
                    print(self.current_token().type)
                    raise Exception("Talk Error: Not a Valid Statement in Body Block")
                body.append(statement)
            self.advance()
            return body
            
        else:
            print(self.current_token().type)
            raise Exception("Talk Error: Expected a Body Block After Conditon")

    def parse_identifier(self):
        if self.current_token().type=="IDENTIFIER":
            var = self.current_token().value
            self.advance()
            return var 
        else:
            raise Exception("Talk Error: Expected a variable name")

    def parse_increments(self):
        value = self.parse_primary()
        if self.next_token()!=None:
            if self.current_token().type=="INCREMENT":
                node = IncrementNode(value)
                self.advance()
            elif self.current_token().type=="DECREMENT":
                node = DecrementNode(value)
                self.advance()
            else:
                print(self.current_token().type)
                raise Exception("Talk Error: Wrong Increment decrement operator after variable")
            return node
        else:
            raise Exception("Talk Error: No Increment or decrement Operator")
    

    def parse_primary(self):
        if self.current_token().type=="NUMBER":
            node = NumberNode(self.current_token().value)
            self.advance()
            return node
        elif self.current_token().type=="STRING":
            node = StringNode(self.current_token().value)
            self.advance()
            return node 
        elif self.current_token().type=="IDENTIFIER":
            node = VariableNode(self.current_token().value)
            self.advance()
            return node
        elif self.current_token().type=="LPAREN":
            self.advance()
            expression = self.parse_expression()
            if self.current_token().type=="RPAREN":
                self.advance()
            else:
                raise Exception("Talk Error: Expected ')'")
            node = ParenNode(expression)
            return node
        elif self.current_token().type=="LBRACE":
            fstring = True
            self.advance()
            expression = self.parse_expression()
            if self.current_token().type=="RBRACE":
                self.advance()
            else:
                raise Exception("Talk Error: Expected ')'")
            node = BraceNode(expression)
            return node
        else:
            print(self.current_token().type)
            raise Exception(f"Talk Error: Expected an expression at line:{self.current_token().line} and column:{self.current_token().column}")

    def parse_expression(self):
        left = self.parse_term()
        while self.current_token() is not None and self.current_token().type in ["PLUS","MINUS"]:
            opr = self.current_token().type
            self.advance()
            right = self.parse_term()
            left = BinaryExpressionNode(left,opr,right)
        return left

    def parse_term(self):
        left = self.parse_primary()
        while self.current_token() is not None and self.current_token().type in ["TIMES","DIVIDED"]:
            if self.current_token().type =="TIMES":
                opr = "TIMES"
            else:
                if self.next_token().type != "BY":
                    raise Exception("Talk Error: Expected 'BY' after 'DIVIDED'")
                opr = "DIVIDED BY"
                self.advance()
            self.advance()
            right = self.parse_primary()
            left = BinaryExpressionNode(left,opr,right)
        return left 
    
    def print_ast(self, node, indent=""):
        if isinstance(node, ShowNode):
            print(indent + "ShowNode")
            self.print_ast(node.value, indent + "    ")
        elif isinstance(node,ParenNode):
            print(indent + "ParenThesisNode")
            self.print_ast(node.value,indent + "    ")
        elif isinstance(node, BinaryExpressionNode):
            print(indent + "BinaryExpressionNode")
            print(indent + "├── Left:")
            self.print_ast(node.left, indent + "│   ")
            print(indent + "├── Operator:", node.operator)
            print(indent + "└── Right:")
            self.print_ast(node.right, indent + "    ")

        elif isinstance(node, NumberNode):
            print(indent + "NumberNode")
            print(indent + "└──", node.value)

        elif isinstance(node, StringNode):
            print(indent + "StringNode")
            print(indent + "└──", node.value)

        elif isinstance(node, VariableNode):
            print(indent + "VariableNode")
            print(indent + "└──", node.name)

        elif isinstance(node, SetNode):
            print(indent + "SetNode")
            print(indent + "├── Name:", node.name)
            print(indent + "└── Value:")
            self.print_ast(node.value, indent + "    ")

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.func_parameters = {}

    def interpret(self,node,local_variables=None):
        if local_variables is None:
            local_variables = {}
        if isinstance(node,ShowNode):
            value = self.interpret(node.value,local_variables)
            print(value)
        elif isinstance(node,SetNode):
            name = node.name
            value = self.interpret(node.value,local_variables)
            self.variables[name] = value
        elif isinstance(node,IfNode):
            condition = self.interpret(node.condition,local_variables)
            if condition:
                for statement in node.body:
                    self.interpret(statement,local_variables)
            else:
                if isinstance(node.else_body,IfNode):
                    self.interpret(node.else_body,local_variables)
                elif node.else_body!=None:
                    for statement in node.else_body:
                        self.interpret(statement,local_variables)
        elif isinstance(node,WhileNode):
            loop = True
            while loop:
                condition = self.interpret(node.condition,local_variables)
                if condition:
                    for statement in node.body:
                        self.interpret(statement,local_variables)
                else:
                    loop = False

        elif isinstance(node,RepeatNode):
            number = self.interpret(node.expression,local_variables)
            for i in range(0,number):
                for statement in node.body:
                    self.interpret(statement,local_variables)

        elif isinstance(node,FuncNode):
            name = self.interpret(node.name,local_variables)
            self.functions[name] = node.body
            self.func_parameters[name] = node.parameters

        elif isinstance(node,CallNode):
            name = self.interpret(node.name,local_variables)
            parameters = self.func_parameters[name]
            if name in self.functions:
                body = self.functions[name]
                arguments = [self.interpret(value,local_variables) for value in node.values]
                if len(parameters)!=len(arguments):
                    raise Exception(f"Talk Error: Function '{name}' expected {len(parameters)} arguments, but got {len(arguments)}")
                function_variables = {parameter.name:value for parameter,value in zip(parameters,arguments)}
                for statement in body:
                    self.interpret(statement,function_variables)
            else:
                raise Exception(f"Talk Error: No Function named {name} exists")

        elif isinstance(node,InputNode):
            name = self.interpret(node.name,local_variables)
            value = input()
            self.variables[name] = value

        elif isinstance(node,ParenNode):
            return self.interpret(node.value,local_variables)
        elif isinstance(node,BraceNode):
            return self.interpret(node.value,local_variables)
        
        elif isinstance(node,IncrementNode):
            if isinstance(node.variable,VariableNode):
                self.variables[node.variable.name] = self.variables[node.variable.name] + 1

        elif isinstance(node,DecrementNode):
            if isinstance(node.variable,VariableNode):
                self.variables[node.variable.name] = self.variables[node.variable.name] - 1

        elif isinstance(node,BinaryExpressionNode):
            left = self.interpret(node.left,local_variables)
            right = self.interpret(node.right,local_variables)
            opr = node.operator
            if opr=="PLUS":
                return left+right
            elif opr=="MINUS":
                return left-right
            elif opr=="TIMES":
                return left*right 
            elif opr=="DIVIDED BY":
                return left/right
            elif opr=="isgreaterthan":
                return left>right
            elif opr=="issmallerthan":
                return left<right
            elif opr=="is":
                return left==right
            elif opr=="isatmost":
                return left<=right 
            elif opr=="isatleast":
                return left>=right 
            elif opr=="isnot":
                return left!=right 
            else:
                print(opr)
                raise Exception("Talk Error: Incorrect Operator type")

        elif isinstance(node,FuncNameNode):
            return node.name
        
        elif isinstance(node,(FuncParaNode,VariableNode)):
            if node.name in local_variables:
                return local_variables[node.name]
            return self.variables[node.name]
            

        elif isinstance(node,NumberNode):
            return node.value
        
        elif isinstance(node,StringNode):
            import re

            def replace_expression(match):
                expression = match.group(1)

                tokens = tokenize(expression)
                parser = Parser(tokens)
                ast = parser.parse_expression()

                result = self.interpret(ast,local_variables)
                return str(result)

            return re.sub(r"\{([^{}]+)\}", replace_expression, node.value)


tokens = tokenize(source)
# for i in tokens:
#     print(i.type,i.value)
parser = Parser(tokens,0)
nodes=parser.parse_program()
#parser.print_ast(nodes[0])
interpreter = Interpreter()
for i in range(0,len(nodes)):
    interpreter.interpret(nodes[i])
