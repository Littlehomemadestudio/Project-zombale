package com.littlehomemadestudio.deadsignal

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.Typeface
import kotlin.math.cos
import kotlin.math.sin

class GameRenderer {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val path = Path()
    private val scratch = RectF()
    private val bold = Typeface.create("sans-serif-condensed", Typeface.BOLD)
    private val medium = Typeface.create("sans-serif-medium", Typeface.NORMAL)
    private val white = Color.rgb(235, 239, 231)
    private val muted = Color.rgb(133, 151, 157)
    private val amber = Color.rgb(245, 184, 75)
    private val red = Color.rgb(217, 78, 66)
    private val ink = Color.rgb(8, 14, 20)

    fun draw(canvas: Canvas, engine: GameEngine, bestScore: Int) {
        canvas.drawColor(Color.rgb(3, 7, 10))
        val viewport = GameViewport.fit(canvas.width, canvas.height)
        val save = canvas.save()
        canvas.translate(viewport.offsetX, viewport.offsetY)
        canvas.scale(viewport.scale, viewport.scale)
        drawCorridor(canvas)
        when (engine.state) {
            RunState.MENU -> drawMenu(canvas, bestScore)
            RunState.PLAYING, RunState.PAUSED -> {
                drawBarricade(canvas, engine)
                drawPlayer(canvas, engine)
                engine.zombies.forEach { drawZombie(canvas, it) }
                drawParticles(canvas, engine)
                drawReticle(canvas, engine)
                drawHud(canvas, engine, bestScore)
                if (engine.state == RunState.PAUSED) drawPause(canvas)
            }
            RunState.GAME_OVER -> {
                drawBarricade(canvas, engine)
                drawPlayer(canvas, engine)
                engine.zombies.forEach { drawZombie(canvas, it) }
                drawHud(canvas, engine, bestScore)
                drawEndCard(canvas, engine, false, bestScore)
            }
            RunState.VICTORY -> {
                drawBarricade(canvas, engine)
                drawPlayer(canvas, engine)
                drawHud(canvas, engine, bestScore)
                drawEndCard(canvas, engine, true, bestScore)
            }
        }
        canvas.restoreToCount(save)
    }

    private fun drawCorridor(c: Canvas) {
        paint.style = Paint.Style.FILL
        paint.shader = android.graphics.LinearGradient(
            0f, 0f, 900f, 1600f,
            intArrayOf(Color.rgb(15, 29, 37), Color.rgb(25, 38, 42), Color.rgb(9, 15, 21)),
            floatArrayOf(0f, 0.58f, 1f),
            android.graphics.Shader.TileMode.CLAMP
        )
        c.drawRect(0f, 0f, 900f, 1600f, paint)
        paint.shader = null

        paint.color = Color.rgb(29, 44, 48)
        path.reset()
        path.moveTo(0f, 0f)
        path.lineTo(900f, 0f)
        path.lineTo(740f, 700f)
        path.lineTo(150f, 700f)
        path.close()
        c.drawPath(path, paint)

        paint.color = Color.rgb(12, 21, 27)
        path.reset()
        path.moveTo(0f, 1600f)
        path.lineTo(900f, 1600f)
        path.lineTo(740f, 1090f)
        path.lineTo(150f, 1090f)
        path.close()
        c.drawPath(path, paint)

        paint.color = Color.rgb(54, 69, 67)
        paint.strokeWidth = 5f
        c.drawLine(150f, 700f, 0f, 0f, paint)
        c.drawLine(740f, 700f, 900f, 0f, paint)
        c.drawLine(150f, 1090f, 0f, 1600f, paint)
        c.drawLine(740f, 1090f, 900f, 1600f, paint)

        for (i in 0..5) {
            val y = 735f + i * 72f
            val inset = i * 15f
            paint.color = if (i % 2 == 0) Color.rgb(37, 52, 56) else Color.rgb(31, 45, 50)
            c.drawRect(0f, y, 900f, y + 4f, paint)
            paint.color = Color.argb(45, 150, 175, 165)
            c.drawLine(0f, y + 7f, 900f, y + 7f, paint)
            paint.color = Color.rgb(62, 76, 72)
            c.drawRect(38f + inset, y - 22f, 52f + inset, y + 28f, paint)
            c.drawRect(848f - inset, y - 22f, 862f - inset, y + 28f, paint)
        }

        paint.color = Color.rgb(72, 85, 79)
        c.drawRoundRect(332f, 130f, 568f, 180f, 9f, 9f, paint)
        paint.color = Color.rgb(171, 177, 144)
        c.drawRoundRect(350f, 140f, 550f, 148f, 4f, 4f, paint)
        paint.color = Color.argb(35, 231, 210, 143)
        c.drawRect(350f, 148f, 550f, 270f, paint)

        for (i in 0..3) {
            val x = 80f + i * 210f
            paint.color = Color.rgb(50, 64, 64)
            c.drawRoundRect(x, 315f, x + 118f, 660f, 7f, 7f, paint)
            paint.color = Color.rgb(12, 22, 27)
            c.drawRoundRect(x + 10f, 330f, x + 108f, 646f, 4f, 4f, paint)
            paint.color = Color.rgb(76, 87, 78)
            c.drawRect(x + 17f, 355f, x + 21f, 625f, paint)
            paint.color = amber
            c.drawCircle(x + 92f, 493f, 4f, paint)
        }

        paint.color = Color.rgb(66, 77, 68)
        c.drawRect(0f, 1160f, 900f, 1166f, paint)
        paint.color = Color.argb(75, 245, 184, 75)
        for (i in 0..11) {
            val x = i * 82f
            path.reset()
            path.moveTo(x, 1600f)
            path.lineTo(x + 28f, 1600f)
            path.lineTo(x + 160f, 1167f)
            path.lineTo(x + 145f, 1167f)
            path.close()
            c.drawPath(path, paint)
        }

        paint.color = Color.argb(24, 0, 0, 0)
        c.drawRect(0f, 0f, 900f, 1600f, paint)
        paint.color = Color.argb(28, 245, 184, 75)
        c.drawCircle(470f, 410f, 250f, paint)
    }

