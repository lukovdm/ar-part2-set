from jinja2 import FileSystemLoader, Environment
from jinja2.environment import Template

def exercise_constants():
    route = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
        [0, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
        [0, 17, 17, 0, 3, 3, 3, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17], 
        [0, 26, 26, 26, 0, 4, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26 ], 
        [0, 5, 5, 5, 5, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], 
        [0, 6, 6, 6, 6, 6, 0, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], 
        [0, 19, 19, 19, 19, 19, 19, 0, 7, 7, 7, 19, 19, 19, 19, 19, 19, 19], 
        [0, 27, 27, 27, 27, 27, 27, 27, 0, 8, 27, 27, 27, 27, 27, 27, 27, 27 ], 
        [0, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9], 
        [0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 10, 10, 10, 10, 10, 10, 10], 
        [0, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 0, 11, 11, 11, 21, 21, 21], 
        [0, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 0, 12, 12, 12, 12, 12], 
        [0, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 0, 13, 13, 13, 13], 
        [0, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 14, 14, 14], 
        [0, 15, 15, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 0, 15, 23], 
        [0, 16, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 0, 25], 
        [0, 24, 24, 18, 18, 18, 18, 20, 20, 20, 20, 22, 22, 22, 22, 24, 24, 0], 
    ]
    sources = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,3,17,7,17,11,17,15,17,16,4,8]
    targets = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,1,17,3,17,7,17,11,17,15,2,6,10]
    return route, list(zip(sources, targets))

def toy_constants():
    sources = [0, 1, 2, 3, 4]
    targets = [0, 2, 3, 4, 1]
    route = [[0, 0, 0, 0, 0], [0, 0, 1, 1, 1], [0, 2, 0, 2, 2], [0, 3, 3, 0, 3], [0, 4, 4, 4, 0]]
    return route, list(zip(sources, targets))

def make_model(route, channels, main):
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('network.smv')
    return template.render(route=route, channels=channels, main=main)
    

if __name__ == "__main__":
    route, channels = exercise_constants()

    exercises = [
        [1,5,9,13],
        [2,4,6],
        [1,3,5,15],
        [11,13,15],
        [11,12,13,15],
        [1,8,10],
        [5,12,14],
        [5,11,14]
    ]

    for i, exercise in enumerate(exercises):
        model = make_model(route, channels, exercise)
        name = chr(ord('a') + i)
        
        with open(f'model_{name}.smv', 'w') as f:
            f.write(model)

    route, channels = toy_constants()
    model = make_model(route, channels, [1,3])
    
    with open('model_4.smv', 'w') as f:
        f.write(model)
