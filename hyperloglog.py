import hashlib
import math
import random

class HyperLogLog:
    def __init__(self, b=10):
        """
        b: número de bits para usar como índice do balde.
        Se b=10, teremos 2^10 = 1024 baldes.
        """
        self.b = b
        self.m = 1 << b  # Número de registros (baldes): 2^b
        self.registers = [0] * self.m # Array de inteiros (ocupa muito pouco espaço)
        
        # Constante de correção alpha (matemática pesada do paper original)
        # Serve para corrigir o viés da estimativa
        self.alpha = self._get_alpha(self.m)

    def _get_alpha(self, m):
        if m == 16: return 0.673
        if m == 32: return 0.697
        if m == 64: return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def _count_leading_zeros(self, val):
        """Conta quantos zeros existem antes do primeiro bit 1"""
        if val == 0: return 32 # Assumindo 32 bits de análise
        zeros = 0
        # Enquanto o bit mais à esquerda não for 1...
        # (1 << 31) cria um número com o bit 31 ligado: 1000...000
        while (val & (1 << 31)) == 0:
            zeros += 1
            val <<= 1 # Desloca para esquerda
        return zeros + 1

    def add(self, item):
        # 1. Cria o hash (SHA1 retorna 160 bits, usamos hex para facilitar)
        # Precisamos de determinismo, então não usamos hash() nativo do Python
        h = hashlib.sha1(str(item).encode('utf-8')).hexdigest()
        x = int(h, 16) # Converte para inteiro gigante
        
        # 2. Determinar o balde (Bucket Index)
        # Pegamos os primeiros 'b' bits para saber onde guardar
        j = x & (self.m - 1) 
        
        # 3. O valor para analisar (resto dos bits)
        w = x >> self.b 
        
        # 4. Contar zeros à esquerda do valor restante
        # Limitamos a 32 bits para simplificar a lógica
        zeros = self._count_leading_zeros(w & 0xFFFFFFFF)
        
        # 5. Guardamos apenas o MAIOR número de zeros visto neste balde
        self.registers[j] = max(self.registers[j], zeros)

    def count(self):
        """Calcula a estimativa usando a Média Harmônica"""
        # Fórmula: Z = Soma( 2^-M[j] )
        Z = sum(2.0 ** -reg for reg in self.registers)
        
        # Fórmula Final: E = alpha * m^2 / Z
        E = self.alpha * (self.m * self.m) / Z
        
        # Correção para pequenos conjuntos (Linear Counting)
        # Se E for pequeno, o HLL perde precisão, então usamos estatística de zeros
        if E <= 2.5 * self.m:
            V = self.registers.count(0) # Quantos baldes estão vazios?
            if V > 0:
                E = self.m * math.log(self.m / V)
                
        return int(E)

# --- Teste de Comparação ---
import sys

# Vamos simular 100.000 usuários únicos
total_items = 100_000
hll = HyperLogLog(b=12) # 4096 baldes
conjunto_real = set()

print(f"Inserindo {total_items} itens...")

for i in range(total_items):
    # Geramos dados aleatórios
    user_id = f"user_{random.randint(0, 10000000)}" 
    hll.add(user_id)
    conjunto_real.add(user_id) # O set guarda a verdade absoluta

# Resultados
real_count = len(conjunto_real)
hll_count = hll.count()
erro = abs(real_count - hll_count) / real_count * 100

print(f"\n--- Resultados ---")
print(f"Contagem Real (Set): {real_count}")
print(f"Estimativa HLL:      {hll_count}")
print(f"Erro:                {erro:.2f}%")

# Comparação de Memória
# sys.getsizeof nem sempre é preciso para objetos complexos, mas dá uma ideia
size_set = sys.getsizeof(conjunto_real) # Bytes (incompleto, pois não conta as strings dentro)
size_hll = sys.getsizeof(hll.registers) # Bytes (array de ints)

print(f"\n--- Comparação de Memória (Estimada) ---")
print(f"Memória do HLL (apenas os registros): ~{size_hll} bytes")
print(f"Memória do Set (apenas a estrutura):  ~{size_set} bytes")
print(f"O Set é no mínimo {size_set // size_hll}x maior (na prática é muito mais).")