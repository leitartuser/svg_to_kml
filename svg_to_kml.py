import os
from xml.dom import minidom
from svg.path import parse_path
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from svgpathtools import Path
import geopandas as gpd
from operator import itemgetter
from kmlfaster import create_kml
import math
import xmltodict
import sys


if len(sys.argv) > 1:
    batch_argument = sys.argv[1]
    if batch_argument == 1:
        id_variable = '@id'
    else:
        id_variable = '@inkscape:label'
else:
    id_variable = '@id' # default value

print(id_variable)


def find_svg():
    svg_strings = []
    for file in os.listdir(".\\input"):
        if file.endswith(".svg"):
            print(os.path.join("\\input", file))
            svg_strings.append(os.path.join("\\input", file))
    return svg_strings


def create_output_filename(inputa):
    return inputa.replace('-', '_')


def svg_to_dictionary(svg_string):
    with open(f".{svg_string}") as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
    return data_dict['svg']


def create_steps(start, stop):
    number_of_steps = 25
    i = 0
    step = (stop - start) / number_of_steps
    steps = []
    while i < number_of_steps + 1:
        x_value = start + (step * i)
        steps.append(x_value)
        i += 1
    return steps


def get_rectangles(rectangles, grp1_tf_matrix, id_var):
    g_1_translate_x, g_1_translate_y = grp1_tf_matrix['translate_x'], grp1_tf_matrix['translate_y']
    rtm = {"translate_x": 0, "translate_y": 0, "scale_factor_x": 1, "scale_factor_y": 1}
    polygon_with_id = []
    if isinstance(rectangles, dict):
        rectangle_point_seq = []
        print("This is rectangles: ")
        print(rectangles)
        x0 = float(rectangles['@x'])
        y0 = float(rectangles['@y'])
        id_ = rectangles[id_var]
        width = float(rectangles['@width'])
        height = float(rectangles['@height'])
        sum_y = g_1_translate_y
        sum_x = g_1_translate_x
        if '@rx' in rectangles.keys():
            rx = float(rectangles['@rx'])
            ry = float(rectangles['@ry'])
            # upper left corner (after switching the coordinate system)
            start, stop = x0, x0 + rx
            steps_lc = create_steps(start, stop)
            for x in steps_lc[::-1]:
                if rx ** 2 - (x - (x0 + rx)) ** 2 > 0:
                    y_minus = y0 + ry - (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + rx)) ** 2) + sum_y
                    rectangle_point_seq.append((x + sum_x, y_minus))
            # lower left corner (after switching the coordinate system)
            for x in steps_lc:
                if rx ** 2 - (x - (x0 + rx)) ** 2 > 0:
                    y_plus = y0 + height - ry + (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + rx)) ** 2) + sum_y
                    rectangle_point_seq.append((x + sum_x, y_plus))
            # lower right corner (after switching the coordinate system)
            start, stop = x0 + width - rx, x0 + width
            steps_rc = create_steps(start, stop)
            for x in steps_rc:
                if rx ** 2 - (x - (x0 + width - rx)) ** 2 > 0:
                    y_plus = y0 + height - ry + (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + width - rx)) ** 2) + sum_y
                    rectangle_point_seq.append((x + sum_x, y_plus))
            # upper right corner (after switching the coordinate system)
            for x in steps_rc[::-1]:
                if rx ** 2 - (x - (x0 + width - rx)) ** 2 > 0:
                    y_minus = y0 + ry - (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + width - rx)) ** 2)  + sum_y
                    rectangle_point_seq.append((x + sum_x, y_minus))
            polygon = Polygon(rectangle_point_seq)
        else:
            polygon = Polygon([(x0, y0),
                               (x0 + width, y0),
                               (x0 + width, y0 + height),
                               (x0, y0 + height)
                               ])
        polygon_with_id.append({"id": id_, "geometries": polygon})
    if isinstance(rectangles, list):
        for irect, rect in enumerate(rectangles):
            rectangle_point_seq = []
            x0 = float(rect['@x'])
            y0 = float(rect['@y'])
            id_ = rect[id_var]
            width = float(rect['@width'])
            height = float(rect['@height'])
            sum_y = g_1_translate_y
            sum_x = g_1_translate_x
            if '@rx' in rect.keys():
                rx = float(rect["@rx"])
                ry = float(rect["@ry"])
                # upper left corner (after switching the coordinate system)
                start, stop = x0, x0 + rx
                steps_lc = create_steps(start, stop)
                for x in steps_lc[::-1]:
                    if rx ** 2 - (x - (x0 + rx)) ** 2 > 0:
                        y_minus = y0 + ry - (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + rx)) ** 2) + sum_y
                        rectangle_point_seq.append((x + sum_x, y_minus))
                # lower left corner (after switching the coordinate system)
                for x in steps_lc:
                    if rx ** 2 - (x - (x0 + rx)) ** 2 > 0:
                        y_plus = y0 + height - ry + (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + rx)) ** 2) + sum_y
                        rectangle_point_seq.append((x + sum_x, y_plus))
                # lower right corner (after switching the coordinate system)
                start, stop = x0 + width - rx, x0 + width
                steps_rc = create_steps(start, stop)
                for x in steps_rc:
                    if rx ** 2 - (x - (x0 + width - rx)) ** 2 > 0:
                        y_plus = y0 + height - ry + (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + width - rx)) ** 2) + sum_y
                        rectangle_point_seq.append((x + sum_x, y_plus))
                # upper right corner (after switching the coordinate system)
                for x in steps_rc[::-1]:
                    if rx ** 2 - (x - (x0 + width - rx)) ** 2 > 0:
                        y_minus = y0 + ry - (ry / rx) * math.sqrt(rx ** 2 - (x - (x0 + width - rx)) ** 2) + sum_y
                        rectangle_point_seq.append((x + sum_x, y_minus))
                polygon = Polygon(rectangle_point_seq)
            else:
                polygon = Polygon([(x0, y0),
                                   (x0 + width, y0),
                                   (x0 + width, y0 + height),
                                   (x0, y0 + height)
                                   ])
            polygon_with_id.append({"id": id_, "geometries": polygon})
    return polygon_with_id


