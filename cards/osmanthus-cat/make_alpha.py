"""将生图模型输出的绿幕人物层转换为真实透明通道。"""

from pathlib import Path

from PIL import Image, ImageFilter


def key_alpha(red, green, blue):
    """根据绿色相对其余通道的优势计算柔和透明度。"""
    dominance = green - max(red, blue)
    if green < 100 or dominance <= 35:
        return 255
    if dominance >= 110:
        return 0
    return round(255 * (110 - dominance) / 75)


def remove_green_spill(red, green, blue, alpha):
    """在半透明边缘削弱绿幕溢色，保留衣物原有的灰绿色。"""
    if alpha <= 0:
        return 0, 0, 0, 0
    if alpha >= 255:
        return red, green, blue, 255
    coverage = alpha / 255
    corrected_green = round((green - (1 - coverage) * 255) / coverage)
    corrected_green = max(0, min(corrected_green, max(red, blue) + 28))
    return red, corrected_green, blue, alpha


def main():
    """读取绿幕源图并生成可供 Blender 与网页使用的透明 PNG。"""
    asset_dir = Path(__file__).resolve().parent / "assets"
    source = Image.open(asset_dir / "subject-chroma.png").convert("RGB")
    source_pixels = source.load()
    alpha = Image.new("L", source.size, 255)
    alpha_pixels = alpha.load()

    for y in range(source.height):
        for x in range(source.width):
            alpha_pixels[x, y] = key_alpha(*source_pixels[x, y])

    edge_alpha = alpha.filter(ImageFilter.MinFilter(5))
    edge_pixels = edge_alpha.load()
    result = Image.new("RGBA", source.size)
    result_pixels = result.load()

    for y in range(source.height):
        for x in range(source.width):
            red, green, blue = source_pixels[x, y]
            if edge_pixels[x, y] < 255:
                green = min(green, max(red, blue) + 6)
            result_pixels[x, y] = remove_green_spill(
                red, green, blue, alpha_pixels[x, y]
            )
    result.save(asset_dir / "subject.png")


if __name__ == "__main__":
    main()
