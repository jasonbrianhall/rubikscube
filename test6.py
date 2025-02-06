import json
from twophase import solve

# Read cube state from JSON
with open('test1.json', 'r') as f:
    cube_state = json.load(f)

# Convert cube state to Kociemba string
def json_to_kociemba(cube_json):
    kociemba_string=""
    color_map = {'WHITE': 'U', 'RED': 'R', 'GREEN': 'F', 
                 'YELLOW': 'D', 'ORANGE': 'L', 'BLUE': 'B'}
    # Left and Right are Switched; Front and Back are Switched
    for x in "top", "left", "back", "bottom", "right", "front":
        #print(cube_json.get(x))
        sorted_dict = dict(sorted(cube_json.get(x).items(), 
                         key=lambda x: (int(x[0].split(',')[0]), int(x[0].split(',')[1]))))
        print(x, sorted_dict)
        if True:
            for y in '0,2', '0,1', '0,0', '1,2', '1,1', '1,0', '2,2', '2,1', '2,0':
                print(sorted_dict.get(y))
                kociemba_string+=color_map.get(sorted_dict.get(y))
        else:
           for y in '0,0', '0,1', '0,2', '1,0', '1,1', '1,2', '2,0', '2,1', '2,2':
                print(sorted_dict.get(y))
                kociemba_string+=color_map.get(sorted_dict.get(y))


    return kociemba_string

# Solve the cube
kociemba_string = json_to_kociemba(cube_state)
#kociemba_string="BBRLBBLRBDLFLRDBDURULBUFDDDDLRLUGGBDLRDFRRLRLFDBFFDGUUD"
#kociemba_string="UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
print(kociemba_string)
solution = solve(kociemba_string)

print(f"Solution: {solution}")
