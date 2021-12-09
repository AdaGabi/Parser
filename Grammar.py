class Grammar:
    def __init__(self, file_name):
        self.__non_terminals = set()
        self.__terminals = set()
        self.__start_symbol = None
        self.__productions = dict()
        self.__is_CFG = True
        self.__read_grammar(file_name)

    def __read_grammar(self, file_name):
        file = open(file_name, 'r')
        self.__non_terminals = set(file.readline().strip().split(' '))
        self.__terminals = set(file.readline().strip().split(' '))
        self.__start_symbol = file.readline().strip()
        production_line = file.readline().strip()
        production_index = 1
        while production_line != "":
            left, right = production_line.split("->")
            left = left.strip()

            if len(left.split(" ")) > 1:
                self.__is_CFG = False

            right = [p.strip() for p in right.strip().split('|')]

            if left not in self.__productions:
                self.__productions[left] = []

            for index in range(len(right)):
                self.__productions[left].append(
                    (right[index], production_index))
                production_index += 1

            production_line = file.readline().strip()

    def get_productions_string(self):
        production_string = ""
        for p in self.__productions:
            production_string += p + ' -> ' + \
                ' | '.join([r[0] for r in self.__productions[p]]) + '\n'

        return production_string

    def get_productions_non_terminal(self, non_terminal):
        return self.__productions[non_terminal]

    def get_non_terminals(self):
        return self.__non_terminals
    
    def get_terminals(self):
        return self.__terminals
    
    def get_start_symbol(self):
        return self.__start_symbol
    
    def get_productions(self):
        return self.__productions

    def check_CFG(self):
        return self.__is_CFG

    def __str__(self):
        return "Non-terminals: " + ' '.join(self.__non_terminals) + "\n" + \
               "Terminals: " + ' '.join(self.__terminals) + "\n" + \
               "Start symbol: " + self.__start_symbol + "\n" + \
               "Productions:\n" + self.get_productions_string()


# g = Grammar("g1.txt")

# print(g.check_CFG())
# print(g.get_productions_non_terminal('A'))
# print(g)
