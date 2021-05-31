import lexer
assembly_code = ""
var_map = dict()
stack_index = -4
declared = set()
label_counters = dict()
function_begin = "\t.globl {name}\n{name}:\n"
move_to_eax = "\tmovl ${}, %eax \n"
function_prologue = "\tpush %ebp\n\tmovl %esp, %ebp\n"
function_epilogue = "\tmovl %ebp, %esp\n\tpop %ebp\n\tret\n"
push_eax_to_stack = "\tpush %eax\n"
pop_from_stack_to_ecx = "\tpop %ecx\n"
swap_eax_ecx = "\tpush %eax\n\tpush %ecx\n\tpop %eax\n\tpop %ecx\n"  # "\txchg %eax %ecx\n" #
move_registers = "\tmovl %{}, %{} \n"


def emit(string):
    global assembly_code
    assembly_code = assembly_code + string


def get_new_label(s):
    if s not in label_counters.keys():
        label_counters[s] = 0
    new_label = s + str(label_counters[s])
    label_counters[s] += 1
    return new_label


"""
EXPECT
"""


def fail(s):
    print(s)
    raise Exception(s)


def assert_token(token, string, forced_fail=False):
    if not forced_fail and token.content() == string:
        return True
    else:
        # TODO exception
        fail("expected \"{str}\" but got \"{token}\" at {line}:{char}".format(str=string, token=token.content(),
                                                                              line=token.line(), char=token.char()))


def token_is_type(token):
    if token.content() in ["int"]:
        return True


def assert_token_identifier(token):
    if token.is_identifier():
        return True
    else:
        return assert_token(token, "")


"""
PARSING
"""


def parse_function_call(tokens):
    return tokens


def parse_factor(tokens):
    # TODO postfix ++ --
    tokens = parse_function_call(tokens)
    if tokens[0].content() == '(':
        tokens = parse_expr(tokens[1:])
        assert_token(tokens[0], ')')
        return tokens[1:]
    elif tokens[0].content().isnumeric():
        emit(move_to_eax.format(tokens[0].content()))

    elif tokens[0].is_identifier():
        offset = var_map[tokens[0].content()]
        emit("\tmovl {}(%ebp), %eax\n".format(offset))
        return tokens[1:]
    else:
        return assert_token(tokens[0], "")
    return tokens[1:]


def parse_unary_expr(tokens):
    # TODO prefix ++ --
    if tokens[0].content() in ['+', '-', '!', '~']:
        if tokens[0].content() == '+':
            tokens = parse_expr(tokens[1:])
        elif tokens[0].content() == '-':
            tokens = parse_expr(tokens[1:])
            emit("\tneg %eax\n")
        elif tokens[0].content() == '!':
            tokens = parse_expr(tokens[1:])
            emit("\tcmpl $0, %eax\n\tmovl $0, %eax\t\nsete %al\n")
        elif tokens[0].content() == '~':
            tokens = parse_expr(tokens[1:])
            emit("\txor $0xFFFFFFFF, %eax\n")
    else:
        tokens = parse_factor(tokens)

    return tokens


def parse_term(tokens):
    tokens = parse_unary_expr(tokens)
    while tokens[0].content() in ['*', '/', '%']:
        operator = tokens[0].content()
        emit(push_eax_to_stack)
        tokens = parse_unary_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        if operator == '*':
            emit("\timul %ecx, %eax\n")
        elif operator == '/':
            emit(swap_eax_ecx)
            emit("\tcdq\n\tidivl %ecx\n")
        else:
            emit(swap_eax_ecx)
            emit("\tcdq\n\tidivl %ecx\n")
            emit(move_registers.format("edx", "eax"))
    return tokens


def parse_additive_expr(tokens):
    tokens = parse_term(tokens)
    while tokens[0].content() in ['+', '-']:
        operator = tokens[0].content()
        emit(push_eax_to_stack)
        tokens = parse_term(tokens[1:])
        emit(pop_from_stack_to_ecx)
        if operator == '+':
            emit("\taddl %ecx, %eax\n")
        else:
            emit(swap_eax_ecx)
            emit("\tsubl %ecx, %eax\n")

    return tokens


def parse_shift_expr(tokens):
    tokens = parse_additive_expr(tokens)
    while tokens[0].content() in ['>>', '<<']:
        operator = tokens[0].content()
        emit(push_eax_to_stack)
        tokens = parse_additive_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        if operator == '<<':
            emit(swap_eax_ecx)
            emit("\tshl %ecx, %eax\n")
        else:
            emit(swap_eax_ecx)
            emit("\tshr %ecx, %eax\n")
    return tokens


def parse_compare_expr(tokens):
    tokens = parse_shift_expr(tokens)
    while tokens[0].content() in ['>', '>=', '<', '<=']:
        operator = tokens[0].content()
        emit(push_eax_to_stack)
        tokens = parse_shift_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        emit("\tcmpl %eax, %ecx\n\tmovl $0, %eax\n")
        if operator == '>':
            emit("\tsetg %al\n")
        elif operator == '>=':
            emit("\tsetge %al\n")
        elif operator == '<':
            emit("\tsetl %al\n")
        elif operator == '<=':
            emit("\tsetle %al\n")
    return tokens


