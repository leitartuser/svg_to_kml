# Import the library
from fastkml import kml


def create_kml(list_of_polygons):
    # Create the root KML object
    k = kml.KML()
    ns = '{http://www.opengis.net/kml/2.2}'

    # Create a KML Document and add it to the KML root object
    d = kml.Document(ns, 'doc1', 'doc name', 'doc description')
    k.append(d)

    # Create a KML Folder and add it to the Document
    f = kml.Folder(ns, 'fid', 'f name', 'f description')
    d.append(f)

    # Create a KML Folder and nest it in the first Folder
    nf = kml.Folder(ns, 'nested-fid', 'nested f name', 'nested f description')
    f.append(nf)

    # Create a second KML Folder within the Document
    f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
    d.append(f2)
    for i, each in enumerate(list_of_polygons):
        # Create a Placemark with a simple polygon geometry and add it to the second folder of the Document
        id = each['id']
        if len(id) == 0:
            id = str(i)

        p = kml.Placemark(ns, id, id, 'description')

        p.geometry = each['geometries']
        f2.append(p)

    new_k = (k.to_string(prettyprint=True))
    return k, new_k

