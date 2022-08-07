config_schema = {
    "name": str,
    "author": str,
    "description": str,
    "hideIconTitle": bool,
    "batteryPercentage": {
        "visible": bool,
        "onleft": bool,
        "offsetX": int,
        "offsetY": int,
        "font": str,
        "size": int,
        "color": str
    },
    "title": {
        "font": str,
        "size": int,
        "color": str
    },
    "hint": {
        "font": str,
        "size": int,
        "color": str
    },
    "currentpage": {
        "color": str
    },
    "total": {
        "color": str
    },
    "grid": {
        "font": str,
        "grid1x4": int,
        "grid3x4": int,
        "color": str,
        "selectedcolor": str
    },
    "list": {
        "font": str,
        "size": int,
        "color": str
    }
}
