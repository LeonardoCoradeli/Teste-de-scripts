import random

# ==============================================================================
# 1. Classes Geométricas Básicas
# ==============================================================================

class Point:
    """Representa um ponto (x, y) e seus dados (ex: 'Motorista A')"""
    def __init__(self, x, y, data=None):
        self.x = x
        self.y = y
        self.data = data

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f}) data='{self.data}'"

class Rectangle:
    """
    Define uma área retangular.
    Importante: x e y são o CENTRO do retângulo.
    w e h são a METADE da largura e altura (raio do centro até a borda).
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, point):
        """Verifica se um ponto está dentro deste retângulo"""
        return (point.x >= self.x - self.w and
                point.x <= self.x + self.w and
                point.y >= self.y - self.h and
                point.y <= self.y + self.h)

    def intersects(self, other):
        """
        Verifica se este retângulo se sobrepõe a outro (usado na busca).
        Lógica: Se um está totalmente à esquerda, direita, cima ou baixo do outro,
        eles NÃO se tocam. Caso contrário, se tocam.
        """
        return not (other.x - other.w > self.x + self.w or  # Outro está à direita
                    other.x + other.w < self.x - self.w or  # Outro está à esquerda
                    other.y - other.h > self.y + self.h or  # Outro está abaixo
                    other.y + other.h < self.y - self.h)    # Outro está acima

# ==============================================================================
# 2. A Estrutura QuadTree
# ==============================================================================

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary # Objeto Rectangle (limites deste nó)
        self.capacity = capacity # Máximo de pontos antes de subdividir
        self.points = []         # Lista de Points neste nó
        self.divided = False     # Flag para saber se tem filhos
        
        # Filhos (Noroeste, Nordeste, Sudoeste, Sudeste)
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

    def subdivide(self):
        """Divide o retângulo atual em 4 quadrantes menores"""
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w
        h = self.boundary.h

        # Cria 4 retângulos filhos com metade do tamanho
        # nw = North West (Noroeste), etc.
        nw_rect = Rectangle(x - w/2, y - h/2, w/2, h/2)
        ne_rect = Rectangle(x + w/2, y - h/2, w/2, h/2)
        sw_rect = Rectangle(x - w/2, y + h/2, w/2, h/2)
        se_rect = Rectangle(x + w/2, y + h/2, w/2, h/2)

        self.nw = QuadTree(nw_rect, self.capacity)
        self.ne = QuadTree(ne_rect, self.capacity)
        self.sw = QuadTree(sw_rect, self.capacity)
        self.se = QuadTree(se_rect, self.capacity)
        
        self.divided = True

    def insert(self, point):
        """Insere um ponto na árvore (recursivo)"""
        
        # 1. Se o ponto não está dentro dos limites deste nó, ignora
        if not self.boundary.contains(point):
            return False

        # 2. Se há espaço neste nó e ele não está dividido, adiciona aqui
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        # 3. Se encheu, divide (se ainda não dividiu)
        if not self.divided:
            self.subdivide()

        # 4. Tenta empurrar o ponto para um dos filhos
        if self.nw.insert(point): return True
        if self.ne.insert(point): return True
        if self.sw.insert(point): return True
        if self.se.insert(point): return True

        # (Teoricamente inalcançável se contains() funcionar bem)
        return False

    def query(self, range_rect, found=None):
        """Busca todos os pontos dentro de uma área (range_rect)"""
        if found is None:
            found = []

        # Otimização Fundamental:
        # Se a área de busca nem encosta neste quadrante, aborta aqui mesmo!
        if not self.boundary.intersects(range_rect):
            return found

        # Verifica os pontos armazenados neste nó
        for p in self.points:
            if range_rect.contains(p):
                found.append(p)

        # Se tiver filhos, continua a busca recursivamente
        if self.divided:
            self.nw.query(range_rect, found)
            self.ne.query(range_rect, found)
            self.sw.query(range_rect, found)
            self.se.query(range_rect, found)

        return found

# ==============================================================================
# 3. Teste Prático (O Radar)
# ==============================================================================

if __name__ == "__main__":
    # --- Configuração do Mundo ---
    # Mundo de 400x400 (Centro em 200,200 com raio de 200)
    world_boundary = Rectangle(200, 200, 200, 200)
    
    # Capacidade baixa (4) para forçar muitas subdivisões e testar a árvore
    qt = QuadTree(world_boundary, capacity=4)

    # --- 1. Inserção de Dados ---
    print("--- Inserindo 200 Pontos Aleatórios ---")
    points_to_insert = 200
    for i in range(points_to_insert):
        # Gera pontos aleatórios entre 0 e 400
        x = random.uniform(0, 400)
        y = random.uniform(0, 400)
        p = Point(x, y, data=f"Objeto {i}")
        qt.insert(p)
    print("Pontos inseridos com sucesso.\n")

    # --- 2. Simulação de Busca (Radar) ---
    # Vamos buscar pontos numa área específica:
    # Centro em (100, 100), com largura total 40x40 (raio 20)
    radar_x, radar_y = 100, 100
    radar_w, radar_h = 20, 20
    
    search_range = Rectangle(radar_x, radar_y, radar_w, radar_h)
    
    print(f"--- Buscando objetos na área: Centro({radar_x}, {radar_y}) +/- ({radar_w}, {radar_h}) ---")
    
    found_points = qt.query(search_range)

    # --- 3. Resultados ---
    print(f"Total encontrado: {len(found_points)}")
    
    if found_points:
        print("\nLista dos objetos encontrados:")
        for p in found_points:
            print(f" - {p.data} em ({p.x:.2f}, {p.y:.2f})")
    else:
        print("Nenhum objeto encontrado nesta área.")

    # Verificação visual da eficiência
    # Se você quiser testar manualmente se funcionou:
    # Todos os pontos printados devem ter X entre 80-120 e Y entre 80-120
    print("\nVerificação:")
    for p in found_points:
        valid_x = (radar_x - radar_w) <= p.x <= (radar_x + radar_w)
        valid_y = (radar_y - radar_h) <= p.y <= (radar_y + radar_h)
        if not (valid_x and valid_y):
            print(f"ERRO: Ponto fora da área encontrado! {p}")
            break
    else:
        print("Todos os pontos encontrados estão validamente dentro da área de busca.")