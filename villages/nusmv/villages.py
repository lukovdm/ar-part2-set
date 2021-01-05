from jinja2 import FileSystemLoader, Environment


def exercise_constants():
    graph = [
        [-1, 29, 21, -1],
        [29, -1, 17, 32],
        [21, 17, -1, 37],
        [-1, 32, 37, -1]
    ]
    v_cap = [-1, 120, 120, 200]
    v_init_cap = [-1, 40, 30, 145]

    return graph, v_cap, v_init_cap

def toy_constants():
    graph = [
        [-1, 1],
        [1, -1],
    ]
    v_cap = [-1, 10]
    v_init_cap = [-1, 10]

    return graph, v_cap, v_init_cap

def make_model(graph, v_max_cap, v_init_cap, t_max_cap):
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('villages.smv')
    return template.render(
        distance=graph, v_max_cap=v_max_cap, v_init_cap=v_init_cap, t_max_cap=t_max_cap)
    
if __name__ == "__main__":
    graph, v_cap, v_init_cap = exercise_constants()

    model = make_model(graph, v_cap, v_init_cap, 300)
    
    with open(f'model_a.smv', 'w') as f:
        f.write(model)

    model = make_model(graph, v_cap, v_init_cap, 320)
    
    with open(f'model_b.smv', 'w') as f:
        f.write(model)

    model = make_model(graph, v_cap, v_init_cap, 318)
    
    with open(f'model_c.smv', 'w') as f:
        f.write(model)

    graph, v_cap, v_init_cap = toy_constants()

    model = make_model(graph, v_cap, v_init_cap, 10)
    
    with open(f'test.smv', 'w') as f:
        f.write(model)
