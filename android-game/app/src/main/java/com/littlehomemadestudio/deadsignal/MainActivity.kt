package com.littlehomemadestudio.deadsignal

import android.app.Activity
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.view.View

class MainActivity : Activity() {
    private lateinit var gameView: GameSurfaceView
    private val progress by lazy { getSharedPreferences("dead_signal_progress", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        window.decorView.systemUiVisibility =
            (View.SYSTEM_UI_FLAG_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN)

        gameView = GameSurfaceView(
            context = this,
            bestScore = { progress.getInt("best_score", 0) },
            onRunEnded = { score ->
                if (score > progress.getInt("best_score", 0)) {
                    progress.edit().putInt("best_score", score).apply()
                }
            }
        )
        setContentView(gameView)
    }

    override fun onPause() {
        if (::gameView.isInitialized) gameView.pauseForLifecycle()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        if (::gameView.isInitialized) gameView.resumeForLifecycle()
    }

    override fun onDestroy() {
        if (::gameView.isInitialized) gameView.release()
        super.onDestroy()
    }
}
