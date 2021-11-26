from Grammar import Grammar


class Parser:
    def __init__(self, grammar: Grammar):
        self.__first_set = dict()
        self.__grammar: Grammar = grammar
        self.__compute_first_set()

    def __compute_first_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__first_set[non_terminal] = self.first_of_non_terminal(non_terminal)

    def first_of_non_terminal(self, non_terminal):
        if non_terminal in self.__first_set:
            return self.__first_set[non_terminal]

        first = set()
        for production, index in self.__grammar.get_productions_non_terminal(non_terminal):
            first_symbol = production.split(' ')[0]
            if first_symbol == 'epsilon':
                first.add(first_symbol)
            elif first_symbol in self.__grammar.get_terminals():
                first.add(first_symbol)
            else:
                for symbol in self.first_of_non_terminal(first_symbol):
                    first.add(symbol)

        return first


g = Grammar("g1.txt")
p = Parser(g)
print(p.first_of_non_terminal("S"))
