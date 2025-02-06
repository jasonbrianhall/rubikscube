    def convert_cube_to_dict(self):
       """Convert the cube state to a dictionary mapping coordinates to colors for each face"""
       cube = self.gl_widget.cube
       cube_dict = {
           'front': {},
           'back': {},
           'left': {},
           'right': {},
           'top': {},
           'bottom': {}
       }
       face_mappings = {
           'front':  {(x, y, 1): (y+1, x+1) for x in range(-1, 2) for y in range(-1, 2)},
           'back':   {(x, y, -1): (y+1, 2-x) for x in range(-1, 2) for y in range(-1, 2)},
           'left':   {(-1, y, z): (y+1, z+1) for y in range(-1, 2) for z in range(-1, 2)},
           'right':  {(1, y, z): (y+1, z+1) for y in range(-1, 2) for z in range(-1, 2)},
           'top':    {(x, 1, z): (z+1, x+1) for x in range(-1, 2) for z in range(-1, 2)},
           'bottom': {(x, -1, z): (z+1, x+1) for x in range(-1, 2) for z in range(-1, 2)}
       }
       
       # Fill the dictionary
       for pos, cubelet in cube.cubelets.items():
           x, y, z = pos
           for face_name, mapping in face_mappings.items():
               if pos in mapping:
                   if face_name in cubelet['colors']:
                       row, col = mapping[pos]
                       if face_name == 'back':
                           pos_key = f"{2-row},{col-1}"
                       else:
                           pos_key = f"{2-row},{2-col}"
                       cube_dict[face_name][pos_key] = cubelet['colors'][face_name].name
    
       print(json.dumps(cube_dict, indent=3))
       #data=robiksolver.solve_cube(cube_dict)
       return cube_dict
