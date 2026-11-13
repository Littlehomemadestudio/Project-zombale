package com.littlehomemadestudio.deadsignal

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class GameEngineTest {
    @Test
    fun newRunStartsWithAPlayableLoadout() {
        val game = GameEngine(7L)
        game.start(RunMode.CLEANUP)

        assertEquals(RunState.PLAYING, game.state)
        assertEquals(1, game.wave)
        assertEquals(100f, game.barricadeHealth, 0.001f)
        assertEquals(12, game.currentMagazine)
        assertEquals(72, game.currentReserve)
    }

    @Test
    fun identicalSeedsProduceIdenticalFirstSpawn() {
        val first = GameEngine(99L)
        val second = GameEngine(99L)
        first.start(RunMode.DEFENSE)
        second.start(RunMode.DEFENSE)

        repeat(25) {
            first.update(0.05f)
            second.update(0.05f)
        }

        assertEquals(first.zombies.size, second.zombies.size)
        assertTrue(first.zombies.isNotEmpty())
        assertEquals(first.zombies.first().kind, second.zombies.first().kind)
        assertEquals(first.zombies.first().x, second.zombies.first().x, 0.001f)
        assertEquals(first.zombies.first().y, second.zombies.first().y, 0.001f)
    }

    @Test
    fun firingConsumesARealRoundAndDamagesAnEnemy() {
        val game = GameEngine(13L)
        game.start(RunMode.CLEANUP)
        repeat(20) { game.update(0.05f) }
        val target = game.zombies.first()
        val healthBefore = target.health

        game.setAim(target.x, target.y)
        game.setTrigger(true)
        game.update(0.05f)
        game.setTrigger(false)

        assertEquals(11, game.currentMagazine)
        assertTrue(target.health < healthBefore || game.score > 0)
    }

    @Test
    fun reloadRestoresMagazineWithoutCreatingReserveAmmo() {
        val game = GameEngine(17L)
        game.start(RunMode.CLEANUP)
        game.setAim(850f, 900f)
        game.setTrigger(true)
        game.update(0.05f)
        game.setTrigger(false)

        game.reload()
        repeat(30) { game.update(0.05f) }

        assertEquals(12, game.currentMagazine)
        assertEquals(71, game.currentReserve)
    }

    @Test
    fun weaponSwitchingChangesTheMagazineAndWeaponIdentity() {
        val game = GameEngine(23L)
        game.start(RunMode.DEFENSE)
        game.switchWeapon()

        assertEquals(WeaponType.CARBINE, game.selectedWeapon)
        assertEquals(28, game.currentMagazine)
    }
}
