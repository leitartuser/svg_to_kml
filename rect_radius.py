from svg_to_kml import find_svg
from xml.dom import minidom
from shapely.geometry import Polygon
import numpy as np











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

#
# all_svgs = find_svg()
#
#
# for svg in all_svgs:
#     doc = minidom.parse(f'.{svg}')
#     rectangles_with_id = get_rectangles(doc)