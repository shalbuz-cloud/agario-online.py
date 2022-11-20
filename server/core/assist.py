from typing import Union


def wall_check(
        coord: Union[int, float], wall: Union[int, float],
        speed_coord: Union[int, float], radius: Union[int, float]
) -> None:
    """Проверка пересечения стен.
    Если достигли левой стены, разрешаем идти только вправо,
    если правой, то только влево.
    Если достигли верхней стены, разрешаем идти только вниз,
    если нижней, то вверх.
    """

    if coord - radius <= 0:  # Верхняя/левая стена
        if speed_coord >= 0:
            coord += speed_coord
    elif coord + radius >= wall:  # Нижняя/правая стена
        if speed_coord <= 0:
            coord += speed_coord
    else:  # Если не достиг стен
        coord += speed_coord
