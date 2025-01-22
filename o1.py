import osmnx as ox
import networkx as nx
import pygame
import random
import time
import threading
from queue import Queue

# Harita merkezi ve yarıçapı
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

# Renk tanımları
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Haritadaki düğümleri pygame koordinatlarına ölçeklendirme
def scale_coordinates(coord, min_val, max_val, screen_size):
    if max_val - min_val == 0:
        return screen_size // 2
    return int((coord - min_val) / (max_val - min_val) * screen_size)

# Düğüm koordinatlarının minimum ve maksimum değerlerini hesapla
nodes = list(graph.nodes(data=True))
min_x = min(node[1]['x'] for node in nodes)
max_x = max(node[1]['x'] for node in nodes)
min_y = min(node[1]['y'] for node in nodes)
max_y = max(node[1]['y'] for node in nodes)

# Ekran boyutu
SCREEN_SIZE = 800

# Düğüm koordinatlarını ölçekle
node_positions = {}
for node in nodes:
    x = node[1]['x']
    y = node[1]['y']
    node_positions[node[0]] = (
        scale_coordinates(x, min_x, max_x, SCREEN_SIZE),
        scale_coordinates(y, min_y, max_y, SCREEN_SIZE)
    )

# Trafik ışığı sınıfı
class TrafficLight:
    def __init__(self, position):
        self.position = position
        self.state = "red"  # Başlangıçta kırmızı
        self.timer = 0

    def update(self):
        # RL tarafından kontrol edileceği için burada zamanlayıcı kullanmıyoruz
        pass

    def is_green(self):
        return self.state == "green"

