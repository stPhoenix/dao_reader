import json

json_d = json.dumps([
    {"type": "title",
     "title": "Read settings"},

    {"type": "options",
     "title": "Font",
     "desc": "Font for text",
     "section": "section1",
     "key": "font",
     "options": ["Times New Roman", "Ar"]},

    {"type": "numeric",
     "title": "Font size",
     "desc": "Font size",
     "section": "section1",
     "key": "font_size"},

    {"type": "options",
     "title": "Background color",
     "desc": "Color",
     "section": "section1",
     "key": "bg_color",
     "options": ["Sepia", "Black", 'White']}
])
