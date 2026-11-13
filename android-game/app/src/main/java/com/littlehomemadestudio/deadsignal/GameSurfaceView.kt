package com.littlehomemadestudio.deadsignal

import android.content.Context
import android.graphics.Canvas
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.SurfaceHolder
import android.view.SurfaceView
import kotlin.math.min

class GameSurfaceView @JvmOverloads constructor(
    context: Context,
    private val bestScore: () -> Int = { 0 },
    private val onRunEnded: (Int) -> Unit = {},
    attrs: AttributeSet? = null
) : SurfaceView(context, attrs), SurfaceHolder.Callback {
    private val engine = GameEngine()
    private val renderer = GameRenderer()
    @Volatile private var loopRunning = false
    @Volatile private var surfaceReady = false
    private var renderThread: Thread? = null
    private var lifecyclePaused = false
    private var pointerDown = false
    private var activeMode = RunMode.CLEANUP

    init {
        holder.addCallback(this)
        isFocusable = true
        isFocusableInTouchMode = true
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        surfaceReady = true
        startLoop()
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) = Unit

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        surfaceReady = false
        stopLoop()
    }

    fun pauseForLifecycle() {
        lifecyclePaused = true
        engine.pause()
        engine.setTrigger(false)
        stopLoop()
    }

    fun resumeForLifecycle() {
        lifecyclePaused = false
        engine.resume()
        startLoop()
    }

    fun release() {
        surfaceReady = false
        stopLoop()
    }

    private fun startLoop() {
        if (!surfaceReady || lifecyclePaused || loopRunning) return
        loopRunning = true
        renderThread = Thread({
            var previous = System.nanoTime()
            while (loopRunning) {
                val now = System.nanoTime()
                val delta = min(0.05f, (now - previous) / 1_000_000_000f)
                previous = now
                engine.update(delta)

                var canvas: Canvas? = null
                try {
                    canvas = holder.lockCanvas()
                    if (canvas != null) renderer.draw(canvas, engine, bestScore())
                } catch (_: IllegalArgumentException) {
                    // The surface can disappear between the readiness check and lockCanvas.
                } finally {
                    if (canvas != null) {
                        try {
                            holder.unlockCanvasAndPost(canvas)
                        } catch (_: IllegalArgumentException) {
                            // Surface teardown owns the canvas now.
                        }
                    }
                }

                if (engine.consumeEndNotification()) onRunEnded(engine.score)
                try {
                    Thread.sleep(16L)
                } catch (_: InterruptedException) {
                    Thread.currentThread().interrupt()
                    break
                }
            }
            loopRunning = false
        }, "DeadSignal-Render").apply {
            priority = Thread.NORM_PRIORITY
            start()
        }
    }

    private fun stopLoop() {
        loopRunning = false
        val thread = renderThread
        if (thread != null && thread !== Thread.currentThread()) {
            thread.interrupt()
            try {
                thread.join(700L)
            } catch (_: InterruptedException) {
                Thread.currentThread().interrupt()
            }
        }
        renderThread = null
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val viewport = GameViewport.fit(width, height)
        val worldX = viewport.toWorldX(event.x)
        val worldY = viewport.toWorldY(event.y)

        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                if (!viewport.contains(event.x, event.y)) {
                    pointerDown = false
                    engine.setTrigger(false)
                    return true
                }
                pointerDown = true
                when (engine.state) {
                    RunState.MENU -> {
                        if (worldY in 900f..1040f) startRun(RunMode.CLEANUP)
                        else if (worldY in 1045f..1175f) startRun(RunMode.DEFENSE)
                    }
                    RunState.GAME_OVER, RunState.VICTORY -> startRun(activeMode)
                    RunState.PAUSED -> engine.resume()
                    RunState.PLAYING -> {
                        if (worldY < 190f && worldX > 760f) {
                            engine.pause()
                        } else if (worldY >= 1370f) {
                            when {
                                worldX < 310f -> engine.repair()
                                worldX < 700f -> engine.reload()
                                else -> engine.switchWeapon()
                            }
                        } else {
                            engine.setAim(worldX, worldY)
                            engine.setTrigger(true)
                        }
                    }
                }
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                if (pointerDown && engine.state == RunState.PLAYING) {
                    if (viewport.contains(event.x, event.y) && worldY < 1320f) {
                        engine.setAim(worldX, worldY)
                        engine.setTrigger(true)
                    } else {
                        engine.setTrigger(false)
                    }
                }
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                pointerDown = false
                engine.setTrigger(false)
                performClick()
                return true
            }
        }
        return true
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }

    private fun startRun(mode: RunMode) {
        activeMode = mode
        engine.start(mode)
        pointerDown = false
    }
}