def get_circles(circles, transform_matrix, id_var):
    ctm = {"translate_x": 0, "translate_y": 0, "scale_factor_x": 1, "scale_factor_y": 1}
    if type(circles) == list:
        for circle in circles:
            x0, y0, r, id_ = float(circle['@cx']), float(circle['@cy']), float(circle['@r']), circle[id_var]
            if 'transform' in circle.keys():
                ctm = transform_matrix(circle['@transform'])
    else:
        x0, y0, r, id_ = float(circles['@cx']), float(circles['@cy']), float(circles['@r']), circles[id_var]
        if 'transform' in circles.keys():
            ctm = transform_matrix(circles['@transform'])
        polygon_with_id = construct_circles(id_, x0, y0, r, transform_matrix, ctm)
    return polygon_with_id


def construct_circles(id_, x0, y0, r, tf_matrix, circle_transform_matrix):
    stepsize = 0.1
    positions = []
    t_ = 0
    polygon_with_id = []
    sum_translate_x = tf_matrix["translate_x"] + circle_transform_matrix["translate_x"]
    sum_translate_y = tf_matrix["translate_y"] + circle_transform_matrix["translate_y"]
    while t_ < 2 * math.pi:
        positions.append(((r * math.cos(t_) + x0) * circle_transform_matrix["scale_factor_x"] + sum_translate_x,
                          (r * math.sin(t_) + y0) * circle_transform_matrix["scale_factor_y"] + sum_translate_y))
        t_ += stepsize
    polygon_with_id.append({"id": id_, "geometries": Polygon(positions)})
    return {"id": id_, "geometries": Polygon(positions)}


