import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Serdivan'ın merkezi için manuel olarak koordinatları belirle
center_point = (40.77104, 30.39945)  # Serdivan'ın yaklaşık koordinatları

# Yarıçapı belirle (metre cinsinden)
radius = 1000  # 1 km

# Harita ayarları (yarıçap içindeki yollar)
graph = ox.graph_from_point(center_point, dist=radius, network_type='drive')

# Kenar renklerini ve kalınlıklarını ayarlamak için yol türlerini kontrol et
edge_colors = []
edge_widths = []

for u, v, k, data in graph.edges(keys=True, data=True):
    # Yolun türünü al (highway)
    highway_type = data.get('highway', 'residential')
    
    # Ana yollar ve bağlantı yollarına daha fazla trafik yoğunluğu ver
    if isinstance(highway_type, list):  # Eğer birden fazla tür varsa
        highway_type = highway_type[0]  # İlkini seç
    
    if highway_type in ['motorway', 'trunk', 'primary']:
        # Ana yollar - yüksek trafik yoğunluğu
        edge_colors.append('red')
        edge_widths.append(3)
    elif highway_type in ['secondary', 'tertiary', 'unclassified']:
        # Orta derecede yollar
        edge_colors.append('orange')
        edge_widths.append(2)
    else:
        # Ara sokaklar, konut yolları - düşük trafik yoğunluğu
        edge_colors.append('green')
        edge_widths.append(1)

# Trafik ışığı sınıfı
class TrafficLight:
    def __init__(self, position, red_duration=30, green_duration=10):
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

# Yoğunluğu hesaplamak için her düğümün kenar sayısını al
node_degrees = dict(graph.degree())
# En yoğun düğümleri bul (kenar sayısına göre sıralı)
sorted_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)
# En yoğun 10 düğüme trafik ışıkları ekle
traffic_light_nodes = sorted_nodes[:10]
traffic_lights = {node: TrafficLight(node) for node in traffic_light_nodes}

# Araç sınıfı (simülasyon için)
class Agent:
    def __init__(self, graph, speed=1):
        self.graph = graph
        # Rastgele başlangıç ve hedef düğümü belirle
        self.position = random.choice(list(graph.nodes))
        self.target = random.choice(list(graph.nodes))
        self.path = None
        self.speed = speed  # Araç hızı
        self.wait_time = 0  # Trafik ışığında bekleme süresi

    def move(self, with_lights=False):
        if not self.path:
            try:
                # Hedefe giden en kısa yolu bul
                self.path = nx.shortest_path(self.graph, self.position, self.target)
            except nx.NetworkXNoPath:
                self.path = []

        if len(self.path) > 1:
            # Sonraki düğüme hareket et
            next_position = self.path[1]
            
            # Eğer trafik ışığı varsa ve kırmızı ışık yanıyorsa dur
            if with_lights and next_position in traffic_lights:
                light = traffic_lights[next_position]
                if not light.is_green():
                    self.wait_time += 1  # Bekleme süresini artır
                    return  # Hareket etme
            
            # Hız dikkate alınarak bir düğüme taşı
            self.position = next_position
            self.path.pop(0)

# Trafik ışıkları olan ve olmayan yoğunluğu ayarlama
num_agents_no_lights = 300  # Trafik ışıkları olmayan araç sayısı
num_agents_with_lights = 100  # Trafik ışıkları olan araç sayısı (daha az yoğun)

# Ajanları oluştur
agents_no_lights = [Agent(graph, speed=2) for _ in range(num_agents_no_lights)]  # Trafik ışıkları olmadan hızlı araçlar
agents_with_lights = [Agent(graph, speed=1) for _ in range(num_agents_with_lights)]  # Trafik ışıklarıyla daha yavaş araçlar

# Yoğunlukları tutmak için listeler
traffic_density_no_lights = []
traffic_density_with_lights = []

