from Grammar import Grammar
import copy


class Parser:
    def __init__(self, grammar: Grammar):
        self.__first_set = dict()
        self.__follow_set = dict()
        self.__grammar: Grammar = grammar
        self.__need_follow = True
        self.__ll1_table = dict()

        self.__compute_first_set()
        if self.__need_follow:
            self.__compute_follow_set()

    def __compute_first_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__first_set[non_terminal] = self.first(non_terminal)

    def first_non_terminal(self, non_terminal):
        if non_terminal in self.__first_set:
            return self.__first_set[non_terminal]

        first = set()
        if non_terminal != "epsilon":
            for production, _ in self.__grammar.get_productions_non_terminal(non_terminal):
                symbols = production.split(' ')

                if symbols[0] == "epsilon":
                    first.add(symbols[0])
                    self.__need_follow = True
                elif symbols[0] in self.__grammar.get_terminals():
                    first.add(symbols[0])
                else:
                    has_epsilon = False  # suppose there is no epsilon
                    for symbol in self.first(symbols[0]):
                        if symbol == "epsilon":
                            has_epsilon = True
                        else:
                            first.add(symbol)

                    idx = 1
                    epsilon_occurrences = 1
                    while has_epsilon and idx < len(symbols):
                        has_epsilon = False  # suppose there is no epsilon
                        for symbol in self.first(symbols[idx]):
                            if symbol == "epsilon":
                                has_epsilon = True
                                epsilon_occurrences += 1
                            else:
                                first.add(symbol)
                        idx += 1

                    if has_epsilon and epsilon_occurrences == len(symbols):
                        first.add("epsilon")

        return first

    def first(self, sequence):
        symbols = sequence.split(' ')
        first = set()
        idx = 0
        has_epsilon = True

        while idx < len(symbols) and has_epsilon:
            has_epsilon = False  # suppose there is no epsilon

            if symbols[idx] == "epsilon":
                first.add(symbols[idx])
                self.__need_follow = True

            elif symbols[idx] in self.__grammar.get_terminals():
                first.add(symbols[idx])

            else:
                # compute first for a non-terminal
                first_non_terminal = self.first_non_terminal(symbols[idx])

                if "epsilon" in first_non_terminal:
                    has_epsilon = True
                    for s in first_non_terminal:
                        if s != "epsilon":
                            first.add(s)
            idx += 1

        if has_epsilon:
            first.add("epsilon")

        return first

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
                        if non_terminal not in production:
                            continue

                        symbols: list = production.split(' ')

                        if symbols.index(non_terminal) < len(symbols) - 1:
                            follow_symbol = symbols[symbols.index(non_terminal) + 1]

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
        for key in self.__first_set:
            first_string += key + ": " + str(self.__first_set[key]) + "\n"

        return first_string

    def get_follow_string(self):
        follow_string = ""
        for key in self.__follow_set:
            follow_string += key + ": " + str(self.__follow_set[key]) + "\n"

        return follow_string

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
                first = self.first(production)
                print(production, first)
                if "epsilon" in first:
                    follow = self.__follow_set[nt]
                    for y in follow:
                        self.__ll1_table[nt, y] = (production, index)
                for x in first:
                    if x != "epsilon":
                        self.__ll1_table[nt, x] = (production, index)

        print(self.__ll1_table)


g = Grammar("g1.txt")
p = Parser(g)
print(p.get_first_string())
print("Follow")
print(p.get_follow_string())
p.ll1_table()
