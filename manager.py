import json
import os
import sys
from pathlib import Path

def lighten_color(hex_color, amount=0.2):
    """Lightens a hex color by a given amount (0.0 to 1.0)."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    new_rgb = [min(255, int(c + (255 - c) * amount)) for c in rgb]
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

def darken_color(hex_color, amount=0.3):
    """Darkens a hex color by a given amount (0.0 to 1.0)."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    new_rgb = [max(0, int(c * (1 - amount))) for c in rgb]
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

def get_bg_colors(primary_hex):
    # Determine if warm or cool
    hex_color = primary_hex.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    is_warm = rgb[0] > rgb[2] # Red > Blue roughly

    if is_warm:
        light_bg = "#FCFAF8"
        dark_bg = "#1A1918"
    else:
        light_bg = "#F8FAFC"
        dark_bg = "#0F172A"
    
    light_border = darken_color(light_bg, 0.05)
    return light_bg, light_border, dark_bg

def generate_palette(primary_hex):
    light_bg, light_border, dark_bg = get_bg_colors(primary_hex)
    return {
        "BRAND_PRIMARY": primary_hex,
        "BRAND_LIGHT": lighten_color(primary_hex, 0.2),
        "BRAND_DARK": darken_color(primary_hex, 0.3),
        "LIGHT_BG": light_bg,
        "LIGHT_BORDER": light_border,
        "DARK_BG": dark_bg
    }

def setup_brand(name):
    print(f"Setting up brand: {name}")
    brand_path = Path(f"brands/{name}.json")
    
    brand_name = input("Enter brand name: ")
    ig_handle = input("Enter Instagram handle (e.g. @mybrand): ")
    primary_color = input("Enter primary brand color (hex): ")
    font_pref = input("Enter font preference (Editorial, Modern, Warm, Technical, Bold, Classic, Rounded): ")
    
    palette = generate_palette(primary_color)
    
    config = {
        "brand_name": brand_name,
        "ig_handle": ig_handle,
        "palette": palette,
        "font_preference": font_pref,
        "logo_initial": brand_name[0].upper() if brand_name else "B"
    }
    
    with open(brand_path, "w") as f:
        json.dump(config, f, indent=4)
    
    print(f"Brand config saved to {brand_path}")

def generate_carousel(brand_name, topic):
    # This would be where the agent generates the specific slide content
    # For now, we'll create a placeholder that shows the system works
    print(f"Generating carousel for {brand_name} on topic: {topic}")
    # ... logic to generate index.html using the brand config ...
    pass

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "setup":
        setup_brand(sys.argv[2] if len(sys.argv) > 2 else "default")
    else:
        print("Usage: python manager.py <setup|generate|export> <brand_name> [args...]")
