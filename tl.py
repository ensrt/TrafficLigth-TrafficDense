import osmnx as ox
import matplotlib.pyplot as plt

# Serdivan'ın merkezi için manuel olarak koordinatları belirle
center_point = (40.7631, 30.3677)  # Serdivan'ın yaklaşık koordinatları

# Yarıçapı belirle (metre cinsinden)
radius = 1000  # 1 km

# Harita ayarları (yarıçap içindeki yollar)
graph = ox.graph_from_point(center_point, dist=radius, network_type='drive')

# Kavşakları ve derecelerini bul
node_degrees = dict(graph.degree())

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

# Haritayı çiz ve trafik yoğunluğunu kenarlarda görselleştir
fig, ax = ox.plot_graph(
    graph, 
    node_size=0,  # Düğümleri gizle (isteğe bağlı)
    edge_color=edge_colors, 
    edge_linewidth=edge_widths, 
    bgcolor='white'
)

plt.show()
