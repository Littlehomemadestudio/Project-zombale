package com.littlehomemadestudio.deadsignal

import kotlin.math.min

/**
 * Uniform, centered mapping between the fixed 900x1600 game world and a device surface.
 * The full world remains visible on every aspect ratio; unused space is letterboxed.
 */
data class GameViewport(
    val scale: Float,
    val offsetX: Float,
    val offsetY: Float
) {
    fun toWorldX(pixelX: Float): Float = (pixelX - offsetX) / scale
    fun toWorldY(pixelY: Float): Float = (pixelY - offsetY) / scale

    fun contains(pixelX: Float, pixelY: Float): Boolean =
        pixelX >= offsetX &&
            pixelX <= offsetX + GameEngine.WORLD_WIDTH * scale &&
            pixelY >= offsetY &&
            pixelY <= offsetY + GameEngine.WORLD_HEIGHT * scale

    companion object {
        fun fit(width: Int, height: Int): GameViewport {
            val surfaceWidth = width.coerceAtLeast(1).toFloat()
            val surfaceHeight = height.coerceAtLeast(1).toFloat()
            val scale = min(
                surfaceWidth / GameEngine.WORLD_WIDTH,
                surfaceHeight / GameEngine.WORLD_HEIGHT
            )
            val renderedWidth = GameEngine.WORLD_WIDTH * scale
            val renderedHeight = GameEngine.WORLD_HEIGHT * scale
            return GameViewport(
                scale = scale,
                offsetX = (surfaceWidth - renderedWidth) / 2f,
                offsetY = (surfaceHeight - renderedHeight) / 2f
            )
        }
    }
}
