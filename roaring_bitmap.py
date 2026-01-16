import array

# Constante Mágica: O ponto de equilíbrio
# Um short (2 bytes) * 4096 = 8192 bytes (8KB)
# Um bitmap de 65536 bits / 8 = 8192 bytes (8KB)
THRESHOLD = 4096 

class Container:
    """Classe base abstrata para os containers"""
    def add(self, val): pass
    def contains(self, val): pass
    def get_type(self): pass

class ArrayContainer(Container):
    """Guarda dados como uma lista ordenada de shorts (inteiros de 16 bits)"""
    def __init__(self):
        # 'H' no array do python significa unsigned short (2 bytes)
        self.content = array.array('H') 

    def add(self, val):
        # Mantém ordenado para permitir busca binária (bisect)
        # Em Python, para simplificar, usaremos verificação linear/in na inserção
        # mas em C/Java isso é inserção ordenada.
        if val not in self.content:
            self.content.append(val)
            # Em produção, manteríamos ordenado a cada insert, 
            # aqui ordenamos apenas para manter a lógica correta se necessário
            # mas arrays Python são flexíveis.
            
    def contains(self, val):
        return val in self.content
    
    def size(self):
        return len(self.content)
    
    def to_bitmap(self):
        """Converte este container para um BitmapContainer"""
        bc = BitmapContainer()
        for val in self.content:
            bc.add(val)
        return bc
    
    def get_type(self):
        return "Array"

class BitmapContainer(Container):
    """Guarda dados como um mapa de bits de 65536 posições"""
    def __init__(self):
        # Em Python, um inteiro tem precisão arbitrária, então funciona como bitset infinito.
        # Na prática (C/Java), isso seria um array de longs fixo de 1024 posições (1024 * 64 bits = 65536)
        self.bitmap = 0
        self.cardinality = 0 # Contador manual de bits ligados

    def add(self, val):
        # Verifica se o bit já está ligado
        if not (self.bitmap & (1 << val)):
            self.bitmap |= (1 << val)
            self.cardinality += 1

    def contains(self, val):
        return (self.bitmap & (1 << val)) > 0
    
    def size(self):
        return self.cardinality
    
    def get_type(self):
        return "Bitmap"

class RoaringBitmap:
    def __init__(self):
        # Dicionário que mapeia os 16 bits superiores (Chave) -> Container
        self.containers = {}

    def add(self, number):
        # 1. Separar High (chave do container) e Low (valor dentro do container)
        # High: desloca 16 bits para a direita
        high = number >> 16
        # Low: pega os últimos 16 bits (máscara 0xFFFF)
        low = number & 0xFFFF

        # 2. Se o container não existe, cria um ArrayContainer (padrão inicial)
        if high not in self.containers:
            self.containers[high] = ArrayContainer()

        container = self.containers[high]
        
        # 3. Adiciona o valor
        container.add(low)

        # 4. A Mágica: Verifica se precisa fazer "Upgrade" do container
        if isinstance(container, ArrayContainer):
            if container.size() > THRESHOLD:
                print(f"[Roaring] Container {high} atingiu {container.size()} itens. Convertendo para Bitmap...")
                # Substitui o objeto Array pelo objeto Bitmap
                self.containers[high] = container.to_bitmap()

    def contains(self, number):
        high = number >> 16
        low = number & 0xFFFF
        
        if high not in self.containers:
            return False
        
        return self.containers[high].contains(low)

    def stats(self):
        print("\n--- Estatísticas do Roaring Bitmap ---")
        for key, cont in self.containers.items():
            print(f"Container ID {key}: Tipo={cont.get_type()}, Itens={cont.size()}")

# --- Testando a Mágica ---

rb = RoaringBitmap()

# 1. Caso Esparso (Array Container)
# Vamos adicionar IDs distantes: 1, 100, 200...
print("Adicionando dados esparsos no container 0...")
for i in range(10):
    rb.add(i * 100)

# 2. Caso Denso (Transição para Bitmap Container)
# Vamos forçar o container ID 5 a encher
print("\nEnchendo o Container 5 com 5000 itens...")
# Para cair no container 5 (High bits = 5), precisamos somar (5 << 16)
base = 5 << 16 
for i in range(4100): # 4100 itens deve estourar o limite de 4096
    rb.add(base + i)

# 3. Teste de Busca
print(f"\nBusca ID {base + 100}: {rb.contains(base + 100)}") # Deve ser True
print(f"Busca ID {base + 9999}: {rb.contains(base + 9999)}") # Deve ser False

# 4. Verificação Interna
rb.stats()