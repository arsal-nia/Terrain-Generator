import random
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera

# Make sure this matches your python file name (terrain vs terrain_generator)
from terrain_generator import Terrain 
from biomes import BiomeManager

app = Ursina()
window.title = '3D Procedural Terrain Generator'
window.borderless = False
window.exit_button.visible = False

active_terrain_entity = None

# ==========================================
# --- UPGRADED UI: COLLAPSIBLE DROP BOX ---
# ==========================================

# 1. Main Toggle Button (Stays visible at the top left)
toggle_btn = Button(
    text='⚙ Terrain Settings ▼', 
    parent=camera.ui, 
    position=(-0.68, 0.45), 
    scale=(0.28, 0.05), 
    color=color.hex('#1f2937') # Sleek dark gray
)

# 2. Container for the drop-down menu
menu_container = Entity(parent=camera.ui, position=(-0.68, 0.4))

# 3. Background Panel
# FIX: Using a 'Button' instead of a normal quad for the background. 
# Buttons consume mouse clicks, which stops your clicks from passing through 
# the UI and accidentally spinning the 3D camera.
menu_bg = Button(
    parent=menu_container, 
    model='quad', 
    color=color.rgba(15, 15, 15, 240), 
    scale=(0.32, 0.75), 
    position=(0, -0.375, 0.1), # Pushed slightly back on Z-axis so text renders in front
    highlight_color=color.rgba(15, 15, 15, 240), # Prevents hover visual glitch
    pressed_color=color.rgba(15, 15, 15, 240)
)

# 4. Inputs and Sliders
Text(text="Seed:", parent=menu_container, position=(-0.14, -0.07), scale=1)
seed_input = InputField(parent=menu_container, position=(0.04, -0.07), scale=(0.18, 0.05), text='42')

scale_slider = Slider(min=10, max=200, default=50, text='Scale', parent=menu_container, position=(-0.08, -0.18), scale=0.8)
octaves_slider = Slider(min=1, max=8, default=4, step=1, text='Octaves', parent=menu_container, position=(-0.08, -0.28), scale=0.8)
roughness_slider = Slider(min=0.1, max=0.9, default=0.5, step=0.05, text='Roughness', parent=menu_container, position=(-0.08, -0.38), scale=0.8)

# 5. Buttons
def randomize_seed():
    seed_input.text = str(random.randint(0, 999999))
    generate_3d_terrain()

randomize_btn = Button(text='Random Seed', parent=menu_container, position=(0, -0.52), scale=(0.25, 0.05), color=color.hex('#4b5563'))
randomize_btn.on_click = randomize_seed

generate_btn = Button(text='GENERATE TERRAIN', parent=menu_container, position=(0, -0.62), scale=(0.28, 0.07), color=color.hex('#0284c7'))

# 6. Toggle Logic
def toggle_menu():
    menu_container.enabled = not menu_container.enabled
    toggle_btn.text = '⚙ Terrain Settings ▲' if menu_container.enabled else '⚙ Terrain Settings ▼'

toggle_btn.on_click = toggle_menu


# ==========================================
# --- 3D GENERATION LOGIC ---
# ==========================================

def generate_3d_terrain():
    global active_terrain_entity
    
    if active_terrain_entity:
        destroy(active_terrain_entity)
    
    generate_btn.text = 'Generating...'
    
    try:
        current_seed = int(seed_input.text)
    except ValueError:
        current_seed = 42 
        seed_input.text = '42'
        
    current_scale = scale_slider.value
    current_octaves = int(octaves_slider.value)
    current_roughness = roughness_slider.value

    my_world = Terrain(
        width=64, 
        height=64, 
        scale=current_scale, 
        octaves=current_octaves, 
        persistence=current_roughness,
        seed=current_seed
    )
    
    biome_manager = BiomeManager()
    color_map = biome_manager.apply_biomes(my_world.height_map)
    
    vertices = []
    colors = []
    triangles = []
    
    width = my_world.width
    depth = my_world.height
    height_multiplier = 15.0 

    for x in range(width - 1):
        for z in range(depth - 1):
            y0 = my_world.height_map[x][z] * height_multiplier
            y1 = my_world.height_map[x+1][z] * height_multiplier
            y2 = my_world.height_map[x+1][z+1] * height_multiplier
            y3 = my_world.height_map[x][z+1] * height_multiplier
            
            v0 = Vec3(x, y0, z)
            v1 = Vec3(x+1, y1, z)
            v2 = Vec3(x+1, y2, z+1)
            v3 = Vec3(x, y3, z+1)
            
            r, g, b = color_map[x][z]
            c = color.rgba(r/255, g/255, b/255, 1.0)
            
            idx = len(vertices)
            vertices.extend([v0, v1, v2, v3])
            colors.extend([c, c, c, c]) 
            
            triangles.append((idx, idx+1, idx+2))
            triangles.append((idx, idx+2, idx+3))

    terrain_mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors)
    active_terrain_entity = Entity(model=terrain_mesh, collider='none') 
    
    active_terrain_entity.x = -width / 2
    active_terrain_entity.z = -depth / 2
    
    generate_btn.text = 'GENERATE TERRAIN'

generate_btn.on_click = generate_3d_terrain

# Environment & Camera
Sky(color=color.rgb(135, 206, 235))

spectator_camera = EditorCamera()
spectator_camera.position = (0, 30, -40) 
spectator_camera.look_at(Vec3(0, 0, 0))  

# Startup Commands
generate_3d_terrain()
toggle_menu() # Automatically hides the menu on startup for a cinematic view!

app.run()