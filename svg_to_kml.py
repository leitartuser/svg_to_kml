import os
from xml.dom import minidom
from svg.path import parse_path
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from svgpathtools import Path
import geopandas as gpd
from operator import itemgetter


def find_svg():
    svg_strings = []
    for file in os.listdir(".\\input"):
        if file.endswith(".svg"):
            print(os.path.join("\\input", file))
            svg_strings.append(os.path.join("\\input", file))
    return svg_strings


def get_rectangles(svg_doc):
    polygons = []
    for irect, rect in enumerate(svg_doc.getElementsByTagName('rect')):
        # if irect > 0:
        x0 = int(rect.getAttribute('x'))
        y0 = int(rect.getAttribute('y'))
        width = float(rect.getAttribute('width'))
        height = float(rect.getAttribute('height'))
        polygon = Polygon([(x0, y0),
                           (x0 + width, y0),
                           (x0 + width, y0 + height),
                           (x0, y0 + height)
                           ])
        polygons.append(polygon)
    return polygons


def get_paths(svg_doc):
    whole_path = []
    for ipath, path in enumerate(svg_doc.getElementsByTagName('path')):
        print('Path', ipath)
        d = path.getAttribute('d')
        parsed = parse_path(d)
        print('Objects:\n', parsed, '\n' + '-' * 20)
        circle_path = []
        for obj in parsed:
            bezier_path = Path(obj)
            num_samples = 10
            for i in range(num_samples):
                if i > 0:
                    bezier = (bezier_path.point(i / (num_samples - 1)))
                    if bezier is not None:
                        circle_path.append(bezier)
        whole_path.append(circle_path)
    return whole_path


def attach_paths_to_polygon(whole_path, polygons):
    for each_path in whole_path:
        circle = []
        for complex_num in each_path:
            imaginary = complex_num.imag
            real = complex_num.real
            point = [float(real), float(imaginary)]
            circle.append(point)
        try:
            polygono = Polygon(circle)
            polygons.append(polygono)
        except:
            print("An exception occurred")
    return polygons


def show_coords(polygons, factor):
    for polygon in polygons:
        # print(polygon)
        x, y = polygon.exterior.xy
        x_float = [float(line) for line in x]
        y_float = [float(line) for line in y]
        plt.plot(x_float, y_float, c="black", linewidth=0.5)
    plt.xlim([0, 4 * 1000 / factor])
    plt.ylim([-4 * 1000 / factor, 0])

    return plt.show()


def determine_min(shape):
    gpdf = gpd.GeoDataFrame(columns=['id', 'distance', 'feature'], geometry=[*shape])
    bounds = gpdf.geometry.apply(lambda x: x.bounds).tolist()
    min_x, min_y, max_x, max_y = min(bounds, key=itemgetter(0))[0], min(bounds, key=itemgetter(1))[1], \
                                 max(bounds, key=itemgetter(2))[2], max(bounds, key=itemgetter(3))[
                                 3]
    print(min_x, min_y, max_x, max_y)
    return min_x, min_y, max_x, max_y


def shift_to_root(shape, diff_x, diff_y):
    all_geometries = []
    for i, polygons in enumerate(shape):
        xx, yy = polygons.exterior.coords.xy
        x = xx.tolist()
        new_x = [each_x - diff_x for each_x in x]
        y = yy.tolist()
        new_y = [each_y - diff_y for each_y in y]
        poly = Polygon(zip(new_x, new_y))
        all_geometries.append(poly)
    print(all_geometries)
    return all_geometries


def resize_polygons(list_of_poly, factor):
    all_geometries = []
    for i, polygons in enumerate(list_of_poly):
        xx, yy = polygons.exterior.coords.xy
        x = xx.tolist()
        new_x = [each_x / factor for each_x in x]
        y = yy.tolist()
        new_y = [each_y / - factor for each_y in y]
        poly = Polygon(zip(new_x, new_y))
        all_geometries.append(poly)
    print(all_geometries)
    return all_geometries


def get_working_dir():
    print(os.getcwd())
    path_to_wdir = os.getcwd()
    return path_to_wdir


def get_pixels(svg_doc):
    width = float(0)
    height = float(0)
    for irect, rect in enumerate(svg_doc.getElementsByTagName('rect')):
        if irect == 0:
            width = float(rect.getAttribute('width'))
            height = float(rect.getAttribute('height'))
    return width, height


def make_qlik_script(width, height, fac):
    script_string = f"""
Let vScale = {fac};
Let Breite = {width};
Let Höhe = {height};

Let Unten_Breite = -$(Höhe)/$(vScale);
Let Links_Laenge = $(Breite)/$(vScale);

Let vScale;
Let Breite;
Let Höhe;
"""
    return script_string


"""define factor"""
fac = 100

cwd = get_working_dir()
os.environ['PROJ_LIB'] = f"{cwd}\\venv\\Lib\\site-packages\\pyproj\\proj_dir\\share\\proj"
import fiona

all_svgs = find_svg()

fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

for each in all_svgs:
    output_file_name = each[6:len(each)-4]
    doc = minidom.parse(f'.{each}')
    poly = get_rectangles(doc)
    added_path = get_paths(doc)
    pixels_width, pixels_height = get_pixels(doc)
    doc.unlink()
    poly = attach_paths_to_polygon(added_path, poly)
    resized_poly = resize_polygons(poly, fac)
    minx, miny, maxx, maxy = determine_min(resized_poly)
    new_polygons = shift_to_root(resized_poly, minx, maxy)
    insert_qlik_string = make_qlik_script(pixels_width, pixels_height, fac)
    print(insert_qlik_string)
    panda = gpd.GeoDataFrame(columns=['id', 'meta_x', 'meta_y'], geometry=[*new_polygons])
    panda.to_file(f'.\\output{output_file_name}.kml', driver='LIBKML')
    # panda.to_file(f'.\\output{output_file_name}.geojson', driver="GeoJSON")


show_coords(new_polygons, fac)
