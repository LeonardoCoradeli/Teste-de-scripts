import math
import hashlib

class BloomFilter:
    def __init__(self, expected_items, error_rate=0.01):
        """
        expected_items (n): Quantos itens você planeja inserir.
        error_rate (p): Chance aceitável de falso positivo (ex: 0.01 = 1%).
        """
        self.capacity = expected_items
        
        # 1. Matemática para definir o tamanho ideal do array de bits (m)
        # Fórmula: m = -(n * ln(p)) / (ln(2)^2)
        self.size_in_bits = int(-(expected_items * math.log(error_rate)) / (math.log(2) ** 2))
        
        # 2. Matemática para definir o número ideal de hashes (k)
        # Fórmula: k = (m / n) * ln(2)
        self.hash_count = int((self.size_in_bits / expected_items) * math.log(2))
        
        # Criando o array de bytes. Como cada byte tem 8 bits, dividimos por 8.
        # Usamos bytearray para economizar memória (melhor que listas).
        self.bit_array = bytearray(math.ceil(self.size_in_bits / 8))
        
        print(f"--- Bloom Filter Criado ---")
        print(f"Capacidade: {self.capacity} itens")
        print(f"Tamanho na memória: {self.size_in_bits} bits ({len(self.bit_array)} bytes)")
        print(f"Número de Hashes (k): {self.hash_count}")
        print(f"Chance de Falso Positivo: {error_rate * 100}%\n")

    def _get_hashes(self, item):
        """
        Gera 'k' índices baseados no item usando Double Hashing.
        """
        item_str = str(item).encode('utf-8')
        
        # Usamos duas funções hash robustas da lib padrão
        # MD5 e SHA1 são rápidos o suficiente para isso
        h1 = int(hashlib.md5(item_str).hexdigest(), 16)
        h2 = int(hashlib.sha1(item_str).hexdigest(), 16)
        
        indices = []
        for i in range(self.hash_count):
            # A mágica do Double Hashing para simular k funções
            idx = (h1 + i * h2) % self.size_in_bits
            indices.append(idx)
        return indices

    def add(self, item):
        """Adiciona um item ao filtro"""
        for index in self._get_hashes(item):
            # Matemática de Bits:
            byte_index = index // 8  # Em qual byte está?
            bit_offset = index % 8   # Qual bit dentro do byte (0-7)?
            
            # Operador OR (|) para ligar o bit
            self.bit_array[byte_index] |= (1 << bit_offset)

    def check(self, item):
        """
        Verifica se o item existe.
        Retorna True: "Talvez exista" (Falso Positivo possível)
        Retorna False: "Com certeza NÃO existe" (100% confiável)
        """
        for index in self._get_hashes(item):
            byte_index = index // 8
            bit_offset = index % 8
            
            # Operador AND (&) para verificar se o bit está ligado
            if not (self.bit_array[byte_index] & (1 << bit_offset)):
                return False # Se um dos bits for 0, o item nunca foi inserido.
        
        return True

# --- Testando a Implementação ---

# Vamos criar um filtro para guardar e-mails suspeitos
# Esperamos 20 itens, com erro de 5%
bf = BloomFilter(expected_items=20, error_rate=0.05)

suspeitos = ["hacker@bad.com", "spam@marketing.com", "virus@trojan.exe"]

# 1. Adicionando itens
print("Adicionando itens...")
for s in suspeitos:
    bf.add(s)

# 2. Testando itens que existem
print(f"Check 'hacker@bad.com': {bf.check('hacker@bad.com')}") # Deve ser True

# 3. Testando itens que NÃO existem
print(f"Check 'usuario@gmail.com': {bf.check('usuario@gmail.com')}") # Deve ser False

# 4. Demonstração visual (bits ligados)
# Vamos ver os primeiros 20 bytes para ver os bits '1' espalhados
print(f"\nEstado parcial da memória (bits ligados):")
bits_visuais = ""
for byte in bf.bit_array[:5]: # Pegando só os primeiros 5 bytes para não poluir
    bits_visuais += format(byte, '08b') + " "
print(bits_visuais + "...")