def get_ellipses(ellipses, grp1_tf_matrix, id_var):
    g_1_translate_x, g_1_translate_y = grp1_tf_matrix['translate_x'], grp1_tf_matrix['translate_y']
    ellipses_with_id = []
    etm = {"translate_x": 0, "translate_y": 0, "scale_factor_x": 1, "scale_factor_y": 1}
    for ellipse in ellipses:
        single_ellipse = []
        x0, y0, rx, ry = float(ellipse['@cx']), float(ellipse['@cy']), float(ellipse['@rx']), float(ellipse['@ry'])
        id_ = ellipse['@id']
        print("This is id_: " + str(id_))
        if 'transform' in ellipse.keys():
            etm = transform_matrix(ellipse['@transform'])
        start, stop = x0 - rx, x0 + rx
        number_of_steps = 25
        step = (stop - start)/number_of_steps
        steps_positiv = []
        i = 0
        # sum up translation
        sum_x = etm['translate_x'] + g_1_translate_x
        sum_y = etm['translate_y'] + g_1_translate_y
        while i < number_of_steps + 1:
            x_value = start + (step * i)
            steps_positiv.append(x_value)
            i += 1
        for each_step in steps_positiv:     # for the positive y-values (remember all coordinates have to be
            x = each_step + sum_x      # written in clockwise fashion)
            if rx**2 - (each_step - x0)**2 > 0:
                y_plus = y0 + (ry/rx) * math.sqrt(rx**2 - (each_step - x0)**2) + sum_y
                single_ellipse.append((x, y_plus))
            elif (rx**2 - (each_step - x0)**2) > -0.05:          # when the content of sqrt is negative
                y_plus = y0 + sum_y
                single_ellipse.append((x, y_plus))
        steps_negativ = steps_positiv[::-1]                     # Array in reversed sequence
        for each_step in steps_negativ:     # for the negative y-values
            x = each_step + sum_x
            if rx**2 - (each_step - x0)**2 > 0:
                y_minus = y0 - (ry/rx) * math.sqrt(rx**2 - (each_step - x0)**2) + sum_y
                single_ellipse.append((x, y_minus))
            elif (rx**2 - (each_step - x0)**2) > -0.05:          # when the content of sqrt is negative
                y_plus = y0 + sum_y
                single_ellipse.append((x, y_plus))
        ellipses_with_id.append({"id": id_, "geometries": Polygon(single_ellipse)})
    return ellipses_with_id


def transform_matrix(transform_string):
    a = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '.', '-']
    translate_x = 0
    translate_y = 0
    x_factor = 1
    y_factor = 1
    if transform_string.startswith("translate"):
        translate = ''.join([s for s in transform_string if s in a])
        translate_x, translate_y = float(translate.split(',')[0]), float(translate.split(',')[1])
    if transform_string.startswith("scale"):
        whitelist_num = set('0123456789,.-')
        factors = ''.join(filter(whitelist_num.__contains__, transform_string))
        x_factor = float(factors[:factors.find(",")])
        y_factor = float(factors[factors.find(",") + 1:])
    return {"translate_x": translate_x, "translate_y": translate_y,
            "scale_factor_x": x_factor, "scale_factor_y": y_factor}


def merge_polygons(circles, ellipses, paths, rectangles):
    polygons = []
    for circle in circles:
        polygons.append(circle)
    for every in paths:
        for path in every:
            polygons.append(path)
    for every in ellipses:
        for ellipse in every:
            polygons.append(ellipse)
    for every in rectangles:
        for rectangle in every:
            polygons.append(rectangle)
    return polygons


def build_geo_dataframe(list_of_geometries):
    polygons_geometries = []
    for each in list_of_geometries:
        polygons_geometries.append(each['geometries'])
    panda = gpd.GeoDataFrame(columns=['id', 'meta_x', 'meta_y'], geometry=[*polygons_geometries])
    panda.to_file(f'.\\output{output_file_name}.kml', driver='LIBKML')
    panda.to_file(f'.\\output{output_file_name}.geojson', driver="GeoJSON")
    return panda


