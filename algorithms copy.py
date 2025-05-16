
import numpy as np
import random
import pandas as pd

class MOACO:
    def __init__(self, dist, tau, alpha=1.0, beta=2.0, evaporation=0.5, q=100.0):
        """
        dist: matriz de distancias (n x n)
        tau: matriz inicial de feromonas (n x n)
        alpha: importancia relativa de la feromona
        beta: importancia relativa de la heurística (1/distancia)
        evaporation: factor de evaporación [0-1]
        q: cantidad total de feromonas depositadas por hormiga
        """
        self.dist = dist
        self.tau = tau
        self.n = dist.shape[0]
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q
        self.best_route = None
        self.best_cost = np.inf
        
        self.log_detallado = []


    def _probabilidad(self, i, no_visitados):
        """Calcula las probabilidades de movimiento desde nodo i hacia no_visitados."""
        attractiveness = []
        for j in no_visitados:
            pheromone = self.tau[i, j] ** self.alpha
            heuristic = (1.0 / self.dist[i, j]) ** self.beta if self.dist[i, j] > 0 else 0
            attractiveness.append(pheromone * heuristic)
        total = sum(attractiveness)
        if total == 0:
            probs = [1/len(no_visitados)] * len(no_visitados)  # distribución uniforme
        else:
            probs = [a/total for a in attractiveness]
        return probs
    """
    def _construir_ruta(self):
        Construye una solución completa para una hormiga.
        ruta = [0]  # empieza en el depósito (suponemos índice 0)
        no_visitados = set(range(1, self.n))

        while no_visitados:
            i = ruta[-1]
            no_vis = list(no_visitados)
            probs = self._probabilidad(i, no_vis)
            siguiente = random.choices(no_vis, weights=probs, k=1)[0]
            ruta.append(siguiente)
            no_visitados.remove(siguiente)

        ruta.append(0)  # vuelta al depósito
        return ruta
    """
    """
    def _construir_ruta(self):
        Construye una solución completa para una hormiga (modo debug activado).
        ruta = [0]  # empieza en el depósito
        no_visitados = set(range(1, self.n))

        while no_visitados:
            i = ruta[-1]
            no_vis = list(no_visitados)
            probs = self._probabilidad(i, no_vis)

            # 🔵 DEBUG: mostrar opciones
            print(f"\nHormiga en nodo {i}")
            for idx, j in enumerate(no_vis):
                print(f"  Opción: {j} (distancia: {self.dist[i, j]:.2f}) - Probabilidad: {probs[idx]*100:.2f}%")

            siguiente = random.choices(no_vis, weights=probs, k=1)[0]

            print(f"➡️  Hormiga eligió moverse a {siguiente}\n")

            ruta.append(siguiente)
            no_visitados.remove(siguiente)

        ruta.append(0)  # vuelta al depósito
        costo_total = self._costo_ruta(ruta)

        print(f"✅ Ruta construida: {ruta}\n")
        print(f"Costo total de la ruta: {costo_total:.2f}\n")

        return ruta
    """
    def _construir_ruta(self, iteracion=None, hormiga_id=None):
        ruta = [0]
        no_visitados = set(range(1, self.n))
        pasos = []

        while no_visitados:
            i = ruta[-1]
            no_vis = list(no_visitados)
            probs = self._probabilidad(i, no_vis)

            paso_log = f"Hormiga en nodo {i}\n"
            for idx, j in enumerate(no_vis):
                paso_log += f"  Opción: {j} (distancia: {self.dist[i, j]:.2f}) - Probabilidad: {probs[idx]*100:.2f}%\n"

            siguiente = random.choices(no_vis, weights=probs, k=1)[0]
            paso_log += f"➡️  Hormiga eligió moverse a {siguiente}\n"

            ruta.append(siguiente)
            no_visitados.remove(siguiente)
            pasos.append(paso_log)

        ruta.append(0)
        costo_total = self._costo_ruta(ruta)

        resumen = (
            f"✅ Ruta construida: {ruta}\n"
            f"💰 Costo total de la ruta: {costo_total:.2f}\n"
            f"📅 Iteración {iteracion} - Hormiga {hormiga_id}\n"
            "--------------------------------------------\n"
        )

        self.log_detallado.append("\n".join(pasos) + resumen)
        return ruta

    def _costo_ruta(self, ruta):
        """Calcula el costo total de una ruta."""
        return sum(self.dist[ruta[i], ruta[i+1]] for i in range(len(ruta) - 1))

    def _evaporar(self):
        """Evapora feromonas."""
        self.tau *= (1 - self.evaporation)

    def _depositar_feromonas(self, rutas, costos):
        """Deposita feromonas según la calidad de cada ruta."""
        for ruta, cost in zip(rutas, costos):
            feromona = self.q / cost
            for i in range(len(ruta) - 1):
                self.tau[ruta[i], ruta[i+1]] += feromona

    def correr(self, n_ants=10, n_iteraciones=100):
        """Corre el algoritmo completo."""
        for it in range(n_iteraciones):
            rutas = []
            costos = []

            for h in range(n_ants):
                ruta = self._construir_ruta(iteracion=it + 1, hormiga_id=h + 1)

                ruta = self._construir_ruta()
                costo = self._costo_ruta(ruta)
                rutas.append(ruta)
                costos.append(costo)

                if costo < self.best_cost:
                    self.best_route = ruta
                    self.best_cost = costo

            self._evaporar()
            self._depositar_feromonas(rutas, costos)

            print(f"Iteración {it+1}: Mejor costo hasta ahora: {self.best_cost:.2f}")

        # Guardar el log detallado
        with open("moaco_log_detallado.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.log_detallado))

        print("📝 Log detallado guardado como 'moaco_log_detallado.txt'")

        return self.best_route, self.best_cost