    private fun drawBarricade(c: Canvas, engine: GameEngine) {
        val integrity = engine.barricadeHealth / GameEngine.MAX_BARRICADE
        paint.color = Color.rgb(11, 18, 22)
        c.drawRoundRect(242f, 735f, 294f, 1160f, 8f, 8f, paint)
        for (i in 0..5) {
            val y = 770f + i * 62f
            paint.color = if (integrity < 0.35f) Color.rgb(83, 48, 43) else Color.rgb(105, 82, 57)
            c.drawRoundRect(248f, y, 288f, y + 48f, 4f, 4f, paint)
            paint.color = Color.rgb(48, 42, 35)
            c.drawRect(252f, y + 7f, 284f, y + 11f, paint)
            paint.color = Color.rgb(176, 139, 84)
            c.drawCircle(256f, y + 8f, 2.5f, paint)
            c.drawCircle(280f, y + 39f, 2.5f, paint)
        }
        paint.color = Color.rgb(42, 47, 43)
        c.drawRect(238f, 740f, 246f, 1155f, paint)
        c.drawRect(290f, 740f, 298f, 1155f, paint)
        paint.color = Color.rgb(24, 30, 32)
        c.drawRoundRect(220f, 680f, 320f, 716f, 6f, 6f, paint)
        text(c, "BARRICADE", 270f, 703f, 15f, amber, Paint.Align.CENTER)
        c.drawRoundRect(218f, 720f, 322f, 729f, 4f, 4f, paint)
        paint.color = Color.rgb(51, 61, 59)
        c.drawRoundRect(220f, 721f, 320f, 728f, 4f, 4f, paint)
        paint.color = if (integrity < 0.3f) red else amber
        c.drawRoundRect(220f, 721f, 220f + 100f * integrity, 728f, 4f, 4f, paint)
    }

