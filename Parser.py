from Grammar import Grammar
import copy


class Parser:
    def __init__(self, grammar: Grammar):
        self.__first_set = dict()
        self.__follow_set = dict()
        self.__grammar: Grammar = grammar
        self.__need_follow = False
        self.__compute_first_set()
        if self.__need_follow:
            self.__compute_follow_set()

    def __compute_first_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__first_set[non_terminal] = self.first(non_terminal)

    def first(self, non_terminal):
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

    def __compute_follow_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__follow_set[non_terminal] = self.follow(non_terminal)

    def follow(self, non_terminal):
        if non_terminal in self.__follow_set:
            return self.__follow_set[non_terminal]

        follow = set()
        if non_terminal == self.__grammar.get_start_symbol():
            follow.add("epsilon")
            return follow

        for nt in self.__grammar.get_productions():
            for production, _ in self.__grammar.get_productions_non_terminal(nt):
                if non_terminal not in production:
                    continue

                symbols: list = production.split(' ')

                # non-terminal is in the right side of the production
                if symbols.index(non_terminal) < len(symbols) - 1:
                    follow_symbol = symbols[symbols.index(non_terminal) + 1]
                    if follow_symbol == "epsilon":
                        follow = follow.union(follow(nt))
                    elif follow_symbol in self.__grammar.get_terminals():
                        follow.add(follow_symbol)
                    else:
                        first_set: set = copy.deepcopy(self.first(follow_symbol))
                        if "epsilon" in first_set:
                            first_set.remove("epsilon")
                            follow = follow.union(self.follow(nt))
                        follow = follow.union(first_set)
                # else:
                #     follow = follow.union(self.follow(nt))
                # follow.add("epsilon")

        return follow

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


g = Grammar("g1.txt")
p = Parser(g)
print(p.get_first_string())
print("Follow")
print(p.get_follow_string())
