import numpy as np
import opensimplex

class NoiseGenerator:
    """
    Handles the mathematical generation of procedural terrain using OpenSimplex Noise 
    and a custom Fractal Brownian Motion (fBm) implementation.
    """
    def __init__(self, width, height, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0, seed=0):
        self.width = width                  # Width of the map grid
        self.height = height                # Height of the map grid
        self.scale = scale                  # Zoom level
        self.octaves = octaves              # Number of detail layers
        self.persistence = persistence      # Amplitude multiplier per octave
        self.lacunarity = lacunarity        # Frequency multiplier per octave
        self.seed = seed                    # Random seed

    def generate_height_map(self):
        # Initialize an empty 2D NumPy array
        world = np.zeros((self.width, self.height))
        
        # Seed the OpenSimplex generator so our worlds are reproducible
        opensimplex.seed(self.seed)

        min_val = float('inf')
        max_val = float('-inf')

        for i in range(self.width):
            for j in range(self.height):
                
                # Reset variables for each coordinate
                amplitude = 1.0
                frequency = 1.0
                noise_val = 0.0

                # --- FRACTAL BROWNIAN MOTION (fBm) LOOP ---
                # We layer multiple 'octaves' of noise on top of each other.
                # Layer 1: Huge, smooth mountains.
                # Layer 2: Smaller hills on the mountains.
                # Layer 3: Boulders on the hills, etc.
                for _ in range(self.octaves):
                    # Calculate coordinate with current frequency and scale
                    x = (i / self.scale) * frequency
                    y = (j / self.scale) * frequency
                    
                    # Generate noise (-1.0 to 1.0) and multiply by current amplitude
                    v = opensimplex.noise2(x, y)
                    noise_val += v * amplitude

                    # Decrease amplitude for the next loop (so fine details are less impactful)
                    amplitude *= self.persistence
                    
                    # Increase frequency for the next loop (so details get smaller and tighter)
                    frequency *= self.lacunarity

                # Store the final layered value
                world[i][j] = noise_val
                
                # Update bounds for normalization
                if noise_val < min_val: 
                    min_val = noise_val
                if noise_val > max_val: 
                    max_val = noise_val

        # Normalize the array so elevations range strictly from 0.0 to 1.0
        return self._normalize(world, min_val, max_val)

    def _normalize(self, world_array, min_val, max_val):
        """Internal helper method to normalize the terrain data."""
        if max_val == min_val:
            return np.zeros_like(world_array)
        return (world_array - min_val) / (max_val - min_val)