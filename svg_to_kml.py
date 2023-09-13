import os
from xml.dom import minidom
from svg.path import parse_path
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from svgpathtools import Path
import geopandas as gpd
from operator import itemgetter
from kmlfaster import create_kml
from kmlfaster import new_create_kml


def find_svg():
    svg_strings = []
    for file in os.listdir(".\\input"):
        if file.endswith(".svg"):
            print(os.path.join("\\input", file))
            svg_strings.append(os.path.join("\\input", file))
    return svg_strings


def get_rectangles(svg_doc):
    polygon_with_id = []
    polygons = []
    for irect, rect in enumerate(svg_doc.getElementsByTagName('rect')):
        # if irect > 0:
        # x0 = int(rect.getAttribute('x'))
        # y0 = int(rect.getAttribute('y'))
        x0 = float(rect.getAttribute('x'))
        y0 = float(rect.getAttribute('y'))
        id = rect.getAttribute('id')
        width = float(rect.getAttribute('width'))
        height = float(rect.getAttribute('height'))
        polygon = Polygon([(x0, y0),
                           (x0 + width, y0),
                           (x0 + width, y0 + height),
                           (x0, y0 + height)
                           ])
        polygons.append(polygon)
        polygon_with_id.append({"id": id, "geometries": polygon})
    # for isvg, svg in enumerate(svg_doc.getElementsByTagName('svg')):
    #     if isvg == 0:
    #         width = float(svg.getAttribute('width'))
    #         height = float(svg.getAttribute('height'))
    #         polygon = Polygon([(x0, y0),
    #                            (x0 + width, y0),
    #                            (x0 + width, y0 + height),
    #                            (x0, y0 + height)
    #                            ])
    #         print("this is the biggest polygon")
    #         print(polygon)
    #         polygons.append(polygon)

    return polygons, polygon_with_id


def get_paths(svg_doc):
    new_whole_path = []
    whole_path = []
    for ipath, path in enumerate(svg_doc.getElementsByTagName('path')):
        print('Path', ipath)
        d = path.getAttribute('d')
        id = path.getAttribute('id')
        print(id)
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
        new_whole_path.append({"id": id, "geometries": circle_path})
    return whole_path, new_whole_path


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


def new_attach_paths_to_polygon(whole_path, polygons):
    all_geometries = []
    for each_path in whole_path:
        circle = []
        for complex_num in each_path['geometries']:
            imaginary = complex_num.imag
            real = complex_num.real
            point = [float(real), float(imaginary)]
            circle.append(point)
        try:
            polygono = Polygon(circle)
            polygons.append({"id": each_path['id'], "geometries": polygono})
            all_geometries.append({"id": each_path['id'], "geometries": polygono})
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


def new_show_coords(polygons, factor):
    for polygon in polygons:
        # print(polygon)
        x, y = polygon['geometries'].exterior.xy
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
    print('This is the min tupel')
    print(min_x, min_y, max_x, max_y)
    return min_x, min_y, max_x, max_y


def new_determine_min(shape):
    test_list = []
    for each in shape:
        print(each['geometries'])
        test_list.append(each['geometries'])
    gpdf = gpd.GeoDataFrame(columns=['id', 'distance', 'feature'], geometry=[*test_list])
    bounds = gpdf.geometry.apply(lambda x: x.bounds).tolist()
    min_x, min_y, max_x, max_y = min(bounds, key=itemgetter(0))[0], min(bounds, key=itemgetter(1))[1], \
                                 max(bounds, key=itemgetter(2))[2], max(bounds, key=itemgetter(3))[
                                 3]
    print('This is the min tupel')
    print(min_x, min_y, max_x, max_y)
    return min_x, min_y, max_x, max_y


def shift_to_root(shape, diff_x, diff_y):
    all_geometries = []
    for i, polygons in enumerate(shape):
        xx, yy = polygons['geometries'].exterior.coords.xy
        x = xx.tolist()
        new_x = [each_x - diff_x for each_x in x]
        y = yy.tolist()
        new_y = [each_y - diff_y for each_y in y]
        poly = Polygon(zip(new_x, new_y))
        all_geometries.append({"id": polygons['id'], "geometries": poly})
    print(all_geometries)
    return all_geometries


