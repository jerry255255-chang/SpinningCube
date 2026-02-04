import math
import time
import os

# 初始化全域變數
A, B, C = 0.0, 0.0, 0.0
width, height = 160, 44
background_ascii_code = '.'
distance_from_cam = 100
K1 = 40
increment_speed = 0.6

# 投影座標與緩衝區
z_buffer = [0.0] * (width * height)
buffer = [background_ascii_code] * (width * height)

def calculate_x(i, j, k):
    return (j * math.sin(A) * math.sin(B) * math.cos(C) - 
            k * math.cos(A) * math.sin(B) * math.cos(C) +
            j * math.cos(A) * math.sin(C) + 
            k * math.sin(A) * math.sin(C) + 
            i * math.cos(B) * math.cos(C))

def calculate_y(i, j, k):
    return (j * math.cos(A) * math.cos(C) + 
            k * math.sin(A) * math.cos(C) -
            j * math.sin(A) * math.sin(B) * math.sin(C) + 
            k * math.cos(A) * math.sin(B) * math.sin(C) -
            i * math.cos(B) * math.sin(C))

def calculate_z(i, j, k):
    return k * math.cos(A) * math.cos(B) - j * math.sin(A) * math.cos(B) + i * math.sin(B)

def calculate_for_surface(cube_x, cube_y, cube_z, ch, horizontal_offset):
    global x, y, z, ooz, xp, yp, idx
    x = calculate_x(cube_x, cube_y, cube_z)
    y = calculate_y(cube_x, cube_y, cube_z)
    z = calculate_z(cube_x, cube_y, cube_z) + distance_from_cam

    if z == 0: return # 防止除以零
    ooz = 1 / z

    # 2D 投影計算
    xp = int(width / 2 + horizontal_offset + K1 * ooz * x * 2)
    yp = int(height / 2 + K1 * ooz * y)

    idx = xp + yp * width
    if 0 <= idx < width * height:
        if ooz > z_buffer[idx]:
            z_buffer[idx] = ooz
            buffer[idx] = ch

def render_frame():
    global A, B, C, buffer, z_buffer
    # 清空緩衝區
    buffer = [background_ascii_code] * (width * height)
    z_buffer = [0.0] * (width * height)

    # 繪製三個不同大小與位置的方塊
    # 設定 (cubeWidth, horizontalOffset)
    cubes = [(20, -2 * 20)] # (10, 1 * 10), (5, 8 * 5)

    for cube_width, horizontal_offset in cubes:
        # 這裡使用 np.arange 會更快，但為了保持純 Python 環境使用 while 模擬
        curr_x = -float(cube_width)
        while curr_x < cube_width:
            curr_y = -float(cube_width)
            while curr_y < cube_width:
                # 六個面
                calculate_for_surface(curr_x, curr_y, -cube_width, '@', horizontal_offset)
                calculate_for_surface(cube_width, curr_y, curr_x, '$', horizontal_offset)
                calculate_for_surface(-cube_width, curr_y, -curr_x, '~', horizontal_offset)
                calculate_for_surface(-curr_x, curr_y, cube_width, '#', horizontal_offset)
                calculate_for_surface(curr_x, -cube_width, -curr_y, ';', horizontal_offset)
                calculate_for_surface(curr_x, cube_width, curr_y, '+', horizontal_offset)
                curr_y += increment_speed
            curr_x += increment_speed

    # 輸出到終端機
    output = []
    for i in range(width * height):
        output.append(buffer[i])
        if (i + 1) % width == 0:
            output.append('\n')
    
    # 使用 ANSI escape code 回到左上角 (避免閃爍)
    print("\x1b[H" + "".join(output), end="")

    # 更新角度
    A += 0.05
    B += 0.05
    C += 0.01

if __name__ == "__main__":
    # 清除螢幕
    print("\x1b[2J", end="")
    try:
        while True:
            render_frame()
            time.sleep(0.05) # 控制 FPS
    except KeyboardInterrupt:
        print("\n動畫已停止。")