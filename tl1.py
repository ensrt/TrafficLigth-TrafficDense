import osmnx as ox
import networkx as nx
import pygame
import random
import time

center_point = (40.759348, 30.363582)  # İstanbul'un merkezine yakın bir koordinat
radius = 1250  # 1250 metre

# Harita ayarları (tüm yollar için)
graph = ox.graph_from_point(center_point, dist=radius, network_type='all')

# Yalnızca en büyük bağlı bileşeni seç
graph = ox.truncate.largest_component(graph)

# Trafik ışıklarını çek
traffic_signals = [node for node, data in graph.nodes(data=True) if 'highway' in data and data['highway'] == 'traffic_signals']

# Trafik ışığı sayısını kontrol et
print(f"Number of traffic lights found: {len(traffic_signals)}")

# Pygame ayarları
pygame.init()  # Pygame'i başlat
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Trafik Simülasyonu")

# Renk tanımları
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Haritadaki düğümleri pygame koordinatlarına ölçeklendirme
def scale_coordinates(coord, min_val, max_val, screen_size):
    return int((coord - min_val) / (max_val - min_val) * screen_size)

# Düğüm koordinatlarının minimum ve maksimum değerlerini hesapla
nodes = list(graph.nodes(data=True))
min_x = min(node[1]['x'] for node in nodes)
max_x = max(node[1]['x'] for node in nodes)
min_y = min(node[1]['y'] for node in nodes)
max_y = max(node[1]['y'] for node in nodes)

# Düğüm koordinatlarını ölçekle
node_positions = {}
for node in nodes:
    x = node[1]['x']
    y = node[1]['y']
    node_positions[node[0]] = (
        scale_coordinates(x, min_x, max_x, screen_size[0]),
        scale_coordinates(y, min_y, max_y, screen_size[1])
    )

# Trafik ışığı sınıfı
class TrafficLight:
    def __init__(self, position, red_duration=10, green_duration=10):
        self.position = position
        self.state = "red"  # İlk durumda kırmızı
        self.timer = 0
        self.red_duration = red_duration  # Kırmızı ışık süresi
        self.green_duration = green_duration  # Yeşil ışık süresi

    def update(self):
        self.timer += 1
        # Süreye göre ışık değiştir
        if self.state == "red" and self.timer >= self.red_duration:
            self.state = "green"
            self.timer = 0
        elif self.state == "green" and self.timer >= self.green_duration:
            self.state = "red"
            self.timer = 0

    def is_green(self):
        return self.state == "green"

# Ajan sınıfı (Araçlar)
# Ajan sınıfı (Araçlar)
class Agent:
    def __init__(self, graph):
        self.graph = graph
        self.position = random.choice(list(graph.nodes))
        self.path = None
        self.speed = random.uniform(1, 2)  # Hız başlangıçta rastgele

    def move(self):
        if not self.path:
            while True:
                # Rastgele bir hedef düğüm seç
                target = random.choice(list(self.graph.nodes))
                try:
                    # Hedefe giden en kısa yolu bul ve mesafeyi kontrol et
                    path_length = nx.shortest_path_length(self.graph, self.position, target)
                    if path_length >= 150:  # 50 düğümden uzun bir yol bulduğumuzda ilerleriz
                        self.path = nx.shortest_path(self.graph, self.position, target)
                        break
                except nx.NetworkXNoPath:
                    continue
        
        if len(self.path) > 1:
            # Sonraki düğüme hareket et
            next_position = self.path[1]

            # Eğer trafik ışığında durması gerekiyorsa dur
            if next_position in traffic_signal_dict and not traffic_signal_dict[next_position].is_green():
                return  # Hareket etme

            # Ajanı bir düğüme taşı
            self.position = next_position
            self.path.pop(0)

    def __init__(self, graph):
        self.graph = graph
        self.position = random.choice(list(graph.nodes))
        self.path = None
        self.speed = random.uniform(1, 2)  # Hız başlangıçta rastgele

    def move(self):
        if not self.path:
            while True:
                # Rastgele bir hedef düğüm seç
                target = random.choice(list(self.graph.nodes))
                try:
                    # Hedefe giden en kısa yolu bul
                    self.path = nx.shortest_path(self.graph, self.position, target)
                    break
                except nx.NetworkXNoPath:
                    continue
        
        if len(self.path) > 1:
            # Sonraki düğüme hareket et
            next_position = self.path[1]

            # Eğer trafik ışığında durması gerekiyorsa dur
            if next_position in traffic_signal_dict and not traffic_signal_dict[next_position].is_green():
                return  # Hareket etme

            # Ajanı bir düğüme taşı
            self.position = next_position
            self.path.pop(0)