def new_resize_polygons(list_of_poly, factor):
    all_geometries = []
    for i, polygons in enumerate(list_of_poly):
        xx, yy = polygons['geometries'].exterior.coords.xy
        x = xx.tolist()
        new_x = [each_x / factor for each_x in x]
        y = yy.tolist()
        new_y = [each_y / - factor for each_y in y]
        poly = Polygon(zip(new_x, new_y))
        all_geometries.append({"id": polygons['id'], "geometries": poly})
    print(all_geometries)
    return all_geometries


def get_working_dir():
    print(os.getcwd())
    path_to_wdir = os.getcwd()
    return path_to_wdir


def get_pixels(svg_doc):
    width = float(0)
    height = float(0)
    for isvg, svg in enumerate(svg_doc.getElementsByTagName('svg')):
        if isvg == 0:
            width = float(svg.getAttribute('width'))
            height = float(svg.getAttribute('height'))
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


def make_new_qlik_script():
    script_string = f""""


modified_1:
Load
	Name,
	Subfield(Area, '],[')								as all_coordinates
Resident [doc name/name2];

modified_2:
Load
	Name,
    PurgeChar(Subfield(all_coordinates, ',', 1), '[')	as x_Wert,
    PurgeChar(Subfield(all_coordinates, ',', 2), ']')	as y_Wert
Resident modified_1;

max_min_table:
Load
	max(replaced_x_Wert)								as max_x_Wert,
    max(replaced_y_Wert)								as max_y_Wert,
    min(replaced_x_Wert)								as min_x_Wert,
    min(replaced_y_Wert)								as min_y_Wert;
Load
	Replace(x_Wert, '.', ',')							as replaced_x_Wert,
    Replace(y_Wert, '.', ',')							as replaced_y_Wert
Resident modified_2;

Drop Table modified_1;


Let Oben_Breite = Peek('max_y_Wert', 0, 'max_min_table');
Let Links_Laenge = Peek('min_x_Wert', 0, 'max_min_table');
Let Unten_Breite = Peek('min_y_Wert', 0, 'max_min_table');
Let Rechts_Laenge = Peek('max_x_Wert', 0, 'max_min_table');

"""
    return script_string


"""define factor"""
fac = 1

cwd = get_working_dir()
os.environ['PROJ_LIB'] = f"{cwd}\\venv\\Lib\\site-packages\\pyproj\\proj_dir\\share\\proj"
import fiona

all_svgs = find_svg()

fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

for each in all_svgs:
    output_file_name = each[6:len(each)-4]
    doc = minidom.parse(f'.{each}')
    poly, polygon_with_id = get_rectangles(doc)
    added_path, new_added_path = get_paths(doc)
    pixels_width, pixels_height = get_pixels(doc)
    doc.unlink()
    poly = attach_paths_to_polygon(added_path, poly)
    new_poly = new_attach_paths_to_polygon(new_added_path, polygon_with_id)
    # resized_poly = resize_polygons(poly, fac)
    resized_poly = new_resize_polygons(new_poly, fac)
    # minx, miny, maxx, maxy = determine_min(resized_poly)
    minx, miny, maxx, maxy = new_determine_min(resized_poly)
    new_polygons = shift_to_root(resized_poly, minx, maxy)
    # new_polygons = resized_poly
    # insert_qlik_string = make_qlik_script(pixels_width, pixels_height, fac)
    insert_qlik_string = make_new_qlik_script()
    print(insert_qlik_string)
    # panda = gpd.GeoDataFrame(columns=['id', 'meta_x', 'meta_y'], geometry=[*new_polygons])
    # panda.to_file(f'.\\output{output_file_name}.kml', driver='LIBKML')
    # panda.to_file(f'.\\output{output_file_name}.geojson', driver="GeoJSON")
    # kml, kml_string = create_kml(new_polygons)
    print(new_polygons)
    kml, kml_string = new_create_kml(new_polygons)
    # print(kml_string)

    with open(f'./output/{output_file_name}.kml', 'w') as f:
        f.write(kml_string)

new_show_coords(new_polygons, fac)
