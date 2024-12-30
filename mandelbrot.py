import tkinter as tk
from PIL import Image, ImageTk
import multiprocessing

WIDTH = 1500
MIN_X, MAX_X = -2, 1
MIN_Y, MAX_Y = -1, 1
ITERATIONS = 200
HEIGHT = int(WIDTH / (MAX_X - MIN_X) * (MAX_Y - MIN_Y))

def mandelbrot(in_re, in_im):
    c_re = (MAX_X - MIN_X) / WIDTH * in_re + MIN_X
    c_im = (MAX_Y - MIN_Y) / HEIGHT * in_im + MIN_Y
    n = 0
    x_re, x2_re = c_re, c_re * c_re
    x_im, x2_im = c_im, c_im * c_im
    while n < ITERATIONS and x2_re + x2_im < 4:
        x_im = 2 * x_re * x_im + c_im
        x_re = x2_re - x2_im + c_re
        x2_re = x_re * x_re
        x2_im = x_im * x_im
        n += 1
    return (1 - n / ITERATIONS) ** 3

def calculate_row(y):
    row = []
    for x in range(WIDTH):
        brightness = mandelbrot(x, y)
        color_value = int(brightness * 255)
        row.append((color_value, color_value, color_value))
    return y, row

def draw_iterations(canvas, start_x, start_y, num_iterations):
    c_re = (MAX_X - MIN_X) / WIDTH * start_x + MIN_X
    c_im = (MAX_Y - MIN_Y) / HEIGHT * start_y + MIN_Y
    x_re, x_im = c_re, c_im

    canvas.create_oval(start_x-2, start_y-2, start_x+2, start_y+2, fill='blue', outline='blue')

    points = [(start_x, start_y)]

    for _ in range(num_iterations):
        x_re_old = x_re
        x_re = x_re * x_re - x_im * x_im + c_re
        x_im = 2 * x_re_old * x_im + c_im

        screen_x = int((x_re - MIN_X) / (MAX_X - MIN_X) * WIDTH)
        screen_y = int((x_im - MIN_Y) / (MAX_Y - MIN_Y) * HEIGHT)

        points.append((screen_x, screen_y))

        if x_re * x_re + x_im * x_im > 10:
            break

    num_points = len(points)
    for i in range(num_points - 1, 0, -1):
        start_x, start_y = points[i-1]
        end_x, end_y = points[i]

        fade_factor = int(255 * (1 - 0.5 * (i / num_points)))
        color = f'#{fade_factor:02x}{0:02x}{0:02x}'

        canvas.create_line(start_x, start_y, end_x, end_y, fill=color)

def on_drag(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y
    update_canvas()

def update_canvas():
    num_iterations = iteration_slider.get()
    canvas.delete("all")
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    draw_iterations(canvas, last_x, last_y, num_iterations)
    canvas.create_window(10, 10, anchor=tk.NW, window=iteration_slider)

def increment_slider(event):
    current_value = iteration_slider.get()
    iteration_slider.set(min(current_value + 1, iteration_slider.cget('to')))
    update_canvas()

def decrement_slider(event):
    current_value = iteration_slider.get()
    iteration_slider.set(max(current_value - 1, iteration_slider.cget('from')))
    update_canvas()

def main():
    global photo, canvas, iteration_slider, last_x, last_y
    root = tk.Tk()
    root.title("Mandelbrot Set")
    image = Image.new("RGB", (WIDTH, HEIGHT))

    with multiprocessing.Pool() as pool:
        results = pool.map(calculate_row, range(HEIGHT))

    for y, row in results:
        for x, color in enumerate(row):
            image.putpixel((x, y), color)

    photo = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)

    iteration_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label='Iterations', length=100)
    iteration_slider.set(25)
    iteration_slider.pack()
    canvas.create_window(10, 10, anchor=tk.NW, window=iteration_slider)

    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<Button-1>", on_drag)

    root.bind("<Right>", increment_slider)
    root.bind("<Left>", decrement_slider)

    last_x, last_y = WIDTH // 2, HEIGHT // 2

    iteration_slider.config(command=lambda val: update_canvas())

    root.mainloop()

if __name__ == "__main__":
    main()
