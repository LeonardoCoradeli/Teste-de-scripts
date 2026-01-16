import os
import time
import glob

class LSMTree:
    def __init__(self, memtable_limit=3, data_dir="lsm_data"):
        self.memtable = {} # Simula a memória RAM
        self.limit = memtable_limit # Limite pequeno para forçar o flush logo
        self.data_dir = data_dir
        self.sstables = [] # Lista com nomes dos arquivos no disco
        
        # Prepara o diretório "disco"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        else:
            # Limpa execuções anteriores
            files = glob.glob(f"{data_dir}/*.txt")
            for f in files: os.remove(f)

    def put(self, key, value):
        """Escrita: O(1) - Só insere na memória"""
        self.memtable[key] = value
        
        # Se encheu a memória, despeja no disco
        if len(self.memtable) >= self.limit:
            self.flush()

    def flush(self):
        """Transforma MemTable em SSTable (Arquivo Imutável)"""
        if not self.memtable:
            return

        # 1. Gera nome único para o arquivo (timestamp)
        filename = os.path.join(self.data_dir, f"segment_{int(time.time()*1000)}.txt")
        
        # 2. Ordena as chaves (Crucial para a SSTable!)
        # Em bancos reais a MemTable já é mantida ordenada (ex: SkipList)
        sorted_items = sorted(self.memtable.items())
        
        # 3. Escrita Sequencial no Disco (Isso é o que faz o LSM ser rápido)
        with open(filename, "w") as f:
            for k, v in sorted_items:
                f.write(f"{k}:{v}\n")
        
        self.sstables.append(filename)
        self.memtable.clear() # Limpa a memória
        print(f"[DISK IO] Flush realizado! Criado {filename}")

    def get(self, key):
        """Leitura: Memória -> Disco (Mais recente -> Mais antigo)"""
        
        # 1. Verifica na MemTable (RAM)
        if key in self.memtable:
            print(f"Chave '{key}' encontrada na Memória.")
            return self.memtable[key]
        
        # 2. Verifica nas SSTables (Disco), do mais novo para o mais velho
        # O 'reversed' é importante: queremos a versão mais atual do dado
        for filename in reversed(self.sstables):
            val = self._search_in_file(filename, key)
            if val:
                print(f"Chave '{key}' encontrada no arquivo {filename}.")
                return val
        
        return None

    def _search_in_file(self, filename, target_key):
        """
        Simula a busca no disco.
        Nota: Em produção, usaríamos um Índice Esparso ou Bloom Filter aqui
        para não ler o arquivo todo.
        """
        try:
            with open(filename, "r") as f:
                for line in f:
                    k, v = line.strip().split(":")
                    if k == target_key:
                        return v
        except FileNotFoundError:
            return None
        return None

    def compact(self):
        """
        Compactação (Merge): Junta todos os arquivos pequenos em um grande.
        Remove duplicatas mantendo apenas a versão mais recente.
        """
        print("\n--- Iniciando Compactação ---")
        full_data = {}
        
        # Lemos os arquivos do MAIS ANTIGO para o MAIS NOVO.
        # Assim, o dado mais novo sobrescreve o antigo no dicionário.
        for filename in self.sstables:
            with open(filename, "r") as f:
                for line in f:
                    k, v = line.strip().split(":")
                    full_data[k] = v # Sobrescreve se já existir
        
        # Remove os arquivos velhos do disco
        for filename in self.sstables:
            os.remove(filename)
        
        self.sstables = []
        
        # Escreve o arquivo compactado único
        # Colocamos os dados na memtable e forçamos um flush
        self.memtable = full_data
        print(f"Compactado {len(full_data)} chaves únicas.")
        self.flush() # Cria o novo arquivo consolidado

# --- Teste de Fogo ---

db = LSMTree(memtable_limit=3)

print("1. Inserindo dados (A, B, C)...")
db.put("user1", "João")
db.put("user2", "Maria")
db.put("user3", "Pedro") # Aqui deve ocorrer o primeiro Flush

print("2. Inserindo mais dados e atualizando (A, D, E)...")
db.put("user1", "João Silva") # Atualização! (User1 agora tem novo valor)
db.put("user4", "Ana")
db.put("user5", "Carlos") # Segundo Flush

# Visualizar o estado atual
print(f"\nArquivos no disco: {db.sstables}")

# Buscas
print("\n3. Buscando dados:")
print(f"Busca user1: {db.get('user1')}") # Deve pegar do SEGUNDO arquivo (João Silva)
print(f"Busca user2: {db.get('user2')}") # Deve pegar do PRIMEIRO arquivo (Maria)

# Compactação
db.compact()

print(f"\nArquivos no disco pós-compactação: {db.sstables}")
# Se você abrir a pasta 'lsm_data', verá apenas um arquivo agora,
# e nele 'user1' será 'João Silva', e não haverá duplicatas.