# Ajan sınıfı (Araçlar)
class Agent:
    def __init__(self, graph):
        self.graph = graph
        self.position = random.choice(list(graph.nodes))
        self.path = None
        self.speed = random.uniform(1, 2)
        self.pos = node_positions[self.position]
        self.target_node = None
        self.reached = False  # Hedefe ulaşıp ulaşmadığını takip eder
        self.stuck_steps = 0  # Aracın hareket edip etmediğini takip eder

    def move(self):
        if self.reached:
            return  # Hedefe ulaştıysa hareket etmez

        if not self.path:
            while True:
                self.target_node = random.choice(list(self.graph.nodes))
                if self.target_node == self.position:
                    continue  # Aynı düğüm seçilmemesi için
                try:
                    self.path = nx.shortest_path(self.graph, self.position, self.target_node)
                    break
                except nx.NetworkXNoPath:
                    continue

        if len(self.path) > 1:
            next_node = self.path[1]
            next_pos = node_positions[next_node]

            # Trafik ışığı kontrolü
            if next_node in traffic_signal_dict and not traffic_signal_dict[next_node].is_green():
                # Trafik ışığı kırmızıysa bekle
                self.stuck_steps += 1
                return

            # Çarpışma kontrolü
            can_move = True
            for other_agent in agents:
                if other_agent is not self and not other_agent.reached:
                    distance = ((other_agent.pos[0] - self.pos[0]) ** 2 + (other_agent.pos[1] - self.pos[1]) ** 2) ** 0.5
                    if distance < 10:
                        can_move = False
                        # Kenar yoğunluğunu artır
                        edge = tuple(sorted((self.position, next_node)))
                        edge_density[edge] += 1
                        break

            if can_move:
                # Kenarın yoğunluğunu artır
                edge = tuple(sorted((self.position, next_node)))
                edge_density[edge] += 1

                # Hedefe doğru ilerle
                dx = next_pos[0] - self.pos[0]
                dy = next_pos[1] - self.pos[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist != 0:
                    self.pos = (self.pos[0] + self.speed * dx / dist, self.pos[1] + self.speed * dy / dist)
                # Düğüme yeterince yaklaştıysa sonraki düğüme geç
                if dist < self.speed:
                    self.position = next_node
                    self.path.pop(0)
                    self.stuck_steps = 0  # Hareket ettiğinden sıfırla

                    # Hedefe ulaşıldıysa
                    if self.position == self.target_node:
                        self.reached = True
            else:
                # Hareket edemezse bekle
                # Kenar yoğunluğunu artır
                edge = tuple(sorted((self.position, next_node)))
                edge_density[edge] += 1

# Trafik ışıklarını oluşturalım
traffic_signal_dict = {}
for signal in traffic_signals:
    traffic_signal_dict[signal] = TrafficLight(signal)

# Ajanları oluştur
agents = [Agent(graph) for _ in range(250)]  # Performans için 100 ajan öneriyorum

# Kenar yoğunluk sözlüğü
edge_density = {tuple(sorted(edge)): 0 for edge in graph.edges()}

# Trafik ışıklarını güncelleme fonksiyonu
def update_traffic_lights(traffic_light_states):
    for node, state in traffic_light_states.items():
        if node in traffic_signal_dict:
            traffic_signal_dict[node].state = state
            traffic_signal_dict[node].timer = 0

# Simülasyon fonksiyonu
def run_simulation(with_traffic_lights, traffic_light_queue):
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Trafik Simülasyonu")

        running = True
        clock = pygame.time.Clock()
        simulation_time = 0  # Simülasyon süresini takip etmek için

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(WHITE)

            # Trafik ışıklarını güncelle
            if with_traffic_lights:
                while not traffic_light_queue.empty():
                    traffic_light_states = traffic_light_queue.get()
                    update_traffic_lights(traffic_light_states)

            # Harita kenarlarını çiz (yoğunluğa göre renklendirme)
            for edge in graph.edges():
                sorted_edge = tuple(sorted(edge))
                start_pos = node_positions[sorted_edge[0]]
                end_pos = node_positions[sorted_edge[1]]
                density = edge_density.get(sorted_edge, 0)
                if density < 5:
                    color = GREEN
                elif density < 10:
                    color = YELLOW
                else:
                    color = RED
                pygame.draw.line(screen, color, start_pos, end_pos, 3)

            # Trafik ışıklarını çiz
            for signal in traffic_signal_dict.values():
                x, y = node_positions[signal.position]
                color = GREEN if signal.is_green() else RED
                pygame.draw.circle(screen, color, (x, y), 10)

            # Ajanları güncelle ve çiz
            for agent in agents:
                agent.move()
                x, y = agent.pos
                pygame.draw.circle(screen, BLUE, (int(x), int(y)), 3)

            pygame.display.flip()
            clock.tick(30)
            simulation_time += 1/30  # Zamanı güncelle

            # Simülasyonu belirli bir süre sonra sonlandırmak için (örneğin 300 saniye)
            if simulation_time >= 300:
                running = False

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

        # Simülasyon tamamlandıktan sonra sonuçları yazdır
        total_agents = len(agents)
        reached_agents = sum(agent.reached for agent in agents)
        not_reached_agents = total_agents - reached_agents

        reached_percentage = (reached_agents / total_agents) * 100
        not_reached_percentage = (not_reached_agents / total_agents) * 100

        print(f"Toplam Ajan Sayısı: {total_agents}")
        print(f"Hedefe Ulaşan Ajan Sayısı: {reached_agents} ({reached_percentage:.2f}%)")
        print(f"Hedefe Ulaşamayan Ajan Sayısı: {not_reached_agents} ({not_reached_percentage:.2f}%)")

# RL kontrolörü (örn. rastgele karar veren bir kontrolör)
def rl_controller(traffic_light_queue):
    while True:
        # Trafik ışığı kararlarını hesapla
        traffic_light_states = {}
        for node in traffic_signal_dict:
            # Örnek olarak, her 5 saniyede bir trafik ışıklarını değiştiriyoruz
            current_time = time.time()
            if int(current_time) % 10 < 5:
                traffic_light_states[node] = 'green'
            else:
                traffic_light_states[node] = 'red'
        # Kararları kuyruğa koy
        traffic_light_queue.put(traffic_light_states)
        # Bir süre bekle
        time.sleep(1)

# Ana program
if __name__ == '__main__':
    traffic_light_queue = Queue()
    rl_thread = threading.Thread(target=rl_controller, args=(traffic_light_queue,), daemon=True)
    rl_thread.start()
    run_simulation(True, traffic_light_queue)