    private fun drawPlayer(c: Canvas, engine: GameEngine) {
        val x = GameEngine.PLAYER_X
        val y = GameEngine.PLAYER_Y
        val kick = engine.recoil * 7f
        paint.color = Color.argb(90, 0, 0, 0)
        c.drawOval(x - 70f, y + 118f, x + 75f, y + 145f, paint)

        paint.color = Color.rgb(16, 24, 28)
        path.reset()
        path.moveTo(x - 38f, y + 105f)
        path.lineTo(x - 28f, y + 8f)
        path.lineTo(x + 28f, y + 8f)
        path.lineTo(x + 43f, y + 105f)
        path.lineTo(x + 24f, y + 119f)
        path.lineTo(x - 26f, y + 119f)
        path.close()
        c.drawPath(path, paint)

        paint.color = Color.rgb(50, 67, 68)
        c.drawRoundRect(x - 33f, y - 9f, x + 34f, y + 91f, 18f, 18f, paint)
        paint.color = Color.rgb(20, 30, 34)
        c.drawRoundRect(x - 23f, y + 70f, x - 7f, y + 142f, 7f, 7f, paint)
        c.drawRoundRect(x + 8f, y + 70f, x + 24f, y + 142f, 7f, 7f, paint)

        paint.color = Color.rgb(163, 143, 116)
        c.drawCircle(x, y - 42f, 29f, paint)
        paint.color = Color.rgb(35, 43, 43)
        c.drawArc(x - 31f, y - 72f, x + 31f, y - 16f, 180f, 180f, true, paint)
        paint.color = Color.rgb(202, 181, 141)
        c.drawRect(x - 27f, y - 43f, x + 27f, y - 34f, paint)
        paint.color = Color.rgb(19, 29, 33)
        c.drawRect(x - 21f, y - 45f, x + 21f, y - 38f, paint)

        paint.color = Color.rgb(72, 91, 85)
        c.drawRoundRect(x + 9f, y + 4f, x + 63f, y + 25f, 9f, 9f, paint)
        paint.color = Color.rgb(28, 38, 39)
        c.drawRoundRect(x + 31f, y - 5f, x + 103f - kick, y + 12f, 5f, 5f, paint)
        paint.color = Color.rgb(8, 14, 18)
        c.drawRect(x + 83f - kick, y - 1f, x + 119f - kick, y + 5f, paint)
        paint.color = amber
        c.drawRect(x + 48f, y + 12f, x + 57f, y + 17f, paint)

        if (engine.shotFlash > 0f) {
            paint.color = Color.argb(220, 255, 205, 105)
            path.reset()
            path.moveTo(x + 116f - kick, y + 2f)
            path.lineTo(x + 158f, y - 13f)
            path.lineTo(x + 145f, y + 4f)
            path.lineTo(x + 160f, y + 17f)
            path.close()
            c.drawPath(path, paint)
        }
    }

    private fun drawZombie(c: Canvas, zombie: Zombie) {
        val x = zombie.x
        val y = zombie.y
        val bob = sin(zombie.phase.toDouble()).toFloat() * 5f
        val scale = when (zombie.kind) {
            EnemyKind.BRUTE -> 1.28f
            EnemyKind.RUNNER -> 0.82f
            EnemyKind.SHAMBLER -> 1f
        }
        val body = if (zombie.hitFlash > 0f) Color.rgb(223, 191, 151) else when (zombie.kind) {
            EnemyKind.BRUTE -> Color.rgb(91, 83, 66)
            EnemyKind.RUNNER -> Color.rgb(76, 111, 99)
            EnemyKind.SHAMBLER -> Color.rgb(89, 104, 91)
        }
        c.save()
        c.translate(x, y + bob)
        c.scale(scale, scale)
        paint.color = Color.argb(95, 0, 0, 0)
        c.drawOval(-38f, 94f, 43f, 112f, paint)

        paint.color = Color.rgb(26, 33, 31)
        c.drawRoundRect(-31f, 30f, -8f, 103f, 8f, 8f, paint)
        c.drawRoundRect(7f, 31f, 30f, 105f, 8f, 8f, paint)
        paint.color = body
        path.reset()
        path.moveTo(-33f, 15f)
        path.lineTo(-25f, -12f)
        path.lineTo(23f, -12f)
        path.lineTo(37f, 27f)
        path.lineTo(24f, 55f)
        path.lineTo(-27f, 50f)
        path.close()
        c.drawPath(path, paint)
        paint.color = Color.rgb(50, 63, 54)
        c.drawLine(-24f, -4f, -57f, 29f + bob, paint)
        c.drawLine(23f, 0f, 55f, 26f - bob, paint)
        paint.strokeWidth = 12f
        paint.strokeCap = Paint.Cap.ROUND
        c.drawLine(-24f, -4f, -57f, 29f, paint)
        c.drawLine(23f, 0f, 55f, 26f, paint)

        paint.color = body
        c.drawCircle(0f, -39f, 27f, paint)
        paint.color = Color.rgb(34, 42, 37)
        c.drawArc(-27f, -66f, 27f, -22f, 190f, 165f, false, paint)
        paint.strokeWidth = 5f
        paint.color = Color.rgb(31, 35, 29)
        c.drawLine(-15f, -43f, -5f, -40f, paint)
        c.drawLine(7f, -40f, 17f, -44f, paint)
        paint.color = if (zombie.kind == EnemyKind.BRUTE) amber else red
        c.drawCircle(-10f, -38f, 3.5f, paint)
        c.drawCircle(11f, -39f, 3.5f, paint)
        paint.color = Color.rgb(39, 34, 29)
        c.drawLine(-7f, -20f, 11f, -18f, paint)
        c.restore()

        if (zombie.health < zombie.kind.health) {
            val ratio = zombie.health.toFloat() / zombie.kind.health
            paint.color = Color.argb(180, 5, 10, 12)
            c.drawRoundRect(x - 34f, y - 92f, x + 34f, y - 84f, 4f, 4f, paint)
            paint.color = red
            c.drawRoundRect(x - 34f, y - 92f, x - 34f + 68f * ratio, y - 84f, 4f, 4f, paint)
        }
    }

