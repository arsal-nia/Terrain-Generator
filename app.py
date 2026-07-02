import sys
import random
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor

# Import our backend logic
from terrain_generator import Terrain
from biomes import BiomeManager

class TerrainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terrain Generator")
        self.setMinimumSize(1024, 768)
        
        # Initialize Backend
        self.current_seed = 42
        self.terrain = Terrain(width=256, height=256, seed=self.current_seed)
        self.biome_manager = BiomeManager()

        self._setup_ui()
        self._apply_stylesheet()
        self.generate_terrain() # Initial generation on load

    def _setup_ui(self):
        """Builds the layout with a strict, modern hierarchy."""
        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (Horizontal Split)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(32, 40, 32, 40)
        sidebar_layout.setSpacing(24)

        # Title
        title_label = QLabel("Procedural Terrain")
        title_label.setObjectName("h1")
        sidebar_layout.addWidget(title_label)

        # Settings Group
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(16)

        # Seed Input
        self.seed_input = self._create_input_group(settings_layout, "Seed", 0, 999999, self.current_seed)
        
        # Scale Slider
        self.scale_slider = self._create_slider_group(settings_layout, "Noise Scale", 10, 300, 100)
        
        # Octaves Slider
        self.octaves_slider = self._create_slider_group(settings_layout, "Octaves (Detail)", 1, 10, 6)
        
        # Persistence Slider (Multiplied by 100 for integer slider)
        self.persistence_slider = self._create_slider_group(settings_layout, "Roughness", 10, 90, 50)

        sidebar_layout.addLayout(settings_layout)

        # Randomize Button
        self.randomize_btn = QPushButton("Randomize Seed")
        self.randomize_btn.setObjectName("secondary_button")
        self.randomize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.randomize_btn.clicked.connect(self.randomize_seed)
        sidebar_layout.addWidget(self.randomize_btn)

        # Spacer to push the generate button to the bottom
        sidebar_layout.addStretch()

        # Generate Button (Primary Action)
        self.generate_btn = QPushButton("Generate Landscape")
        self.generate_btn.setObjectName("primary_button")
        self.generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_btn.clicked.connect(self.generate_terrain)
        sidebar_layout.addWidget(self.generate_btn)

        # --- RIGHT MAIN AREA ---
        main_area = QFrame()
        main_area.setObjectName("main_area")
        main_area_layout = QVBoxLayout(main_area)
        main_area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Image Container (Canvas)
        self.canvas_container = QFrame()
        self.canvas_container.setObjectName("canvas_container")
        self.canvas_container.setFixedSize(540, 540) # Add padding around 512x512 image
        canvas_layout = QVBoxLayout(self.canvas_container)
        canvas_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shadow for the canvas (Vercel/Stripe style subtle shadow)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 15)) # 15 out of 255 opacity
        shadow.setOffset(0, 10)
        self.canvas_container.setGraphicsEffect(shadow)

        self.image_label = QLabel()
        self.image_label.setFixedSize(512, 512)
        self.image_label.setScaledContents(True)
        canvas_layout.addWidget(self.image_label)

        main_area_layout.addWidget(self.canvas_container)

        # Add parts to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(main_area)

    def _create_input_group(self, parent_layout, label_text, min_val, max_val, default_val):
        """Creates a clean typography label and spinbox pair."""
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        label = QLabel(label_text)
        label.setObjectName("input_label")
        
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default_val)
        spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons) # Hide clunky arrows
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        parent_layout.addLayout(layout)
        return spinbox

    def _create_slider_group(self, parent_layout, label_text, min_val, max_val, default_val):
        """Creates a clean label and slider pair."""
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        label = QLabel(label_text)
        label.setObjectName("input_label")
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(label)
        layout.addWidget(slider)
        parent_layout.addLayout(layout)
        return slider

    def randomize_seed(self):
        new_seed = random.randint(0, 999999)
        self.seed_input.setValue(new_seed)
        self.generate_terrain()

    def generate_terrain(self):
        """Fetches UI parameters, updates terrain, and renders the image."""
        self.generate_btn.setText("Generating...")
        QApplication.processEvents() # Force UI update for the button text

        # 1. Fetch values
        seed = self.seed_input.value()
        scale = float(self.scale_slider.value())
        octaves = self.octaves_slider.value()
        persistence = float(self.persistence_slider.value()) / 100.0

        # 2. Update Generator
        # 2. Update Generator and Regenerate
        self.terrain.regenerate(
            new_seed=seed,
            new_scale=scale,
            new_octaves=octaves,
            new_persistence=persistence
        )

        # 3. Generate Math & Biomes
        color_map = self.biome_manager.apply_biomes(self.terrain.height_map)

        # 4. Convert NumPy array to QPixmap for rendering
        # Ensure memory is contiguous and transposed correctly for QImage
        color_map = np.ascontiguousarray(np.transpose(color_map, (1, 0, 2)))
        height, width, channels = color_map.shape
        bytes_per_line = channels * width
        
        q_img = QImage(color_map.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # 5. Display
        self.image_label.setPixmap(pixmap)
        self.generate_btn.setText("Generate Landscape")

    def _apply_stylesheet(self):
        """Injects a modern, premium QSS (CSS) stylesheet."""
        self.setStyleSheet("""
            /* Global settings */
            QMainWindow, QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
                color: #111827; /* Very dark gray for text */
            }

            /* Main Areas */
            #sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E5E7EB; /* Thin, soft border */
            }
            #main_area {
                background-color: #F9FAFB; /* Soft off-white */
            }

            /* Typography */
            #h1 {
                font-size: 20px;
                font-weight: 600;
                color: #000000;
                letter-spacing: -0.5px;
            }
            #input_label {
                font-size: 12px;
                font-weight: 500;
                color: #6B7280; /* Subtle label gray */
            }

            /* Inputs */
            QSpinBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #FFFFFF;
                font-size: 14px;
            }
            QSpinBox:focus {
                border: 1px solid #000000; /* Crisp focus state */
            }

            /* Sliders */
            QSlider::groove:horizontal {
                border-radius: 2px;
                height: 4px;
                background: #E5E7EB;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                border: 1px solid #000000;
            }

            /* Primary Button (Vercel/Linear style dark button) */
            #primary_button {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 14px;
            }
            #primary_button:hover {
                background-color: #1F2937;
            }
            #primary_button:pressed {
                background-color: #374151;
            }

            /* Secondary Button (Minimalist outline) */
            #secondary_button {
                background-color: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 500;
                font-size: 13px;
            }
            #secondary_button:hover {
                background-color: #F3F4F6;
                color: #000000;
            }

            /* Canvas Container (The frame holding the map) */
            #canvas_container {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern apps look best without the standard Windows/macOS focus rectangles
    app.setStyle("Fusion") 
    
    window = TerrainApp()
    window.show()
    sys.exit(app.exec())