def parse_equality_expr(tokens):
    tokens = parse_compare_expr(tokens)
    while tokens[0].content() in ['==', '!=']:
        operator = tokens[0].content()
        emit(push_eax_to_stack)
        tokens = parse_compare_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        emit("\tcmpl %eax, %ecx\n\tmovl $0, %eax\n")
        if operator == '==':
            emit("\tsete %al\n")
        elif operator == '!=':
            emit("\tsetne %al\n")
    return tokens


def parse_bit_and_expr(tokens):
    tokens = parse_equality_expr(tokens)
    while tokens[0].content() == "&":
        emit(push_eax_to_stack)
        tokens = parse_equality_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        emit("\tand %ecx, %eax\n")
    return tokens


def parse_bit_xor_expr(tokens):
    tokens = parse_bit_and_expr(tokens)
    while tokens[0].content() == "^":
        emit(push_eax_to_stack)
        tokens = parse_bit_and_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        emit("\txor %ecx, %eax\n")
    return tokens


def parse_bit_or_expr(tokens):
    tokens = parse_bit_xor_expr(tokens)
    while tokens[0].content() == "|":
        emit(push_eax_to_stack)
        tokens = parse_bit_xor_expr(tokens[1:])
        emit(pop_from_stack_to_ecx)
        emit("\tor %ecx, %eax\n")
    return tokens


def parse_logical_and_expr(tokens):
    tokens = parse_bit_or_expr(tokens)
    label_end = ""
    if tokens[0].content() == "&&":
        label_end = get_new_label("_logical_expr_end")
    while tokens[0].content() == "&&":
        label_next = get_new_label("_next_logical_expr")
        emit("\tcmpl $0, %eax\n\tjne {label_next}\n\tjmp {label_end}\n{label_next}:\n"
             .format(label_next=label_next, label_end=label_end))
        tokens = parse_bit_or_expr(tokens[1:])
    if label_end != "":
        emit(label_end + ":\n")
    return tokens


def parse_logical_or_expr(tokens):
    tokens = parse_logical_and_expr(tokens)
    label_end = ""
    if tokens[0].content() == "||":
        label_end = get_new_label("_logical_expr_end")
    while tokens[0].content() == "||":
        label_next = get_new_label("_next_logical_expr")
        emit("\tcmpl $0, %eax\n\tje {label_next}\n\tmovl $1, %eax\n\tjmp {label_end}\n{label_next}:\n"
             .format(label_next=label_next, label_end=label_end))
        tokens = parse_logical_and_expr(tokens[1:])
    if label_end != "":
        emit(label_end + ":\n")
    return tokens


def parse_conditional_expr(tokens):
    tokens = parse_logical_or_expr(tokens)
    if tokens[0].content() == '?':
        else_label = get_new_label("_else")
        end_if_label = get_new_label("_end_if")
        emit("\tcmpl $0, %eax\n\tje {}\n".format(else_label))
        tokens = parse_expr(tokens[1:])
        emit("\tjmp {end_if_label}\n{else_label}:\n"
             .format(end_if_label=end_if_label, else_label=else_label))
        assert_token(tokens[0], ':')
        tokens = parse_conditional_expr(tokens[1:])
        emit("{}:\n".format(end_if_label))
    return tokens


def parse_expr(tokens):
    if tokens[0].is_identifier():
        id = tokens[0].content()
        if id in var_map.keys():
            if tokens[1].content() == '=':
                tokens = parse_conditional_expr(tokens[2:])
                offset = var_map[id]
                emit("\tmovl %eax, {}(%ebp)\n".format(offset))
                return tokens
            elif tokens[1].content() == "+=":
                tokens = parse_conditional_expr(tokens[2:])
                offset = var_map[id]
                emit("\taddl %eax, {}(%ebp)\n".format(offset))
                return tokens
            elif tokens[1].content() == "-=":
                tokens = parse_conditional_expr(tokens[2:])
                offset = var_map[id]
                emit("\tsubl %eax, {}(%ebp)\n".format(offset))
                return tokens
            elif tokens[1].content() == "*=":
                tokens = parse_conditional_expr(tokens[2:])
                offset = var_map[id]
                emit("\tmull %eax, {}(%ebp)\n".format(offset))
                return tokens
            else:
                return parse_conditional_expr(tokens)
        else:
            fail("{} is not found".format(id))
            return tokens
    else:
        return parse_conditional_expr(tokens)


def parse_declaration(tokens):
    global stack_index
    if token_is_type(tokens[0]):  # declaration
        if tokens[1].is_identifier():
            id = tokens[1].content()
            if id in declared:
                fail("{} is declared".format(id))
            if tokens[2].content() == '=':
                tokens = parse_expr(tokens[3:])
                emit("\tpushl %eax\n")
            else:
                assert_token(tokens[2], ';')
                emit("\tpush $0\n")
                tokens = tokens[2:]
            declared.add(id)
            var_map[id] = stack_index
            stack_index -= 4
            assert_token(tokens[0], ";")
            return tokens[1:]


