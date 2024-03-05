from svg_to_kml import find_svg
from xml.dom import minidom
from shapely.geometry import Polygon
import numpy as np
import os










# def get_rectangles(svg_doc):
#     polygon_with_id = []
#     for irect, rect in enumerate(svg_doc.getElementsByTagName('rect')):
#         x0 = float(rect.getAttribute('x'))
#         y0 = float(rect.getAttribute('y'))
#         id_ = rect.getAttribute('id')
#         rx = rect.getAttribute('rx')
#         if len(rx) > 0:
#             print("rx")
#         width = float(rect.getAttribute('width'))
#         height = float(rect.getAttribute('height'))
#         polygon = Polygon([(x0, y0),
#                            (x0 + width, y0),
#                            (x0 + width, y0 + height),
#                            (x0, y0 + height)
#                            ])
#         polygon_with_id.append({"id": id_, "geometries": polygon})
#     return polygon_with_id



svg_strings = []
for file in os.listdir(".\\input"):
    if file.endswith(".svg"):
        print(os.path.join("\\input", file))
        svg_strings.append(os.path.join("\\input", file))


for svg in svg_strings:
    doc = minidom.parse(f'.{svg}')
    for ig, g_1 in enumerate(doc.getElementsByTagName('g')):
        print(g_1.getAttribute('id'))