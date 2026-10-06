from .entities import Player, Ghost, GhostStates


class GameState:
    def _player_respawn(self, player: Player) -> None:
        player.x = player.spawn_x
        player.y = player.spawn_y

    def check_collision(self, player: Player, ghosts: list[Ghost], config) -> None:
        points_per_ghost = config["points_per_ghost"]

        for ghost in ghosts:
            if (player.x, player.y) != (ghost.x, ghost.y):
                continue

            if ghost.state == GhostStates.SCARED:
                player.score += points_per_ghost
                ghost.state = GhostStates.EATEN
            elif ghost.state == GhostStates.CHASE:
                player.lives -= 1
                self._player_respawn(player)
