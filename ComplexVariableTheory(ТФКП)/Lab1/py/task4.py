import time
import turtle

# function of making koch snowflake
# size is the total length of the 0-order straight line, n is the order
def koch(size, n):
    if n == 0:
        turtle.fd(size)
    else:
        # The angle the turtle turns when drawing the one order
        for angle in [0, 60, -120, 60]:
            turtle.left(angle)
            koch(size/3, n-1)

def main(size, n):
    turtle.setup(800, 400)
    turtle.pensize(2)
    turtle.penup()
    turtle.goto(-300, 100)
    turtle.pendown()
    turtle.pencolor('red')
    koch(size, n)
    turtle.right(120)
    turtle.pencolor('green')
    koch(size, n)
    turtle.right(120)
    turtle.pencolor('blue')
    koch(size, n)
    turtle.right(120)
    turtle.hideturtle()

size, n = eval(input('Please enter the size, n: '))
main(size, n)
print("Program Ended")
time.sleep(5)