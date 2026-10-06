from .entities import Player, Ghost, GhostStates


class GameState:
    def check_collisions(self, player: Player, ghosts: list[Ghost], points_per_ghost: int) -> None:
        for ghost in ghosts:
            if (player.x, player.y) != (ghost.x, ghost.y):
                continue

            if ghost.state == GhostStates.SCARED:
                player.score += points_per_ghost
                ghost.state = GhostStates.EATEN
            elif ghost.state == GhostStates.CHASE:
                player.lives -= 1
                player.respawn()
