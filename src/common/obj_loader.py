import logging
logger = logging.getLogger(__file__)

import numpy as np
import re
from typing import Tuple, List, Dict, Any

COMMENT_REGEXP = re.compile(r'#[^\n]*\n')
FLOAT_REGEXP  = re.compile(r'(?:\s+(-?\d*\.?\d*(?:[Ee][+-]?\d+)?))')
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
    > attributes = scene.as_numpy('P3_T2')
    > # or
    > attributes, face_indices = scene.as_numpy_indexed('N2_P2_T1')

    """

    def __init__(self, wavefront_filepath: str, parse=True, verbose=True):
        """wavefront_filepath: should be an existing file path to a Wavefront file
           parse: if True the long parsing operation will be run immediately
           verbose: if False, nothing will be logged in console"""
        self.filepath = wavefront_filepath
        self.verbose = verbose
        if parse:
            self.parse()

    def parse(self):
        """Run the long executing parsing operation"""
        with open(self.filepath, 'r') as f:
            self.parsed = ParsedWavefront.parse_string(f.read(), self.verbose)

    @staticmethod
    def parse_string(wavefront_str: str, verbose:bool = True) -> Dict[str, Any]:
        """Extracts data from a multiline string that follows Wavefront (OBJ) file format"""

        # data for glDrawArrays
        positions_parsed, positions_array_indices = [], []
        texcoords_parsed, texcoords_array_indices = [], []
        normals_parsed  , normals_array_indices   = [], []

        # data for glDrawElements
        positions_indices, texcoords_indices, normals_indices = [], [], []
        face_vertex_indices = []
        current_vertex_index = 0
        vertex_index_cache = {}

        # remove comments from parsing
        wavefront_str = COMMENT_REGEXP.sub('\n', wavefront_str)

        for line_idx, line in enumerate(wavefront_str.splitlines()):
            line = line.strip()
            if len(line) == 0:
                continue

            if line.startswith('vt'): # vertex texture coordinates
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                texcoords_parsed.append(attribute_floats)
            elif line.startswith('vn'): # vertex normals
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                normals_parsed.append(attribute_floats)
            elif line.startswith('v'): # vertex positions
                attribute_floats = tuple(map(float, FLOAT_REGEXP.findall(line)))
                positions_parsed.append(attribute_floats)
            elif line.startswith('f'): # face
                # helping function to parse indices of 1 vertex, which may be in forms:
                # 'a/b/c', 'a//c', 'a/b', 'a'
                def add_vertex_indices(*regexp_groups):
                    v, t, n = match.group(*regexp_groups)
                    v = int(v) - 1
                    positions_array_indices.append(v)
                    if t:
                        t = int(t) - 1
                        texcoords_array_indices.append(t)
                    if n:
                        n = int(n) - 1
                        normals_array_indices.append(n)
                    vertex_index = vertex_index_cache.get((v,t,n))
                    if not vertex_index:
                        nonlocal current_vertex_index
                        vertex_index_cache[(v,t,n)] = vertex_index = current_vertex_index
                        current_vertex_index += 1
                        positions_indices.append(v)
                        if t is not None: texcoords_indices.append(t)
                        if n is not None: normals_indices.append(n)
                    face_vertex_indices.append(vertex_index)


                match = FACE_REGEXP.match(line)
                if match is None:
                    if verbose: logger.warning(f'Bad face on line {line_idx+1}:"{line}"')
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
                if verbose: logger.warning(f'Unsupported line {line_idx+1}:"{line}"')
            if verbose: logger.debug(f'Processed line {line_idx+1}:"{line}"')

        # check that either for all faces a certain attribute is defined,
        # or for all faces the attribute is undifined (missing)
        if len(texcoords_array_indices) not in [0, len(positions_array_indices)] or \
           len(normals_array_indices)   not in [0, len(positions_array_indices)]:
            raise Exception(f'Inconsistent faces definition"')

        parse_result = dict(
            positions_parsed        = positions_parsed,
            positions_array_indices = positions_array_indices,
            positions_indices       = positions_indices,
            texcoords_parsed        = texcoords_parsed,
            texcoords_array_indices = texcoords_array_indices,
            texcoords_indices       = texcoords_indices,
            normals_parsed          = normals_parsed,
            normals_array_indices   = normals_array_indices,
            normals_indices         = normals_indices,
            face_vertex_indices     = face_vertex_indices,
        )
        return parse_result

    def as_numpy(self, attributes_layout: str, dtype=np.float32) -> np.array:
        """Returns an interleaved NumPy array of attributes (OpenGL ARRAY_BUFFER used with glDrawArrays) """
        p = self.parsed['positions_array_indices']
        t = self.parsed['texcoords_array_indices']
        n = self.parsed['normals_array_indices']
        interleaved_data = self.__make_interleaved_attributes(
            attributes_layout, dtype=dtype,
            positions_indices=p, texcoords_indices=t, normals_indices=n)

        return interleaved_data

    def as_numpy_indexed(self, attributes_layout: str, attrib_dtype=np.float32, indices_dtype=np.uint32) -> Tuple[np.array, np.array]:
        """Returns an interleaved NumPy array of attributes (OpenGL ARRAY_BUFFER) and respective
           index array which indexes the attributes array to define triangles (OpenGL ELEMENT_ARRAY_BUFFER)
           This pair can be used for OpenGL glDrawElements call"""
        p = self.parsed['positions_indices']
        t = self.parsed['texcoords_indices']
        n = self.parsed['normals_indices']
        interleaved_data = self.__make_interleaved_attributes(
            attributes_layout, dtype=attrib_dtype,
            positions_indices=p, texcoords_indices=t, normals_indices=n)

        face_vertex_indices = np.array(self.parsed['face_vertex_indices'], dtype=indices_dtype)

        return interleaved_data, face_vertex_indices

    def __make_interleaved_attributes(self, attributes_layout, positions_indices, texcoords_indices, normals_indices, dtype) -> np.array:
        """
        Parsed vertex attributes arrays may contain a different number of entries
        Given `positions_indices`, `texcoords_indices`, `normals_indices` of the same length,
        this function builds 1 numpy array with interleaved data for each vertex.
        For example (here P1 may mean 3 numbers (x,y,z))
        parsed: positions texcoords normals
                    P0       T0        N0
                    P1       T1        N1
                    P2                 N2
                    P3

        indices:    0        0         2
                    1        0         2
                    2        1         1
                    3        1         0
                    0        0         1
        and layout string: P3_N3_T2,
        the function constructs an array with the structure
                    P0       N3        T0
                    P1       N2        T0
                    P2       N1        T1
                    P3       N0        T1
                    P0       N1        T0
        """
        parts = parse_interleaved_layout(attributes_layout)

        attributes = {}
        if positions_indices:
            attributes['P'] = np.array(self.parsed['positions_parsed'])[np.array(positions_indices)]
        if texcoords_indices:
            attributes['T'] = np.array(self.parsed['texcoords_parsed'])[np.array(texcoords_indices)]
        if normals_indices:
            attributes['N'] = np.array(self.parsed['normals_parsed'])[np.array(normals_indices)]

        arrays_to_stack = []
        for key, used_coordinates in parts:
            assert key in attributes, f"OBJ file doesn't include data for part '{key}'"
            extension_width = max(0,used_coordinates-attributes[key].shape[1])
            if extension_width:
                attributes[key] = np.pad(attributes[key], ((0,0),(0,extension_width)))
            arrays_to_stack.append(attributes[key][:, :used_coordinates])

        interleaved_data = np.ascontiguousarray(
            np.hstack(arrays_to_stack), dtype=dtype)
        return interleaved_data

def parse_interleaved_layout(layout_str: str) -> List[Tuple[str, int]]:
    """ Parses the layout string into an array of tokens
        Example string: 'P3_T2_N3'
        Returns: [('P', 3), ('T', 2), ('N', 3)]
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
    print(list(map(float, FLOAT_REGEXP.findall('v 1 2.0 2. 0.3 -.03 -4E+3 .01e-1'))))
    assert list(map(float, FLOAT_REGEXP.findall('v 1 2.0 2. 0.3 -.03 -4E+3 .01e-1'))) == \
        [1.0, 2.0, 2.0, 0.3, -0.03, -4000.0, 0.001]

    print('Testing spot_control_mesh.obj')
    scene = ParsedWavefront('assets/spot_cow/spot_triangulated.obj')
    attributes               = scene.as_numpy('T1_P3')

    print('Attributes', attributes)
    print(attributes.size)
    attributes, face_indices = scene.as_numpy_indexed('T1_P3')
    print('Indexed attributes', attributes)
    print(attributes.size, 'indices:', face_indices.size)

    d = np.abs(attributes).sum(axis=-1)
    print(d.min(), d.mean(), d.max())
    hi = d > 4
    #print('@'*10, hi, attributes[hi])
    for i in range(hi.size):
        if hi[i]:
            print('Found', i, attributes[i])

    # print('Testing head.obj')
    # scene = ParsedWavefront('assets/human_head/head.obj')
    # attributes   = scene.as_numpy('P4_T1')
    # print(attributes)
    # print(attributes.shape)
    # attributes, face_indices = scene.as_numpy_indexed('P4_T1')
    # print('Indexed attributes', attributes)
    # print(attributes.shape, 'indices:', face_indices.shape)