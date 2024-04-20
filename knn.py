import time
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

time_limit = 1800

def extract_data(filepath):
    data = {}
    with open(filepath, "r") as file:
        data['m'] = int(file.readline().strip())  # Numero de proyectos
        data['n'] = int(file.readline().strip())  # Numero de tareas
        data['B'] = int(file.readline().strip())  # Budget maximo
        # Ganancia de cada proyecto
        data['profits'] = list(map(int, file.readline().strip().split()))
        # Costo de cada tarea
        data['costs'] = list(map(int, file.readline().strip().split()))
        data['tasks'] = [list(map(int, file.readline().strip().split()))
                         for _ in range(data['m'])]  # Matriz de asociacion de tareas
    return data

def kmeans_cluster(data):
    # Transformar los datos a una matriz numpy
    X = np.array(data['profits']).reshape(-1, 1)

    # Aplicar K-Means con K=4
    kmeans = KMeans(n_clusters=4)
    kmeans.fit(X)
    clusters = kmeans.predict(X)

    return clusters

def select_next_cluster(current_cluster, clusters, selected_clusters):
    # Encuentra el cluster más cercano que no haya sido seleccionado aún
    min_distance = float('inf')
    next_cluster = -1
    for i, cluster in enumerate(clusters):
        if i not in selected_clusters:
            distance = abs(current_cluster - cluster)
            if distance < min_distance:
                min_distance = distance
                next_cluster = i
    return next_cluster

def plot(time_data, profit_data):
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, profit_data, linestyle='-')
    plt.title('Objective Function Value Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Total Profit')
    plt.grid(True)
    plt.show()

def project_cost(tasks, costs, covered_tasks):
    return sum(costs[k] for k in range(len(tasks)) if tasks[k] and not covered_tasks[k])

max_profit = 0  # Inicialización global
best_project_set = []  # Inicialización global

def minimal_forward_checking(i, selected_projects, remaining_budget, profits, costs, tasks, covered_tasks, times, profit_changes, start_time):
    global max_profit, best_project_set  # Declarar uso de variables globales

    # Registro de tiempo y ganancias
    current_time = time.time() - start_time
    print(f"TIEMPO ACTUAL: {current_time}")
    times.append(current_time)
    current_profit = sum(profits[k] for k in range(len(selected_projects)) if selected_projects[k] == 1)
    profit_changes.append(current_profit)

    
    # Comprobación y actualización de máximo
    if current_profit > max_profit:
        max_profit = current_profit
        best_project_set = [k for k, selected in enumerate(selected_projects) if selected]

    if current_time > time_limit or i == len(selected_projects):
        return False, profit_changes, times, selected_projects

    for decision in [1, 0]:
        original_state = (remaining_budget, list(covered_tasks))
        selected_projects[i] = decision
        if decision:
            constraint, new_remaining_budget, new_covered_tasks = update(i, decision, costs, tasks, remaining_budget, covered_tasks)
            if not constraint:
                continue
            if check_forward(i, selected_projects, costs, tasks, new_remaining_budget, new_covered_tasks):
                result = minimal_forward_checking(i + 1, selected_projects, new_remaining_budget, profits, costs, tasks, new_covered_tasks, times, profit_changes, start_time)
                if result[0]:
                    return result
            remaining_budget, covered_tasks = original_state  # Restaurar el estado original
        else:
            if check_forward(i, selected_projects, costs, tasks, remaining_budget, covered_tasks):
                result = minimal_forward_checking(i + 1, selected_projects, remaining_budget, profits, costs, tasks, covered_tasks, times, profit_changes, start_time)
                if result[0]:
                    return result
    return False, profit_changes, times, selected_projects

def check_forward(i, selected_projects, costs, tasks, remaining_budget, covered_tasks):
    # Verifica cada proyecto futuro para asegurarse de que aún pueda ser completado si es necesario
    for j in range(i + 1, len(selected_projects)):
        if selected_projects[j] == 1:  # Solo considerar si se planea seleccionar el proyecto
            project_cost = sum(costs[k] for k in range(len(tasks[j])) if tasks[j][k] and not covered_tasks[k])
            if project_cost > remaining_budget:
                return False  # No se puede cumplir este proyecto con el presupuesto restante
    return True

def restore(i, selected_projects, remaining_budget, costs, tasks, covered_tasks):
    # Restaura el presupuesto y el estado de tareas cubiertas antes de la decisión en el índice i
    selected_projects[i] = 0  # Asegura que el proyecto no está seleccionado
    remaining_budget = sum(costs[k] for k in range(len(tasks[i])) if tasks[i][k] and covered_tasks[k]) + remaining_budget
    for k in range(len(tasks[i])):
        if tasks[i][k]:
            covered_tasks[k] = 0  # Marcar la tarea como no cubierta si el proyecto fue deseleccionado

def update(i, decision, costs, tasks, remaining_budget, covered_tasks):
    if decision == 1:  # Si se decide seleccionar el proyecto
        project_cost = sum(costs[k] for k, task in enumerate(tasks[i]) if task and not covered_tasks[k])
        if remaining_budget >= project_cost:
            new_remaining_budget = remaining_budget - project_cost
            new_covered_tasks = covered_tasks[:]
            for k in range(len(tasks[i])):
                if tasks[i][k]:
                    new_covered_tasks[k] = 1
            return True, new_remaining_budget, new_covered_tasks
        else:
            return False, remaining_budget, covered_tasks  # No hay presupuesto suficiente, no actualizar nada
    return True, remaining_budget, covered_tasks  # No se selecciona el proyecto, no cambios en el estado

def main():
    global max_profit, best_project_set
    
    # Solo trabajar con el archivo 2-2024.txt
    data = extract_data('2-2024.txt')
    selected_projects = [0] * data['m']
    covered_tasks = [0] * data['n']
    times, profit_changes = [], []
    start_time = time.time()

    # Aplicar K-Means para clusterizar los proyectos
    clusters = kmeans_cluster(data)

    # Inicializar la selección de clusters
    selected_clusters = set()

    while True:
        # Seleccionar el siguiente cluster
        next_cluster = select_next_cluster(len(selected_clusters), clusters, selected_clusters)
        if next_cluster == -1:
            break
        selected_clusters.add(next_cluster)

        # Seleccionar proyectos dentro del cluster
        for idx, cluster in enumerate(clusters):
            if cluster == next_cluster:
                sol, profit_changes, times, final_selection = minimal_forward_checking(idx, selected_projects, data['B'], data['profits'], data['costs'], data['tasks'], covered_tasks, times, profit_changes, start_time)

    if sol:
        print("Llegó a solución")
    else:
        print("No llegó a solución")

    print(f"Max Profit: {max_profit}")
    print(f"Best Project Set for Max Profit: {best_project_set}")
    plot(times, profit_changes)

if __name__ == '__main__':
    main()
