import logging
logger = logging.getLogger(__file__)

import numpy as np
import re

COMMENT_REGEXP = re.compile(r'#[^\n]*\n')
FLOAT_REGEXP  = re.compile(r'(?:\s+(-?\d*\.?\d*))')
FACE_REGEXP = re.compile(
    r'^f\s+(\d+)(?:/(\d+)?)?(?:/(\d+))?\s+(\d+)(?:/(\d+)?)?(?:/(\d+))?\s+(\d+)(?:/(\d+)?)?(?:/(\d+))?(?:\s+(\d+)(?:/(\d+)?)?(?:/(\d+))?)?$')

class ParsedWavefront:
    """
    Parses basic data from Wavefront data format (also known as .OBJ file):
    - vertex positions
    - vertex texture coordinates
    - vertex normals
    - indices for faces (quads are transformed into triangles).

    Comments starting with '#' are ignored
    Extended capabilities of Wavefront files are ignored (groups, materials, etc)

    Allows to comprise this data as interleaved NumPy arrays ready for OpenGL rendering\

    Example Usage:

    > import obj_loader
    > scene = obj_loader.ParsedWavefront('path/to/scene.obj')
    > attributes   = scene.attributes_as_numpy('P3_T2')
    > face_indices = scene.faces_as_numpy()

    """

    def __init__(self, wavefront_filepath: str, parse=True):
        self.filepath = wavefront_filepath
        if parse:
            self.parse()

    def parse(self):
        with open(self.filepath, 'r') as f:
            p, t, n = ParsedWavefront.parse_string(f.read())
        self.positions, self.positions_indices = p
        self.texture_coordinates, self.texture_coordinates_indices = t
        self.normals, self.normals_indices = n


    @staticmethod
    def parse_string(wavefront_str: str):
        positions          , positions_indices           = [], []
        texture_coordinates, texture_coordinates_indices = [], []
        normals            , normals_indices             = [], []

        wavefront_str = COMMENT_REGEXP.sub('\n', wavefront_str)

        for line_idx, line in enumerate(wavefront_str.splitlines()):
            line = line.strip()
            if len(line) == 0:
                continue

            if line.startswith('vt'): # vertex texture coordinates
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                texture_coordinates.append(attribute_floats)
            elif line.startswith('vn'): # vertex normals
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                normals.append(attribute_floats)
            elif line.startswith('v'): # vertex positions
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                positions.append(attribute_floats)
            elif line.startswith('f'): # face
                # helping function to parse 1 vertex indices which may be in fomrs:
                # 'a/b/c', 'a//c', 'a/b', 'a'
                def add_vertex_indices(*regexp_groups):
                    v, t, n = match.group(*regexp_groups)
                    positions_indices.append(int(v)-1)
                    if t: texture_coordinates_indices.append(int(t)-1)
                    if n: normals_indices.append(int(n)-1)


                match = FACE_REGEXP.match(line)
                if match is None:
                    logger.warning(f'Bad face on line {line_idx+1}:"{line}"')
                    continue

                add_vertex_indices(1 , 2 , 3 )
                add_vertex_indices(4 , 5 , 6 )
                add_vertex_indices(7 , 8 , 9 )
                if match.group(10) is not None:
                    # it's a quad, split into two triangles
                    add_vertex_indices(1 , 2 , 3 )
                    add_vertex_indices(7 , 8 , 9 )
                    add_vertex_indices(10, 11, 12)
            else:
                logger.warning(f'Unsupported line {line_idx+1}:"{line}"')
            logger.debug(f'Processed line {line_idx+1}:"{line}"')

        # check that either for all faces a certain attribute is defined,
        # or for all faces the attribute is undifined (missing)
        if len(texture_coordinates_indices) not in [0, len(positions_indices)] or \
           len(normals_indices)             not in [0, len(positions_indices)]:
            raise Exception(f'Inconsistent faces definition"')

        return (positions, positions_indices), \
               (texture_coordinates, texture_coordinates_indices), \
               (normals, normals_indices)



    def attributes_as_numpy(self, attributes_layout: str, dtype=np.float32) -> np.array:
        parts = parse_interleaved_layout(attributes_layout)
        attributes = {}

        if self.positions_indices:
            attributes['P'] = np.array(self.positions)[self.positions_indices]
        if self.texture_coordinates_indices:
            attributes['T'] = np.array(self.texture_coordinates)[self.texture_coordinates_indices]
        if self.normals_indices:
            attributes['N'] = np.array(self.normals)[self.normals_indices]

        arrays_to_stack = []
        for key, used_coordinates in parts:
            assert key in attributes, f"OBJ file doesn't include data for part '{key}'"
            extension_width = max(0,used_coordinates-attributes[key].shape[1])
            extended = np.pad(attributes[key], ((0,0),(0,extension_width)))
            arrays_to_stack.append(extended[:, :used_coordinates])

        interleaved_data = np.ascontiguousarray(
            np.hstack(arrays_to_stack), dtype=dtype)

        return interleaved_data

def parse_interleaved_layout(layout_str):
    """ Example string: 'P3_T2_N3'
    meaning 3 position values, 2 texture coordinates, 3 normal values"""
    parts = layout_str.upper().split('_')
    parsed_parts = []
    added_parts = set()
    for part in parts:
        assert part != '', "Must separate the parts with a single underscore '_'"
        assert len(part) == 2, "Each part should be of two characters: <letter><digit>"
        assert part[0] in ['P', 'T', 'N'], "Can only use part letter: 'P' (vertex positions), 'T' (texture coordinates), 'N' (vertex normals)"
        assert part[1].isdigit(), "Each part should be of two characters: <letter><digit>"
        assert part[0] not in added_parts, "Can't specify the same part twice"
        parsed_parts.append((part[0], int(part[1])))
        added_parts.add(part[0])
    return parsed_parts

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)

    # testing validity
    assert FACE_REGEXP.match('f 9//0 2/1/3 4/5').groups() == \
        ('9', None, '0', '2', '1', '3', '4', '5', None, None, None, None)
    assert FACE_REGEXP.match('f 0/1 2/3 4/5').groups() == \
        ('0', '1', None, '2', '3', None, '4', '5', None, None, None, None)
    assert FACE_REGEXP.match('f 0 2/1/3 4/5').groups() == \
        ('0', None, None, '2', '1', '3', '4', '5', None, None, None, None)
    assert list(map(float, FLOAT_REGEXP.findall('v 1 2.0 2. 0.3 -.03'))) == [1.0, 2.0, 2.0, 0.3, -0.03]

    print('Testing spot_control_mesh.obj')
    scene = ParsedWavefront('assets/spot_cow/spot_control_mesh.obj')
    attributes   = scene.attributes_as_numpy('T1_P3')
    # face_indices = scene.faces_as_numpy()
    # print(face_indices)
    # print(face_indices.shape)

    print('Testing head.obj')
    scene = ParsedWavefront('assets/human_head/head.obj')
    attributes   = scene.attributes_as_numpy('P4_T1')
    print(attributes)
    print(attributes.shape)
    # face_indices = scene.faces_as_numpy()
    # print(face_indices)
    # print(face_indices.shape)
