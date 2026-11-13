package com.littlehomemadestudio.deadsignal

import java.util.Random
import kotlin.math.PI
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

enum class RunMode { CLEANUP, DEFENSE }
enum class RunState { MENU, PLAYING, PAUSED, GAME_OVER, VICTORY }

enum class EnemyKind(val health: Int, val speed: Float, val reward: Int, val radius: Float) {
    SHAMBLER(48, 47f, 15, 36f),
    RUNNER(30, 88f, 22, 29f),
    BRUTE(145, 28f, 55, 51f)
}

enum class WeaponType(
    val title: String,
    val magazineSize: Int,
    val reserveStart: Int,
    val damage: Int,
    val interval: Float,
    val spread: Float,
    val reloadSeconds: Float
) {
    SIDEARM("SIDEARM", 12, 72, 44, 0.34f, 0.035f, 1.05f),
    CARBINE("CARBINE", 28, 140, 25, 0.115f, 0.052f, 1.45f),
    BREACHER("BREACHER", 6, 42, 78, 0.72f, 0.19f, 1.7f)
}

data class Magazine(var rounds: Int, var reserve: Int)

data class Zombie(
    val id: Int,
    val kind: EnemyKind,
    var x: Float,
    var y: Float,
    var health: Int,
    var attackClock: Float = 0f,
    var hitFlash: Float = 0f,
    var phase: Float = 0f
)

data class CombatParticle(
    var x: Float,
    var y: Float,
    var vx: Float,
    var vy: Float,
    var life: Float,
    val maxLife: Float
)

class GameEngine(seed: Long = 41L) {
    companion object {
        const val WORLD_WIDTH = 900f
        const val WORLD_HEIGHT = 1600f
        const val PLAYER_X = 150f
        const val PLAYER_Y = 930f
        const val DEFENSE_LINE = 280f
        const val MAX_BARRICADE = 100f
        const val MAX_PLAYER_HEALTH = 100f
    }

    private val random = Random(seed)
    private val magazines = mutableMapOf(
        WeaponType.SIDEARM to Magazine(WeaponType.SIDEARM.magazineSize, WeaponType.SIDEARM.reserveStart),
        WeaponType.CARBINE to Magazine(WeaponType.CARBINE.magazineSize, WeaponType.CARBINE.reserveStart),
        WeaponType.BREACHER to Magazine(WeaponType.BREACHER.magazineSize, WeaponType.BREACHER.reserveStart)
    )

    val zombies = mutableListOf<Zombie>()
    val particles = mutableListOf<CombatParticle>()

    var state: RunState = RunState.MENU
        private set
    var mode: RunMode = RunMode.CLEANUP
        private set
    var selectedWeapon: WeaponType = WeaponType.SIDEARM
        private set
    var score: Int = 0
        private set
    var wave: Int = 1
        private set
    var barricadeHealth: Float = MAX_BARRICADE
        private set
    var playerHealth: Float = MAX_PLAYER_HEALTH
        private set
    var repairCharges: Int = 3
        private set
    var aimX: Float = 720f
        private set
    var aimY: Float = PLAYER_Y
        private set
    var shotFlash: Float = 0f
        private set
    var recoil: Float = 0f
        private set
    var hitMarker: Float = 0f
        private set

    private var nextZombieId = 0
    private var spawnedInWave = 0
    private var waveSize = 6
    private var spawnClock = 0.8f
    private var intermission = 0f
    private var fireClock = 0f
    private var reloadClock = 0f
    private var triggerHeld = false
    private var endedNotified = false

    val currentMagazine: Int
        get() = magazines.getValue(selectedWeapon).rounds
    val currentReserve: Int
        get() = magazines.getValue(selectedWeapon).reserve
    val isReloading: Boolean
        get() = reloadClock > 0f
    val corridor: Int
        get() = wave
    val zombiesRemainingInWave: Int
        get() = (waveSize - spawnedInWave).coerceAtLeast(0) + zombies.size

    fun start(newMode: RunMode) {
        mode = newMode
        state = RunState.PLAYING
        score = 0
        wave = 1
        barricadeHealth = MAX_BARRICADE
        playerHealth = MAX_PLAYER_HEALTH
        repairCharges = 3
        selectedWeapon = WeaponType.SIDEARM
        magazines.values.forEach {
            it.rounds = when (magazines.entries.firstOrNull { entry -> entry.value === it }?.key) {
                WeaponType.SIDEARM -> WeaponType.SIDEARM.magazineSize
                WeaponType.CARBINE -> WeaponType.CARBINE.magazineSize
                else -> WeaponType.BREACHER.magazineSize
            }
            it.reserve = when (magazines.entries.firstOrNull { entry -> entry.value === it }?.key) {
                WeaponType.SIDEARM -> WeaponType.SIDEARM.reserveStart
                WeaponType.CARBINE -> WeaponType.CARBINE.reserveStart
                else -> WeaponType.BREACHER.reserveStart
            }
        }
        zombies.clear()
        particles.clear()
        nextZombieId = 0
        spawnedInWave = 0
        waveSize = 6
        spawnClock = 0.75f
        intermission = 0f
        fireClock = 0f
        reloadClock = 0f
        triggerHeld = false
        shotFlash = 0f
        recoil = 0f
        hitMarker = 0f
        endedNotified = false
    }