    private fun drawParticles(c: Canvas, engine: GameEngine) {
        engine.particles.forEach { particle ->
            val alpha = (255f * (particle.life / particle.maxLife).coerceIn(0f, 1f)).toInt()
            paint.color = Color.argb(alpha, 237, 151, 87)
            c.drawCircle(particle.x, particle.y, 2.5f + particle.life * 5f, paint)
        }
    }

    private fun drawReticle(c: Canvas, engine: GameEngine) {
        val x = engine.aimX
        val y = engine.aimY
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 2.5f
        paint.color = if (engine.hitMarker > 0f) white else amber
        c.drawCircle(x, y, 20f, paint)
        c.drawLine(x - 31f, y, x - 9f, y, paint)
        c.drawLine(x + 9f, y, x + 31f, y, paint)
        c.drawLine(x, y - 31f, x, y - 9f, paint)
        c.drawLine(x, y + 9f, x, y + 31f, paint)
        paint.style = Paint.Style.FILL
    }

    private fun drawHud(c: Canvas, engine: GameEngine, bestScore: Int) {
        panel(c, 24f, 24f, 876f, 178f, Color.argb(225, 8, 16, 21))
        text(c, "DEAD SIGNAL", 52f, 74f, 34f, white)
        text(c, "FIELD OPERATIONS  /  " + engine.mode.name, 54f, 105f, 15f, amber)
        text(c, "SECTOR " + engine.wave.toString().padStart(2, '0'), 54f, 151f, 22f, white)
        text(c, "SCORE  " + engine.score, 330f, 74f, 24f, white)
        text(c, "BEST  " + maxOf(bestScore, engine.score), 332f, 105f, 15f, muted)
        text(c, "THREATS  " + engine.zombiesRemainingInWave, 332f, 151f, 17f, muted)

        text(c, "VITALS", 690f, 62f, 14f, muted)
        bar(c, 690f, 76f, 164f, 12f, engine.playerHealth / GameEngine.MAX_PLAYER_HEALTH, red)
        text(c, "AMMO", 690f, 119f, 14f, muted)
        text(c, engine.currentMagazine.toString().padStart(2, '0') + " / " + engine.currentReserve, 690f, 155f, 25f, white)
        if (engine.isReloading) text(c, "RELOADING", 690f, 179f, 12f, amber)

        panel(c, 22f, 1324f, 876f, 155f, Color.argb(225, 8, 16, 21))
        text(c, "HOLD TO AIM + FIRE", 450f, 1354f, 16f, muted, Paint.Align.CENTER)
        button(c, 40f, 1380f, 250f, 145f, "PATCH", engine.repairCharges.toString(), amber)
        button(c, 522f, 1380f, 690f, 145f, "RELOAD", "R", white)
        button(c, 710f, 1380f, 870f, 145f, "SWAP", engine.selectedWeapon.title, amber)
        text(c, "REPAIRS " + engine.repairCharges, 165f, 1510f, 13f, muted, Paint.Align.CENTER)
    }

    private fun drawMenu(c: Canvas, bestScore: Int) {
        paint.color = Color.argb(155, 3, 9, 13)
        c.drawRect(0f, 0f, 900f, 1600f, paint)
        text(c, "NIGHTFALL PROTOCOL", 450f, 390f, 23f, amber, Paint.Align.CENTER)
        text(c, "DEAD", 450f, 540f, 112f, white, Paint.Align.CENTER)
        text(c, "SIGNAL", 450f, 640f, 112f, white, Paint.Align.CENTER)
        paint.color = red
        c.drawRect(282f, 676f, 618f, 683f, paint)
        text(c, "THE LAST SAFE LINE IS BREAKING.", 450f, 740f, 20f, muted, Paint.Align.CENTER)
        panel(c, 120f, 835f, 780f, 1160f, Color.argb(225, 8, 17, 22))
        text(c, "01  /  CLEAR THE SECTORS", 450f, 890f, 19f, amber, Paint.Align.CENTER)
        button(c, 165f, 930f, 735f, 1030f, "START CLEANUP", "5 SECTORS", amber)
        button(c, 165f, 1055f, 735f, 1155f, "HOLD THE LINE", "ENDLESS DEFENSE", white)
        text(c, "DRAG TO AIM  •  HOLD TO FIRE", 450f, 1260f, 19f, white, Paint.Align.CENTER)
        text(c, "PATCH THE BARRICADE  /  MANAGE YOUR MAGAZINE", 450f, 1300f, 14f, muted, Paint.Align.CENTER)
        text(c, "PERSONAL BEST  " + bestScore, 450f, 1450f, 17f, amber, Paint.Align.CENTER)
        text(c, "OFFLINE FIELD BUILD  •  v0.1", 450f, 1510f, 13f, muted, Paint.Align.CENTER)
    }

