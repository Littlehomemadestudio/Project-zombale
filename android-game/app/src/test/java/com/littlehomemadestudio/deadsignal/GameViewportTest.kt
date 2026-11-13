package com.littlehomemadestudio.deadsignal

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class GameViewportTest {
    @Test
    fun tallPhoneLetterboxesVerticallyWithoutStretching() {
        val viewport = GameViewport.fit(1080, 2400)

        assertEquals(1.2f, viewport.scale, 0.0001f)
        assertEquals(0f, viewport.offsetX, 0.0001f)
        assertEquals(240f, viewport.offsetY, 0.0001f)
        assertEquals(450f, viewport.toWorldX(540f), 0.0001f)
        assertEquals(800f, viewport.toWorldY(1200f), 0.0001f)
        assertFalse(viewport.contains(540f, 200f))
        assertTrue(viewport.contains(540f, 240f))
        assertTrue(viewport.contains(540f, 2160f))
    }

    @Test
    fun standardPortraitUsesTheWholeSurface() {
        val viewport = GameViewport.fit(1080, 1920)

        assertEquals(1.2f, viewport.scale, 0.0001f)
        assertEquals(0f, viewport.offsetX, 0.0001f)
        assertEquals(0f, viewport.offsetY, 0.0001f)
        assertEquals(0f, viewport.toWorldX(0f), 0.0001f)
        assertEquals(1600f, viewport.toWorldY(1920f), 0.0001f)
    }

    @Test
    fun wideSurfaceCentersTheWorldHorizontally() {
        val viewport = GameViewport.fit(2400, 1080)

        assertEquals(0.675f, viewport.scale, 0.0001f)
        assertEquals(896.25f, viewport.offsetX, 0.01f)
        assertEquals(0f, viewport.offsetY, 0.0001f)
        assertFalse(viewport.contains(800f, 540f))
        assertTrue(viewport.contains(900f, 540f))
    }
}