    fun pause() {
        if (state == RunState.PLAYING) {
            state = RunState.PAUSED
            triggerHeld = false
        }
    }

    fun resume() {
        if (state == RunState.PAUSED) state = RunState.PLAYING
    }

    fun setAim(x: Float, y: Float) {
        aimX = x.coerceIn(PLAYER_X + 20f, WORLD_WIDTH - 12f)
        aimY = y.coerceIn(500f, 1250f)
    }

    fun setTrigger(held: Boolean) {
        triggerHeld = held && state == RunState.PLAYING
    }

    fun reload() {
        if (state != RunState.PLAYING || reloadClock > 0f) return
        val magazine = magazines.getValue(selectedWeapon)
        if (magazine.rounds >= selectedWeapon.magazineSize || magazine.reserve <= 0) return
        reloadClock = selectedWeapon.reloadSeconds
        triggerHeld = false
    }

    fun switchWeapon() {
        if (state != RunState.PLAYING || reloadClock > 0f) return
        val unlocked = if (score >= 180) {
            listOf(WeaponType.SIDEARM, WeaponType.CARBINE, WeaponType.BREACHER)
        } else {
            listOf(WeaponType.SIDEARM, WeaponType.CARBINE)
        }
        val next = (unlocked.indexOf(selectedWeapon) + 1) % unlocked.size
        selectedWeapon = unlocked[next]
        triggerHeld = false
        fireClock = 0f
    }

    fun repair() {
        if (state != RunState.PLAYING || repairCharges <= 0 || barricadeHealth >= MAX_BARRICADE) return
        barricadeHealth = min(MAX_BARRICADE, barricadeHealth + 32f)
        repairCharges--
        addParticles(270f, 950f, 7, 0xFFF0B44C.toInt())
    }

    fun consumeEndNotification(): Boolean {
        if ((state == RunState.GAME_OVER || state == RunState.VICTORY) && !endedNotified) {
            endedNotified = true
            return true
        }
        return false
    }

    fun update(deltaSeconds: Float) {
        if (state != RunState.PLAYING) return
        val dt = deltaSeconds.coerceIn(0f, 0.05f)
        if (dt <= 0f) return

        fireClock = (fireClock - dt).coerceAtLeast(0f)
        shotFlash = (shotFlash - dt).coerceAtLeast(0f)
        recoil = (recoil - dt * 3.2f).coerceAtLeast(0f)
        hitMarker = (hitMarker - dt * 2.8f).coerceAtLeast(0f)

        if (reloadClock > 0f) {
            reloadClock -= dt
            if (reloadClock <= 0f) finishReload()
        } else if (triggerHeld && fireClock <= 0f) {
            fireOnce()
        }

        if (intermission > 0f) {
            intermission -= dt
            if (intermission <= 0f) advanceWave()
        } else {
            if (spawnedInWave < waveSize) {
                spawnClock -= dt
                if (spawnClock <= 0f && zombies.size < 10) {
                    spawnZombie()
                    spawnClock = max(0.58f, 1.35f - wave * 0.055f) + random.nextFloat() * 0.38f
                }
            }
            updateZombies(dt)
            if (spawnedInWave >= waveSize && zombies.isEmpty()) intermission = 1.65f
        }

        updateParticles(dt)
        if (playerHealth <= 0f) state = RunState.GAME_OVER
    }

    private fun advanceWave() {
        if (mode == RunMode.CLEANUP && wave >= 5) {
            state = RunState.VICTORY
            return
        }
        wave++
        spawnedInWave = 0
        waveSize = if (mode == RunMode.CLEANUP) 6 + (wave - 1) * 2 else 7 + wave * 2
        spawnClock = 0.85f
        barricadeHealth = min(MAX_BARRICADE, barricadeHealth + 10f)
        if (mode == RunMode.DEFENSE && wave % 3 == 0) repairCharges = min(5, repairCharges + 1)
    }

    private fun spawnZombie() {
        val roll = random.nextFloat()
        val kind = when {
            wave >= 3 && roll < 0.16f -> EnemyKind.BRUTE
            roll < 0.36f -> EnemyKind.RUNNER
            else -> EnemyKind.SHAMBLER
        }
        val lanes = floatArrayOf(770f, 890f, 1010f, 1125f)
        val y = lanes[random.nextInt(lanes.size)] + (random.nextFloat() - 0.5f) * 26f
        zombies += Zombie(nextZombieId++, kind, 875f, y, kind.health, phase = random.nextFloat() * 6f)
        spawnedInWave++
    }