# Figür 1: Trafik ışıkları olmadan animasyon
fig1, ax1 = plt.subplots(figsize=(10, 10))
ox.plot_graph(graph, ax=ax1, node_size=0, edge_color=edge_colors, edge_linewidth=edge_widths, bgcolor='white')
scat_no_lights = ax1.scatter([], [], c='blue', s=20, zorder=5)
ax1.set_title("Trafik Işıkları Olmadan")

def animate_no_lights(frame):
    # Araçları güncelle
    for agent in agents_no_lights:
        agent.move(with_lights=False)
    
    # Araç konumlarını güncelle
    agent_positions = [(graph.nodes[agent.position]['x'], graph.nodes[agent.position]['y']) for agent in agents_no_lights]
    scat_no_lights.set_offsets(agent_positions)

    # Trafik yoğunluğunu hesapla
    density_count = {edge: 0 for edge in graph.edges(keys=True)}
    for agent in agents_no_lights:
        if len(agent.path) > 1:
            edge = (agent.position, agent.path[1], 0)
            if edge in density_count:
                density_count[edge] += 1
    traffic_density_no_lights.append(density_count)

    return scat_no_lights,

ani_no_lights = animation.FuncAnimation(fig1, animate_no_lights, frames=100, interval=200, blit=True)

# Figür 2: Trafik ışıklarıyla animasyon
fig2, ax2 = plt.subplots(figsize=(10, 10))
ox.plot_graph(graph, ax=ax2, node_size=0, edge_color=edge_colors, edge_linewidth=edge_widths, bgcolor='white')
scat_with_lights = ax2.scatter([], [], c='blue', s=20, zorder=5)
light_positions = [(graph.nodes[node]['x'], graph.nodes[node]['y']) for node in traffic_lights.keys()]
# Trafik ışıklarını siyah ve daha belirgin yap
ax2.scatter(
    [pos[0] for pos in light_positions], 
    [pos[1] for pos in light_positions], 
    c='black', 
    s=200,  # Sembollerin boyutunu artırdık
    marker='x',  # Sembolleri 'x' olarak değiştirdik
    zorder=10, 
    label='Traffic Light'
)
ax2.set_title("Trafik Işıklarıyla")
ax2.legend()

def animate_with_lights(frame):
    # Trafik ışıklarını güncelle
    for light in traffic_lights.values():
        light.update()

    # Araçları güncelle
    for agent in agents_with_lights:
        agent.move(with_lights=True)
    
    # Araç konumlarını güncelle
    agent_positions = [(graph.nodes[agent.position]['x'], graph.nodes[agent.position]['y']) for agent in agents_with_lights]
    scat_with_lights.set_offsets(agent_positions)

    # Trafik yoğunluğunu hesapla
    density_count = {edge: 0 for edge in graph.edges(keys=True)}
    for agent in agents_with_lights:
        if len(agent.path) > 1:
            edge = (agent.position, agent.path[1], 0)
            if edge in density_count:
                density_count[edge] += 1
    traffic_density_with_lights.append(density_count)

    return scat_with_lights,

ani_with_lights = animation.FuncAnimation(fig2, animate_with_lights, frames=100, interval=200, blit=True)

plt.show()

# Trafik yoğunluk oranlarını görselleştirmek için
def plot_density_comparison(density_no_lights, density_with_lights):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Her iki simülasyon için toplam yoğunluğu hesapla
    total_density_no_lights = [sum(density.values()) for density in density_no_lights]
    total_density_with_lights = [sum(density.values()) for density in density_with_lights]

    # Grafiği çiz
    ax.plot(total_density_no_lights, label='Trafik Işıkları Olmadan', color='blue')
    ax.plot(total_density_with_lights, label='Trafik Işıklarıyla', color='orange')

    ax.set_title('Trafik Yoğunluğu Karşılaştırması')
    ax.set_xlabel('Zaman (frame)')
    ax.set_ylabel('Toplam Yoğunluk')
    ax.legend()
    plt.show()

# Yoğunlukları karşılaştır
plot_density_comparison(traffic_density_no_lights, traffic_density_with_lights)
