from Grammar import Grammar
import copy


class Parser:
    def __init__(self, grammar: Grammar):
        self.__first_set = dict()
        self.__follow_set = dict()
        self.__grammar: Grammar = grammar
        self.__need_follow = False
        self.__ll1_table = dict()
        self.__parsing_tree = list()

        self.__compute_first()
        if self.__need_follow:
            self.__compute_follow_set()
        self.ll1_table()

    def __compute_first(self):
        prev_first_set = dict()

        for non_terminal in self.__grammar.get_non_terminals():
            prev_first_set[non_terminal] = set()

        while True:
            current_first = copy.deepcopy(prev_first_set)

            for non_terminal in self.__grammar.get_non_terminals():
                # if non_terminal == "simplstmt":
                #     print(non_terminal)
                #     pass
                for production, _ in self.__grammar.get_productions_non_terminal(non_terminal):
                    symbols = production.split(' ')

                    if symbols[0] in self.__grammar.get_terminals():
                        current_first[non_terminal].add(symbols[0])
                    elif symbols[0] == 'epsilon':
                        self.__need_follow = True
                        current_first[non_terminal].add(symbols[0])
                    else:
                        concatenation_result = self.__concatenation_length1(symbols, prev_first_set)
                        current_first[non_terminal] = current_first[non_terminal].union(concatenation_result)

            different = False
            for key in current_first:
                if current_first[key] != prev_first_set[key]:
                    different = True

            if not different:
                self.__first_set = current_first
                return

            prev_first_set = copy.deepcopy(current_first)

    def first(self, sequence):
        if sequence == 'epsilon':
            return sequence

        symbols = sequence.split(' ')
        if len(symbols) == 1:
            if symbols[0] in self.__grammar.get_terminals():
                return {symbols[0]}

            return self.__first_set[symbols[0]]
        return self.__concatenation_length1(symbols, self.__first_set)

    def __concatenation_length1(self, symbols, first_set):
        if symbols[0] in self.__grammar.get_terminals():
            set1 = {symbols[0]}
        else:
            set1 = first_set[symbols[0]]

        if len(symbols) == 1:
            return set1

        if len(set1) > 0:
            concatenation_result = set()
            i = 1
            while i < len(symbols):
                if symbols[i] in self.__grammar.get_terminals():
                    set2 = {symbols[i]}
                else:
                    set2 = first_set[symbols[i]]

                if len(set2) == 0:
                    break

                for s1 in set1:
                    for s2 in set2:
                        if s1 == 'epsilon':
                            concatenation_result.add(s2)
                        else:
                            concatenation_result.add(s1)

                set1 = set2
                i += 1

            return concatenation_result

        return set1

    def __compute_follow_set(self):
        follow_sets = list()
        follow_sets.append(dict())

        for non_terminal in self.__grammar.get_non_terminals():
            follow_sets[0][non_terminal] = set()

        follow_sets[0][self.__grammar.get_start_symbol()] = {"epsilon"}

        i = 0

        while True:
            i += 1
            current_follow = copy.deepcopy(follow_sets[i - 1])
            for non_terminal in self.__grammar.get_non_terminals():
                for nt in self.__grammar.get_productions():
                    for production, _ in self.__grammar.get_productions_non_terminal(nt):
                        symbols: list = production.split(' ')
                        if non_terminal not in symbols:
                            continue
                        
                        indices = [i+1 for i, x in enumerate(symbols) if x == non_terminal]   
                        for idx in indices:
                            if idx < len(symbols):
                                follow_symbol = symbols[idx]

                                first_set: set = copy.deepcopy(self.first(follow_symbol))
                                if "epsilon" in first_set:
                                    first_set.remove("epsilon")
                                    current_follow[non_terminal] = current_follow[non_terminal].union(
                                        follow_sets[i - 1][nt])
                                current_follow[non_terminal] = current_follow[non_terminal].union(first_set)
                            else:
                                if nt == non_terminal:
                                    continue
                                current_follow[non_terminal] = current_follow[non_terminal].union(follow_sets[i - 1][nt])

            follow_sets.append(current_follow)

            if follow_sets[i] == follow_sets[i - 1]:
                break

        self.__follow_set = follow_sets.pop()

    def get_first_string(self):
        first_string = ""
        for key in sorted(list(self.__first_set)):
            first_string += key + ": " + str(self.__first_set[key]) + "\n"

        return first_string

    def get_follow_string(self):
        follow_string = ""
        for key in sorted(list(self.__follow_set)):
            follow_string += key + ": " + str(self.__follow_set[key]) + "\n"

        return follow_string

    def print_ll1_table(self):
        symbols = list(self.__grammar.get_non_terminals() | self.__grammar.get_terminals())
        symbols.append("$")
        terminals = list(self.__grammar.get_terminals())
        terminals.append("$")
        ll1_table_string = ' '.join([s for s in terminals]) + "\n"

        for s in symbols:
            ll1_table_string += s + ": " + ' '.join([str(self.__ll1_table[s, t]) for t in terminals]) + "\n"

        print(ll1_table_string)

    def ll1_table(self):
        symbols = self.__grammar.get_non_terminals() | self.__grammar.get_terminals() | {"$"}
        for s in symbols:
            for terminal in self.__grammar.get_terminals() | {"$"}:
                if s == terminal == "$":
                    self.__ll1_table[s, terminal] = ("accept", -1)
                elif s == terminal:
                    self.__ll1_table[s, terminal] = ("pop", -1)
                else:
                    self.__ll1_table[s, terminal] = ("error", -1)

        for nt in self.__grammar.get_productions():
            for production, index in self.__grammar.get_productions_non_terminal(nt):
                try:
                    first = self.first(production)
                except Exception as e:
                    print("PRODUCTION", production)

                if "epsilon" in first:
                    follow = self.__follow_set[nt]
                    for y in follow:
                        self.__ll1_table[nt, y] = (production, index)
                for x in first:
                    if x != "epsilon":
                        self.__ll1_table[nt, x] = (production, index)

        return self.__ll1_table

    def parsing_algo(self, sequence):
        input_stack = sequence.split(' ')
        working_stack = list()
        output_stack = list()

        input_stack.append('$')
        working_stack.append(self.__grammar.get_start_symbol())
        working_stack.append('$')

        while len(input_stack) > 0:
            input_elem = input_stack[0]
            working_elem = working_stack[0]
            if working_elem == 'epsilon':
                working_stack.pop(0)
            else:
                ll1_entry = self.__ll1_table[working_elem, input_elem]

                if ll1_entry[0] == 'pop':
                    working_stack.pop(0)
                    input_stack.pop(0)

                elif ll1_entry[0] == 'error':
                    print("Error at: ", input_elem, working_elem)
                    return

                elif ll1_entry[0] == 'accept':
                    print("Sequence accepted")
                    self.tree(output_stack)
                    return

                else:
                    working_stack.pop(0)  # eliminate symbol from working stack
                    rhs_production = ll1_entry[0].split()
                    working_stack = rhs_production + working_stack  # add the new symbols
                    output_stack += [ll1_entry[1]]  # add the production number

    def tree(self, output_stack):
        self.__parsing_tree = list()
        self.__parsing_tree.append({"index": 1, "info": self.__grammar.get_start_symbol(), "parent": 0, "left": 0})

        self.__tree_rec(output_stack, 1)

    def __tree_rec(self, output_stack, parent_index):
        index = len(self.__parsing_tree) + 1
        prod_index = output_stack.pop(0)
        production_symbols = self.__grammar.get_production_by_index(prod_index)[1].split(' ')
        left = 0
        indexes = []
        for s in production_symbols:
            self.__parsing_tree.append({"index": index, "info": s, "parent": parent_index, "left": left})
            indexes.append(index)
            left = index
            index += 1

        for i in range(len(production_symbols)):
            if production_symbols[i] in self.__grammar.get_non_terminals():
                self.__tree_rec(output_stack, indexes[i])

        if len(output_stack) == 0:
            return

    def print_parsing_tree(self):
        for line in self.__parsing_tree:
            print("index: ", line["index"], "info: ", line["info"], "parent: ", line["parent"], "left: ", line["left"])


g = Grammar("g2.txt")
p = Parser(g)
# print(p.get_first_string())
# print("Follow")
# print(p.get_follow_string())
# p.print_ll1_table()
stack = p.parsing_algo("go { number array [ const ] id ; }")
p.print_parsing_tree()
# print(g.get_productions())
# output = p.parsing_algo("d a d a")
# print(output)
# print(p.tree(output))