    private fun updateZombies(dt: Float) {
        val iterator = zombies.iterator()
        while (iterator.hasNext()) {
            val zombie = iterator.next()
            zombie.hitFlash = (zombie.hitFlash - dt).coerceAtLeast(0f)
            zombie.phase += dt * (if (zombie.kind == EnemyKind.RUNNER) 8f else 3.5f)
            if (zombie.x > DEFENSE_LINE) {
                val lanePressure = if (zombie.kind == EnemyKind.RUNNER) 1.08f else 1f
                zombie.x -= zombie.kind.speed * lanePressure * dt
                if (zombie.x <= DEFENSE_LINE) zombie.x = DEFENSE_LINE
            } else {
                zombie.attackClock += dt
                if (zombie.attackClock >= 0.85f) {
                    zombie.attackClock = 0f
                    if (barricadeHealth > 0f) {
                        barricadeHealth = (barricadeHealth - if (zombie.kind == EnemyKind.BRUTE) 13f else 7f).coerceAtLeast(0f)
                        addParticles(270f, zombie.y, 2, 0xFFD99A58.toInt())
                    } else {
                        playerHealth = (playerHealth - if (zombie.kind == EnemyKind.BRUTE) 12f else 6f).coerceAtLeast(0f)
                    }
                }
            }
        }
    }

    private fun fireOnce() {
        val magazine = magazines.getValue(selectedWeapon)
        if (magazine.rounds <= 0) {
            reload()
            return
        }
        magazine.rounds--
        fireClock = selectedWeapon.interval
        shotFlash = 0.075f
        recoil = 1f
        val angle = atan2((aimY - PLAYER_Y).toDouble(), (aimX - PLAYER_X).toDouble()).toFloat()
        val range = 760f
        val candidates = zombies
            .map { zombie ->
                val dx = zombie.x - PLAYER_X
                val dy = zombie.y - PLAYER_Y
                val distance = sqrt(dx * dx + dy * dy)
                val targetAngle = atan2(dy.toDouble(), dx.toDouble()).toFloat()
                val difference = absAngle(angle - targetAngle)
                Triple(zombie, distance, difference)
            }
            .filter { it.second <= range && it.third <= selectedWeapon.spread + it.first.kind.radius / max(120f, it.second) }
            .sortedBy { it.second }
        val targetCount = if (selectedWeapon == WeaponType.BREACHER) 2 else 1
        var hit = false
        candidates.take(targetCount).forEach { candidate ->
            val zombie = candidate.first
            zombie.health -= selectedWeapon.damage
            zombie.hitFlash = 0.13f
            hit = true
            addParticles(zombie.x, zombie.y, if (selectedWeapon == WeaponType.BREACHER) 8 else 4, 0xFFCB735C.toInt())
            if (zombie.health <= 0) {
                score += zombie.kind.reward
                addParticles(zombie.x, zombie.y, 10, 0xFFB84F43.toInt())
            }
        }
        if (hit) hitMarker = 1f
        zombies.removeAll { it.health <= 0 }
        addParticles(190f, 900f - recoil * 8f, 2, 0xFFF5B84B.toInt())
    }

    private fun finishReload() {
        val magazine = magazines.getValue(selectedWeapon)
        val needed = selectedWeapon.magazineSize - magazine.rounds
        val loaded = min(needed, magazine.reserve)
        magazine.rounds += loaded
        magazine.reserve -= loaded
        reloadClock = 0f
    }

    private fun updateParticles(dt: Float) {
        val iterator = particles.iterator()
        while (iterator.hasNext()) {
            val particle = iterator.next()
            particle.life -= dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy += 180f * dt
            if (particle.life <= 0f) iterator.remove()
        }
    }

    private fun addParticles(x: Float, y: Float, count: Int, color: Int) {
        repeat(count) {
            val angle = random.nextFloat() * (2f * PI.toFloat())
            val speed = 35f + random.nextFloat() * 170f
            val life = 0.18f + random.nextFloat() * 0.34f
            particles += CombatParticle(
                x, y,
                cos(angle) * speed,
                sin(angle) * speed - 30f,
                life, life
            )
        }
        while (particles.size > 120) particles.removeAt(0)
    }

    private fun absAngle(value: Float): Float {
        val wrapped = (value + PI.toFloat()) % (2f * PI.toFloat())
        val normalized = if (wrapped < 0f) wrapped + 2f * PI.toFloat() else wrapped
        return kotlin.math.abs(normalized - PI.toFloat())
    }
}
