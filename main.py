import time
import matplotlib.pyplot as plt

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


def plot(time_data, profit_data):
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, profit_data, linestyle='-')
    plt.title('Objective Function Value Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Total Profit')
    plt.grid(True)
    plt.show()

max_profit = 0  # Inicialización global
best_project_set = []  # Inicialización global

def minimal_forward_checking(i, selected_projects, remaining_budget, profits, costs, tasks, covered_tasks, times, profit_changes, start_time):
    global max_profit, best_project_set  # Declarar uso de variables globales

    # Registro de tiempo y ganancias
    current_time = time.time() - start_time
    print(f"TIEMPO ACTUAAAAAAAAAAAAAAAAAAAAAAAAAAAAL: {current_time}")
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
            print(f"Budget {remaining_budget}")
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
        save = [k for k, task in enumerate(tasks[i]) if task and not covered_tasks[k]]
        print(f"Project {i}: Tasks to be costed: {save}")
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
    global max_profit, best_project_set  # Si es necesario manejar como globales
    max_profit = 0
    best_project_set = []
    for i in range(3):
        data = extract_data('data/'+str(i+1)+'-2024.txt')
        m = data['m']
        n = data['n']
        B = data['B']
        profits = data['profits']
        costs = data['costs']
        tasks = data['tasks']
        # Variable para guardar el mejor set de proyectos
        selected_projects = [0] * m
        # Variable para guardar si se ha realizado una tarea
        covered_tasks = [0] * n
        # Timing 
        times = []
        profit_changes = []
        start_time = time.time()
        sol, profit_changes, times, final_selection, max_profit, best_project_set  = minimal_forward_checking(0, selected_projects, B, profits, costs, tasks, covered_tasks, times, profit_changes, start_time)
        if sol:
            print("Llego a solución")
        else:
            print("No llegó a solución")
        print("Total Profit:", sum(profit_changes), "Final Selection:", final_selection)
        print(f"File {i}: Max Profit: {max_profit}")
        print(f"Best Project Set for Max Profit: {best_project_set}")
        plot(times, profit_changes)



if __name__ == '__main__':
    main()
