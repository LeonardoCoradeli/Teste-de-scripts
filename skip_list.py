import random

class SkipNode:
    def __init__(self, key, level):
        self.key = key
        # Lista de ponteiros para o próximo nó em cada nível
        # forward[0] é o next padrão, forward[1] é o pulo maior, etc.
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level=4, p=0.5):
        self.MAX_LEVEL = max_level # Altura máxima da torre
        self.P = p # Probabilidade de subir de nível (cara ou coroa)
        self.header = SkipNode(-1, self.MAX_LEVEL) # Nó sentinela inicial
        self.level = 0 # Nível atual mais alto da lista

    def random_level(self):
        """Decide aleatoriamente a altura do novo nó"""
        lvl = 0
        while random.random() < self.P and lvl < self.MAX_LEVEL:
            lvl += 1
        return lvl

    def insert(self, key):
        update = [None] * (self.MAX_LEVEL + 1)
        current = self.header

        # 1. Encontrar a posição de inserção (descendo os níveis)
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current # Guarda o caminho para atualizar ponteiros depois

        # 2. Criar o nó e decidir seu nível
        lvl = self.random_level()

        # Se o novo nível for maior que o atual da lista, atualiza o header
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.header
            self.level = lvl

        # 3. Inserir o nó e ajustar ponteiros
        new_node = SkipNode(key, lvl)
        for i in range(lvl + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
            
        print(f"Inserido {key} com nível {lvl}")

    def search(self, key):
        """Busca otimizada: O(log n)"""
        current = self.header
        
        # Começa do topo e vai descendo
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
        
        # Chegou no nível 0, verifica o próximo
        current = current.forward[0]
        
        if current and current.key == key:
            return True
        return False

    def display(self):
        """Visualização das camadas"""
        print("\nVisualização da Skip List:")
        for i in range(self.level, -1, -1):
            current = self.header.forward[i]
            line = f"Nível {i}: "
            while current:
                line += f"{current.key} -> "
                current = current.forward[i]
            print(line + "None")

# --- Teste ---
print("\n--- Skip List ---")
sl = SkipList(max_level=3)

# Inserindo números ordenados (pior caso para lista normal, ok para Skip List)
for num in [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]:
    sl.insert(num)

sl.display()

print(f"\nBusca pelo 19: {sl.search(19)}") # Deve ser True
print(f"Busca pelo 99: {sl.search(99)}") # Deve ser False