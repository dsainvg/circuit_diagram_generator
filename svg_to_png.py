
import os
import sys

try:
    from PyQt5.QtGui import QImage, QPainter, QColor
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QSize
    USE_PYQT = True
except ImportError:
    USE_PYQT = False
    try:
        import cairosvg
    except ImportError:
        cairosvg = None

def svg_to_png(svg_path, output_dir='outputs'):
    # Create outputs directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Get filename without extension
    filename = os.path.splitext(os.path.basename(svg_path))[0]
    
    # Create output path
    output_path = os.path.join(output_dir, f'{filename}.png')
    
    if USE_PYQT:
        # Create a QApplication instance if one doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            raise ValueError(f"Invalid SVG file: {svg_path}")
            
        size = renderer.defaultSize()
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        
        image.save(output_path)
        
    elif cairosvg:
        # Convert SVG to PNG
        cairosvg.svg2png(url=svg_path, write_to=output_path)
    else:
        raise ImportError("No suitable SVG library found. Please install PyQt5 or cairosvg.")
    
    return output_path

if __name__ == "__main__":
    svg_path = "circuit_diagram.svg"
    output_path = svg_to_png(svg_path)
    print(f"SVG converted to PNG: {output_path}")
    # Replace with your SVG file path