def parse_statement(tokens):
    global var_map, declared, stack_index
    if tokens[0].content() == "return":  # return statement
        tokens = parse_expr(tokens[1:])
        assert_token(tokens[0], ";")
        return tokens[1:]
    elif tokens[0].content() == "if":  # if statement
        assert_token(tokens[1], '(')
        tokens = parse_expr(tokens[2:])
        assert_token(tokens[0], ')')

        else_label = get_new_label("_else")
        end_if_label = get_new_label("_end_if")
        emit("\tcmpl $0, %eax\n\tje {}\n".format(else_label))
        tokens = parse_block_item(tokens[1:])

        if tokens[0].content() == "else":
            emit("\tjmp {end_if_label}\n{else_label}:\n"
                 .format(end_if_label=end_if_label, else_label=else_label))
            tokens = parse_block_item(tokens[1:])
            emit("{}:\n".format(end_if_label))
        else:
            emit("{}:\n".format(else_label))
        return tokens
    elif tokens[0].content() == "do":
        begin_label = get_new_label("_loop_begin")
        emit("{}:\n".format(begin_label))
        tokens = parse_block_item(tokens[1:])
        assert_token(tokens[0], "while")
        assert_token(tokens[1], '(')
        tokens = parse_expr(tokens[2:])
        emit("\tcmpl $0, %eax\n\tjne {}\n".format(begin_label))
        assert_token(tokens[0], ')')
        assert_token(tokens[1], ';')
        return tokens[2:]
    elif tokens[0].content() == "while":
        begin_label, end_label = get_new_label("_loop_begin"), get_new_label("_loop_end")
        assert_token(tokens[1], '(')
        emit("{}:\n".format(begin_label))
        tokens = parse_expr(tokens[2:])
        emit("\tcmpl $0, %eax\n\tje {}\n".format(end_label))
        assert_token(tokens[0], ')')
        tokens = parse_block_item(tokens[1:])
        emit("\tjmp {begin}\n{end}:\n".format(begin=begin_label, end=end_label))
        return tokens
    elif tokens[0].content() == "for":
        current_var_map, current_stack_index, current_declared = var_map.copy(), stack_index, declared.copy()
        declared = set()

        assert_token(tokens[1], '(')
        if tokens[2].content() == ';':
            tokens = tokens[3:]
        else:
            tokens = parse_block_item(tokens[2:])
        begin_label, end_label = get_new_label("_loop_begin"), get_new_label("_loop_end")
        emit("{}:\n".format(begin_label))
        if tokens[0].content() == ';':
            emit("\tmovl $1 %eax\n")
        else:
            tokens = parse_expr(tokens)
        assert_token(tokens[0], ';')
        tokens = tokens[1:]
        emit("\tcmpl $0, %eax\n\tje {}\n".format(end_label))
        end_loop_tokens = []
        while tokens[0].content() != ')':
            end_loop_tokens.append(tokens[0])
            tokens = tokens[1:]
        assert_token(tokens[0], ')')
        tokens = parse_block_item(tokens[1:])
        end_loop_tokens.append(lexer.Token("dummy token", "", 0, 0))
        end_loop_tokens = parse_expr(end_loop_tokens)
        if end_loop_tokens[0].content() != "dummy token":
            assert_token(end_loop_tokens[0], ')', forced_fail=True)
        emit("\tjmp {begin}\n{end}:\n".format(begin=begin_label, end=end_label))

        emit("\taddl ${}, %esp\n".format((current_stack_index - stack_index)))
        var_map, stack_index, declared = current_var_map, current_stack_index, current_declared
        return tokens
    elif tokens[0].content() == '{':  # block_element
        current_var_map, current_stack_index, current_declared = var_map.copy(), stack_index, declared.copy()
        declared = set()

        tokens = tokens[1:]
        while tokens and tokens[0].content() != '}':
            tokens = parse_block_item(tokens)
        assert_token(tokens[0], '}')

        emit("\taddl ${}, %esp\n".format((current_stack_index - stack_index)))
        var_map, stack_index, declared = current_var_map, current_stack_index, current_declared
        return tokens[1:]
    else:
        tokens = parse_expr(tokens)
        assert_token(tokens[0], ';')
        return tokens[1:]


def parse_block_item(tokens):
    if token_is_type(tokens[0]):
        tokens = parse_declaration(tokens)
    else:
        tokens = parse_statement(tokens)
    return tokens


def parse_function(tokens):
    global assembly_code
    token_is_type(tokens[0])
    assert_token_identifier(tokens[1])
    assert_token(tokens[2], '(')
    assert_token(tokens[3], ')')
    assert_token(tokens[4], '{')

    emit(function_begin.format(name=tokens[1].content()))
    emit(function_prologue)
    tokens = tokens[5:]
    while tokens and tokens[0].content() != '}':
        tokens = parse_block_item(tokens)
    emit(function_epilogue)
    return tokens[1:]


def parse_program(token_list):
    tokens = token_list
    while tokens:
        tokens = parse_function(tokens)


def parse(token_list):
    global assembly_code
    assembly_code = ""
    parse_program(token_list)
    return assembly_code
