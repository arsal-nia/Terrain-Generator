from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from terrain_generator import Terrain
from biomes import BiomeManager

def create_3d_terrain():
    """Converts the 2D height map array into a 3D Mesh object."""
    print("Generating math data...")
    # Keep the grid at 64x64 or 128x128. Python is slow at building massive 
    # 3D meshes manually. 64x64 generates instantly.
    my_world = Terrain(width=64, height=64, scale=20.0, octaves=4, seed=42)
    biome_manager = BiomeManager()
    
    print("Applying biomes...")
    color_map = biome_manager.apply_biomes(my_world.height_map)
    
    print("Building 3D geometry...")
    vertices = []
    colors = []
    triangles = []
    
    width = my_world.width
    depth = my_world.height
    
    # How high the mountains should reach in 3D space
    height_multiplier = 15.0 

    # Loop through the grid to create vertices and triangles (Quads)
    for x in range(width - 1):
        for z in range(depth - 1):
            
            # 1. Calculate the 4 corners of the current grid square (Quad)
            y0 = my_world.height_map[x][z] * height_multiplier
            y1 = my_world.height_map[x+1][z] * height_multiplier
            y2 = my_world.height_map[x+1][z+1] * height_multiplier
            y3 = my_world.height_map[x][z+1] * height_multiplier
            
            # Define the 3D coordinates for these corners
            v0 = Vec3(x, y0, z)
            v1 = Vec3(x+1, y1, z)
            v2 = Vec3(x+1, y2, z+1)
            v3 = Vec3(x, y3, z+1)
            
            # 2. Get the biome color for this specific square
            # Ursina expects colors to be divided by 255
            r, g, b = color_map[x][z]
            c = color.rgba(r/255, g/255, b/255, 1.0)
            
            # 3. Add the vertices and colors to our lists
            # A Quad is made of two triangles: (v0, v1, v2) and (v0, v2, v3)
            current_vertex_count = len(vertices)
            
            vertices.extend([v0, v1, v2, v3])
            colors.extend([c, c, c, c]) # Apply the same color to all 4 corners
            
            # Define the indices for the two triangles
            triangles.append((current_vertex_count, current_vertex_count+1, current_vertex_count+2))
            triangles.append((current_vertex_count, current_vertex_count+2, current_vertex_count+3))

    # Create the actual 3D Entity in Ursina
    terrain_mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors)
    terrain_entity = Entity(model=terrain_mesh, collider='mesh')
    
    # Center the terrain in the world
    terrain_entity.x = -width / 2
    terrain_entity.z = -depth / 2
    
    return terrain_entity

# --- Main Application ---
app = Ursina()

# Hide the FPS counter and window frame for a cleaner look
window.title = '3D Procedural Terrain'
window.borderless = False
window.exit_button.visible = False

# Build the world
terrain_entity = create_3d_terrain()

# Add a sky environment
Sky(color=color.rgb(135, 206, 235)) # Soft blue sky

# Drop a player into the world!
# Position them slightly above the ground in the center of the map
player = FirstPersonController()
player.y = 20 
player.gravity = 0.5 

print("Controls: W A S D to move. Space to jump. Mouse to look. ESC to quit.")
app.run()