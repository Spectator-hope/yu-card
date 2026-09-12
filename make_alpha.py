"""把生成图中的棋盘背景转换为真实透明通道。"""

from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


def is_background(pixel):
    """判断像素是否属于近中性灰的棋盘背景。"""
    red, green, blue = pixel
    high = max(pixel)
    low = min(pixel)
    return 72 <= high <= 248 and high - low <= 18


def main():
    """从画布边缘泛洪，生成带柔化边缘的真实透明主体图。"""
    path = Path(__file__).resolve().parent / "assets" / "subject.png"
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()
    visited = bytearray(width * height)
    queue = deque()

    def enqueue(x, y):
        index = y * width + x
        if not visited[index] and is_background(pixels[x, y]):
            visited[index] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)
    for x, y in ((220, 220), (210, 300), (230, 330), (200, 400), (180, 500),
                 (230, 700), (260, 760), (220, 850), (120, 900), (240, 900),
                 (155, 1040), (180, 1050), (820, 250),
                 (880, 300), (930, 700), (980, 900)):
        enqueue(x, y)

    while queue:
        x, y = queue.popleft()
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    alpha = Image.new("L", image.size, 255)
    alpha_data = alpha.load()
    for y in range(height):
        row = y * width
        for x in range(width):
            if visited[row + x]:
                alpha_data[x, y] = 0

    alpha = alpha.filter(ImageFilter.GaussianBlur(0.7))
    result = image.convert("RGBA")
    result.putalpha(alpha)
    result.save(path)


if __name__ == "__main__":
    main()
