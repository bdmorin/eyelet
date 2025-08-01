"""Catppuccin color themes for Eyelet TUI"""

from dataclasses import dataclass


@dataclass
class CatppuccinColors:
    """Color definitions for Catppuccin themes"""
    
    # Base colors
    rosewater: str
    flamingo: str
    pink: str
    mauve: str
    red: str
    maroon: str
    peach: str
    yellow: str
    green: str
    teal: str
    sky: str
    sapphire: str
    blue: str
    lavender: str
    
    # Surface colors
    text: str
    subtext1: str
    subtext0: str
    overlay2: str
    overlay1: str
    overlay0: str
    surface2: str
    surface1: str
    surface0: str
    base: str
    mantle: str
    crust: str


# Catppuccin Mocha (dark theme)
MOCHA = CatppuccinColors(
    # Base colors
    rosewater="#f5e0dc",
    flamingo="#f2cdcd",
    pink="#f5c2e7",
    mauve="#cba6f7",
    red="#f38ba8",
    maroon="#eba0ac",
    peach="#fab387",
    yellow="#f9e2af",
    green="#a6e3a1",
    teal="#94e2d5",
    sky="#89dceb",
    sapphire="#74c7ec",
    blue="#89b4fa",
    lavender="#b4befe",
    
    # Surface colors
    text="#cdd6f4",
    subtext1="#bac2de",
    subtext0="#a6adc8",
    overlay2="#9399b2",
    overlay1="#7f849c",
    overlay0="#6c7086",
    surface2="#585b70",
    surface1="#45475a",
    surface0="#313244",
    base="#1e1e2e",
    mantle="#181825",
    crust="#11111b",
)


# Catppuccin Latte (light theme)
LATTE = CatppuccinColors(
    # Base colors
    rosewater="#dc8a78",
    flamingo="#dd7878",
    pink="#ea76cb",
    mauve="#8839ef",
    red="#d20f39",
    maroon="#e64553",
    peach="#fe640b",
    yellow="#df8e1d",
    green="#40a02b",
    teal="#179299",
    sky="#04a5e5",
    sapphire="#209fb5",
    blue="#1e66f5",
    lavender="#7287fd",
    
    # Surface colors
    text="#4c4f69",
    subtext1="#5c5f77",
    subtext0="#6c6f85",
    overlay2="#7c7f93",
    overlay1="#8c8fa1",
    overlay0="#9ca0b0",
    surface2="#acb0be",
    surface1="#bcc0cc",
    surface0="#ccd0da",
    base="#eff1f5",
    mantle="#e6e9ef",
    crust="#dce0e8",
)


def get_theme_css(theme: CatppuccinColors) -> str:
    """Generate Textual CSS for a Catppuccin theme"""
    return f"""
    /* Catppuccin Theme Variables */
    App {{
        background: {theme.base};
        color: {theme.text};
    }}
    
    /* Primary colors for different elements */
    .primary {{ color: {theme.blue}; }}
    .secondary {{ color: {theme.mauve}; }}
    .success {{ color: {theme.green}; }}
    .warning {{ color: {theme.yellow}; }}
    .error {{ color: {theme.red}; }}
    .info {{ color: {theme.sky}; }}
    
    /* Surface colors */
    .surface {{ background: {theme.surface0}; }}
    .surface-1 {{ background: {theme.surface1}; }}
    .surface-2 {{ background: {theme.surface2}; }}
    
    /* Text hierarchy */
    .text {{ color: {theme.text}; }}
    .text-muted {{ color: {theme.subtext1}; }}
    .text-dim {{ color: {theme.subtext0}; }}
    
    /* Borders and overlays */
    .border {{ border: solid {theme.overlay0}; }}
    .border-focused {{ border: solid {theme.blue}; }}
    
    /* Button variants */
    Button {{
        background: {theme.surface1};
        color: {theme.text};
        border: none;
    }}
    
    Button:hover {{
        background: {theme.surface2};
    }}
    
    Button:focus {{
        background: {theme.surface2};
        border: solid {theme.blue};
    }}
    
    Button.primary {{
        background: {theme.blue};
        color: {theme.base};
    }}
    
    Button.primary:hover {{
        background: {theme.sapphire};
    }}
    
    Button.success {{
        background: {theme.green};
        color: {theme.base};
    }}
    
    Button.warning {{
        background: {theme.yellow};
        color: {theme.base};
    }}
    
    Button.error {{
        background: {theme.red};
        color: {theme.base};
    }}
    
    /* Input fields */
    Input {{
        background: {theme.surface0};
        color: {theme.text};
        border: solid {theme.overlay0};
    }}
    
    Input:focus {{
        border: solid {theme.blue};
    }}
    
    /* Lists and tables */
    DataTable {{
        background: {theme.base};
        color: {theme.text};
    }}
    
    DataTable > .datatable--header {{
        background: {theme.surface0};
        color: {theme.text};
        text-style: bold;
    }}
    
    DataTable > .datatable--cursor {{
        background: {theme.surface1};
        color: {theme.text};
    }}
    
    /* Scrollbars */
    ScrollBar {{
        background: {theme.surface0};
    }}
    
    ScrollBar > .scrollbar--thumb {{
        background: {theme.overlay0};
    }}
    
    /* Header and Footer */
    Header {{
        background: {theme.mantle};
        color: {theme.text};
    }}
    
    Footer {{
        background: {theme.mantle};
        color: {theme.text};
    }}
    
    /* Tabs */
    Tabs > Tab {{
        background: {theme.surface0};
        color: {theme.subtext1};
    }}
    
    Tabs > Tab.-active {{
        background: {theme.base};
        color: {theme.text};
        border-bottom: solid {theme.blue};
    }}
    
    /* Modals and overlays */
    ModalScreen {{
        background: rgba(0, 0, 0, 0.5);
    }}
    
    Modal {{
        background: {theme.base};
        border: solid {theme.overlay0};
    }}
    """