from Grammar import Grammar


class Parser:
    def __init__(self, grammar: Grammar):
        self.__first_set = dict()
        self.__follow_set = dict()
        self.__grammar: Grammar = grammar
        self.__compute_first_set()
        self.__compute_follow_set()

    def __compute_first_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__first_set[non_terminal] = self.first(non_terminal)

    def first(self, non_terminal):
        if non_terminal in self.__first_set:
            return self.__first_set[non_terminal]

        first = set()
        for production, _ in self.__grammar.get_productions_non_terminal(non_terminal):
            first_symbol = production.split(' ')[0]
            if first_symbol == 'Є':
                first.add(first_symbol)
            elif first_symbol in self.__grammar.get_terminals():
                first.add(first_symbol)
            else:
                for symbol in self.first(first_symbol):
                    first.add(symbol)

        return first

    def __compute_follow_set(self):
        for non_terminal in self.__grammar.get_non_terminals():
            self.__follow_set[non_terminal] = self.follow(non_terminal)

    def follow(self, non_terminal):
        if non_terminal in self.__follow_set:
            return self.__follow_set[non_terminal]

        follow = set()
        if non_terminal == self.__grammar.get_start_symbol():
            follow.add('Є') 

        for nt in self.__grammar.get_productions():
            for production, _ in self.__grammar.get_productions_non_terminal(nt):
                if non_terminal not in production:
                    continue

                symbols: list = production.split(' ')
                
                if symbols.index(non_terminal) < len(symbols) - 1:
                    follow_symbol = symbols[symbols.index(non_terminal) + 1]
                    if follow_symbol == 'Є':
                        follow = follow.union(follow(nt))
                    elif follow_symbol in self.__grammar.get_terminals():
                        follow.add(follow_symbol)
                    else:
                        first_set: set = self.first(follow_symbol)
                        if 'Є' in first_set:
                            first_set.remove('Є')
                            follow = follow.union(self.follow(nt))
                        follow = follow.union(first_set)
                else:
                    follow = follow.union(self.follow(nt))
                
        return follow


g = Grammar("g1.txt")
p = Parser(g)
# print(p.first("S"))
print('Foolo')
# print(p.follow('B'))

