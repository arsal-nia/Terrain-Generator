import numpy as np

class BiomeManager:
    """
    Handles the translation of raw height map data into environmental biomes and colors.
    """
    def __init__(self):
        # Define elevation thresholds and their corresponding RGB colors.
        # The float represents the maximum elevation limit for that biome.
        self.biomes = [
            (0.35, [15, 94, 156]),      # Deep Water (Dark Blue)
            (0.45, [35, 137, 218]),     # Shallow Water (Light Blue)
            (0.50, [210, 180, 140]),    # Sand/Beach (Tan)
            (0.70, [34, 139, 34]),      # Forest/Grassland (Green)
            (0.85, [128, 128, 128]),    # Mountain/Rock (Gray)
            (1.00, [255, 255, 255])     # Snow (White)
        ]

    def apply_biomes(self, height_map):
        """
        Takes a 2D height map (floats 0.0 to 1.0) and returns a 3D NumPy array 
        representing the RGB image (width, height, 3).
        """
        # Get the dimensions of the incoming height map
        width, height = height_map.shape
        
        # Create an empty 3D array for the RGB values. 
        # We use dtype=np.uint8 because RGB color values range from 0 to 255.
        color_map = np.zeros((width, height, 3), dtype=np.uint8)

        # Iterate through every coordinate on the map
        for i in range(width):
            for j in range(height):
                elevation = height_map[i, j]
                
                # Check the elevation against our thresholds
                for threshold, color in self.biomes:
                    if elevation <= threshold:
                        color_map[i, j] = color
                        break # Stop checking once we find the correct biome
                        
        return color_map