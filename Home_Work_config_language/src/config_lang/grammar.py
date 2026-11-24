#Грамматика учебного конфигурационного языка

GRAMMAR = r"""
start: config_item*

config_item: const_decl | dict

const_decl: NAME "is" const_value ";"

?const_value: NUMBER            -> number
            | const_expr

const_expr: "." expr "."

?expr: expr "+" term   -> add
     | expr "-" term   -> sub
     | term

?term: term "*" factor -> mul
     | term "/" factor -> div
     | factor

?factor: NUMBER                              -> number
       | NAME                                -> var
       | "(" expr ")"
       | "abs" "(" expr ")"                  -> abs_fn
       | "min" "(" expr ("," expr)* ")"      -> min_fn

dict: "{" entry* "}"

entry: NAME "->" value "."?

?value: NUMBER    -> number
      | dict
      | const_expr
      | NAME       -> var

NAME: /[_a-z]+/
NUMBER: /[+-]?\d+\.\d+/

COMMENT: /\/\*[\s\S]*?\*\//

%import common.WS
%ignore WS
%ignore COMMENT
"""
