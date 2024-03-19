from tree_sitter import Language, Parser
from queue import LifoQueue


def refactor_code(code: bytes, parser: Parser) -> bytes:
    tree = parser.parse(code)
    cursor = tree.walk()

    parents_stack = LifoQueue()
    block_count = 0
    names_to_new = {}
    names_counter = 1
    previous_leaf = None

    symbol_check = {',', ':', '=', '+', '-', '*', '**', '/', '//', '%', '&', '|', '^', '~', '<<', '>>',
                    '+=', '-=', '*=', '**=', '/=', '//=', '%=', '&=', '|=', '^=', '<<=', '>>=', '\\',
                    '==', '>=', '<=', '!=', '>', '<', '{', '}', ']', ')'}
    previous_symbol_check = {'(', '['}
    symbol_check = set(map(lambda x: bytes(x, 'utf-8'), symbol_check))
    previous_symbol_check = set(map(lambda x: bytes(x, 'utf-8'), previous_symbol_check))

    result = b''

    visited_children = False
    while True:
        current = cursor.node
        if not visited_children:
            if cursor.goto_first_child():
                parents_stack.put(current.type)
                if current.type == 'block':
                    block_count += 1
            else:
                visited_children = True
                if current.type == 'comment':
                    continue

                text = current.text
                if current.type == 'identifier':
                    if text not in names_to_new:
                        names_to_new[text] = bytes(f'name_{names_counter}', 'utf-8')
                        names_counter += 1
                    text = names_to_new[text]

                if previous_leaf is None:
                    result += text
                else:
                    if previous_leaf.end_point[0] < current.start_point[0]:
                        result += bytes('\n', 'utf-8')
                        if block_count > 0:
                            result += bytes(' ' * block_count, 'utf-8')
                    elif previous_leaf.end_point[1] < current.start_point[1] and \
                            not (previous_leaf.text in symbol_check or current.text in symbol_check) and \
                            not (previous_leaf.text in previous_symbol_check):
                        result += bytes(' ', 'utf-8')
                    result += text
                previous_leaf = current

        elif cursor.goto_next_sibling():
            visited_children = False

        elif cursor.goto_parent():
            if parents_stack.get() == 'block':
                block_count -= 1

        else:
            break

    return result


if __name__ == '__main__':
    # заменить путь
    py = Language("python.so", "python")
    python_parser = Parser()
    python_parser.set_language(py)

    with open("task_1.in", "rb") as f:
        old_code = f.read()
    new_code = refactor_code(old_code, python_parser)
    with open("task_1.out", "wb") as f:
        f.write(new_code)