    private fun drawPause(c: Canvas) {
        paint.color = Color.argb(185, 3, 8, 12)
        c.drawRect(0f, 0f, 900f, 1600f, paint)
        panel(c, 130f, 650f, 770f, 960f, Color.rgb(12, 23, 29))
        text(c, "FIELD PAUSED", 450f, 770f, 45f, white, Paint.Align.CENTER)
        text(c, "TAP ANYWHERE TO RESUME", 450f, 850f, 18f, amber, Paint.Align.CENTER)
    }

    private fun drawEndCard(c: Canvas, engine: GameEngine, victory: Boolean, bestScore: Int) {
        paint.color = Color.argb(190, 3, 8, 12)
        c.drawRect(0f, 0f, 900f, 1600f, paint)
        panel(c, 105f, 570f, 795f, 1090f, Color.rgb(12, 22, 28))
        text(c, if (victory) "SECTOR SECURED" else "LINE OVERRUN", 450f, 710f, 42f, if (victory) amber else red, Paint.Align.CENTER)
        text(c, "FINAL SCORE", 450f, 805f, 17f, muted, Paint.Align.CENTER)
        text(c, engine.score.toString(), 450f, 900f, 76f, white, Paint.Align.CENTER)
        text(c, "BEST  " + maxOf(bestScore, engine.score), 450f, 960f, 18f, amber, Paint.Align.CENTER)
        button(c, 165f, 1000f, 735f, 1090f, "RUN IT BACK", "TAP TO REDEPLOY", white)
    }

    private fun panel(c: Canvas, left: Float, top: Float, right: Float, bottom: Float, color: Int) {
        paint.color = color
        c.drawRoundRect(left, top, right, bottom, 18f, 18f, paint)
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 2f
        paint.color = Color.argb(95, 129, 154, 150)
        c.drawRoundRect(left, top, right, bottom, 18f, 18f, paint)
        paint.style = Paint.Style.FILL
        paint.color = amber
        c.drawRect(left + 18f, top + 18f, left + 24f, top + 52f, paint)
    }

    private fun button(c: Canvas, left: Float, top: Float, right: Float, bottom: Float, title: String, subtitle: String, accent: Int) {
        paint.color = Color.rgb(23, 37, 43)
        c.drawRoundRect(left, top, right, bottom, 13f, 13f, paint)
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 2f
        paint.color = Color.argb(180, accent ushr 16 and 255, accent ushr 8 and 255, accent and 255)
        c.drawRoundRect(left, top, right, bottom, 13f, 13f, paint)
        paint.style = Paint.Style.FILL
        text(c, title, (left + right) / 2f, top + 39f, 19f, accent, Paint.Align.CENTER)
        text(c, subtitle, (left + right) / 2f, top + 69f, 13f, muted, Paint.Align.CENTER)
    }

    private fun bar(c: Canvas, x: Float, y: Float, width: Float, height: Float, ratio: Float, color: Int) {
        paint.color = Color.rgb(38, 51, 55)
        c.drawRoundRect(x, y, x + width, y + height, height / 2f, height / 2f, paint)
        paint.color = color
        c.drawRoundRect(x, y, x + width * ratio.coerceIn(0f, 1f), y + height, height / 2f, height / 2f, paint)
    }

    private fun text(c: Canvas, value: String, x: Float, y: Float, size: Float, color: Int, align: Paint.Align = Paint.Align.LEFT) {
        paint.shader = null
        paint.style = Paint.Style.FILL
        paint.color = color
        paint.textSize = size
        paint.textAlign = align
        paint.typeface = if (size >= 20f) bold else medium
        c.drawText(value, x, y, paint)
    }
}
