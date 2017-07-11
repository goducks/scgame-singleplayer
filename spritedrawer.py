import os
import sdl2
import sdl2.ext as sdl2ext
import sdl2.sdlimage as sdlimage
from ctypes import c_int, pointer
import drawable

class spriteMaker(object):
    def __init__(self, renderer, x, y, w, h, imagename, dupetexture, useimagesize=False):
        if imagename == '' and dupetexture is None:
            raise sdl2ext.SDLError()

        if isinstance(renderer, sdl2ext.Renderer):
            self.renderer = renderer.renderer
        elif isinstance(renderer, sdl2.render.SDL_Renderer):
            self.renderer = renderer

        if dupetexture is not None:
            self.texture = dupetexture
        else:
            fullpath = os.path.join(os.path.dirname(__file__), 'resources/images', imagename)
            self.texture = self._createTexture(fullpath)
        if self.texture is None:
            raise sdl2ext.SDLError()

        self.x = x
        self.y = y
        if useimagesize:
            # reset size if using image dimensions
            pw = pointer(c_int(0))
            ph = pointer(c_int(0))
            sdl2.SDL_QueryTexture(self.texture, None, None, pw, ph)
            self.width = pw.contents.value
            self.height = ph.contents.value
        else:
            self.width = w
            self.height = h

        drawable.Drawable.drawList.append(self)

    def _createTexture(self, fullpath):
        surface = sdlimage.IMG_Load(fullpath)
        if surface is None:
            raise sdlimage.IMG_GetError()
        texture = sdl2.render.SDL_CreateTextureFromSurface(self.renderer, surface)
        if texture is None:
            raise sdl2ext.SDLError()
        sdl2.surface.SDL_FreeSurface(surface)
        return texture

    def render(self):
        dst = sdl2.SDL_Rect(self.x, self.y, self.width, self.height)
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, dst)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getX(self):
        return self.x

    def getY(self):
        return self.y
