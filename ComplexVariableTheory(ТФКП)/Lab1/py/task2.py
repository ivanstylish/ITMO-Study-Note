import turtle
import time


def mandelbrot(c, max_iter):
    """
    计算点c在曼德勃罗集中的迭代次数
    c: 复数点
    max_iter: 最大迭代次数
    返回: 逃逸前的迭代次数
    """
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:  # 逃逸条件
            return n
        z = z * z + c  # 曼德勃罗迭代公式
    return max_iter  # 如果未逃逸，返回最大迭代次数


def draw_mandelbrot_complete():
    """
    完整的曼德勃罗集绘制程序，支持不同迭代次数和放大功能
    """
    # 设置画布
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.title("曼德勃罗集")
    screen.bgcolor("black")
    screen.tracer(0, 0)  # 关闭动画

    # 创建turtle
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.penup()

    # 定义不同的视图区域（用于放大）
    views = [
        # (x_min, x_max, y_min, y_max, 描述, 推荐迭代次数)
        (-2.0, 1.0, -1.5, 1.5, "完整视图", 50),
        (-0.5, 0.5, -0.5, 0.5, "中心放大", 100),
        (-0.75, -0.65, 0.1, 0.2, "边缘细节", 200),
    ]

    # 定义不同的最大迭代次数
    max_iters = [20, 50, 100, 200]

    print("曼德勃罗集可视化程序")
    print("====================")

    # 为每个视图和迭代次数组合绘制图像
    for view_idx, (x_min, x_max, y_min, y_max, description, recommended_iter) in enumerate(views):
        print(f"\n视图 {view_idx + 1}: {description}")
        print(f"坐标范围: x[{x_min:.2f}, {x_max:.2f}], y[{y_min:.2f}, {y_max:.2f}]")

        for iter_idx, max_iter in enumerate(max_iters):
            print(f"  绘制中... 迭代次数: {max_iter}")
            start_time = time.time()

            # 清空画布
            t.clear()
            screen.bgcolor("black")

            # 设置分辨率（根据视图大小调整）
            if (x_max - x_min) < 1.0:
                width, height = 400, 400  # 放大视图使用较高分辨率
            else:
                width, height = 300, 300  # 完整视图使用较低分辨率

            # 缩放因子
            x_scale = (x_max - x_min) / width
            y_scale = (y_max - y_min) / height

            # 遍历每个像素
            for x_pixel in range(width):
                for y_pixel in range(height):
                    # 将像素坐标转换为复数坐标
                    x = x_min + x_pixel * x_scale
                    y = y_min + y_pixel * y_scale
                    c = complex(x, y)

                    # 计算迭代次数
                    iter_count = mandelbrot(c, max_iter)

                    # 根据迭代次数选择颜色
                    if iter_count == max_iter:
                        color = "black"  # 曼德勃罗集内的点
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

    print("\n所有视图绘制完成!")
    screen.exitonclick()


# 运行程序
if __name__ == "__main__":
    draw_mandelbrot_complete()