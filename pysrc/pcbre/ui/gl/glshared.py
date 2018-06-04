import pkg_resources

from pcbre.ui.gl.shadercache import ShaderCache
from pcbre.ui.gl.textrender import TextRender
from pcbre.ui.gl.textatlas import SDFTextAtlas

__author__ = "davidc"


sans_serif_atlas = SDFTextAtlas(
    pkg_resources.resource_filename("pcbre.resources", "Vera.ttf")
)


class GLShared(object):
    def __init__(self):
        self.shader_cache = ShaderCache()
        self.text = TextRender(self, sans_serif_atlas)

    def initializeGL(self):
        self.text.initializeGL()
        self.text.updateTexture()
