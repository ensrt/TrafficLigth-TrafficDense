import osmnx as ox
import networkx as nx
import pygame
import random
import numpy as np

# Simülasyon ve trafik grafiği oluşturma
center_point = (40.759348, 30.363582)  # Serdivan'a yakın bir koordinat
radius = 1250  # 1250 metre
graph = ox.graph_from_point(center_point, dist=radius, network_type='all')
graph = ox.truncate.largest_component(graph)

# Trafik yoğunluğu hesaplayıcı
def calculate_traffic_density(agents):
    traffic_density = reset_traffic_density()
    for agent in agents:
        if agent.path and len(agent.path) > 1:
            edge = (agent.position, agent.path[1], 0)
            if edge in traffic_density:
                traffic_density[edge] += 1
    return sum(traffic_density.values())

# RL Parametreleri
alpha = 0.1  # Öğrenme hızı
gamma = 0.9  # İndirim faktörü
epsilon = 0.1  # Epsilon-greedy araştırma/sömürü oranı
episodes = 500_000  # Episode sayısı

# Trafik ışıklarının yoğunluğu azaltıp azaltmadığına bağlı olarak ödül fonksiyonu
def reward_function(initial_density, final_density):
    if final_density < initial_density:
        reward = (initial_density - final_density) / initial_density * 100  # Yüzde ödül
    else:
        reward = -10  # Trafik artarsa ceza
    return reward

# Q-learning yapısı
Q_table = {}  # Q tablosunu başlangıçta boş olarak başlatıyoruz

# Trafik yoğunluğu sıfırlama
def reset_traffic_density():
    return {edge: 0 for edge in graph.edges(keys=True)}

# Trafik ışıklarını rastgele koymak için aday kenarları belirliyoruz
def get_random_light_locations():
    return random.sample(list(graph.nodes), 15)  # 15 rastgele düğüm seçiyoruz

# Ajan sınıfı (Araçlar)
class Agent:
    def __init__(self, graph):
        self.graph = graph
        self.position = random.choice(list(graph.nodes))
        self.path = None
        self.speed = random.uniform(1, 2)

    def move(self):
        if not self.path:
            while True:
                target = random.choice(list(self.graph.nodes))
                try:
                    self.path = nx.shortest_path(self.graph, self.position, target)
                    break
                except nx.NetworkXNoPath:
                    continue
        
        if len(self.path) > 1:
            next_position = self.path[1]
            self.position = next_position
            self.path.pop(0)

# Trafik ışıklarını simüle eden RL ajanı
def run_rl_simulation(traffic_lights):
    agents = [Agent(graph) for _ in range(550)]  # Ajan oluştur
    initial_density = calculate_traffic_density(agents)  # Başlangıç yoğunluğu
    final_density = calculate_traffic_density(agents)  # Trafik ışıklarıyla oluşan yoğunluk
    return initial_density, final_density

# Q-learning döngüsü
for episode in range(episodes):
    # Trafik ışıkları için rastgele bir state (durum) seç
    current_state = tuple(get_random_light_locations())

    # Q-table girişlerini kontrol et, yoksa başlat
    if current_state not in Q_table:
        Q_table[current_state] = np.zeros(2)  # İki aksiyon: 0 = ışık koyma, 1 = ışık koyma
    
    # Epsilon-greedy strateji
    if random.uniform(0, 1) < epsilon:
        action = random.choice([0, 1])  # Rastgele aksiyon
    else:
        action = np.argmax(Q_table[current_state])  # En iyi aksiyonu seç
    
    # Simülasyonu aksiyona göre çalıştır
    initial_density, final_density = run_rl_simulation(current_state)

    # Ödül hesapla
    reward = reward_function(14596, final_density)  # Sabit trafik ışığı olmadan yoğunluk = 14596
    
    # Q-learning güncelleme
    next_state = tuple(get_random_light_locations())  # Bir sonraki rastgele durum
    if next_state not in Q_table:
        Q_table[next_state] = np.zeros(2)  # İki aksiyon
    best_next_action = np.argmax(Q_table[next_state])

    Q_table[current_state][action] += alpha * (reward + gamma * Q_table[next_state][best_next_action] - Q_table[current_state][action])

    if episode % 1000 == 0:
        print(f"Episode: {episode}, Reward: {reward}")

# En iyi ışık yerleşimlerini bul ve göster
best_state = max(Q_table, key=lambda state: np.max(Q_table[state]))
print(f"En iyi trafik ışığı yerleşimleri: {best_state}")
