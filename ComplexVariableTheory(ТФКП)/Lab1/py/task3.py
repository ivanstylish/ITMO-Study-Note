import turtle
import time


def julia(c, z, max_iter):
    """
    计算点z在朱利亚集中的迭代次数
    c: 固定参数（复数）
    z: 测试点（复数）
    max_iter: 最大迭代次数
    返回: 逃逸前的迭代次数
    """
    for n in range(max_iter):
        if abs(z) > 2:  # 逃逸条件
            return n
        z = z * z + c  # 朱利亚迭代公式
    return max_iter


def draw_julia_complete():
    """
    完整的朱利亚集绘制程序，支持不同c值和迭代次数
    """
    # 设置画布
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.title("朱利亚集 - 完整版本")
    screen.bgcolor("black")
    screen.tracer(0, 0)  # 关闭动画

    # 创建turtle
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.penup()

    # 定义不同的c值（朱利亚集参数）
    c_value = [
        complex(-0.5251993, 0.5251993),  # 漂亮的螺旋
    ]

    c_descriptions = [
        "漂亮的螺旋 (-0.5251993 + 0.5251993i)",
        "经典树枝状 (-0.7 + 0.27015i)",
        "复杂结构 (-0.8 + 0.156i)",
        "康威型 (0.285 + 0.01i)",
        "雪花状 (-0.4 + 0.6i)",
        "星云状 (0.3 + 0.5i)"
    ]

    # 定义不同的最大迭代次数
    max_iters = [20, 50, 100, 200]

    print("朱利亚集可视化程序")
    print("==================")

    # 为每个c值和迭代次数组合绘制图像
    for c_idx, (c, description) in enumerate(zip(c_value, c_descriptions)):
        print(f"\nc值 {c_idx + 1}: {description}")

        for iter_idx, max_iter in enumerate(max_iters):
            print(f"  绘制中... 迭代次数: {max_iter}")
            start_time = time.time()

            # 清空画布
            t.clear()
            screen.bgcolor("black")

            # 设置视图参数
            x_min, x_max = -1.5, 1.5
            y_min, y_max = -1.5, 1.5
            width, height = 400, 400

            # 缩放因子
            x_scale = (x_max - x_min) / width
            y_scale = (y_max - y_min) / height

            # 遍历每个像素
            for x_pixel in range(width):
                for y_pixel in range(height):
                    # 将像素坐标转换为复数坐标
                    x = x_min + x_pixel * x_scale
                    y = y_min + y_pixel * y_scale
                    z = complex(x, y)

                    # 计算迭代次数
                    iter_count = julia(c, z, max_iter)

                    # 根据迭代次数选择颜色
                    if iter_count == max_iter:
                        color = "white"  # 朱利亚集内的点
                    else:
                        # 创建彩色效果
                        intensity = iter_count / max_iter
                        if intensity < 0.2:
                            color = "dark blue"
                        elif intensity < 0.4:
                            color = "blue"
                        elif intensity < 0.6:
                            color = "cyan"
                        elif intensity < 0.8:
                            color = "yellow"
                        else:
                            color = "red"

                    # 绘制点
                    screen_x = (x_pixel - width / 2) * 800 / width
                    screen_y = (height / 2 - y_pixel) * 800 / height
                    t.goto(screen_x, screen_y)
                    t.dot(800 // width, color)

                # 每行完成后更新屏幕
                if x_pixel % 50 == 0:
                    screen.update()

            screen.update()
            end_time = time.time()
            print(f"    完成! 耗时: {end_time - start_time:.2f}秒")

            # 等待用户查看
            print("    按任意键继续...")
            input()

    print("\n所有c值绘制完成!")
    screen.exitonclick()


# 运行程序
if __name__ == "__main__":
    draw_julia_complete()