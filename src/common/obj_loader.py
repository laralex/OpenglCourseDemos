import logging
log = logging.getLogger(__file__)

import numpy as np
import re
import enum


COMMENT_REGEXP        = re.compile(
    r'#[^\n]*\n', flags=re.MULTILINE,)
FACE_REGEXP           = re.compile(
    r'^f\s+(\d+)(/(\d+)?(/(\d+))?)?\s+(\d+)(/(\d+)?(/(\d+))?)?\s+(\d+)(/(\d+)?(/(\d+))?)?(\s+(\d+)(/(\d+)?(/(\d+))?)?)?$')
POSITION_REGEXP       = re.compile(
    r'^v\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)$')
TEXTURE_COORDS_REGEXP = re.compile(
    r'^vt\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)(?:\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?))?$')
NORMAL_REGEXP         = re.compile(
    r'^vn\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)\s+(-?\d+(?:\.\d+)?(?:[Ee]-?\d+)?)$')

class AttributesLayout(enum.Enum):
    POS3 = 1
    TEX2 = 2
    NORM3 = 3
    POS3_TEX2 = 4
    POS3_NORM3 = 5
    TEX2_NORM3 = 6
    POS3_TEX2_NORM3 = 7

    def as_iterable(self):
        return {
            self.POS3           : tuple(self.POS3),
            self.TEX2           : tuple(self.POS3),
            self.NORM3          : tuple(self.NORM3),
            self.POS3_TEX2      : tuple(self.POS3, self.TEX2),
            self.POS3_NORM3     : tuple(self.POS3, self.NORM3),
            self.TEX2_NORM3     : tuple(self.TEX2, self.NORM3),
            self.POS3_TEX2_NORM3: tuple(self.POS3, self.TEX2, self.NORM3),
        }[self.value]

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

    > from obj_loader import ParsedWavefront, AttributesLayout
    > scene = ParsedWavefront('path/to/scene.obj')
    > attributes   = scene.attributes_as_numpy(AttributesLayout.POS3_TEX2)
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
        def none2zero(x):
            return 0.0 if x is None else float(x)

        positions          , positions_indices           = [], []
        texture_coordinates, texture_coordinates_indices = [], []
        normals            , normals_indices             = [], []

        wavefront_str = COMMENT_REGEXP.sub('\n', wavefront_str)
        for line_idx, line in enumerate(wavefront_str.splitlines()):
            line = line.strip()

            if not line:
                continue

            parsed = False

            for regexp, destination in [
                (POSITION_REGEXP        , positions),
                (TEXTURE_COORDS_REGEXP  , texture_coordinates),
                (NORMAL_REGEXP          , normals)]:

                match = regexp.match(line)
                if match is not None:
                    destination.append(tuple(map(none2zero, match.groups())))
                    parsed = True
                    break

            if parsed:
                continue

            match = FACE_REGEXP.match(line)
            if match is not None:
                def add_vertex_indices(regexp_groups):
                    v, t, n = match.group(*regexp_groups)
                    positions_indices.append(int(v))
                    if t:
                        texture_coordinates_indices.append(int(t))
                    if n:
                        normals_indices.append(int(t))

                add_vertex_indices(1 , 3 , 5 )
                add_vertex_indices(6 , 8 , 10)
                add_vertex_indices(11, 13, 15)
                if match.group(16) is not None:
                    # it's a quad, split into two triangles
                    add_vertex_indices(1 , 3 , 5 )
                    add_vertex_indices(11, 13, 15)
                    add_vertex_indices(17, 19, 21)

            log.debug(f'Unsupported line {line_idx+1}:"{line}"')

        if any(len(arr) not in [0, len(positions_indices)]
               for arr in [texture_coordinates_indices, normals_indices]):
            raise Exception(f'Inconsistent faces definition"')

        return (positions, positions_indices), \
               (texture_coordinates, texture_coordinates_indices), \
               (normals, normals_indices)


    def attributes_as_numpy(self, attributes_layout: AttributesLayout, dtype=np.float32) -> np.array:
        assert isinstance(attributes_layout, AttributesLayout),\
            "Use only objects of type VertexAttribute to specify attributes_order"

        attributes = {
            AttributesLayout.POS3  : self.positions[self.positions_indices],
            AttributesLayout.TEX2  : self.texture_coordinates[self.texture_coordinates_indices],
            AttributesLayout.NORM3 : self.normals[self.normals_indices],
        }

        interleaved_data = np.hstack(
            attributes[k]
            for k in attributes_layout.as_iterable())
        return np.ascontiguousarray(interleaved_data, dtype=dtype)

    def faces_as_numpy(self, dtype=np.uint32):
        return np.ascontiguousarray(self.faces, dtype=dtype)

if __name__ == "__main__":
    scene = ParsedWavefront('../../assets/spot_cow/spot_control_mesh.obj')
    attributes   = scene.attributes_as_numpy(AttributesLayout.POS3_TEX2)
    face_indices = scene.faces_as_numpy()
    print(attributes)
    print(face_indices)
