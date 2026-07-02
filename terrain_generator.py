import numpy as np
from noise_generator import NoiseGenerator

class Terrain:
    """
    Represents the physical world grid. Acts as a container and manager for 
    height maps, biomes, and terrain features.
    """
    def __init__(self, width=200, height=200, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0, seed=0):
        self.width = width
        self.height = height
        self.seed = seed
        
        # Store generator settings so we can easily modify and regenerate later
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        
        # Initialize the noise generator with our parameters
        self.noise_generator = NoiseGenerator(
            width=self.width,
            height=self.height,
            scale=self.scale,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            seed=self.seed
        )
        
        # Core data arrays
        self.height_map = None
        self.color_map = None  # Will hold RGB biome data in Phase 4
        
        # Automatically generate the initial height map upon creation
        self.generate()

    def generate(self):
        """
        Triggers the noise generator to create or update the height map.
        """
        print(f"Generating {self.width}x{self.height} terrain (Seed: {self.seed})...")
        self.height_map = self.noise_generator.generate_height_map()
        print("Terrain generation complete!")

    def regenerate(self, new_seed=None, new_scale=None, new_octaves=None, new_persistence=None, new_lacunarity=None):
        """
        Updates parameters and regenerates the map. Perfect for interactive UI sliders.
        """
        if new_seed is not None:
            self.seed = new_seed
            self.noise_generator.seed = new_seed
        if new_scale is not None:
            self.scale = new_scale
            self.noise_generator.scale = new_scale
        if new_octaves is not None:
            self.octaves = new_octaves
            self.noise_generator.octaves = new_octaves
        if new_persistence is not None:
            self.persistence = new_persistence
            self.noise_generator.persistence = new_persistence
        if new_lacunarity is not None:
            self.lacunarity = new_lacunarity
            self.noise_generator.lacunarity = new_lacunarity
            
        self.generate()

    def get_elevation_at(self, x, y):
        """
        Safely queries the elevation at a specific (x, y) coordinate.
        Returns 0.0 if out of bounds.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.height_map[x][y]
        return 0.0

    def get_statistics(self):
        """
        Returns basic statistical data about the generated terrain.
        """
        if self.height_map is None:
            return {}
            
        return {
            "min_elevation": float(np.min(self.height_map)),
            "max_elevation": float(np.max(self.height_map)),
            "mean_elevation": float(np.mean(self.height_map)),
            "std_deviation": float(np.std(self.height_map))
        }