def get_paths(path_list, tf_matrix, id_var):
    g_2_translate_x, g_2_translate_y = tf_matrix['translate_x'], tf_matrix['translate_y']
    full_path = []
    polygons = []
    for path in path_list:
        ptm = {"translate_x": 0, "translate_y": 0}
        print(path['@d'])
        d = path['@d']
        if '@transform' in path.keys():
            ptm = transform_matrix(path['@transform'])
        parsed = parse_path(d)
        print('Objects:\n', parsed, '\n' + '-' * 20)
        arc_path = []
        for obj in parsed:
            bezier_path = Path(obj)
            num_samples = 10
            for i in range(num_samples):
                if i > 0:
                    bezier = (bezier_path.point(i / (num_samples - 1)))  # needs svgpathtools 1.5.1
                    if bezier is not None:
                        arc_path.append(bezier)
        full_path.append({"id": path[id_var], "geometries": arc_path,
                          "translate_x": ptm['translate_x'], "translate_y": ptm['translate_y']})
    for each_path in full_path:
        translate_x = each_path['translate_x'] + g_2_translate_x
        translate_y = each_path['translate_y'] + g_2_translate_y
        path_geometry = []
        for complex_num in each_path['geometries']:
            imaginary = complex_num.imag + translate_y
            real = complex_num.real + translate_x
            point = [float(real), float(imaginary)]
            path_geometry.append(point)
        try:
            polygono = Polygon(path_geometry)
            polygons.append({"id": each_path['id'], "geometries": polygono})
            # all_geometries.append({"id": each_path['id'], "geometries": polygono})
        except:
            print("An exception occurred")
    return polygons


def show_coords(polygons, factor):
    for polygon in polygons:
        x, y = polygon['geometries'].exterior.xy
        x_float = [float(line) for line in x]
        y_float = [float(line) for line in y]
        plt.plot(x_float, y_float, c="black", linewidth=0.5)
    plt.xlim([0, 4 * 1000 / factor])
    plt.ylim([-4 * 1000 / factor, 0])
    return plt.show()


def determine_min(shapes, whole_document):
    min_x = float(whole_document['rect']['@x'])
    min_y = float(whole_document['rect']['@y'])
    max_x = float(whole_document['rect']['@x']) + float(whole_document['rect']['@width'])
    max_y = float(whole_document['rect']['@y']) + float(whole_document['rect']['@height'])
    # if len(shapes) > 0:
    #     print(shapes)
    #     shapelist = []
    #     for shape in shapes:
    #         shapelist.append(shape['geometries'])
    #     gpdf = gpd.GeoDataFrame(columns=['id', 'distance', 'feature'], geometry=[*shapelist])
    #     bounds = gpdf.geometry.apply(lambda x: x.bounds).tolist()
    #     min_x, min_y, max_x, max_y = min(bounds, key=itemgetter(0))[0], min(bounds, key=itemgetter(1))[1], \
    #                                  max(bounds, key=itemgetter(2))[2], max(bounds, key=itemgetter(3))[
    #                                      3]
    #     print('This is the min tupel')
    #     print(min_x, min_y, max_x, max_y)
    # else:
    #     min_x, min_y, max_x, max_y = 0, 0, 0, 0
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
    return all_geometries


def resize_polygons(list_of_poly):
    factor = 1
    all_geometries = []
    for i, polygons in enumerate(list_of_poly):
        xx, yy = polygons['geometries'].exterior.coords.xy
        x = xx.tolist()
        new_x = [each_x / factor for each_x in x]
        y = yy.tolist()
        new_y = [each_y / - factor for each_y in y]
        poly = Polygon(zip(new_x, new_y))
        all_geometries.append({"id": polygons['id'], "geometries": poly})
    return all_geometries


def get_working_dir():
    print(os.getcwd())
    path_to_wdir = os.getcwd()
    return path_to_wdir


