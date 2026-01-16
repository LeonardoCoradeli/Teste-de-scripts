class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # O "ponteiro" para o próximo nó

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        """Adiciona ao final da lista"""
        new_node = Node(data)
        
        # Se a lista estiver vazia, o novo nó é a cabeça
        if not self.head:
            self.head = new_node
            return
        
        # Se não, percorre até o último nó
        current = self.head
        while current.next:
            current = current.next
        
        current.next = new_node

    def display(self):
        """Mostra a lista visualmente"""
        elems = []
        current = self.head
        while current:
            elems.append(str(current.data))
            current = current.next
        print(" -> ".join(elems) + " -> None")

    def search(self, target):
        """Busca linear: O(n)"""
        current = self.head
        while current:
            if current.data == target:
                return True
            current = current.next
        return False

# --- Teste ---
print("--- Lista Encadeada Simples ---")
ll = LinkedList()
ll.append(10)
ll.append(20)
ll.append(30)
ll.display() # 10 -> 20 -> 30 -> None