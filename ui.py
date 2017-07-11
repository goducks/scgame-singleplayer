import os
import sdl2
import sdl2.ext as sdl2ext
import drawable
from ctypes import c_int, pointer
from sdl2.sdlttf import (TTF_OpenFont, TTF_CloseFont, TTF_RenderText_Shaded, TTF_GetError, TTF_Init, TTF_Quit )

class textMaker(drawable.GameObject):
    def __init__(self, renderer, text = "", xpos = 0, ypos = 0, fontSize = 24,
                       textColor = sdl2.pixels.SDL_Color(255, 255, 255),
                       backgroundColor = sdl2.pixels.SDL_Color(0, 0, 0), fontname = "Arial.ttf"):
        sdl2.SDL_ClearError()
        if isinstance(renderer, sdl2ext.Renderer):
            self.renderer = renderer.renderer
        elif isinstance(renderer, sdl2.render.SDL_Renderer):
            self.renderer = renderer
        else:
            raise TypeError("unsupported renderer type")

        # to make fonts work, create a folder in the same folder as this script called 'font'
        # this font can be downloaded from: http://www.glukfonts.pl/font.php?font=Glametrix
        #  font = os.path.join(os.path.dirname(__file__), 'font', 'Glametrix.otf')
        # this font is just copied from your Mac in /Library/fonts/Arial.ttf to the 'font' folder
        if fontname == "":
            raise TTF_GetError()

        TTF_Init()
        font = os.path.join(os.path.dirname(__file__), 'resources/fonts', fontname)
        p = sdl2.SDL_GetError()
        if font is None or not p == '':
            print p
            raise TTF_GetError()

        self.font = TTF_OpenFont(font, fontSize)
        if self.font is None:
            raise TTF_GetError()
        self._text = text
        self.x = xpos
        self.y = ypos
        self.fontSize = fontSize
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.texture = self._createTexture()
        drawable.Drawable.drawList.append(self)
        # TODO
        # I'm not sure if Sarah added this or if it was original code, but closing the font
        # at the end of the init means subsequent updateTexture calls will fail. It seems more
        # logical to keep the font open for the duration of the instance lifetime. That said,
        # at some point we need to ensure we are cleaning up properly
        # TTF_CloseFont(self.font)

    def _createTexture(self):
        textSurface = TTF_RenderText_Shaded(self.font, self._text, self.textColor, self.backgroundColor)
        if textSurface is None:
            raise TTF_GetError()
        texture = sdl2.render.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        if texture is None:
            raise sdl2ext.SDLError()
        sdl2.surface.SDL_FreeSurface(textSurface)
        return texture

    def _updateTexture(self):
        textureToDelete = self.texture
        self.texture = self._createTexture()
        sdl2.render.SDL_DestroyTexture(textureToDelete)

    def render(self):
        dst = sdl2.SDL_Rect(self.x, self.y)
        w = pointer(c_int(0))
        h = pointer(c_int(0))
        sdl2.SDL_QueryTexture(self.texture, None, None, w, h)
        dst.w = w.contents.value
        dst.h = h.contents.value
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, dst)

    def getText(self):
        return self._text

    def setText(self, value):
        if self._text == value:
            return
        self._text = value
        self._updateTexture()

    def update(self, time):
        pass

class renderLives(textMaker):
    def __init__(self, renderer, lives, xpos, ypos):
        self.message = "Lives " + str(lives)
        self.x = xpos
        self.y = ypos
        renderLives.renderer = renderer
        super(renderLives, self).__init__(self.renderer, self.message, self.x, self.y,
                                          16, fontname="8-BIT WONDER.TTF")

    def updateLives(self, lives):
        self.message = "Lives " + str(lives)
        self.setText(self.message)

class renderScore(textMaker):
    def __init__(self, renderer, score, xpos, ypos):
        self.message = "Score " + str(score)
        self.x = xpos
        self.y = ypos
        renderScore.renderer = renderer
        super(renderScore, self).__init__(self.renderer, self.message, self.x, self.y,
                                          16, fontname="8-BIT WONDER.TTF")

    def updateScore(self, score):
        self.message = "Score " + str(score)
        self.setText(self.message)
