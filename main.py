import matplotlib.pyplot as plt
from terrain_generator import Terrain
from biomes import BiomeManager

def main():
    print("Generating terrain data...")
    
    # 1. Create the terrain object
    my_world = Terrain(
        width=256, 
        height=256, 
        scale=100.0, 
        octaves=6, 
        persistence=0.5, 
        lacunarity=2.0, 
        seed=42 
    )
    
    print("Applying biomes...")
    
    # 2. Initialize the Biome Manager and generate the color map
    biome_manager = BiomeManager()
    color_map = biome_manager.apply_biomes(my_world.height_map)
    
    print("Rendering map...")
    
    # 3. Set up the Matplotlib figure
    plt.figure(figsize=(8, 8))
    plt.title("Procedural Terrain - Colored Biomes (Seed: 42)")
    
    # 4. Visualize the 3D RGB array
    # We no longer need cmap='gray' because we are passing raw RGB colors
    plt.imshow(color_map, origin='lower')
    
    # 5. Display the window
    plt.axis('off') # Hiding the axes makes it look more like a real map
    plt.show()

if __name__ == "__main__":
    main()