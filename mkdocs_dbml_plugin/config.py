HEADER_HEIGHT = 48
ROW_HEIGHT = 36
TABLE_BOTTOM_PADDING = 12
FIELD_Y_START = 66
TABLE_GROUP_PADDING = 24
SVG_PADDING = 50
CONN_GAP = 20.0

THEMES = {
    "default": {
        "gradient_start": "#667eea",
        "gradient_end": "#764ba2",
        "line_color": "#6366f1",
        "bg_color": "#f9fafb",
        "border_color": "#e5e7eb",
    },
    "ocean": {
        "gradient_start": "#2E3192",
        "gradient_end": "#1BFFFF",
        "line_color": "#0ea5e9",
        "bg_color": "#f0f9ff",
        "border_color": "#bae6fd",
    },
    "sunset": {
        "gradient_start": "#FA8BFF",
        "gradient_end": "#2BD2FF",
        "line_color": "#f43f5e",
        "bg_color": "#fff1f2",
        "border_color": "#fecdd3",
    },
    "forest": {
        "gradient_start": "#134E5E",
        "gradient_end": "#71B280",
        "line_color": "#10b981",
        "bg_color": "#f0fdf4",
        "border_color": "#bbf7d0",
    },
    "dark": {
        "gradient_start": "#4c1d95",
        "gradient_end": "#7c3aed",
        "line_color": "#818cf8",
        "bg_color": "#1f2937",
        "border_color": "#374151",
    },
    "dark_gray": {
        "gradient_start": "#4b5563",
        "gradient_end": "#6b7280",
        "line_color": "#9ca3af",
        "bg_color": "#1f2937",
        "border_color": "#374151",
    },
    "black": {
        "gradient_start": "#050505",
        "gradient_end": "#1a1a1a",
        "line_color": "#ffffff",
        "bg_color": "#000000",
        "border_color": "#141414",
    },
}


def get_theme_colors(theme_name="default"):
    return THEMES.get(theme_name, THEMES["default"])
