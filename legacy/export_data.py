import graph_to_csv

location = "Plaza Independencia, Mendoza, Argentina"
radius = 3000

try:
    graph_to_csv.graph_from_address_to_csv(location, radius)
except:
    graph_to_csv.graph_from_place_to_csv(location)

""" 
# Cargar la matriz
dist = np.load("dist_matrix.npy")

#Ids Nodos
poi_ids = [4801, 187, 17258, 61]

# Crear un DataFrame
df = pd.DataFrame(dist, index=poi_ids, columns=poi_ids)

# Cargar la matriz de distancias
dist = np.load("dist_matrix.npy")
n = dist.shape[0]

# Definir parámetros
umbral_cercania = 300.0  # metros
tau_cercano = 1.0         # feromonas para caminos cortos
tau_lejano = 0.1          # feromonas para caminos largos

# Crear matriz de feromonas
tau = np.full((n, n), tau_lejano)

# Asignar feromonas mayores en caminos cercanos
for i in range(n):
    for j in range(n):
        if i != j and dist[i, j] < umbral_cercania:
            tau[i, j] = tau_cercano

# Mostrar la matriz
print("Matriz inicial de feromonas:")
print(tau)


# Crear MOACO
aco = MOACO(dist, tau)

# Ejecutar MOACO
mejor_ruta, mejor_costo = aco.correr(n_ants=10, n_iteraciones=30)

print("Mejor ruta encontrada:", mejor_ruta)
print("Costo total:", mejor_costo)

index = mejor_ruta[0]
list_tupla = []
for i in mejor_ruta[1:]:
    list_tupla.append((poi_ids[index],poi_ids[i]))
    index = i

print(list_tupla)
 """

#graph_map.create_graph_map()


"""
####

import matplotlib.pyplot as plt
import seaborn as sns

# Cargar la matriz de distancias
dist = np.load("dist_matrix.npy")

# Crear un DataFrame para etiquetar filas y columnas
df = pd.DataFrame(dist, index=poi_ids, columns=poi_ids)

# Crear el heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(df, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5)

# Opciones del gráfico
plt.title("Mapa de calor de distancias entre POIs")
plt.xlabel("Destino")
plt.ylabel("Origen")
plt.show()

"""