# Trafik yoğunluğunu tutan bir veri yapısı
def reset_traffic_density():
    return {edge: 0 for edge in graph.edges(keys=True)}

traffic_density = reset_traffic_density()

# Trafik ışıklarını oluşturalım
traffic_signal_dict = {}
for signal in traffic_signals:
    traffic_signal_dict[signal] = TrafficLight(signal, red_duration=15, green_duration=15)  # Örnek: 15 saniye kırmızı, 15 saniye yeşil

# Ajanları oluştur
agents = [Agent(graph) for _ in range(550)]  # 550 ajan oluştur

# İlk aşama: Trafik ışığı olmadan simülasyon
def run_simulation(with_traffic_lights):
    running = True
    clock = pygame.time.Clock()
    traffic_density = reset_traffic_density()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Çıkış olayını işleyip döngüyü bitir

        screen.fill(WHITE)

        # Harita kenarlarını çiz (yoğunluklara göre renk)
        for edge, count in traffic_density.items():
            start_pos = node_positions[edge[0]]
            end_pos = node_positions[edge[1]]
            # Trafik yoğunluğuna göre renk belirle
            if count < 5:
                edge_color = GREEN
            elif count < 15:
                edge_color = YELLOW
            else:
                edge_color = RED
            pygame.draw.line(screen, edge_color, start_pos, end_pos, 3)

        # Trafik ışıklarını çiz ve güncelle (eğer varsa)
        if with_traffic_lights:
            for signal in traffic_signal_dict.values():
                signal.update()
                x, y = node_positions[signal.position]
                # Trafik ışığının durumuna göre renk belirle
                color = GREEN if signal.is_green() else RED
                pygame.draw.circle(screen, color, (x, y), 10)  # Trafik ışığını göster

        # Ajanları güncelle ve çiz
        for agent in agents:
            # Ajanın şu anki konumunu çiz (mavi noktalar)
            x, y = node_positions[agent.position]
            pygame.draw.circle(screen, BLUE, (x, y), 3)
            
            # Bir sonraki düğüme hareket et
            agent.move()

            # Trafik yoğunluğunu güncelle
            if len(agent.path) > 1:
                edge = (agent.position, agent.path[1], 0)
                if edge in traffic_density:
                    traffic_density[edge] += 1

        # Ekranı güncelle
        pygame.display.flip()
        clock.tick(10)  # Simülasyon hızını ayarlar

    return traffic_density

# Ajanları yeniden oluştur (ikinci simülasyon için)
def reset_agents():
    return [Agent(graph) for _ in range(550)]  # Ajanları baştan oluştur

# İlk aşama: Trafik ışıkları olmadan
print("Trafik ışıkları olmadan simülasyon başlıyor...")
initial_traffic_density = run_simulation(with_traffic_lights=False)

# Yoğun bölgelere trafik ışıkları ekleyelim
sorted_edges = sorted(initial_traffic_density.items(), key=lambda item: item[1], reverse=True)
top_traffic_nodes = set()

# En yoğun kenarların düğümlerine trafik ışığı ekle
for edge, _ in sorted_edges[:15]:  # En yoğun 15 kenarı seç
    top_traffic_nodes.add(edge[0])
    top_traffic_nodes.add(edge[1])

for node in top_traffic_nodes:
    traffic_signal_dict[node] = TrafficLight(node)

# İkinci simülasyon öncesinde ajanları sıfırlıyoruz
agents = reset_agents()

# İkinci aşama: Trafik ışıkları ile
print("Trafik ışıkları ile simülasyon başlıyor...")
final_traffic_density = run_simulation(with_traffic_lights=True)

# Pygame'i düzgün bir şekilde kapat
pygame.quit()

# Sonuçları karşılaştır
# Sonuçları karşılaştır ve yüzde farkını hesapla
def compare_densities(initial, final):
    initial_total = sum(initial.values())  # Trafik ışıksız toplam yoğunluk
    final_total = sum(final.get(edge, 0) for edge in initial)  # Trafik ışıklı toplam yoğunluk (her iki simülasyondaki ortak kenarlar için)
    
    # Yüzde farkını hesapla
    if initial_total > 0:  # Bölme hatalarını önlemek için
        improvement_percentage = ((initial_total - final_total) / initial_total) * 100
    else:
        improvement_percentage = 0

    print(f"Trafik ışıksız toplam yoğunluk: {initial_total}")
    print(f"Trafik ışıklı toplam yoğunluk: {final_total}")
    print(f"Trafik ışıkları ile yoğunluk yüzde {improvement_percentage:.2f} oranında azaldı.")

# Trafik yoğunluklarını karşılaştır ve sonuçları yazdır
compare_densities(initial_traffic_density, final_traffic_density)