def get_pixels(svg_doc):
    a = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    width = float(0)
    height = float(0)
    for isvg, svg in enumerate(svg_doc.getElementsByTagName('svg')):
        if isvg == 0:
            raw_width = svg.getAttribute('width')
            cleaned_width = ''.join([s for s in raw_width if s in a])
            width = float(cleaned_width)
            raw_height = svg.getAttribute('height')
            cleaned_height = ''.join([s for s in raw_height if s in a])
            height = float(cleaned_height)
    return width, height


def make_new_qlik_script(min_x, min_y, max_x, max_y, file_name):
    script_string = f"""

Let {file_name}_Oben_Breite = -{round(float(min_y), 5)};
Let {file_name}_Links_Laenge = {round(float(min_x), 5)};
Let {file_name}_Unten_Breite = -{round(float(max_y), 5)};
Let {file_name}_Rechts_Laenge = {round(float(max_x), 5)};


"""

    return script_string


def main_routine(svg_geometery, id_):
    paths, circles, ellipses, rectangles = [], [], [], []
    for g_1 in svg_geometery['g']:
        g_1_transform_matrix = {"translate_x": 0, "translate_y": 0, "scale_factor_x": 1, "scale_factor_y": 1}
        if 'g' in g_1.keys():
            g_2 = g_1['g']
            for element in g_2:
                g_2_transform_matrix = {"translate_x": 0, "translate_y": 0, "scale_factor_x": 1, "scale_factor_y": 1}
                keys_of_element = element.keys()
                if '@transform' in keys_of_element:
                    g_2_transform_matrix = transform_matrix(element['@transform'])
                if 'path' in keys_of_element:
                    path_ = get_paths(element['path'], g_2_transform_matrix, id_)
                    paths.append(path_)
                if 'circle' in keys_of_element:
                    circle_ = get_circles(element['circle'], g_2_transform_matrix, id_)
                    circles.append(circle_)
                if 'rect' in keys_of_element:
                    rect_ = get_rectangles(element['rect'], g_2_transform_matrix, id_)
                    rectangles.append(rect_)
                if 'ellipse' in keys_of_element:
                    ellip_ = get_ellipses(element['ellipse'], g_2_transform_matrix, id_)
                    ellipses.append(ellip_)
        else:
            keys_of_g_1 = g_1.keys()
            if '@transform' in g_1.keys():
                g_1_transform_matrix = transform_matrix(g_1['@transform'])
            if 'path' in keys_of_g_1:
                path_ = get_paths(g_1['path'], g_1_transform_matrix, id_)
                paths.append(path_)
            if 'circle' in keys_of_g_1:
                circle_ = get_circles(g_1['circle'], g_1_transform_matrix, id_)
                circles.append(circle_)
            if 'rect' in keys_of_g_1:
                rect_ = get_rectangles(g_1['rect'], g_1_transform_matrix, id_)
                rectangles.append(rect_)
            if 'ellipse' in keys_of_g_1:
                ellip_ = get_ellipses(g_1['ellipse'], g_1_transform_matrix, id_)
                ellipses.append(ellip_)
        merged_polygons = merge_polygons(circles, ellipses, paths, rectangles)
        resized_polygons = resize_polygons(merged_polygons)
        kml, kml_string = create_kml(resized_polygons)
        with open(f'./output/{output_file_name}.kml', 'w') as f:
            f.write(kml_string)
    show_coords(resized_polygons, 1)
    return resized_polygons


"""define factor"""
devision_factor = 1


cwd = get_working_dir()
os.environ['PROJ_LIB'] = f"{cwd}\\venv\\Lib\\site-packages\\pyproj\\proj_dir\\share\\proj"
import fiona

all_svgs = find_svg()

fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

for each in all_svgs:
    input_file_name = each[7:len(each) - 4]
    output_file_name = create_output_filename(input_file_name)
    dictionary = svg_to_dictionary(each)
    result = main_routine(dictionary, id_variable)
    minx, miny, maxx, maxy = determine_min(result, dictionary)
    insert_qlik_string = make_new_qlik_script(minx, miny, maxx, maxy, output_file_name)
    print(insert_qlik_string)


